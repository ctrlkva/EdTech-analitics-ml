import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import streamlit as st
from pathlib import Path

# =========================================================================
# 1. ГЛОБАЛЬНАЯ НАСТРОЙКА ИНТЕРФЕЙСА STREAMLIT
# =========================================================================
st.set_page_config(
    page_title="Прогноз для онлайн-школы", 
    page_icon="📈", 
    layout="wide"  # Двухколоночный режим отображения контента
)

st.title("🔮 Прогнозирование посещаемости:")
st.markdown("---")


# =========================================================================
# 2. ОПТИМИЗИРОВАННЫЙ ПАЙПЛАЙН ЗАГРУЗКИ И ОЧИСТКИ ВРЕМЕННОГО РЯДА
# =========================================================================
@st.cache_data  # Хеширование результатов для предотвращения повторного ETL при интерактивных действиях
def load_and_process_data():
    """
    Выполняет полный цикл сборки данных (ETL) из реляционных CSV-выгрузок,
    фильтрацию целевого бизнес-сегмента и многоэтапную очистку временного ряда от аномалий.
    """
    # Динамическое определение корневой директории проекта относительно текущего скрипта
    root_dir = Path(__file__).resolve().parent.parent
    
    # Поиск директории с сырыми данными (регистронезависимый поиск папки 'data')
    data_dir = None
    for folder in root_dir.iterdir():
        if folder.is_dir() and folder.name.lower() == "data":
            data_dir = folder
            break

    if data_dir is None or not data_dir.exists():
        st.error(f"Критическая ошибка: Папка 'data' не найдена в корне {root_dir}")
        st.stop()

    # Маппинг файлов в папке для безопасного извлечения по нижнему регистру имени
    files = {f.name.lower(): f for f in data_dir.iterdir() if f.is_file()}

    try:
        groups = pd.read_csv(files["groups.csv"])
        lessons = pd.read_csv(files["lessons.csv"])
        attendances = pd.read_csv(files["attendances.csv"])
    except KeyError as e:
        st.error(f"В папке данных не найден файл: {e}. Доступные файлы: {list(files.keys())}")
        st.stop()

    # --- РЕЛЯЦИОННОЕ ОБЪЕДИНЕНИЕ (STAGING LAYER) ---
    # Связывание транзакционных логов посещаемости с расписанием занятий
    bd_online = lessons.merge(
        attendances, left_on="_id", right_on="lessonId", how="inner"
    )
    # Обогащение выборки метаданными учебных групп (филиалы, направления)
    bd_online = bd_online.merge(
        groups, left_on="groupId", right_on="_id", how="inner"
    )

    # Жесткая бизнес-комфильтрация: выделение целевого онлайн-филиала платформы
    bd_online = bd_online[
        bd_online["filial"] == "63c63702397ca6783eb57fa2"
    ].copy()

    # Парсинг временных меток с приведением к единому стандарту UTC и валидацией битых записей
    bd_online["parsed_date"] = pd.to_datetime(
        bd_online["date"], errors="coerce", utc=True
    )
    bd_online = bd_online.dropna(subset=["parsed_date"])

    # Векторизованная помесячная агрегация (расчет абсолютного количества визитов в месяц)
    monthly_counts = (
        bd_online.groupby(bd_online["parsed_date"].dt.to_period("M"))
        .size()
        .reset_index(name="count")
    )
    
    # Хронологическое выравнивание и создание строкового идентификатора периода для графиков
    monthly_counts = monthly_counts.sort_values("parsed_date").reset_index(drop=True)
    monthly_counts["date_str"] = monthly_counts["parsed_date"].astype(str)

    # --- ЭТАПЫ ОЧИСТКИ ВРЕМЕННОГО РЯДА ОТ АНОМАЛИЙ (TIME-SERIES CLEANING) ---
    # Шаг 2.1: ТУПИКОВЫЙ ФИЛЬТР ГРАНИЦ. Отсечение незавершенных отчетных периодов на краях выборки
    monthly_counts = monthly_counts[
        (monthly_counts["date_str"] >= "2021-12") & 
        (monthly_counts["date_str"] <= "2023-11")
    ].reset_index(drop=True)

    # Шаг 2.2: ЛОКАЛЬНЫЙ СГЛАЖИВАЮЩИЙ ФИЛЬТР. Поиск резких просадок через скользящее окно с окном шириной 3
    rolling_window = monthly_counts["count"].rolling(window=3, center=True, min_periods=1)
    rolling_mean = rolling_window.mean()
    rolling_std = rolling_window.std().fillna(monthly_counts["count"].std() * 0.1)

    # Логический маскирующий фильтр: просадка трафика ниже 1.5 стандартных отклонений признается техническим сбоем
    is_anomaly = monthly_counts["count"] < (rolling_mean - 1.5 * rolling_std)
    monthly_counts = monthly_counts[~is_anomaly].reset_index(drop=True)

    # Шаг 2.3: МЕДИАННЫЙ FALLBACK. Фильтрация околонулевых аномальных месяцев (порог отсечения — 20% от медианы ряда)
    median_visits = monthly_counts["count"].median()
    monthly_counts = monthly_counts[monthly_counts["count"] >= (median_visits * 0.2)].reset_index(drop=True)

    return monthly_counts


# Запуск пайплайна обработки данных
df = load_and_process_data()

# Валидация достаточности выборки: для годового лага и тренда требуется репрезентативный объем данных
if len(df) < 13:
    st.error(
        "Недостаточно данных для обучения расширенной модели с лагами. Требуется как минимум 13 месяцев истории."
    )
else:
    # Расчет статистических констант для бизнес-бенчмаркинга на графиках
    mean_val = round(df["count"].mean(), 1)
    median_val = round(df["count"].median(), 1)

    # =========================================================================
    # 3. ИНЖИНИРИНГ ПРИЗНАКОВ ДЛЯ ЛИНЕЙНОЙ РЕГРЕССИИ (FEATURE ENGINEERING)
    # =========================================================================
    # Глобальный линейный тренд (порядковый возрастающий индекс месяцев)
    df["month_index"] = np.arange(len(df))
    df["calendar_month"] = df["parsed_date"].dt.month

    # ФАКТОР 1: Макро-лаг глубиной 12 месяцев (Lag_12).
    # Передает модели жесткую зависимость от аналогичного периода прошлого года.
    # Страхует от утечки данных (Data Leakage) — при шаге прогноза на 6 месяцев вперед этот лаг ВСЕГДА известен из истории.
    df["lag_12"] = df["count"].shift(12)
    df["lag_12"] = df["lag_12"].fillna(df["count"].median())  # Обработка холодных стартовых периодов

    # ФАКТОР 2: Тригонометрическое циклическое кодирование сезонности.
    # Преобразует дискретные месяцы в непрерывные координаты на окружности (связывает декабрь с январем)
    df["month_sin"] = np.sin(2 * np.pi * df["calendar_month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["calendar_month"] / 12)

    # Матрица признаков (X) и вектор целевой переменной (y)
    feature_cols = ["month_index", "month_sin", "month_cos", "lag_12"]
    X = df[feature_cols]
    y = df["count"]

    # Инициализация и обучение базового регрессионного оценщика
    model = LinearRegression()
    model.fit(X, y)

    # Расчет финального коэффициента детерминации после внедрения Feature Engineering
    r2_score = model.score(X, y)

    # =========================================================================
    # 4. РАСЧЕТ ВНЕВЫБОРОЧНОГО ПРОГНОЗА НА 6 МЕСЯЦЕВ (OUT-OF-SAMPLE FORECASTING)
    # =========================================================================
    future_months = 6
    last_period = df["parsed_date"].max()

    # Генерация индексной и календарной сетки для будущего периода прогнозирования
    future_periods = [last_period + i for i in range(1, future_months + 1)]
    future_indices = np.arange(len(df), len(df) + future_months)
    future_calendar_months = [p.month for p in future_periods]

    # Безопасное извлечение значений Lag_12 для будущих точек (берём фактические значения за прошлый год)
    future_lags = []
    for fp in future_periods:
        target_past_period = fp - 12
        past_row = df[df["parsed_date"] == target_past_period]
        if not past_row.empty:
            # .values[0] гарантирует, что мы берем конкретное число (скаляр), а не объект массива
            future_lags.append(past_row["count"].values[0])
        else:
            future_lags.append(df["count"].median())  # Фолбэк при отсутствии исторических записей

    # Сборка прогнозной матрицы признаков
    X_future = pd.DataFrame(
        {
            "month_index": future_indices,
            "month_sin": np.sin(2 * np.pi * np.array(future_calendar_months) / 12),
            "month_cos": np.cos(2 * np.pi * np.array(future_calendar_months) / 12),
            "lag_12": future_lags,
        }
    )

    # Инференс модели с обрезкой математически невозможных отрицательных объемов трафика
    future_preds = model.predict(X_future[feature_cols])
    future_preds = np.clip(future_preds, a_min=0, a_max=None)

    # Маркировка строк для разделения на графике
    df["type"] = "История"

    # Сборка результирующего прогнозного датафрейма
    df_future = pd.DataFrame(
        {
            "parsed_date": future_periods,
            "count": future_preds,
            "date_str": [str(p) for p in future_periods],
            "type": "Прогноз",
        }
    )

    # Объединение для построения непрерывных линий тренда
    df_all = pd.concat([df, df_future], ignore_index=True)

    # =========================================================================
    # 5. СТРУКТУРИРОВАНИЕ И ФОРМАТИРОВАНИЕ ИНТЕРФЕЙСА ДАШБОРДА
    # =========================================================================
    col1, col2 = st.columns(2, gap="large")

    # КОЛОНКА 1: Бизнес-метрики, описание и табличные данные
    with col1:
        st.subheader("🤖 Описание ML-модели")
        st.markdown(
            """
        Для прогнозирования используется **Линейная регрессия**, усиленная методами **Feature Engineering**. 
        Модель учитывает четыре комплексных фактора:
        1. **Глобальный тренд** (индекс месяца).
        2. **Циклическая макро-сезонность** (тригонометрическое кодирование непрерывности месяцев через синусы и косинусы).
        3. **Годовой исторический лаг (Lag 12)** (значения посещаемости ровно год назад для учета долгосрочной памяти ряда без риска утечки данных).
        """
        )

        # Вывод ключевой метрики эффективности модели
        st.metric(label="Качество модели (R² Score)", value=f"{r2_score:.2f}")
        st.caption(
            "Чем ближе R² к 1.0, тем точнее модель описывает исторические колебания."
        )

        st.subheader("📋 Таблица прогноза")
        st.dataframe(
            df_future[["date_str", "count"]].rename(
                columns={"date_str": "Месяц", "count": "Прогноз посещений"}
            ),
            hide_index=True,
        )

    # КОЛОНКА 2: Визуализация данных (Отрисовка графиков)
    with col2:
        st.subheader("📈 График истории и прогноза")

        fig, ax = plt.subplots(figsize=(10, 5))
        plt.rc("font", size=10)

        # Отрисовка фактических исторических точек
        ax.plot(
            df["date_str"],
            df["count"],
            color="#1f77b4",
            label="История (Факт)",
            linewidth=2,
            zorder=3
        )
        ax.scatter(df["date_str"], df["count"], color="#1f77b4", s=40, zorder=3)

        # Отрисовка пунктирной линии прогнозных значений
        ax.plot(
            df_all["date_str"],
            df_all["count"],
            color="#ff7f0e",
            linestyle="--",
            label="Прогноз модели",
            alpha=0.8,
        )
        ax.scatter(
            df_future["date_str"],
            df_future["count"],
            color="#ff7f0e",
            s=40,
            marker="s",  # Квадратные маркеры для визуального отличия прогноза
        )

        # Статистические линии поддержки бенчмарков (Среднее и Медиана)
        ax.axhline(
            y=mean_val,
            color="red",
            linestyle="-.",
            linewidth=1.2,
            label=f"Среднее за историю ({mean_val})",
            alpha=0.7
        )
        ax.axhline(
            y=median_val,
            color="green",
            linestyle=":",
            linewidth=1.5,
            label=f"Медиана за историю ({median_val})",
            alpha=0.7
        )

        # Настройка координатной сетки, осей и легенды
        ax.set_xlabel("Месяц")
        ax.set_ylabel("Количество посещений")
        plt.xticks(rotation=45)
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend()

        # Интеграция готовой Matplotlib-фигуры в холст Streamlit
        st.pyplot(fig)

import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from pymongo import MongoClient

def run_pipeline():
    print("Запуск сквозного ML-пайплайна...")
    
    # Подключение к MongoDB и выгрузка отфильтрованного представления (View)
    try:
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        db = client["EdTechDB"]
        # Проверяем доступность коллекции/представления
        if "bd_online_aggregated" not in db.list_collection_names():
            print("Представление 'bd_online_aggregated' не найдено. Пожалуйста, запустите сначала скрипт создания View.")
            return
        
        data = list(db["bd_online_aggregated"].find({}))
        df_raw = pd.DataFrame(data)
        print(f"Успешно загружено {len(df_raw)} записей из MongoDB.")
    except Exception as e:
        print(f"Ошибка подключения к MongoDB: {e}")
        return

    if df_raw.empty:
        print("База данных пуста. Нечего обрабатывать.")
        return

    # Преобразование данных и агрегация по месяцам
    df_raw["parsed_date"] = pd.to_datetime(df_raw["date"], errors="coerce")
    df_raw["parsed_date"] = df_raw["parsed_date"].dt.tz_localize(None)
    df_raw = df_raw.dropna(subset=["parsed_date"])

    monthly_counts = (
        df_raw.groupby(df_raw["parsed_date"].dt.to_period("M"))
        .size()
        .reset_index(name="count")
    )
    monthly_counts = monthly_counts.sort_values("parsed_date").reset_index(drop=True)
    monthly_counts["date_str"] = monthly_counts["parsed_date"].astype(str)

    # Очистка временного ряда от выбросов (Логика проекта)
    monthly_counts = monthly_counts[
        (monthly_counts["date_str"] >= "2021-12") & 
        (monthly_counts["date_str"] <= "2023-11")
    ].reset_index(drop=True)

    if len(monthly_counts) < 6:
        print(f"Критическая ошибка: Недостаточно исторических данных для обучения модели ({len(monthly_counts)} мес. из 6 необходимых).")
        return

    rolling_window = monthly_counts["count"].rolling(window=3, center=True, min_periods=1)
    rolling_mean = rolling_window.mean()
    rolling_std = rolling_window.std().fillna(monthly_counts["count"].std() * 0.1)

    is_anomaly = monthly_counts["count"] < (rolling_mean - 1.5 * rolling_std)
    monthly_counts = monthly_counts[~is_anomaly].reset_index(drop=True)

    median_visits = monthly_counts["count"].median()
    monthly_counts = monthly_counts[monthly_counts["count"] >= (median_visits * 0.2)].reset_index(drop=True)
    print(f"Очистка завершена. Доступно {len(monthly_counts)} месяцев чистой истории.")

    # Обучение Линейной Регрессии и Предсказание на полгода вперед
    monthly_counts["month_index"] = np.arange(len(monthly_counts))
    monthly_counts["calendar_month"] = monthly_counts["parsed_date"].dt.month

    X = monthly_counts[["month_index", "calendar_month"]]
    y = monthly_counts["count"]

    model = LinearRegression()
    model.fit(X, y)
    r2_score = model.score(X, y)
    print(f"Модель обучена. Качество R² Score = {r2_score:.2f}")

    # Генерация будущего периода 
    future_months = 6
    last_period = monthly_counts["parsed_date"].max()
    last_hist_row = monthly_counts.iloc[-1]
    
    future_periods = [last_period + i for i in range(1, future_months + 1)]
    future_indices = np.arange(len(monthly_counts), len(monthly_counts) + future_months)
    future_calendar_months = [p.month for p in future_periods]

    X_future = pd.DataFrame({
        "month_index": future_indices,
        "calendar_month": future_calendar_months
    })

    future_preds = model.predict(X_future)
    future_preds = np.clip(future_preds, a_min=0, a_max=None)

    monthly_counts["type"] = "История"
    
    # Стыковочный месяц дублируем для непрерывности графика
    df_future = pd.DataFrame({
        "parsed_date": [last_hist_row["parsed_date"]] + future_periods,
        "count": [last_hist_row["count"]] + list(future_preds),
        "date_str": [last_hist_row["date_str"]] + [str(p) for p in future_periods],
        "type": ["Прогноз"] + ["Прогноз"] * future_months,
        "month_index": [last_hist_row["month_index"]] + list(future_indices),
        "calendar_month": [last_hist_row["calendar_month"]] + future_calendar_months
    })

    output_dataset = pd.concat([monthly_counts, df_future], ignore_index=True)
    output_dataset["parsed_date"] = output_dataset["parsed_date"].astype(str)

    # Экспорт результатов для контроля
    output_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "predictions_output.csv")
    output_dataset.to_csv(output_path, sep=",", index=False, encoding="utf-8-sig")

    print(f"Результаты трансформации и предсказания сохранены в: data/predictions_output.csv")


if __name__ == "__main__":
    run_pipeline()

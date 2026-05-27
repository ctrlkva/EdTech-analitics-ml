import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import streamlit as st
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"
groups = pd.read_csv(DATA_DIR / "groups.csv")
lessons = pd.read_csv(DATA_DIR / "lessons.csv")
attendances = pd.read_csv(DATA_DIR / "attendances.csv")

st.set_page_config(
    page_title="Прогноз для онлайн-школы", page_icon="📈", layout="wide"
)

st.title("🔮 Прогнозирование посещаемости: ")
st.markdown("---")


@st.cache_data
def load_and_process_data():
    groups = pd.read_csv("../data/groups.csv")
    lessons = pd.read_csv("../data/lessons.csv")
    attendances = pd.read_csv("../data/attendances.csv")

    # Data pipeline: merge relational data structures
    bd_online = lessons.merge(
        attendances, left_on="_id", right_on="lessonId", how="inner"
    )
    bd_online = bd_online.merge(
        groups, left_on="groupId", right_on="_id", how="inner"
    )

    # Filter data by target branch ID
    bd_online = bd_online[
        bd_online["filial"] == "63c63702397ca6783eb57fa2"
    ].copy()

    # Datetime parsing and handling invalid records
    bd_online["parsed_date"] = pd.to_datetime(
        bd_online["date"], errors="coerce", utc=True
    )
    bd_online = bd_online.dropna(subset=["parsed_date"])

    # Fast vectorized aggregation by calendar month
    monthly_counts = (
        bd_online.groupby(bd_online["parsed_date"].dt.to_period("M"))
        .size()
        .reset_index(name="count")
    )
    
    # Sort chronologically
    monthly_counts = monthly_counts.sort_values("parsed_date").reset_index(drop=True)
    monthly_counts["date_str"] = monthly_counts["parsed_date"].astype(str)

    # --- TIME SERIES DATA CLEANING & OUTLIER REMOVAL ---
    # Step 1: Filter historical boundaries (remove incomplete tails)
    monthly_counts = monthly_counts[
        (monthly_counts["date_str"] >= "2021-12") & 
        (monthly_counts["date_str"] <= "2023-11")
    ].reset_index(drop=True)

    # Step 2: Use rolling metrics to detect local drops in the middle of timeline
    rolling_window = monthly_counts["count"].rolling(window=3, center=True, min_periods=1)
    rolling_mean = rolling_window.mean()
    rolling_std = rolling_window.std().fillna(monthly_counts["count"].std() * 0.1)

    is_anomaly = monthly_counts["count"] < (rolling_mean - 1.5 * rolling_std)
    monthly_counts = monthly_counts[~is_anomaly].reset_index(drop=True)

    # Step 3: Global threshold fallback
    median_visits = monthly_counts["count"].median()
    monthly_counts = monthly_counts[monthly_counts["count"] >= (median_visits * 0.2)].reset_index(drop=True)
    # ------------------------------------------------------------------------

    return monthly_counts


df = load_and_process_data()

if len(df) < 6:
    st.error(
        "Недостаточно данных для обучения модели. Требуется как минимум 6 месяцев истории."
    )
else:
    # --- Calculate Historical Metrics ---
    mean_val = round(df["count"].mean(), 1)
    median_val = round(df["count"].median(), 1)

    # --- Feature Engineering for Time Series Forecasting ---
    df["month_index"] = np.arange(len(df))
    df["calendar_month"] = df["parsed_date"].dt.month

    X = df[["month_index", "calendar_month"]]
    y = df["count"]

    model = LinearRegression()
    model.fit(X, y)

    r2_score = model.score(X, y)

    # --- Out-of-Sample Forecasting (Next 6 Months) ---
    future_months = 6
    last_period = df["parsed_date"].max()

    future_periods = [last_period + i for i in range(1, future_months + 1)]
    future_indices = np.arange(len(df), len(df) + future_months)
    future_calendar_months = [p.month for p in future_periods]

    X_future = pd.DataFrame(
        {
            "month_index": future_indices,
            "calendar_month": future_calendar_months,
        }
    )

    future_preds = model.predict(X_future)
    future_preds = np.clip(future_preds, a_min=0, a_max=None)

    df["type"] = "История"

    df_future = pd.DataFrame(
        {
            "parsed_date": future_periods,
            "count": future_preds,
            "date_str": [str(p) for p in future_periods],
            "type": "Прогноз",
        }
    )

    df_all = pd.concat([df, df_future], ignore_index=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.subheader("🤖 Описание ML-модели")
        st.markdown(
            """
        Для прогнозирования используется **Линейная регрессия**, обученная на исторических данных школы. 
        Модель учитывает два ключевых фактора:
        1. **Глобальный тренд** (растет ли общая популярность школы со временем).
        2. **Сезонность** (в какие календарные месяцы студенты традиционно учатся активнее всего).
        """
        )

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

    with col2:
        st.subheader("📈 График истории и прогноза")

        fig, ax = plt.subplots(figsize=(10, 5))
        plt.rc("font", size=10)

        # Plot historical data
        ax.plot(
            df["date_str"],
            df["count"],
            color="#1f77b4",
            label="История (Факт)",
            linewidth=2,
            zorder=3
        )
        ax.scatter(df["date_str"], df["count"], color="#1f77b4", s=40, zorder=3)

        # Plot forecast
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
            marker="s",
        )

        # --- NEW: Plot Mean and Median Lines ---
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

        ax.set_xlabel("Месяц")
        ax.set_ylabel("Количество посещений")
        plt.xticks(rotation=45)
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend()

        st.pyplot(fig)

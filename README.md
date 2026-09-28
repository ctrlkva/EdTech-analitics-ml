# 🔮 EdTech Attendance Analytics & Forecasting Dashboard
## 📈 Live Dashboard Demo: [Streamlit App](https://ctrlkva.streamlit.app/)
An interactive Data Science platform featuring a **Streamlit** dashboard for educational center analytics, complete with an automated data cleaning pipeline and a 6-month attendance forecast model.

---

## 📈 Alternative BI Live Deployments
Explore alternative enterprise BI implementations available in the [powerbi branch](https://github.com/ctrlkva/EdTech-analitics-ml/tree/powerbi):
* 🌐 **[Live Yandex DataLens Public Dashboard](https://datalens.ru/vxb6u0h99na8e-edtech-analytics-dashboard?_share_link=org)**
* 📊 **Power BI Desktop Report** *(Native `.pbix` implementation)*

---

## 🎯 Project Overview
This project transforms raw database exports into a strategic analytical tool, handling vectorized ETL, time-series anomaly filtering, and predictive modeling using `scikit-learn`.
<img width="2549" height="1167" alt="image" src="https://github.com/user-attachments/assets/94bc8cfd-975d-41f9-a924-6cb6c7a8321b" />

---

## 📊 Baseline Model Analysis & Technical Backlog

### 1. Key Insights from EDA & Current Performance
As part of the Exploratory Data Analysis (EDA), attendance patterns on the EdTech platform were thoroughly investigated, revealing two critical cyclic user behavior components:
* **Micro-Seasonality:** Pronounced weekly traffic fluctuations with clear attendance drops on weekends and peak activity during mid-week.
* **Macro-Seasonality:** Long-term academic year cycles, driven by calendar-specific drop periods (summer holidays, January and May public holidays) and autumn/spring peaks in educational activity.

The initial baseline model developed using Linear Regression achieved an **R² score of 0.11 across a 6-month forecasting horizon**.
* **Root Cause of Low Metrics:** Standard temporal features (one-hot encoding of days of the week and months) fail to capture the autoregressive nature of the time series, non-linear long-term trends, and abrupt calendar anomalies unique to the EdTech sector.
* **Role of the Current Model:** The model successfully functions as a starting baseline and architectural blueprint for the end-to-end ML pipeline—spanning data extraction from MongoDB to the final prediction export.

### 🎯 Technical Backlog for Moving to Sequential Architectures

To enhance forecasting accuracy, a step-by-step migration plan has been established to transition toward specialized time-series algorithms (Prophet / ARIMA):

#### 🛠 Sprint 1: Statistical Autoregressive Integration (SARIMAX)
* **Stationarity & Autocorrelation Testing** — Execute an Augmented Dickey-Fuller (ADF) test and plot ACF / PACF charts to mathematically determine optimal autoregressive lags (p, q).
* **SARIMAX Model Implementation** — Deploy the algorithm with an explicit weekly seasonal period (s=7) to stabilize micro-seasonality tracking.
* **Exogenous Macro-Factors Evaluation** — Incorporate external exogenous variables (session flags, holiday periods) to smooth out the forecast line.

#### 🚀 Sprint 2: Migration to Facebook Prophet (Event & Calendar Management)
* **Data Adapter Development** — Build a data transformation layer to reshape aggregated data from MongoDB into Prophet’s required target schema (`ds`, `y`).
* **Holiday & Slump Modeling** — Integrate a custom calendar featuring Russian public holidays and sector-specific EdTech events (summer breaks) to eliminate artificial trend drops.
* **Hyperparameter Tuning & Decomposition** — Fine-tune change-points sensitivity (`changepoints`) and visualize extracted trend components using `model.plot_components()`.

#### 📈 Sprint 3: Cross-Validation & Benchmarking
* **Rolling-Window Validation** — Implement a `TimeSeriesSplit` cross-validation scheme (or Prophet's native diagnostic tools) to accurately evaluate quality over a 6-month horizon without data leakage.
* **Comprehensive Benchmark Report** — Aggregate metrics (R², MAE, RMSE) from the Linear Regression baseline, SARIMAX, and Prophet into a unified analysis matrix to select the final production-ready solution.
* **Export Pipeline Update** — Adapt the export script to align the final `predictions_output.csv` file structure with the reporting requirements of Power BI / Yandex DataLens dashboards.
* 
<img width="987" height="968" alt="image" src="https://github.com/user-attachments/assets/3ce4fe53-134f-4735-82d1-61342e599f99" />

---

## 🛠️ Tech Stack
* Python, Streamlit, Pandas, NumPy, Scikit-Learn, Matplotlib, Seaborn.

---

## 🚀 How to Run Locally

```bash
git clone https://github.com/ctrlkva/EdTech-analitics-ml
cd EdTech-analitics-ml
pip install -r requirements.txt
streamlit run src/app.py
```

## 🏗️ Building Your Own Streamlit Dashboard
To create or customize your dashboard in `src/app.py`:
1. Load cached data from the `data/` directory using Streamlit utilities.
2. Generate temporal features and trend indicators.
3. Configure interactive controls via `st.sidebar` and layout elements using `st.columns()`.

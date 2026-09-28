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
This project transforms raw database exports from an educational center into a strategic analytical tool. It successfully addresses three core challenges:

1. **🗄️ Data Engineering (DB-level ETL):** Relational joining of `lessons`, `attendances`, and `groups` collections directly within the MongoDB database using aggregated views, coupled with strict filtering for the target online branch.
2. **📈 Time-Series Pipeline:** An automated data cleaning script that clips incomplete boundary periods, eliminates local traffic drops using a rolling mean (1.5 standard deviations threshold filter), and applies a median fallback algorithm.
3. **🤖 Predictive Modeling:** A time-series model built on Linear Regression (`scikit-learn`) that accounts for the school's global growth trend and calendar seasonality components, generating a continuous 6-month forecast.

<img width="2449" height="1109" alt="image" src="https://github.com/user-attachments/assets/bf53f933-fcc4-4f04-9abd-955381aba0ba" />

---

## 📊 Model Selection Rationale & Technical Backlog

### 1. Feature Engineering Results & Quality Evolution
The initial basic model implementation demonstrated low predictive accuracy (**R² = 0.11**), as standard linear time indices failed to capture the complex, repetitive cyclical structure of the data.

To overcome this bottleneck, a comprehensive **Feature Engineering** phase was executed, which successfully escalated the final model performance to **R² = 0.84 over a 6-month forecasting horizon**:
* **Trigonometric Time Encoding (`month_sin` / `month_cos`):** Converts discrete calendar month numbers into continuous 2D coordinates on a circle. This mathematically links December and January under a continuous cyclical dependency, allowing the linear model to properly approximate macro-seasonality.
* **Long-Term Autoregressive Lag (`lag_12`):** Integrates the historical target value exactly 12 months (1 year) prior into the feature matrix. This provides the regression engine with a strong autoregressive predictor and long-term time-series memory.
* **Data Leakage Protection:** Because the depth of the annual lag (`t-12`) strictly exceeds the required out-of-sample forecasting horizon (6 months), all future feature values are guaranteed to be known from actual historical records. This ensures absolute mathematical cleanliness during inference without any future data leakage.

### 2. Model Selection Process
During the evolution of the predictive component, three alternative architectures were evaluated to transition from the baseline linear regression:
* **Facebook Prophet:** Rejected due to over-smoothing tendencies (the model struggles with sharp, step-like attendance drops typical of academic vacation periods in EdTech) and slower execution speeds.
* **ETNA (AutoML by T-Bank):** A powerful domestic open-source framework. Deferred during the MVP phase due to heavy infrastructure overhead required for cross-validation setup relative to a single target metric.
* **CatBoostRegressor (Gradient Boosting by Yandex):** **Selected as the target production architecture.** Gradient boosting integrates seamlessly with the existing tabular representation of the time series (reusing the engineered trigonometric and lag features). Driven by its tree-based split structure, it naturally isolates sudden non-linear traffic drops, processes inference within milliseconds, and will maximize the current R² = 0.84 baseline by mapping complex non-linear combinations.

---

### 🎯 Technical Backlog (Brief)

The optimization roadmap for the predictive pipeline is re-oriented toward tabular data engineering and gradient boosting deployment:

#### 🛠️ Sprint 1: CatBoost Integration & Baseline Tuning
* **CatBoost Baseline Implementation:** Substitute `LinearRegression` with `CatBoostRegressor` using the current feature space to secure immediate baseline accuracy improvements.
* **Overfitting Prevention:** Configure model regularization parameters, tune the optimal learning rate, and restrict maximum tree depth to stabilize out-of-sample forecasting performance.

#### 🚀 Sprint 2: Advanced Feature Engineering
* **Macro Feature Generation:** Inject a custom Russian public holiday and academic vacation calendar as explicit binary indicators.
* **Exponential Smoothing:** Calculate Exponential Moving Average (EMA) historical features to capture short-term localized trend adjustments within the platform.

#### 📈 Sprint 3: Validation & UI Optimization
* **Time-Series Cross-Validation:** Establish a rolling-window evaluation loop using `TimeSeriesSplit` to test model limits rigorously without data leakage.
* **In-App Residual Analytics:** Deploy automatic error calculations (MAE, RMSE) and integrate residual distribution plots directly into the Streamlit dashboard for real-time inference monitoring.
  
<img width="1069" height="841" alt="Снимок экрана 2026-09-28 223634" src="https://github.com/user-attachments/assets/2539ee85-5ddc-46d2-b1ec-5f20b8c24659" />

---

## 🛠️ Tech Stack
* Python, Streamlit, Pandas, NumPy, Scikit-Learn, Matplotlib, Seaborn.

---

## 🚀 How to Run Locally

```bash
# Clone the repository
git clone https://github.com
cd EdTech-analitics-ml

# Install dependencies
pip install -r requirements.txt

# Launch the interactive web app
streamlit run src/app.py
```

## 🏗️ Customization & Streamlit Dashboard Architecture
To alter the user interface logic or expand chart displays within the primary application file `src/app.py`:
1. Leverage Streamlit's native caching mechanisms (`@st.cache_data`) to prevent redundant data processing on every interactive user click.
2. Build time-series transformation rules and integrate reactive sidebar configuration widgets using `st.sidebar`.
3. Organize analytical components (KPI cards, tabular grids, trend visualizations) into crisp layouts using `st.columns()` and fluid containers.

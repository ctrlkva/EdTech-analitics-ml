# Yes Online Attendance Analytics & Forecasting Dashboard 📈

A production-ready data science project featuring an interactive web dashboard for educational center attendance analysis and time-series forecasting.

## 🎯 Project Overview
This project transforms raw database exports of students' attendances into a strategic analytical tool. It solves two critical tasks:
1. **Data Engineering (Pipeline):** Vectorized cleaning, relational merging (`lessons`, `attendances`, `groups`), and automatic filtering of incomplete reporting periods (handling historical and trailing edge data anomalies).
2. **Predictive Modeling:** A Time-Series Regression model built with `scikit-learn` that captures global growth trends and cyclical seasonal components to forecast student attendance 6 months into the future.

## 🛠️ Tech Stack
- **Language:** Python
- **Dashboard Framework:** Streamlit (Modern Web UI replacement for legacy Tkinter)
- **Data Engineering:** Pandas, NumPy
- **Machine Learning:** Scikit-Learn (LinearRegression)
- **Visualization:** Matplotlib

## 📁 Repository Structure
```text
├── data/
│   ├── groups.csv
│   ├── lessons.csv
│   └── attendances.csv
├── src/
│   └── app.py                # Main Streamlit web application
├── README.md                 # Project documentation
└── requirements.txt          # Environment dependencies
```

## 🧠 Model Validation Note
The model achieves an **R² Score of 0.13** after strict data cleaning. While the baseline linear model successfully identifies the stable core trend and winter/summer seasonality bounds, the score reflects high variance in month-to-month student behavior, paving the way for future iterations using advanced sequential models (like Prophet or ARIMA).

## 🚀 How to Run Locally

1. Clone this repository:
   ```bash
   git clone https://github.com/ctrlkva/YesOnlineStatistics
   cd YesOnlineStatistics
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Launch the web dashboard:
   ```bash
   streamlit run src/app.py
   ```
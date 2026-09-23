# 🔮 EdTech Attendance Analytics & Forecasting Dashboard

> An interactive **Power BI** & **Yandex DataLens** analytical dashboard platform integrated with a local **MongoDB** database. Features an automated time-series data cleansing pipeline and an end-to-end Machine Learning (**ML**) engine for a 6-month out-of-sample attendance forecast.

---

## 📈 Live Dashboard Demo
* 📊 **[Open Yandex DataLens Public Dashboard](https://datalens.yandex/vxb6u0h99na8e?_share_link=public)** *(Interactive cloud web access)*
<img width="1948" height="981" alt="image" src="https://github.com/user-attachments/assets/1c89bf56-f110-4413-b57d-0e18f7c074f4" />

---

## 🎯 Project Overview
This project transforms raw database exports of an educational center into a strategic analytical tool. It successfully solves three critical tasks:

1. **🗄️ Data Engineering (In-DB ETL):** Relational schema merging (`lessons`, `attendances`, `groups`) on the MongoDB database level using aggregation views and strict filtering of the target online platform branch.
2. **📈 Time-Series Pipeline:** An automated data cleaning script that truncates incomplete boundary reporting periods, removes localized drops via a rolling average (1.5 standard deviations threshold filter), and applies a median fallback algorithm.
3. **🤖 Predictive Modeling:** A time-series model built with `scikit-learn` (LinearRegression) that captures global growth trends and calendar seasonality components to forecast student attendance 6 months into the future.
<img width="1750" height="998" alt="powerbi" src="https://github.com/user-attachments/assets/a4499a90-ec3f-413d-884a-838f26451aff" />


---

## 🛠️ Tech Stack
- **Database:** MongoDB 🍃 (Aggregation Views, Mongosh Scripting)
- **ETL / Transformation:** Power Query ⚡ + Python 🐍 (Pandas, NumPy)
- **Machine Learning:** Scikit-Learn 🧠 (LinearRegression)
- **BI / Visualization:** Power BI Desktop 📊 (DAX Measures, Native KPI Cards, Analytical Trendlines)
- **Cloud Analytics:** Yandex DataLens 🌐 (Cloud Ingestion, Shared Public BI Dashboards)

---

## 📁 Repository Structure
```text
├── 📂 data/                    # Source tables + pipeline output results
│   ├── 📄 attendances.csv      # Student attendance transactional logs
│   ├── 📄 groups.csv           # Reference directory for academic groups and branches
│   ├── 📄 lessons.csv          # Schedule records of conducted classes
│   └── 📄 predictions_output.csv # Consolidated pipeline forecast results
├── 📂 reports/                 # Business intelligence reporting layer
│   └── 📊 dashboard.pbix       # Production Power BI dashboard file
├── 📂 screenshots/             # Interface visualizations for repository documentation
│   ├── 🖼️ powerbi.png                # Power BI main dashboard overview screenshot
│   └── 🖼️ datalens.png         # Yandex DataLens dashboard overview screenshot
├── 📂 scripts/                 # Automation scripts for database initialization and ML
│   ├── 📜 create_view.js       # Database schema view deployment script for Mongosh
│   ├── ⚙️ db_import.py         # Automated CSV ingestion pipeline into MongoDB
│   └── ⚙️ pipeline.py          # Standalone data transformation and prediction script
├── 🛠️ .gitignore               # Build cache, environment, and user-specific metadata filters
├── 📝 README.md                # Project documentation and architecture guide
└── 📋 requirements.txt         # Python runtime environment dependencies
```

---

## 🚀 Local Deployment Guide

### 1. Environment Initialization
Clone this repository to your local directory and install the necessary Python packages (ensure that Python and a local instance of MongoDB Community Server are running on your machine):

```powershell
git clone https://github.com
cd EdTech-analitics-ml
pip install -r requirements.txt
```

### 2. Database Deployment & Schema Mapping
To automatically create the required collections and ingest the data into your local database instance, execute the primary seed script in your terminal (PowerShell/CMD):

```powershell
python scripts/db_import.py
```

Next, deploy the aggregation view script to connect and filter your collections. You can do this in one of two ways:

* **Option A (Via System Terminal):** Run the following command directly from your project root:
  ```powershell
  mongosh mongodb://localhost:27017/EdTechDB scripts/create_view.js
  ```

* **Option B (Via MongoDB Compass UI):** Open MongoDB Compass, connect to your server, click the **>_ MONGOSH** tab at the very bottom of the window to open the integrated shell, and execute the JavaScript aggregation code from `scripts/create_view.js` directly.

*Result:* A pre-filtered virtual collection named `bd_online_aggregated` will be safely provisioned inside your database.

### 3. Running the ML Pipeline
You can trigger the standalone processing pipeline in the background to calculate target baseline historical metrics and generate a projection dataset without opening any graphical user interfaces:

```powershell
python scripts/pipeline.py
```
The resulting 6-month forward data structure will automatically save to `data/predictions_output.csv`.

### 4. Navigating the Power BI Dashboard
1. Launch **Power BI Desktop**.
2. Open the reporting template located at `reports/dashboard.pbix`.
3. Click the **Refresh** button on the Home ribbon tab.

Power BI will automatically query your local MongoDB database via the embedded Python engine layer, compute the underlying linear regression parameters, and refresh all interactive canvas assets (including "Total Attendances", "Historical Median", and "Historical Average" KPI blocks).

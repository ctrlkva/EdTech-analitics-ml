\# 🔮 EdTech Attendance Analytics \& Forecasting Dashboard



> An interactive \*\*Power BI\*\* analytical dashboard integrated with a local \*\*MongoDB\*\* database, featuring an automated time-series data cleansing pipeline and an end-to-end Machine Learning (\*\*ML\*\*) engine for a 12-month out-of-sample attendance forecast.



\---



\## 🎯 Project Overview

This project transforms raw relational database exports of students' attendances into a strategic business intelligence tool. It covers three foundational engineering layers:



1\. \*\*🗄️ Data Engineering (In-DB ETL):\*\* Relational schema merging (`lessons`, `attendances`, `groups`) executed on the database level using MongoDB Aggregation Views, including server-side filtering of the target online platform branch.

2\. \*\*📈 Time-Series Pipeline:\*\* An automated Python preprocessing script that truncates incomplete boundary reporting periods, removes localized drops via a rolling standard deviation filter (1.5 σ threshold), and applies a median fallback strategy.

3\. \*\*🤖 Predictive Modeling:\*\* A Time-Series Regression model built with `scikit-learn` (LinearRegression) that simultaneously captures global baseline growth trends and cyclical calendar seasonality components to output a continuous 12-month projection.



\---



\## 🛠️ Tech Stack

\- \*\*Database:\*\* MongoDB 🍃 (Aggregation Views, Mongosh Scripting)

\- \*\*ETL / Transformation:\*\* Power Query ⚡ + Python 🐍 (Pandas, NumPy)

\- \*\*Machine Learning:\*\* Scikit-Learn 🧠 (LinearRegression)

\- \*\*BI / Visualization:\*\* Power BI Desktop 📊 (DAX Measures, Native KPI Cards, Trendlines, Custom Analytics Lines)



\---



\## 📁 Repository Structure

```text

├── 📂 data/                    # Raw source tables + model predictions

│   ├── 📄 attendances.csv      # Student attendance transactional logs

│   ├── 📄 groups.csv           # Reference directory for academic groups and branches

│   ├── 📄 lessons.csv          # Schedule records of conducted classes

│   └── 📄 predictions\_output.csv # Consolidated pipeline forecast results

├── 📂 reports/                 # Business intelligence reporting layer

│   └── 📊 dashboard.pbix       # Production Power BI dashboard file

├── 📂 screenshots/             # Interface visualizations for repository documentation

├── 📂 scripts/                 # Automation scripts for database initialization and ML

│   ├── 📜 create\_view.js       # Database schema view deployment script for Mongosh

│   ├── ⚙️ db\_import.py         # Automated CSV ingestion pipeline into MongoDB

│   └── ⚙️ pipeline.py          # Standalone data transformation and prediction script

├── 📄 .gitattributes           # Git repository configuration attributes

├── 🛠️ .gitignore               # Build cache, environment, and user-specific metadata filters

├── 📝 README.md                # Project documentation and architecture guide

└── 📋 requirements.txt         # Python runtime environment dependencies

```



\---



\## 🚀 Local Deployment Guide



\### 1. Environment Initialization

Clone this repository to your local directory and install the necessary Python packages. Ensure that Python and a local instance of MongoDB Community Server are running on your machine:



```bash

git clone https://github.com

cd EdTech-analitics-ml

pip install -r requirements.txt

```



\### 2. Database Deployment \& Schema Mapping

To automatically create the required collections and ingest the data into your local database instance, execute the primary seed script:



```bash

python scripts/db\_import.py

```



Next, open MongoDB Compass, navigate to the newly created `EdTechDB` database, activate the integrated \*\*Mongosh\*\* shell panel at the bottom of the interface, and deploy the aggregation view script:



```bash

mongosh mongodb://localhost:27017/EdTechDB scripts/create\_view.js

```

\*Result:\* A pre-filtered virtual collection named `bd\_online\_aggregated` will be safely provisioned inside your database.



\### 3. Running the ML Pipeline

You can trigger the standalone processing pipeline in the background to calculate target baseline historical metrics and generate a projection dataset without opening any graphical user interfaces:



```bash

python scripts/pipeline.py

```

The resulting 12-month forward data structure will overwrite or save directly to `data/predictions\_output.csv`.



\### 4. Navigating the Power BI Dashboard

1\. Launch \*\*Power BI Desktop\*\*.

2\. Open the reporting template located at `reports/dashboard.pbix`.

3\. Click the \*\*Refresh\*\* button on the Home ribbon tab.



Power BI will automatically query your local MongoDB database via the embedded Python engine layer, compute the underlying linear regression parameters, and refresh all interactive canvas assets (including "Total Attendances", "Historical Median", and "Historical Average" KPI blocks).


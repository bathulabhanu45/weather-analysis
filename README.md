# Weather Data Analysis System
A Simple, Clean, Beginner-Friendly College Mini-Project

## Project Overview
**Weather Data Analysis System** is an academic mini-project designed to import, validate, clean, analyze, and visualize historical meteorological observations (temperature, humidity, and rainfall). 

Built strictly with clean, beginner-friendly architecture using **Python Flask**, **Pandas**, **NumPy**, **MySQL**, and **Chart.js**, this project focuses purely on **historical statistical analysis and data quality auditing** without complex forecasting or black-box AI models.

---

## Key Features

### 1. Home Page
- Clean academic header with website title, project subtitle, and overview.
- **"Upload Weather Data"** button to jump directly to file ingestion.
- **"Load Sample Dataset"** button for immediate 1-click demonstration during viva/evaluation.
- Direct link to download the sample CSV template (`sample_weather_data.csv`).

### 2. Interactive Dashboard
Four primary summary metric cards:
- **Total Weather Records**
- **Average Temperature (°C)**
- **Average Humidity (%)**
- **Total Rainfall (mm)**
- Supporting metrics: Minimum Temperature, Maximum Temperature, Locations Monitored, and Date Span.

### 3. CSV File Upload & Validation
- Simple drag-and-drop / file selector for CSV files.
- Validates the required columns: `Date`, `Location`, `Temperature`, `Humidity`, `Rainfall`.
- Validates data formats:
  - Dates must resolve to `YYYY-MM-DD`.
  - Locations must be non-empty strings.
  - Temperature must be numeric between `-60°C` and `65°C`.
  - Humidity must be between `0%` and `100%`.
  - Rainfall must be non-negative (`>= 0.0 mm`).
- Displays uploaded file details: Filename, file size, valid records count, invalid rows count.

### 4. Descriptive Data Analysis (Pandas & NumPy)
- Calculates minimum, maximum, and mean temperature.
- Calculates average relative humidity and cumulative rainfall.
- **Monthly Summary Table**: Aggregates records, average temp, min/max temp, average humidity, and total rainfall per month.
- **Location Summary Table**: Compares meteorological metrics across different cities.

### 5. Charts & Data Visualization (Chart.js)
Four clear, responsive charts with proper units and labels:
1. **Line Chart**: Temperature Trends (°C over time).
2. **Bar Chart**: Monthly Rainfall (mm precipitation per month).
3. **Bar Chart**: Monthly Average Temperature (°C per month).
4. **Line Chart**: Humidity Trends (% relative humidity over time).
- Ability to filter charts by city location.

### 6. Weather Records Management
- Tabular display of all validated weather records (Date, Location, Temperature, Humidity, Rainfall).
- Search by location or date.
- Filter by city and date ranges.
- Pagination controls (15 records per page).
- **Export Filtered Records** directly to a local CSV file.

### 7. Data Quality & Audit Report
- Tracks valid vs. invalid rows.
- Reports missing values per column.
- Transparently logs every rejected row with:
  - Exact row number in the CSV.
  - Raw original data.
  - Issue category (e.g., Missing Value, Invalid Date, Out of Range).
  - Clear explanation of why the record was excluded.

---

## Design and Color Scheme
- **Background**: Simple white (`#ffffff` / `#f8fafc`).
- **Primary Color**: Light blue (`#0284c7`, `#e0f2fe`).
- **Headings & Buttons**: Dark blue (`#1e3a8a`, `#1e40af`).
- **Cards & Sections**: Light grey (`#f1f5f9`, `#f8fafc`).
- Clean, minimal, readable typography, no neon or dark themes.

---

## Technology Stack
- **Frontend**: HTML5, CSS3, Vanilla JavaScript, Chart.js.
- **Backend**: Python Flask.
- **Data Processing**: Pandas, NumPy.
- **Database**: MySQL (with automatic SQLite fallback for zero-setup local execution).

---

## Project Structure
```
weather2/
│
├── app.py                      # Flask application routes and API endpoints
├── config.py                   # Configuration (MySQL settings, paths)
├── database.py                 # Database abstraction layer (MySQL & SQLite fallback)
├── data_processor.py           # Pandas and NumPy analysis and validation logic
├── schema.sql                  # MySQL database creation script
├── sample_weather_data.csv     # 95 realistic multi-city sample weather records
├── sample_with_errors.csv      # Test CSV with intentional errors for testing Quality Report
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
│
├── static/
│   ├── css/
│   │   └── style.css           # Clean styling (white, light blue, dark blue, light grey)
│   └── js/
│       ├── main.js             # UI events, AJAX file upload, table filters & pagination
│       └── charts.js           # Chart.js initialization and updates
│
├── templates/
│   └── index.html              # Clean single-page college portal layout
│
└── uploads/                    # Directory for user uploaded CSV files
```

---

## Quick Start Guide

### 1. Prerequisites
- Python 3.9+ installed.
- (Optional) MySQL Server or XAMPP / WampServer.

### 2. Setup Virtual Environment & Install Dependencies
```bash
# Clone or navigate to the project directory
cd weather2

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Configuration (MySQL)
To use MySQL:
1. Open your MySQL client (e.g. MySQL Workbench, phpMyAdmin, or terminal).
2. Execute the `schema.sql` script:
   ```bash
   mysql -u root -p < schema.sql
   ```
3. Update database credentials in `config.py` if needed:
   ```python
   MYSQL_HOST = 'localhost'
   MYSQL_USER = 'root'
   MYSQL_PASSWORD = 'your_mysql_password'
   MYSQL_DATABASE = 'weather_analysis_db'
   ```
> **Note**: If MySQL server is not running on your machine, the application will **automatically and smoothly fall back to a local SQLite database (`weather_data.db`)**, ensuring that the project will never crash and can be demonstrated immediately!

### 4. Run the Application
```bash
python3 app.py
```
Open your web browser and navigate to:
```
http://127.0.0.1:5001
```

---

## Demonstration Steps for College Presentation / Viva
1. **Initial View**: Click **"Load Sample Dataset"** on the home page. The dashboard will instantly populate with 95 records spanning Mumbai, Delhi, and Bengaluru across the full year 2024.
2. **Dashboard Cards**: Show the calculated aggregate metrics (Avg Temp: ~26.1°C, Avg Humidity: ~64.5%, Total Rainfall: ~1477.8 mm).
3. **Charts**: Scroll to the Charts section to showcase:
   - Temperature variation across the year.
   - Monsoon precipitation peaks (June-July) in the Monthly Rainfall bar chart.
   - Humidity trends and monthly average temperatures.
   - Filter charts by individual city using the dropdown.
4. **Data Quality Demonstration**:
   - Scroll to **Upload CSV**.
   - Upload `sample_with_errors.csv` (provided in the repository).
   - Scroll to the **Data Quality Report** section to highlight the detected errors (e.g., negative humidity, non-numeric temperature, invalid date strings) and explain how the system gracefully sanitized the dataset.
5. **Weather Records Table**: Demonstrate live search by city name, date filtering, and clicking **"Export Filtered Records"** to download the results.


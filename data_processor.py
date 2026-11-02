import pandas as pd
import numpy as np
from datetime import datetime

REQUIRED_COLUMNS = ['Date', 'Location', 'Temperature', 'Humidity', 'Rainfall']

def validate_and_process_csv(filepath):
    """
    Reads an uploaded CSV file, validates columns, checks data quality,
    separates valid and invalid rows, and returns processed records along with quality logs.
    """
    try:
        # Read CSV file
        raw_df = pd.read_csv(filepath)
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to parse CSV file: {str(e)}',
            'valid_records': [],
            'quality_logs': [],
            'column_missing_counts': {},
            'summary': {}
        }

    # Normalize column names: strip whitespace
    raw_df.columns = [str(c).strip() for c in raw_df.columns]

    # Map column names case-insensitively to required standard names
    col_map = {}
    for req in REQUIRED_COLUMNS:
        match = [c for c in raw_df.columns if c.lower() == req.lower()]
        if match:
            col_map[match[0]] = req

    # Check for missing required columns
    missing_required = [req for req in REQUIRED_COLUMNS if req not in col_map.values()]
    if missing_required:
        return {
            'success': False,
            'error': f"CSV is missing required column(s): {', '.join(missing_required)}. Expected columns: Date, Location, Temperature, Humidity, Rainfall.",
            'valid_records': [],
            'quality_logs': [],
            'column_missing_counts': {},
            'summary': {}
        }

    # Rename to canonical names
    df = raw_df.rename(columns=col_map)

    # Calculate missing values count in raw dataset
    column_missing_counts = {}
    for col in REQUIRED_COLUMNS:
        column_missing_counts[col] = int(df[col].isna().sum())

    valid_records = []
    quality_logs = []

    # Process row by row with validation
    for idx, row in df.iterrows():
        row_num = idx + 2 # +2 for 1-based indexing + header row
        raw_row_dict = {col: (None if pd.isna(row[col]) else row[col]) for col in REQUIRED_COLUMNS}
        raw_str = ", ".join([f"{k}: {v}" for k, v in raw_row_dict.items()])

        row_errors = []

        # 1. Validate Date
        date_val = row.get('Date')
        parsed_date_str = None
        if pd.isna(date_val) or str(date_val).strip() == '':
            row_errors.append(("Missing Value", "Date is missing or blank", "Row ignored"))
        else:
            try:
                # Flexible date parsing
                parsed_dt = pd.to_datetime(date_val, errors='raise')
                parsed_date_str = parsed_dt.strftime('%Y-%m-%d')
            except Exception:
                row_errors.append(("Invalid Date", f"Cannot parse date '{date_val}'. Format should be YYYY-MM-DD", "Row ignored"))

        # 2. Validate Location
        loc_val = row.get('Location')
        parsed_loc = None
        if pd.isna(loc_val) or str(loc_val).strip() == '':
            row_errors.append(("Missing Value", "Location is missing or empty", "Row ignored"))
        else:
            parsed_loc = str(loc_val).strip()

        # 3. Validate Temperature
        temp_val = row.get('Temperature')
        parsed_temp = None
        if pd.isna(temp_val) or str(temp_val).strip() == '':
            row_errors.append(("Missing Value", "Temperature value is missing", "Row ignored"))
        else:
            try:
                parsed_temp = float(temp_val)
                # Physical range check
                if parsed_temp < -60 or parsed_temp > 65:
                    row_errors.append(("Out of Range", f"Temperature {parsed_temp}°C is outside plausible bounds (-60°C to 65°C)", "Row ignored"))
            except ValueError:
                row_errors.append(("Invalid Type", f"Non-numeric temperature value '{temp_val}'", "Row ignored"))

        # 4. Validate Humidity
        hum_val = row.get('Humidity')
        parsed_hum = None
        if pd.isna(hum_val) or str(hum_val).strip() == '':
            row_errors.append(("Missing Value", "Humidity value is missing", "Row ignored"))
        else:
            try:
                parsed_hum = float(hum_val)
                # Humidity must be 0 to 100%
                if parsed_hum < 0 or parsed_hum > 100:
                    row_errors.append(("Out of Range", f"Humidity {parsed_hum}% must be between 0% and 100%", "Row ignored"))
            except ValueError:
                row_errors.append(("Invalid Type", f"Non-numeric humidity value '{hum_val}'", "Row ignored"))

        # 5. Validate Rainfall
        rain_val = row.get('Rainfall')
        parsed_rain = 0.0
        if pd.isna(rain_val) or str(rain_val).strip() == '':
            row_errors.append(("Missing Value", "Rainfall value is missing", "Row ignored"))
        else:
            try:
                parsed_rain = float(rain_val)
                if parsed_rain < 0:
                    row_errors.append(("Out of Range", f"Rainfall cannot be negative ({parsed_rain} mm)", "Row ignored"))
                elif parsed_rain > 1500:
                    row_errors.append(("Out of Range", f"Rainfall {parsed_rain} mm exceeds realistic daily threshold (1500 mm)", "Row ignored"))
            except ValueError:
                row_errors.append(("Invalid Type", f"Non-numeric rainfall value '{rain_val}'", "Row ignored"))

        # If any validation errors, log them and skip row
        if row_errors:
            for issue_type, desc, action in row_errors:
                quality_logs.append({
                    'row_number': row_num,
                    'raw_data': raw_str,
                    'issue_type': issue_type,
                    'description': desc,
                    'action_taken': action
                })
        else:
            # Row is completely valid
            valid_records.append({
                'record_date': parsed_date_str,
                'location': parsed_loc,
                'temperature': round(parsed_temp, 2),
                'humidity': round(parsed_hum, 2),
                'rainfall': round(parsed_rain, 2)
            })

    total_rows = len(df)
    valid_count = len(valid_records)
    invalid_count = total_rows - valid_count

    return {
        'success': True,
        'error': None,
        'total_rows': total_rows,
        'valid_count': valid_count,
        'invalid_count': invalid_count,
        'valid_records': valid_records,
        'quality_logs': quality_logs,
        'column_missing_counts': column_missing_counts
    }


def compute_weather_analytics(records):
    """
    Takes a list of valid record dictionaries and computes comprehensive analytics
    using Pandas and NumPy:
    - Overall summary (min, max, avg temp; avg humidity; total rainfall)
    - Monthly summary table
    - Daily trend series for charts
    - Location breakdown
    """
    if not records:
        return {
            'has_data': False,
            'total_records': 0,
            'summary': {
                'total_records': 0,
                'min_temp': 0.0,
                'max_temp': 0.0,
                'avg_temp': 0.0,
                'avg_humidity': 0.0,
                'total_rainfall': 0.0,
                'unique_locations': 0,
                'date_range': 'N/A'
            },
            'monthly_summary': [],
            'location_summary': [],
            'chart_data': {
                'dates': [],
                'temperatures': [],
                'humidities': [],
                'rainfalls': [],
                'monthly_labels': [],
                'monthly_rain': [],
                'monthly_avg_temp': []
            }
        }

    df = pd.DataFrame(records)
    df['record_date'] = pd.to_datetime(df['date'] if 'date' in df.columns else df['record_date'])
    df['temperature'] = pd.to_numeric(df['temperature'])
    df['humidity'] = pd.to_numeric(df['humidity'])
    df['rainfall'] = pd.to_numeric(df['rainfall'])

    # Sort chronologically
    df = df.sort_values(by='record_date')

    # Core statistics using NumPy & Pandas
    temp_array = df['temperature'].to_numpy()
    hum_array = df['humidity'].to_numpy()
    rain_array = df['rainfall'].to_numpy()

    min_temp = float(np.min(temp_array))
    max_temp = float(np.max(temp_array))
    avg_temp = float(np.mean(temp_array))
    avg_humidity = float(np.mean(hum_array))
    total_rainfall = float(np.sum(rain_array))
    total_records = len(df)
    unique_locations = int(df['location'].nunique())

    min_date = df['record_date'].min().strftime('%d %b %Y')
    max_date = df['record_date'].max().strftime('%d %b %Y')
    date_range_str = f"{min_date} to {max_date}" if min_date != max_date else min_date

    # Monthly Summary
    df['year_month'] = df['record_date'].dt.to_period('M').astype(str)
    df['month_name'] = df['record_date'].dt.strftime('%b %Y')

    monthly_group = df.groupby(['year_month', 'month_name']).agg(
        record_count=('record_date', 'count'),
        avg_temp=('temperature', 'mean'),
        min_temp=('temperature', 'min'),
        max_temp=('temperature', 'max'),
        avg_humidity=('humidity', 'mean'),
        total_rainfall=('rainfall', 'sum')
    ).reset_index().sort_values(by='year_month')

    monthly_summary = []
    for _, row in monthly_group.iterrows():
        monthly_summary.append({
            'period': row['year_month'],
            'month_name': row['month_name'],
            'record_count': int(row['record_count']),
            'avg_temp': round(float(row['avg_temp']), 2),
            'min_temp': round(float(row['min_temp']), 2),
            'max_temp': round(float(row['max_temp']), 2),
            'avg_humidity': round(float(row['avg_humidity']), 1),
            'total_rainfall': round(float(row['total_rainfall']), 2)
        })

    # Location Summary
    loc_group = df.groupby('location').agg(
        records=('record_date', 'count'),
        avg_temp=('temperature', 'mean'),
        min_temp=('temperature', 'min'),
        max_temp=('temperature', 'max'),
        avg_humidity=('humidity', 'mean'),
        total_rainfall=('rainfall', 'sum')
    ).reset_index().sort_values(by='records', ascending=False)

    location_summary = []
    for _, row in loc_group.iterrows():
        location_summary.append({
            'location': row['location'],
            'records': int(row['records']),
            'avg_temp': round(float(row['avg_temp']), 2),
            'min_temp': round(float(row['min_temp']), 2),
            'max_temp': round(float(row['max_temp']), 2),
            'avg_humidity': round(float(row['avg_humidity']), 1),
            'total_rainfall': round(float(row['total_rainfall']), 2)
        })

    # Daily aggregation for line charts (averaging multi-location records on the same day)
    daily_group = df.groupby(df['record_date'].dt.strftime('%Y-%m-%d')).agg(
        avg_temp=('temperature', 'mean'),
        avg_humidity=('humidity', 'mean'),
        sum_rainfall=('rainfall', 'sum')
    ).reset_index().sort_values(by='record_date')

    chart_dates = daily_group['record_date'].tolist()
    chart_temps = [round(float(t), 2) for t in daily_group['avg_temp']]
    chart_hum = [round(float(h), 1) for h in daily_group['avg_humidity']]
    chart_rain = [round(float(r), 2) for r in daily_group['sum_rainfall']]

    # Monthly chart series
    monthly_labels = [m['month_name'] for m in monthly_summary]
    monthly_rain = [m['total_rainfall'] for m in monthly_summary]
    monthly_avg_temp = [m['avg_temp'] for m in monthly_summary]

    return {
        'has_data': True,
        'total_records': total_records,
        'summary': {
            'total_records': total_records,
            'min_temp': round(min_temp, 2),
            'max_temp': round(max_temp, 2),
            'avg_temp': round(avg_temp, 2),
            'avg_humidity': round(avg_humidity, 1),
            'total_rainfall': round(total_rainfall, 2),
            'unique_locations': unique_locations,
            'date_range': date_range_str
        },
        'monthly_summary': monthly_summary,
        'location_summary': location_summary,
        'chart_data': {
            'dates': chart_dates,
            'temperatures': chart_temps,
            'humidities': chart_hum,
            'rainfalls': chart_rain,
            'monthly_labels': monthly_labels,
            'monthly_rain': monthly_rain,
            'monthly_avg_temp': monthly_avg_temp
        }
    }


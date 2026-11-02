import os
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from config import Config
from database import (
    init_db,
    get_active_db_type,
    insert_upload_history,
    insert_weather_records,
    insert_data_quality_logs,
    fetch_weather_records,
    fetch_quality_logs,
    fetch_upload_history,
    clear_all_data
)
from data_processor import validate_and_process_csv, compute_weather_analytics

app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize DB tables on startup
active_database_type = init_db()

# Auto-seed sample data if database is empty so tables and graphs show data immediately
def auto_seed_sample_if_empty():
    records = fetch_weather_records()
    if len(records) == 0:
        sample_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sample_weather_data.csv')
        if os.path.exists(sample_path):
            file_size = os.path.getsize(sample_path)
            res = validate_and_process_csv(sample_path)
            if res['success'] and res['valid_records']:
                upload_id = insert_upload_history('sample_weather_data.csv', file_size, res['total_rows'], res['valid_count'], res['invalid_count'])
                records_to_insert = [
                    (upload_id, r['record_date'], r['location'], r['temperature'], r['humidity'], r['rainfall'])
                    for r in res['valid_records']
                ]
                insert_weather_records(records_to_insert)
                print(f"[DATABASE] Auto-loaded {len(records_to_insert)} sample records on startup.")

auto_seed_sample_if_empty()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@app.route('/')
def home():
    """Renders the main single-page application."""
    return render_template('index.html', db_type=get_active_db_type())

@app.route('/api/status', methods=['GET'])
def get_system_status():
    """Returns database status and high-level counts."""
    records = fetch_weather_records()
    history = fetch_upload_history()
    return jsonify({
        'status': 'online',
        'database_engine': get_active_db_type().upper(),
        'total_records': len(records),
        'uploads_count': len(history)
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handles CSV file upload, validation, quality check, and database insertion."""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part in the request.'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file was selected for upload.'}), 400

    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'Invalid file type. Only .csv files are supported.'}), 400

    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(save_path)
    file_size = os.path.getsize(save_path)

    # Process and validate CSV using Pandas
    result = validate_and_process_csv(save_path)

    if not result['success']:
        # Cleanup uploaded file if unparseable
        if os.path.exists(save_path):
            os.remove(save_path)
        return jsonify({'success': False, 'message': result['error']}), 400

    total_rows = result['total_rows']
    valid_count = result['valid_count']
    invalid_count = result['invalid_count']
    valid_records = result['valid_records']
    quality_logs = result['quality_logs']

    # Insert into upload history
    upload_id = insert_upload_history(filename, file_size, total_rows, valid_count, invalid_count)

    # Insert valid records into database
    if valid_records:
        records_to_insert = [
            (upload_id, r['record_date'], r['location'], r['temperature'], r['humidity'], r['rainfall'])
            for r in valid_records
        ]
        insert_weather_records(records_to_insert)

    # Insert data quality error logs into database
    if quality_logs:
        logs_to_insert = [
            (upload_id, log['row_number'], log['raw_data'], log['issue_type'], log['description'], log['action_taken'])
            for log in quality_logs
        ]
        insert_data_quality_logs(logs_to_insert)

    return jsonify({
        'success': True,
        'message': f"CSV processed successfully! {valid_count} valid records imported, {invalid_count} invalid records logged.",
        'upload_info': {
            'upload_id': upload_id,
            'filename': filename,
            'file_size_formatted': f"{round(file_size / 1024, 2)} KB",
            'total_rows': total_rows,
            'valid_count': valid_count,
            'invalid_count': invalid_count,
            'missing_counts': result['column_missing_counts']
        }
    })

@app.route('/api/load-sample', methods=['POST'])
def load_sample_data():
    """Populates the database with the provided sample_weather_data.csv for quick demo."""
    sample_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sample_weather_data.csv')
    if not os.path.exists(sample_path):
        return jsonify({'success': False, 'message': 'Sample data file not found.'}), 404

    file_size = os.path.getsize(sample_path)
    result = validate_and_process_csv(sample_path)
    if not result['success']:
        return jsonify({'success': False, 'message': result['error']}), 400

    upload_id = insert_upload_history('sample_weather_data.csv', file_size, result['total_rows'], result['valid_count'], result['invalid_count'])

    records_to_insert = [
        (upload_id, r['record_date'], r['location'], r['temperature'], r['humidity'], r['rainfall'])
        for r in result['valid_records']
    ]
    insert_weather_records(records_to_insert)

    return jsonify({
        'success': True,
        'message': f"Sample dataset loaded successfully! {result['valid_count']} records imported.",
        'records_loaded': result['valid_count']
    })

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Computes overall statistics, monthly aggregates, and chart series."""
    location = request.args.get('location', 'all')
    date_from = request.args.get('date_from', None)
    date_to = request.args.get('date_to', None)

    records = fetch_weather_records(search="", location=location, date_from=date_from, date_to=date_to)
    analytics = compute_weather_analytics(records)
    return jsonify(analytics)

@app.route('/api/records', methods=['GET'])
def get_records():
    """Returns weather records with search, filtering, and pagination support."""
    search = request.args.get('search', '').strip()
    location = request.args.get('location', 'all')
    date_from = request.args.get('date_from', None)
    date_to = request.args.get('date_to', None)
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 15))

    all_records = fetch_weather_records(search=search, location=location, date_from=date_from, date_to=date_to)
    total_count = len(all_records)

    start = (page - 1) * per_page
    end = start + per_page
    paginated_records = all_records[start:end]

    return jsonify({
        'total': total_count,
        'page': page,
        'per_page': per_page,
        'total_pages': (total_count + per_page - 1) // per_page if total_count > 0 else 1,
        'records': paginated_records
    })

@app.route('/api/locations', methods=['GET'])
def get_locations():
    """Returns unique list of locations present in the database."""
    records = fetch_weather_records()
    locations = sorted(list(set([r['location'] for r in records])))
    return jsonify({'locations': locations})

@app.route('/api/quality-report', methods=['GET'])
def get_quality_report():
    """Returns full data quality analysis: missing counts, invalid rows, valid counts, and explanations."""
    logs = fetch_quality_logs()
    uploads = fetch_upload_history()
    records = fetch_weather_records()

    total_uploaded_rows = sum([u['total_rows'] for u in uploads]) if uploads else len(records)
    total_valid = len(records)
    total_invalid = len(logs)

    # Tally issue categories
    issue_counts = {}
    for log in logs:
        itype = log['issue_type']
        issue_counts[itype] = issue_counts.get(itype, 0) + 1

    return jsonify({
        'total_uploaded_rows': total_uploaded_rows,
        'total_valid_records': total_valid,
        'total_invalid_records': total_invalid,
        'issue_counts': issue_counts,
        'detailed_logs': logs[:100], # return latest 100 logs
        'uploads': uploads
    })

@app.route('/api/reset', methods=['POST'])
def reset_database():
    """Clears all weather data and logs for demonstration reset."""
    clear_all_data()
    return jsonify({'success': True, 'message': 'All weather records and logs cleared successfully.'})

@app.route('/download-sample')
def download_sample():
    """Serves the sample weather CSV file for download."""
    sample_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sample_weather_data.csv')
    return send_file(sample_path, as_attachment=True, download_name='sample_weather_data.csv')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f"Weather Data Analysis System running at http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)


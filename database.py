import sqlite3
import os
import logging
from config import Config

logger = logging.getLogger(__name__)

# Track active database type in memory
ACTIVE_DB_TYPE = "sqlite"
_MYSQL_AVAILABLE = None

def check_mysql_availability():
    """Check once if MySQL server is reachable."""
    global _MYSQL_AVAILABLE
    if _MYSQL_AVAILABLE is not None:
        return _MYSQL_AVAILABLE
    if Config.DB_TYPE != 'mysql':
        _MYSQL_AVAILABLE = False
        return False
    try:
        import mysql.connector
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            connection_timeout=1
        )
        conn.close()
        _MYSQL_AVAILABLE = True
        return True
    except Exception as e:
        logger.warning(f"MySQL unavailable: {e}")
        _MYSQL_AVAILABLE = False
        return False

def get_mysql_connection(create_db=False):
    """Attempt to establish a MySQL connection using mysql.connector."""
    if not check_mysql_availability():
        return None
    try:
        import mysql.connector
        if create_db:
            return mysql.connector.connect(
                host=Config.MYSQL_HOST,
                port=Config.MYSQL_PORT,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                connection_timeout=1
            )
        else:
            return mysql.connector.connect(
                host=Config.MYSQL_HOST,
                port=Config.MYSQL_PORT,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=Config.MYSQL_DATABASE,
                connection_timeout=1
            )
    except Exception as e:
        logger.warning(f"MySQL connection error: {e}")
        return None

def get_sqlite_connection():
    """Establish a connection to the SQLite database."""
    conn = sqlite3.connect(Config.SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_db_connection():
    """Returns an active database connection (MySQL if available, otherwise SQLite fallback)."""
    global ACTIVE_DB_TYPE
    if ACTIVE_DB_TYPE == "mysql" and check_mysql_availability():
        mysql_conn = get_mysql_connection()
        if mysql_conn and mysql_conn.is_connected():
            return mysql_conn
    
    # Fallback to SQLite
    ACTIVE_DB_TYPE = "sqlite"
    return get_sqlite_connection()

def init_db():
    """Initialize database tables for MySQL or SQLite."""
    global ACTIVE_DB_TYPE

    # Check if MySQL can be used
    if Config.DB_TYPE == 'mysql':
        try:
            root_conn = get_mysql_connection(create_db=True)
            if root_conn:
                cursor = root_conn.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.MYSQL_DATABASE}` CHARACTER SET utf8mb4;")
                root_conn.close()

                mysql_conn = get_mysql_connection()
                if mysql_conn:
                    cursor = mysql_conn.cursor()
                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS upload_history (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        filename VARCHAR(255) NOT NULL,
                        file_size_bytes INT NOT NULL,
                        total_rows INT NOT NULL,
                        valid_rows INT NOT NULL,
                        invalid_rows INT NOT NULL,
                        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                    """)

                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS weather_records (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        upload_id INT NULL,
                        record_date DATE NOT NULL,
                        location VARCHAR(100) NOT NULL,
                        temperature DECIMAL(5, 2) NOT NULL,
                        humidity DECIMAL(5, 2) NOT NULL,
                        rainfall DECIMAL(6, 2) NOT NULL DEFAULT 0.00,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_date (record_date),
                        INDEX idx_location (location)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                    """)

                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS data_quality_logs (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        upload_id INT NULL,
                        row_number INT NOT NULL,
                        raw_data TEXT,
                        issue_type VARCHAR(100) NOT NULL,
                        description TEXT NOT NULL,
                        action_taken VARCHAR(50) NOT NULL,
                        logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                    """)
                    mysql_conn.commit()
                    mysql_conn.close()
                    ACTIVE_DB_TYPE = "mysql"
                    print("[DATABASE] Connected and initialized MySQL successfully.")
                    return "mysql"
        except Exception as e:
            print(f"[DATABASE] Notice: MySQL unavailable ({e}). Using SQLite for quick zero-setup operation.")

    # SQLite initialization
    ACTIVE_DB_TYPE = "sqlite"
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS upload_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        file_size_bytes INTEGER NOT NULL,
        total_rows INTEGER NOT NULL,
        valid_rows INTEGER NOT NULL,
        invalid_rows INTEGER NOT NULL,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS weather_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        upload_id INTEGER NULL,
        record_date TEXT NOT NULL,
        location TEXT NOT NULL,
        temperature REAL NOT NULL,
        humidity REAL NOT NULL,
        rainfall REAL NOT NULL DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS data_quality_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        upload_id INTEGER NULL,
        row_number INTEGER NOT NULL,
        raw_data TEXT,
        issue_type TEXT NOT NULL,
        description TEXT NOT NULL,
        action_taken TEXT NOT NULL,
        logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()
    print("[DATABASE] Connected and initialized SQLite successfully.")
    return "sqlite"

def get_active_db_type():
    return ACTIVE_DB_TYPE

def insert_upload_history(filename, file_size_bytes, total_rows, valid_rows, invalid_rows):
    """Insert a record into upload_history and return inserted ID."""
    conn = get_db_connection()
    upload_id = None
    try:
        cursor = conn.cursor()
        if ACTIVE_DB_TYPE == "mysql":
            query = """
            INSERT INTO upload_history (filename, file_size_bytes, total_rows, valid_rows, invalid_rows)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (filename, file_size_bytes, total_rows, valid_rows, invalid_rows))
            upload_id = cursor.lastrowid
        else:
            query = """
            INSERT INTO upload_history (filename, file_size_bytes, total_rows, valid_rows, invalid_rows)
            VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(query, (filename, file_size_bytes, total_rows, valid_rows, invalid_rows))
            upload_id = cursor.lastrowid
        conn.commit()
    finally:
        conn.close()
    return upload_id

def insert_weather_records(records_list):
    """Insert batch of validated weather records: [(upload_id, date, location, temp, humidity, rain), ...]"""
    if not records_list:
        return 0
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if ACTIVE_DB_TYPE == "mysql":
            query = """
            INSERT INTO weather_records (upload_id, record_date, location, temperature, humidity, rainfall)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(query, records_list)
        else:
            query = """
            INSERT INTO weather_records (upload_id, record_date, location, temperature, humidity, rainfall)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.executemany(query, records_list)
        conn.commit()
        return len(records_list)
    finally:
        conn.close()

def insert_data_quality_logs(logs_list):
    """Insert batch of data quality error logs: [(upload_id, row_num, raw_data, issue_type, desc, action), ...]"""
    if not logs_list:
        return 0
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if ACTIVE_DB_TYPE == "mysql":
            query = """
            INSERT INTO data_quality_logs (upload_id, row_number, raw_data, issue_type, description, action_taken)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(query, logs_list)
        else:
            query = """
            INSERT INTO data_quality_logs (upload_id, row_number, raw_data, issue_type, description, action_taken)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.executemany(query, logs_list)
        conn.commit()
        return len(logs_list)
    finally:
        conn.close()

def fetch_weather_records(search="", location="all", date_from=None, date_to=None):
    """Fetch all weather records matching filters."""
    conn = get_db_connection()
    records = []
    try:
        cursor = conn.cursor()
        sql = "SELECT id, upload_id, record_date, location, temperature, humidity, rainfall, created_at FROM weather_records WHERE 1=1"
        params = []

        if search:
            if ACTIVE_DB_TYPE == "mysql":
                sql += " AND (location LIKE %s OR record_date LIKE %s)"
                params.extend([f"%{search}%", f"%{search}%"])
            else:
                sql += " AND (location LIKE ? OR record_date LIKE ?)"
                params.extend([f"%{search}%", f"%{search}%"])

        if location and location != "all":
            if ACTIVE_DB_TYPE == "mysql":
                sql += " AND location = %s"
            else:
                sql += " AND location = ?"
            params.append(location)

        if date_from:
            if ACTIVE_DB_TYPE == "mysql":
                sql += " AND record_date >= %s"
            else:
                sql += " AND record_date >= ?"
            params.append(date_from)

        if date_to:
            if ACTIVE_DB_TYPE == "mysql":
                sql += " AND record_date <= %s"
            else:
                sql += " AND record_date <= ?"
            params.append(date_to)

        sql += " ORDER BY record_date ASC, id ASC"

        if ACTIVE_DB_TYPE == "mysql":
            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()
            for r in rows:
                records.append({
                    "id": r[0],
                    "upload_id": r[1],
                    "date": str(r[2]),
                    "location": r[3],
                    "temperature": float(r[4]),
                    "humidity": float(r[5]),
                    "rainfall": float(r[6]),
                    "created_at": str(r[7])
                })
        else:
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            for r in rows:
                records.append({
                    "id": r["id"],
                    "upload_id": r["upload_id"],
                    "date": str(r["record_date"]),
                    "location": r["location"],
                    "temperature": float(r["temperature"]),
                    "humidity": float(r["humidity"]),
                    "rainfall": float(r["rainfall"]),
                    "created_at": str(r["created_at"])
                })
    finally:
        conn.close()
    return records

def fetch_quality_logs(upload_id=None):
    """Fetch data quality logs."""
    conn = get_db_connection()
    logs = []
    try:
        cursor = conn.cursor()
        if upload_id:
            sql = "SELECT id, upload_id, row_number, raw_data, issue_type, description, action_taken, logged_at FROM data_quality_logs WHERE upload_id = ?" if ACTIVE_DB_TYPE != "mysql" else "SELECT id, upload_id, row_number, raw_data, issue_type, description, action_taken, logged_at FROM data_quality_logs WHERE upload_id = %s"
            params = (upload_id,)
        else:
            sql = "SELECT id, upload_id, row_number, raw_data, issue_type, description, action_taken, logged_at FROM data_quality_logs ORDER BY id DESC"
            params = ()

        cursor.execute(sql, params)
        rows = cursor.fetchall()

        if ACTIVE_DB_TYPE == "mysql":
            for r in rows:
                logs.append({
                    "id": r[0],
                    "upload_id": r[1],
                    "row_number": r[2],
                    "raw_data": r[3],
                    "issue_type": r[4],
                    "description": r[5],
                    "action_taken": r[6],
                    "logged_at": str(r[7])
                })
        else:
            for r in rows:
                logs.append({
                    "id": r["id"],
                    "upload_id": r["upload_id"],
                    "row_number": r["row_number"],
                    "raw_data": r["raw_data"],
                    "issue_type": r["issue_type"],
                    "description": r["description"],
                    "action_taken": r["action_taken"],
                    "logged_at": str(r["logged_at"])
                })
    finally:
        conn.close()
    return logs

def fetch_upload_history():
    """Fetch upload history records."""
    conn = get_db_connection()
    history = []
    try:
        cursor = conn.cursor()
        sql = "SELECT id, filename, file_size_bytes, total_rows, valid_rows, invalid_rows, uploaded_at FROM upload_history ORDER BY id DESC"
        cursor.execute(sql)
        rows = cursor.fetchall()
        if ACTIVE_DB_TYPE == "mysql":
            for r in rows:
                history.append({
                    "id": r[0],
                    "filename": r[1],
                    "file_size": r[2],
                    "total_rows": r[3],
                    "valid_rows": r[4],
                    "invalid_rows": r[5],
                    "uploaded_at": str(r[6])
                })
        else:
            for r in rows:
                history.append({
                    "id": r["id"],
                    "filename": r["filename"],
                    "file_size": r["file_size_bytes"],
                    "total_rows": r["total_rows"],
                    "valid_rows": r["valid_rows"],
                    "invalid_rows": r["invalid_rows"],
                    "uploaded_at": str(r["uploaded_at"])
                })
    finally:
        conn.close()
    return history

def clear_all_data():
    """Delete all records from database tables for a fresh start."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM weather_records")
        cursor.execute("DELETE FROM data_quality_logs")
        cursor.execute("DELETE FROM upload_history")
        conn.commit()
        return True
    finally:
        conn.close()


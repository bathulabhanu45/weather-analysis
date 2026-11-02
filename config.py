import os

class Config:
    """Application configuration for Weather Data Analysis System."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'college_project_secret_key_2024')
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'csv'}

    # Database configuration
    # Default is MySQL; if connection fails, automatically fall back to SQLite for convenience
    DB_TYPE = os.environ.get('DB_TYPE', 'mysql').lower() # 'mysql' or 'sqlite'
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'weather_analysis_db')

    # SQLite fallback database file
    SQLITE_DB_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'weather_data.db')


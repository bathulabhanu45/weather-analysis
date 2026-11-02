-- ====================================================================
-- College Project: Weather Data Analysis System
-- Database Schema for MySQL
-- ====================================================================

-- 1. Create Database if not exists
CREATE DATABASE IF NOT EXISTS weather_analysis_db;
USE weather_analysis_db;

-- 2. Drop tables if they already exist (for clean re-run)
DROP TABLE IF EXISTS data_quality_logs;
DROP TABLE IF EXISTS weather_records;
DROP TABLE IF EXISTS upload_history;

-- 3. Upload History Table (tracks uploaded CSV files)
CREATE TABLE upload_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_size_bytes INT NOT NULL,
    total_rows INT NOT NULL,
    valid_rows INT NOT NULL,
    invalid_rows INT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Weather Records Table (stores validated historical weather entries)
CREATE TABLE weather_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    upload_id INT NULL,
    record_date DATE NOT NULL,
    location VARCHAR(100) NOT NULL,
    temperature DECIMAL(5, 2) NOT NULL COMMENT 'Temperature in degrees Celsius',
    humidity DECIMAL(5, 2) NOT NULL COMMENT 'Relative Humidity in percentage',
    rainfall DECIMAL(6, 2) NOT NULL DEFAULT 0.00 COMMENT 'Precipitation in millimeters',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (upload_id) REFERENCES upload_history(id) ON DELETE SET NULL,
    INDEX idx_date (record_date),
    INDEX idx_location (location)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Data Quality Logs Table (logs issues detected during CSV validation)
CREATE TABLE data_quality_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    upload_id INT NULL,
    row_number INT NOT NULL,
    raw_data TEXT,
    issue_type VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    action_taken VARCHAR(50) NOT NULL COMMENT 'e.g., Ignored / Skipped / Defaulted',
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (upload_id) REFERENCES upload_history(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Sample query for demonstration in viva:
-- SELECT location, AVG(temperature) AS avg_temp, AVG(humidity) AS avg_humidity, SUM(rainfall) AS total_rain
-- FROM weather_records
-- GROUP BY location;


-- Complete database schema for Asset Management System

CREATE TABLE IF NOT EXISTS suppliers (
    name VARCHAR(255) PRIMARY KEY,
    contact VARCHAR(255),
    email VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS inventory (
    name VARCHAR(255) PRIMARY KEY,
    quantity INTEGER NOT NULL,
    price DECIMAL(10,2) DEFAULT 0.0,
    description TEXT,
    low_stock_threshold INTEGER DEFAULT 5,
    category VARCHAR(255) DEFAULT 'Uncategorized',
    supplier VARCHAR(255),
    department VARCHAR(255) NULL,
    location VARCHAR(255) NULL,
    model VARCHAR(255) NULL,
    brand VARCHAR(255) NULL,
    serial_number VARCHAR(255) NULL,
    purchase_date DATE NULL,
    depreciation_method VARCHAR(50) DEFAULT 'straight_line',
    useful_life_years INT DEFAULT 5,
    salvage_value DECIMAL(10,2) DEFAULT 0.0,
    FOREIGN KEY (supplier) REFERENCES suppliers(name) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS `groups` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255),
    password_hash VARCHAR(255),
    name VARCHAR(255),
    profile_picture VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS user_groups (
    user_id INT,
    group_id INT,
    PRIMARY KEY (user_id, group_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES `groups`(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS asset_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_name VARCHAR(255) NOT NULL,
    action VARCHAR(50) NOT NULL,
    quantity INT NOT NULL,
    person VARCHAR(255),
    department VARCHAR(255),
    location VARCHAR(255),
    notes TEXT,
    username VARCHAR(255),
    user_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (asset_name) REFERENCES inventory(name) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS email_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender VARCHAR(255),
    password VARCHAR(255),
    recipient VARCHAR(255),
    smtp_server VARCHAR(255) DEFAULT 'smtp.gmail.com',
    port INTEGER DEFAULT 587
);

CREATE TABLE IF NOT EXISTS dashboard_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    widget_name VARCHAR(100) NOT NULL,
    is_enabled BOOLEAN DEFAULT TRUE,
    display_order INT DEFAULT 0,
    UNIQUE KEY unique_user_widget (user_id, widget_name)
);

CREATE TABLE IF NOT EXISTS dashboard_charts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    chart_name VARCHAR(100) NOT NULL,
    is_enabled BOOLEAN DEFAULT TRUE,
    display_order INT DEFAULT 0,
    UNIQUE KEY unique_user_chart (user_id, chart_name)
);

CREATE DATABASE IF NOT EXISTS db_asset;

USE db_asset;

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
    FOREIGN KEY (supplier) REFERENCES suppliers(name) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS email_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender VARCHAR(255),
    password VARCHAR(255),
    recipient VARCHAR(255),
    smtp_server VARCHAR(255) DEFAULT 'smtp.gmail.com',
    port INTEGER DEFAULT 587
);
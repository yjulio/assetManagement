-- Advanced Asset Management Tables Migration--  Date: March 3, 2026
-- Description: Creates tables for asset groups, registry, attributes, damage tracking, transfers, and types

USE db_asset;

-- Asset Groups Table
CREATE TABLE IF NOT EXISTS asset_groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    code VARCHAR(20),
    parent_id INT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES asset_groups(id) ON DELETE SET NULL,
    INDEX idx_name (name),
    INDEX idx_code (code),
    INDEX idx_parent (parent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Asset Attributes Table (for custom fields)
CREATE TABLE IF NOT EXISTS asset_attributes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    attribute_name VARCHAR(100) NOT NULL UNIQUE,
    data_type ENUM('text', 'number', 'date', 'boolean', 'select') DEFAULT 'text',
    is_required BOOLEAN DEFAULT FALSE,
    options TEXT NULL, -- JSON for select options
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_attribute_name (attribute_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Asset Attribute Values Table (stores actual values)
CREATE TABLE IF NOT EXISTS asset_attribute_values (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_name VARCHAR(255) NOT NULL,
    attribute_id INT NOT NULL,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (attribute_id) REFERENCES asset_attributes(id) ON DELETE CASCADE,
    UNIQUE KEY unique_asset_attribute (asset_name, attribute_id),
    INDEX idx_asset_name (asset_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Asset Damage Table
CREATE TABLE IF NOT EXISTS asset_damage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_name VARCHAR(255) NOT NULL,
    damage_type ENUM('Physical', 'Software', 'Other') DEFAULT 'Physical',
    description TEXT,
    severity ENUM('Low', 'Medium', 'High', 'Critical') DEFAULT 'Medium',
    reported_by VARCHAR(255),
    reported_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Open', 'In Progress', 'Resolved', 'Closed') DEFAULT 'Open',
    resolution_notes TEXT,
    resolved_date TIMESTAMP NULL,
    resolved_by VARCHAR(255),
    repair_cost DECIMAL(10,2) DEFAULT 0.00,
    INDEX idx_asset (asset_name),
    INDEX idx_status (status),
    INDEX idx_reported_date (reported_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Asset Transfers Table
CREATE TABLE IF NOT EXISTS asset_transfers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_name VARCHAR(255) NOT NULL,
    from_location VARCHAR(255),
    to_location VARCHAR(255) NOT NULL,
    from_department VARCHAR(255),
    to_department VARCHAR(255),
    from_person VARCHAR(255),
    to_person VARCHAR(255),
    transferred_by VARCHAR(255),
    transfer_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    status ENUM('Pending', 'In Transit', 'Completed', 'Cancelled') DEFAULT 'Completed',
    INDEX idx_asset (asset_name),
    INDEX idx_transfer_date (transfer_date),
    INDEX idx_from_location (from_location),
    INDEX idx_to_location (to_location)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Asset Types Table (enhanced categories)
CREATE TABLE IF NOT EXISTS asset_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type_name VARCHAR(100) NOT NULL UNIQUE,
    type_code VARCHAR(20),
    description TEXT,
    parent_type_id INT NULL,
    depreciation_rate DECIMAL(5,2) DEFAULT 0.00,
    default_useful_life INT DEFAULT 5,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_type_id) REFERENCES asset_types(id) ON DELETE SET NULL,
    INDEX idx_type_name (type_name),
    INDEX idx_type_code (type_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Asset Assignment Table (who is responsible for what)
CREATE TABLE IF NOT EXISTS asset_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_name VARCHAR(255) NOT NULL,
    assigned_to VARCHAR(255) NOT NULL,
    department VARCHAR(255),
    assigned_by VARCHAR(255),
    assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    return_date TIMESTAMP NULL,
    status ENUM('Active', 'Returned', 'Terminated') DEFAULT 'Active',
    notes TEXT,
    INDEX idx_asset (asset_name),
    INDEX idx_assigned_to (assigned_to),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert some default asset types
INSERT IGNORE INTO asset_types (type_name, type_code, description, depreciation_rate, default_useful_life) VALUES
('Computer Equipment', 'COMP', 'Computers, laptops, servers, networking equipment', 20.00, 5),
('Office Furniture', 'FURN', 'Desks, chairs, cabinets, shelving', 10.00, 10),
('Vehicles', 'VEH', 'Cars, trucks, motorcycles, company vehicles', 15.00, 8),
('Software', 'SOFT', 'Software licenses and subscriptions', 33.33, 3),
('Office Equipment', 'OFFC', 'Printers, copiers, phones, fax machines', 20.00, 5),
('Mobile Devices', 'MOB', 'Smartphones, tablets, mobile devices', 25.00, 4),
('Network Equipment', 'NET', 'Routers, switches, access points, cables', 20.00, 5),
('Tools & Equipment', 'TOOL', 'Hand tools, power tools, equipment', 10.00, 10),
('Building & Infrastructure', 'BLDG', 'Buildings, facilities, infrastructure', 5.00, 20),
('Other Assets', 'OTH', 'Miscellaneous assets', 10.00, 10);

-- Insert some default asset attributes
INSERT IGNORE INTO asset_attributes (attribute_name, data_type, is_required) VALUES
('Warranty Period', 'text', FALSE),
('Vendor Name', 'text', FALSE),
('Installation Date', 'date', FALSE),
('Last Service Date', 'date', FALSE),
('Service Interval (months)', 'number', FALSE),
('Asset Condition', 'select', FALSE),
('Insurance Policy Number', 'text', FALSE),
('Building Floor', 'text', FALSE),
('Room Number', 'text', FALSE),
('IP Address', 'text', FALSE);

COMMIT;

SELECT 'Advanced asset management tables created successfully!' as status;

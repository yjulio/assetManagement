-- Locations table for managing physical locations where assets are stored
CREATE TABLE IF NOT EXISTS locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    code VARCHAR(50) UNIQUE,
    type ENUM('Office', 'Warehouse', 'Store', 'Branch', 'Remote', 'Other') DEFAULT 'Office',
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    postal_code VARCHAR(20),
    phone VARCHAR(50),
    contact_person VARCHAR(255),
    capacity INT DEFAULT 0,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    INDEX idx_name (name),
    INDEX idx_code (code),
    INDEX idx_type (type),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert some default locations
INSERT INTO locations (name, code, type, description, created_by) VALUES
('Main Office', 'HQ-001', 'Office', 'Headquarters main building', 'system'),
('Warehouse A', 'WH-A01', 'Warehouse', 'Primary storage warehouse', 'system'),
('Store 1', 'ST-001', 'Store', 'Retail store location', 'system')
ON DUPLICATE KEY UPDATE name=name;

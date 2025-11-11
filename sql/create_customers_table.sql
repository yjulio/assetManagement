-- Customers table for managing external customers who use/lease assets
CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_code VARCHAR(50) UNIQUE,
    company_name VARCHAR(255) NOT NULL,
    contact_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    mobile VARCHAR(50),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    postal_code VARCHAR(20),
    website VARCHAR(255),
    tax_id VARCHAR(100),
    customer_type ENUM('Individual', 'Corporate', 'Government', 'Non-Profit', 'Other') DEFAULT 'Corporate',
    status ENUM('Active', 'Inactive', 'Suspended', 'Pending') DEFAULT 'Active',
    credit_limit DECIMAL(15,2) DEFAULT 0.00,
    payment_terms VARCHAR(100),
    notes TEXT,
    assigned_assets_count INT DEFAULT 0,
    total_value DECIMAL(15,2) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    INDEX idx_company_name (company_name),
    INDEX idx_customer_code (customer_code),
    INDEX idx_customer_type (customer_type),
    INDEX idx_status (status),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Customer asset assignments tracking
CREATE TABLE IF NOT EXISTS customer_assets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    asset_name VARCHAR(255) NOT NULL,
    assigned_date DATE NOT NULL,
    expected_return_date DATE,
    actual_return_date DATE,
    lease_amount DECIMAL(10,2) DEFAULT 0.00,
    status ENUM('Active', 'Returned', 'Overdue', 'Damaged') DEFAULT 'Active',
    notes TEXT,
    assigned_by VARCHAR(255),
    returned_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    INDEX idx_customer_id (customer_id),
    INDEX idx_asset_name (asset_name),
    INDEX idx_status (status),
    INDEX idx_assigned_date (assigned_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert sample customers
INSERT INTO customers (customer_code, company_name, contact_name, email, phone, customer_type, status, payment_terms, created_by) VALUES
('CUST-001', 'Acme Corporation', 'John Smith', 'john@acme.com', '+1-555-0100', 'Corporate', 'Active', 'Net 30', 'system'),
('CUST-002', 'Tech Solutions Ltd', 'Jane Doe', 'jane@techsolutions.com', '+1-555-0200', 'Corporate', 'Active', 'Net 15', 'system'),
('CUST-003', 'City Government', 'Mike Johnson', 'mike@citygovt.org', '+1-555-0300', 'Government', 'Active', 'Net 60', 'system')
ON DUPLICATE KEY UPDATE company_name=company_name;

-- Create departments table
CREATE TABLE IF NOT EXISTS departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    manager VARCHAR(255),
    location VARCHAR(255),
    budget DECIMAL(15, 2) DEFAULT 0,
    phone VARCHAR(50),
    email VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_code (code),
    INDEX idx_name (name),
    INDEX idx_is_active (is_active)
);

-- Insert sample departments
INSERT INTO departments (name, code, description, manager, location, budget, phone, email, is_active) VALUES
('Information Technology', 'IT', 'Manages all IT infrastructure, software, and technical support services', 'John Smith', 'Building A, Floor 3', 500000.00, '+678-123-4567', 'it@vbos.gov.vu', TRUE),
('Human Resources', 'HR', 'Handles recruitment, employee relations, and personnel management', 'Sarah Johnson', 'Building B, Floor 2', 250000.00, '+678-123-4568', 'hr@vbos.gov.vu', TRUE),
('Finance', 'FIN', 'Manages financial planning, accounting, and budget administration', 'Michael Brown', 'Building A, Floor 1', 800000.00, '+678-123-4569', 'finance@vbos.gov.vu', TRUE),
('Statistics', 'STAT', 'Conducts data collection, analysis, and statistical reporting', 'Emily Davis', 'Building C, Floor 2', 600000.00, '+678-123-4570', 'statistics@vbos.gov.vu', TRUE),
('Administration', 'ADMIN', 'Handles general administrative services and office management', 'David Wilson', 'Building A, Floor 2', 300000.00, '+678-123-4571', 'admin@vbos.gov.vu', TRUE);

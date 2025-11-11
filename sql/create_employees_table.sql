-- Create employees table
CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50),
    mobile VARCHAR(50),
    date_of_birth DATE,
    gender ENUM('Male', 'Female', 'Other'),
    department_id INT,
    position VARCHAR(100),
    employment_type ENUM('Full-Time', 'Part-Time', 'Contract', 'Temporary') DEFAULT 'Full-Time',
    hire_date DATE,
    termination_date DATE,
    salary DECIMAL(15, 2),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(50),
    photo_path VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    INDEX idx_employee_id (employee_id),
    INDEX idx_name (last_name, first_name),
    INDEX idx_department (department_id),
    INDEX idx_is_active (is_active),
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL
);

-- Insert sample employees
INSERT INTO employees (
    employee_id, first_name, last_name, email, phone, date_of_birth, gender,
    department_id, position, employment_type, hire_date, salary, city
) VALUES
('EMP001', 'John', 'Smith', 'john.smith@vbos.gov.vu', '+678-555-0101', '1985-03-15', 'Male', 3, 'IT Manager', 'Full-Time', '2020-01-15', 75000.00, 'Port Vila'),
('EMP002', 'Sarah', 'Johnson', 'sarah.johnson@vbos.gov.vu', '+678-555-0102', '1990-07-22', 'Female', 4, 'HR Manager', 'Full-Time', '2019-05-20', 70000.00, 'Port Vila'),
('EMP003', 'Michael', 'Brown', 'michael.brown@vbos.gov.vu', '+678-555-0103', '1982-11-08', 'Male', 2, 'Finance Director', 'Full-Time', '2018-03-10', 95000.00, 'Port Vila'),
('EMP004', 'Emily', 'Davis', 'emily.davis@vbos.gov.vu', '+678-555-0104', '1988-05-30', 'Female', 1, 'Administrative Officer', 'Full-Time', '2021-08-01', 55000.00, 'Port Vila'),
('EMP005', 'David', 'Wilson', 'david.wilson@vbos.gov.vu', '+678-555-0105', '1992-09-14', 'Male', 1, 'Admin Assistant', 'Full-Time', '2022-02-15', 45000.00, 'Port Vila'),
('EMP006', 'Lisa', 'Anderson', 'lisa.anderson@vbos.gov.vu', '+678-555-0106', '1987-12-03', 'Female', 6, 'Procurement Officer', 'Full-Time', '2020-06-10', 62000.00, 'Port Vila'),
('EMP007', 'James', 'Taylor', 'james.taylor@vbos.gov.vu', '+678-555-0107', '1984-04-25', 'Male', 5, 'Operations Manager', 'Full-Time', '2019-11-05', 78000.00, 'Port Vila'),
('EMP008', 'Maria', 'Martinez', 'maria.martinez@vbos.gov.vu', '+678-555-0108', '1991-08-17', 'Female', 3, 'Systems Analyst', 'Full-Time', '2021-03-22', 65000.00, 'Port Vila');

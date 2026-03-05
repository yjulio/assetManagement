-- Create company_info table
CREATE TABLE IF NOT EXISTS company_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    legal_name VARCHAR(255),
    abbreviation VARCHAR(50),
    description TEXT,
    logo_path VARCHAR(255),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'Vanuatu',
    phone VARCHAR(50),
    fax VARCHAR(50),
    email VARCHAR(255),
    website VARCHAR(255),
    tax_id VARCHAR(100),
    registration_number VARCHAR(100),
    fiscal_year_start DATE,
    currency VARCHAR(10) DEFAULT 'VUV',
    timezone VARCHAR(50) DEFAULT 'Pacific/Efate',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by VARCHAR(100)
);

-- Insert default company info for Department of Local Authorities
INSERT INTO company_info (
    name, 
    legal_name, 
    abbreviation, 
    description,
    address,
    city,
    country,
    phone,
    email,
    website,
    currency,
    timezone
) VALUES (
    'Department of Local Authorities',
    'Vanuatu National Statistics Office',
    'VBOS',
    'The Department of Local Authorities is responsible for managing and overseeing local government operations, providing support and coordination to municipalities and district councils.',
    'PMB 9019',
    'Port Vila',
    'Vanuatu',
    '+678 23450',
    'statistics@vbos.gov.vu',
    'https://vnso.gov.vu',
    'VUV',
    'Pacific/Efate'
);

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

-- Insert default company info for Vanuatu Bureau Of Statistics
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
    'Vanuatu Bureau Of Statistics',
    'Vanuatu National Statistics Office',
    'VBOS',
    'The Vanuatu Bureau of Statistics is the principal statistical agency of the Government of Vanuatu, responsible for collecting, analyzing, and disseminating official statistics.',
    'PMB 9019',
    'Port Vila',
    'Vanuatu',
    '+678 23450',
    'statistics@vbos.gov.vu',
    'https://vnso.gov.vu',
    'VUV',
    'Pacific/Efate'
);

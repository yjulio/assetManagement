-- Asset Purchase Order (APO) System Table
-- This table stores all APO records with file attachments

CREATE TABLE IF NOT EXISTS apo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    apo_number VARCHAR(100) UNIQUE NOT NULL,
    supplier VARCHAR(255) NOT NULL,
    department VARCHAR(255),
    apo_date DATE NOT NULL,
    delivery_date DATE,
    amount DECIMAL(12,2) NOT NULL,
    status VARCHAR(50) DEFAULT 'Pending',
    description TEXT,
    notes TEXT,
    uploaded_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier) REFERENCES suppliers(name) ON DELETE RESTRICT
);

-- APO Files Table - stores file attachments for each APO
CREATE TABLE IF NOT EXISTS apo_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    apo_id INT NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    saved_filename VARCHAR(255) NOT NULL,
    file_size BIGINT,
    file_type VARCHAR(100),
    uploaded_by VARCHAR(255),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (apo_id) REFERENCES apo(id) ON DELETE CASCADE
);

-- APO Items Table - stores line items for each APO
CREATE TABLE IF NOT EXISTS apo_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    apo_id INT NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    description TEXT,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (apo_id) REFERENCES apo(id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX idx_apo_number ON apo(apo_number);
CREATE INDEX idx_apo_status ON apo(status);
CREATE INDEX idx_apo_date ON apo(apo_date);
CREATE INDEX idx_apo_supplier ON apo(supplier);

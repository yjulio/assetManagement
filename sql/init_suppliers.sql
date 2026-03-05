-- Database initialization script for Asset Management System
-- Adds default suppliers to prevent foreign key constraint errors

USE db_asset;

-- Insert default suppliers
INSERT IGNORE INTO suppliers (name, contact, email) VALUES 
('Unknown', 'N/A', 'N/A'),
('Default', 'N/A', 'N/A'),
('Office Supplies Co', '+678-555-0101', 'sales@officesupplies.vu'),
('Tech Solutions Vanuatu', '+678-555-0202', 'info@techsolutions.vu'),
('Furniture Warehouse', '+678-555-0303', 'contact@furniturewarehouse.vu'),
('Computer Store VU', '+678-555-0404', 'support@computerstore.vu'),
('General Equipment Ltd', '+678-555-0505', 'orders@generalequipment.vu');

-- Verify suppliers were added
SELECT COUNT(*) as total_suppliers FROM suppliers;
SELECT name, contact FROM suppliers ORDER BY name;

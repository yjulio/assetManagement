-- Migration to add new asset fields
-- Date: February 8, 2026

USE db_asset;

-- Add Responsible Officer field
ALTER TABLE inventory ADD COLUMN IF NOT EXISTS responsible_officer VARCHAR(255) DEFAULT NULL AFTER supplier;

-- Add Province Name field
ALTER TABLE inventory ADD COLUMN IF NOT EXISTS province_name VARCHAR(100) DEFAULT NULL AFTER responsible_officer;

-- Add Island field
ALTER TABLE inventory ADD COLUMN IF NOT EXISTS island VARCHAR(100) DEFAULT NULL AFTER province_name;

-- Add Unit/Section field
ALTER TABLE inventory ADD COLUMN IF NOT EXISTS unit_section VARCHAR(255) DEFAULT NULL AFTER island;

-- Add Asset Category field (different from existing 'category')
ALTER TABLE inventory ADD COLUMN IF NOT EXISTS asset_category VARCHAR(255) DEFAULT NULL AFTER unit_section;

-- Add LPO Number field
ALTER TABLE inventory ADD COLUMN IF NOT EXISTS lpo_number VARCHAR(100) DEFAULT NULL AFTER asset_category;

-- Add Asset Condition field with specific values
ALTER TABLE inventory ADD COLUMN IF NOT EXISTS asset_condition ENUM('Excellent', 'Good', 'Fair', 'Poor', 'Broken') DEFAULT 'Good' AFTER lpo_number;

-- Add Asset Tag field
ALTER TABLE inventory ADD COLUMN IF NOT EXISTS asset_tag VARCHAR(100) DEFAULT NULL AFTER asset_condition;

-- Add image fields for storing pictures
ALTER TABLE inventory ADD COLUMN IF NOT EXISTS image_1 VARCHAR(500) DEFAULT NULL AFTER asset_tag;
ALTER TABLE inventory ADD COLUMN IF NOT EXISTS image_2 VARCHAR(500) DEFAULT NULL AFTER image_1;
ALTER TABLE inventory ADD COLUMN IF NOT EXISTS image_3 VARCHAR(500) DEFAULT NULL AFTER image_2;
ALTER TABLE inventory ADD COLUMN IF NOT EXISTS image_4 VARCHAR(500) DEFAULT NULL AFTER image_3;
ALTER TABLE inventory ADD COLUMN IF NOT EXISTS image_5 VARCHAR(500) DEFAULT NULL AFTER image_4;

-- Add index on asset_tag for quick lookups
CREATE INDEX IF NOT EXISTS idx_asset_tag ON inventory(asset_tag);

-- Add index on lpo_number for quick lookups
CREATE INDEX IF NOT EXISTS idx_lpo_number ON inventory(lpo_number);

-- Add index on responsible_officer for filtering
CREATE INDEX IF NOT EXISTS idx_responsible_officer ON inventory(responsible_officer);

-- Add index on asset_condition for filtering
CREATE INDEX IF NOT EXISTS idx_asset_condition ON inventory(asset_condition);

-- Display the updated table structure
DESCRIBE inventory;

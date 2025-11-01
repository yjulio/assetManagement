-- Migration script to update asset_transactions table
-- This updates existing tables to use asset_name instead of item_name
-- and expands the action enum to include all transaction types

USE db_asset;

-- First, check if item_name column exists and rename it to asset_name
SET @column_exists = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = 'db_asset' 
    AND TABLE_NAME = 'asset_transactions' 
    AND COLUMN_NAME = 'item_name'
);

SET @sql = IF(@column_exists > 0,
    'ALTER TABLE asset_transactions CHANGE COLUMN item_name asset_name VARCHAR(255) NOT NULL',
    'SELECT "Column already renamed or does not exist" AS status'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Drop existing enum and recreate with all actions
ALTER TABLE asset_transactions MODIFY COLUMN action VARCHAR(50) NOT NULL;

-- Update any existing records to use new action values (if any need updating)
-- No data changes needed, just schema update

-- Add user_id column if it doesn't exist
SET @user_id_exists = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = 'db_asset' 
    AND TABLE_NAME = 'asset_transactions' 
    AND COLUMN_NAME = 'user_id'
);

SET @sql2 = IF(@user_id_exists = 0,
    'ALTER TABLE asset_transactions ADD COLUMN user_id VARCHAR(255) AFTER username',
    'SELECT "user_id column already exists" AS status'
);

PREPARE stmt2 FROM @sql2;
EXECUTE stmt2;
DEALLOCATE PREPARE stmt2;

-- Note: The enum constraint is removed above. If you want to keep it as enum:
-- ALTER TABLE asset_transactions MODIFY COLUMN action ENUM('checkout','checkin','maintenance','dispose','move','reserve','assign','lease','contract') NOT NULL;


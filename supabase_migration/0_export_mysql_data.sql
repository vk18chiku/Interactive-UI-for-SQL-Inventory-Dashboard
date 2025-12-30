-- ========================================
-- MYSQL DATA EXPORT SCRIPT
-- Run this in your MySQL database to export your actual data
-- ========================================
-- Instructions:
-- 1. Connect to your MySQL database
-- 2. Run these SELECT statements
-- 3. Export results as CSV
-- 4. Use the CSV to import into Supabase
-- ========================================

-- Export Suppliers
SELECT supplier_id, supplier_name, contact_name, email, phone, address
FROM suppliers
ORDER BY supplier_id;

-- Export Products
SELECT product_id, product_name, category, price, stock_quantity, reorder_level, supplier_id
FROM products_
ORDER BY product_id;

-- Export Shipments
SELECT shipment_id, product_id, supplier_id, quantity_received, shipment_date
FROM shipments
ORDER BY shipment_id;

-- Export Stock Entries
SELECT entry_id, product_id, change_quantity, change_type, entry_date
FROM stock_entries
ORDER BY entry_id;

-- Export Reorders
SELECT reorder_id, product_id, reorder_quantity, reorder_date, status
FROM reorders
ORDER BY reorder_id;

-- ========================================
-- OR USE MYSQLDUMP (Recommended)
-- ========================================
-- Run this command in your terminal:
-- mysqldump -h localhost -u root -p --port=3307 dummy_project suppliers products_ shipments stock_entries reorders > mysql_data_export.sql
--
-- Then manually convert MySQL syntax to PostgreSQL:
-- 1. Replace backticks (`) with nothing
-- 2. Replace AUTO_INCREMENT with SERIAL
-- 3. Replace ENGINE=InnoDB with nothing
-- 4. Replace `` quotes with "" or nothing
-- 5. Adjust data types (DATETIME -> TIMESTAMP, etc.)

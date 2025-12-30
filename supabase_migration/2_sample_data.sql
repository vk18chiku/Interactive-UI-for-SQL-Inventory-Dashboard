-- ========================================
-- SUPABASE DATA MIGRATION SCRIPT
-- Sample Data Insertion
-- ========================================
-- NOTE: Replace this sample data with your actual MySQL data export
-- You can export from MySQL using: mysqldump or SELECT INTO OUTFILE
-- ========================================

-- ========================================
-- 1. INSERT SAMPLE SUPPLIERS
-- ========================================
-- Delete this section if you have actual data to import

INSERT INTO suppliers (supplier_id, supplier_name, contact_name, email, phone, address) VALUES
(1, 'Tech Suppliers Inc', 'John Doe', 'john@techsuppliers.com', '+1-555-0101', '123 Tech Street, Silicon Valley, CA'),
(2, 'Office Supplies Co', 'Jane Smith', 'jane@officesupplies.com', '+1-555-0102', '456 Office Blvd, New York, NY'),
(3, 'Electronics Warehouse', 'Bob Johnson', 'bob@elecwarehouse.com', '+1-555-0103', '789 Electronic Ave, Austin, TX'),
(4, 'Furniture World', 'Alice Brown', 'alice@furnitureworld.com', '+1-555-0104', '321 Furniture Rd, Chicago, IL'),
(5, 'Smart Gadgets Ltd', 'Charlie Wilson', 'charlie@smartgadgets.com', '+1-555-0105', '654 Gadget Lane, Seattle, WA');

-- Reset supplier sequence
SELECT setval('suppliers_supplier_id_seq', (SELECT MAX(supplier_id) FROM suppliers));

-- ========================================
-- 2. INSERT SAMPLE PRODUCTS
-- ========================================

INSERT INTO products_ (product_id, product_name, category, price, stock_quantity, reorder_level, supplier_id) VALUES
(1, 'Laptop Computer', 'Electronics', 999.99, 50, 10, 1),
(2, 'Office Chair', 'Furniture', 199.99, 100, 20, 4),
(3, 'Wireless Mouse', 'Electronics', 29.99, 200, 50, 3),
(4, 'Desk Lamp', 'Office Supplies', 49.99, 75, 15, 2),
(5, 'Smart Watch', 'Electronics', 299.99, 30, 10, 5),
(6, 'Standing Desk', 'Furniture', 599.99, 25, 5, 4),
(7, 'USB-C Cable', 'Electronics', 19.99, 150, 30, 1),
(8, 'Notebook Set', 'Office Supplies', 14.99, 300, 50, 2),
(9, 'Bluetooth Speaker', 'Electronics', 79.99, 60, 15, 3),
(10, 'Ergonomic Keyboard', 'Electronics', 89.99, 80, 20, 1);

-- Reset products sequence
SELECT setval('products__product_id_seq', (SELECT MAX(product_id) FROM products_));

-- ========================================
-- 3. INSERT SAMPLE SHIPMENTS
-- ========================================

INSERT INTO shipments (shipment_id, product_id, supplier_id, quantity_received, shipment_date) VALUES
(1, 1, 1, 50, CURRENT_DATE - INTERVAL '30 days'),
(2, 2, 4, 100, CURRENT_DATE - INTERVAL '25 days'),
(3, 3, 3, 200, CURRENT_DATE - INTERVAL '20 days'),
(4, 4, 2, 75, CURRENT_DATE - INTERVAL '15 days'),
(5, 5, 5, 30, CURRENT_DATE - INTERVAL '10 days');

-- Reset shipments sequence
SELECT setval('shipments_shipment_id_seq', (SELECT MAX(shipment_id) FROM shipments));

-- ========================================
-- 4. INSERT SAMPLE STOCK ENTRIES
-- ========================================

INSERT INTO stock_entries (entry_id, product_id, change_quantity, change_type, entry_date, notes) VALUES
(1, 1, 50, 'Restock', CURRENT_DATE - INTERVAL '30 days', 'Initial stock'),
(2, 1, -10, 'Sale', CURRENT_DATE - INTERVAL '25 days', 'Bulk order'),
(3, 2, 100, 'Restock', CURRENT_DATE - INTERVAL '25 days', 'Initial stock'),
(4, 2, -20, 'Sale', CURRENT_DATE - INTERVAL '20 days', 'Office renovation'),
(5, 3, 200, 'Restock', CURRENT_DATE - INTERVAL '20 days', 'Initial stock'),
(6, 3, -30, 'Sale', CURRENT_DATE - INTERVAL '15 days', 'Regular sales'),
(7, 4, 75, 'Restock', CURRENT_DATE - INTERVAL '15 days', 'Initial stock'),
(8, 5, 30, 'Restock', CURRENT_DATE - INTERVAL '10 days', 'Initial stock'),
(9, 5, -5, 'Sale', CURRENT_DATE - INTERVAL '5 days', 'Individual sales');

-- Reset stock_entries sequence
SELECT setval('stock_entries_entry_id_seq', (SELECT MAX(entry_id) FROM stock_entries));

-- ========================================
-- 5. INSERT SAMPLE REORDERS
-- ========================================

INSERT INTO reorders (reorder_id, product_id, reorder_quantity, reorder_date, status) VALUES
(1, 1, 20, CURRENT_DATE - INTERVAL '5 days', 'Ordered'),
(2, 3, 100, CURRENT_DATE - INTERVAL '3 days', 'Pending');

-- Reset reorders sequence
SELECT setval('reorders_reorder_id_seq', (SELECT MAX(reorder_id) FROM reorders));

-- ========================================
-- DATA MIGRATION COMPLETE
-- ========================================

-- Verify data
SELECT 'Suppliers: ' || COUNT(*) FROM suppliers
UNION ALL
SELECT 'Products: ' || COUNT(*) FROM products_
UNION ALL
SELECT 'Shipments: ' || COUNT(*) FROM shipments
UNION ALL
SELECT 'Stock Entries: ' || COUNT(*) FROM stock_entries
UNION ALL
SELECT 'Reorders: ' || COUNT(*) FROM reorders;

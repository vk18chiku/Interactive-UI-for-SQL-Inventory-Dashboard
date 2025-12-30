-- ========================================
-- SUPABASE MIGRATION SCRIPT
-- Inventory Management System
-- PostgreSQL (Supabase) Schema
-- ========================================

-- Enable UUID extension (optional, but useful)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ========================================
-- 1. CREATE TABLES
-- ========================================

-- Suppliers Table
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id SERIAL PRIMARY KEY,
    supplier_name VARCHAR(255) NOT NULL,
    contact_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products Table
CREATE TABLE IF NOT EXISTS products_ (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    price NUMERIC(10, 2) NOT NULL,
    stock_quantity INTEGER NOT NULL DEFAULT 0,
    reorder_level INTEGER NOT NULL DEFAULT 0,
    supplier_id INTEGER REFERENCES suppliers(supplier_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Shipments Table
CREATE TABLE IF NOT EXISTS shipments (
    shipment_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products_(product_id),
    supplier_id INTEGER REFERENCES suppliers(supplier_id),
    quantity_received INTEGER NOT NULL,
    shipment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Stock Entries Table
CREATE TABLE IF NOT EXISTS stock_entries (
    entry_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products_(product_id),
    change_quantity INTEGER NOT NULL,
    change_type VARCHAR(50) NOT NULL CHECK (change_type IN ('Sale', 'Restock', 'Adjustment')),
    entry_date DATE NOT NULL DEFAULT CURRENT_DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reorders Table
CREATE TABLE IF NOT EXISTS reorders (
    reorder_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products_(product_id),
    reorder_quantity INTEGER NOT NULL,
    reorder_date DATE NOT NULL DEFAULT CURRENT_DATE,
    status VARCHAR(50) NOT NULL DEFAULT 'Pending' CHECK (status IN ('Pending', 'Ordered', 'Received', 'Cancelled')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- 2. CREATE INDEXES FOR PERFORMANCE
-- ========================================

CREATE INDEX idx_products_supplier ON products_(supplier_id);
CREATE INDEX idx_products_category ON products_(category);
CREATE INDEX idx_stock_entries_product ON stock_entries(product_id);
CREATE INDEX idx_stock_entries_date ON stock_entries(entry_date);
CREATE INDEX idx_shipments_product ON shipments(product_id);
CREATE INDEX idx_reorders_product ON reorders(product_id);
CREATE INDEX idx_reorders_status ON reorders(status);

-- ========================================
-- 3. CREATE VIEW: Product Inventory History
-- ========================================

CREATE OR REPLACE VIEW product_inventory_history AS
SELECT 
    pih.product_id,
    pih.record_type,
    pih.record_date,
    pih.quantity,
    pih.change_type,
    pr.supplier_id
FROM (
    SELECT 
        product_id,
        'Shipment' AS record_type,
        shipment_date AS record_date,
        quantity_received AS quantity,
        NULL AS change_type
    FROM shipments
    
    UNION ALL
    
    SELECT 
        product_id,
        'Stock Entry' AS record_type,
        entry_date AS record_date,
        change_quantity AS quantity,
        change_type
    FROM stock_entries
) pih
JOIN products_ pr ON pr.product_id = pih.product_id
ORDER BY pih.record_date DESC;

-- ========================================
-- 4. CREATE FUNCTIONS (Stored Procedures)
-- ========================================

-- Function to add new product
CREATE OR REPLACE FUNCTION add_new_product_manual_id(
    p_name VARCHAR,
    p_category VARCHAR,
    p_price NUMERIC,
    p_stock INTEGER,
    p_reorder INTEGER,
    p_supplier INTEGER
) RETURNS INTEGER AS $$
DECLARE
    new_prod_id INTEGER;
    new_shipment_id INTEGER;
    new_entry_id INTEGER;
BEGIN
    -- Generate new product ID
    SELECT COALESCE(MAX(product_id), 0) + 1 INTO new_prod_id FROM products_;
    
    -- Insert into products table
    INSERT INTO products_(product_id, product_name, category, price, stock_quantity, reorder_level, supplier_id)
    VALUES (new_prod_id, p_name, p_category, p_price, p_stock, p_reorder, p_supplier);
    
    -- Generate new shipment ID
    SELECT COALESCE(MAX(shipment_id), 0) + 1 INTO new_shipment_id FROM shipments;
    
    -- Insert into shipments table
    INSERT INTO shipments (shipment_id, product_id, supplier_id, quantity_received, shipment_date)
    VALUES (new_shipment_id, new_prod_id, p_supplier, p_stock, CURRENT_DATE);
    
    -- Generate new entry ID
    SELECT COALESCE(MAX(entry_id), 0) + 1 INTO new_entry_id FROM stock_entries;
    
    -- Insert into stock_entries table
    INSERT INTO stock_entries(entry_id, product_id, change_quantity, change_type, entry_date)
    VALUES (new_entry_id, new_prod_id, p_stock, 'Restock', CURRENT_DATE);
    
    RETURN new_prod_id;
END;
$$ LANGUAGE plpgsql;

-- Function to mark reorder as received
CREATE OR REPLACE FUNCTION mark_reorder_as_received(
    in_reorder_id INTEGER
) RETURNS VOID AS $$
DECLARE
    prod_id INTEGER;
    qty INTEGER;
    sup_id INTEGER;
    new_shipment_id INTEGER;
    new_entry_id INTEGER;
BEGIN
    -- Get product_id and quantity from reorders
    SELECT product_id, reorder_quantity
    INTO prod_id, qty
    FROM reorders
    WHERE reorder_id = in_reorder_id;
    
    -- Get supplier_id from products
    SELECT supplier_id
    INTO sup_id
    FROM products_
    WHERE product_id = prod_id;
    
    -- Update reorder status to 'Received'
    UPDATE reorders
    SET status = 'Received', updated_at = CURRENT_TIMESTAMP
    WHERE reorder_id = in_reorder_id;
    
    -- Update stock quantity in products table
    UPDATE products_
    SET stock_quantity = stock_quantity + qty, updated_at = CURRENT_TIMESTAMP
    WHERE product_id = prod_id;
    
    -- Generate new shipment ID
    SELECT COALESCE(MAX(shipment_id), 0) + 1 INTO new_shipment_id FROM shipments;
    
    -- Insert record into shipments table
    INSERT INTO shipments(shipment_id, product_id, supplier_id, quantity_received, shipment_date)
    VALUES (new_shipment_id, prod_id, sup_id, qty, CURRENT_DATE);
    
    -- Generate new entry ID
    SELECT COALESCE(MAX(entry_id), 0) + 1 INTO new_entry_id FROM stock_entries;
    
    -- Insert record into stock_entries for Restock
    INSERT INTO stock_entries(entry_id, product_id, change_quantity, change_type, entry_date)
    VALUES (new_entry_id, prod_id, qty, 'Restock', CURRENT_DATE);
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- 5. CREATE TRIGGERS FOR AUTO-UPDATE
-- ========================================

-- Trigger to update products_.updated_at on modification
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products_
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reorders_updated_at
    BEFORE UPDATE ON reorders
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- MIGRATION COMPLETE
-- ========================================
-- Next: Run the data migration script (2_data_migration.sql)

# 🚀 SIMPLE SUPABASE SETUP GUIDE

## ✅ What You Need
- ✅ Supabase URL: `https://tgidccomqsaxrcqqarvz.supabase.co`
- ✅ Service Role Key: Already configured in code

---

## 📝 STEP 1: Create Tables in Supabase

1. Go to: https://supabase.com/dashboard/project/tgidccomqsaxrcqqarvz
2. Click **SQL Editor** on left sidebar
3. Click **New Query**
4. Copy and paste this SQL script:

```sql
-- Create Tables
CREATE TABLE suppliers (
    supplier_id SERIAL PRIMARY KEY,
    supplier_name VARCHAR(255),
    contact_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT
);

CREATE TABLE products_ (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(255),
    category VARCHAR(100),
    price NUMERIC(10, 2),
    stock_quantity INTEGER DEFAULT 0,
    reorder_level INTEGER DEFAULT 0,
    supplier_id INTEGER REFERENCES suppliers(supplier_id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE shipments (
    shipment_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products_(product_id),
    supplier_id INTEGER REFERENCES suppliers(supplier_id),
    quantity_received INTEGER,
    shipment_date DATE DEFAULT CURRENT_DATE
);

CREATE TABLE stock_entries (
    entry_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products_(product_id),
    change_quantity INTEGER,
    change_type VARCHAR(50),
    entry_date DATE DEFAULT CURRENT_DATE,
    notes TEXT
);

CREATE TABLE reorders (
    reorder_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products_(product_id),
    reorder_quantity INTEGER,
    reorder_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(50) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create View
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
JOIN products_ pr ON pr.product_id = pih.product_id;
```

5. Click **RUN** (or press Ctrl+Enter)
6. Wait for "Success" message

---

## 📊 STEP 2: Import Your Data

### Option A: Manual Entry (For Testing)
1. Go to **Table Editor**
2. Click on each table (suppliers, products_, etc.)
3. Click **Insert row** → **Insert**
4. Add sample data

### Option B: Import from MySQL (For Production)

#### Export from MySQL:
```powershell
# In PowerShell, navigate to project folder
cd "C:\Users\hp\Downloads\Day 5-20250408T181523Z-001\Projects\Interactive UI for SQL Inventaroy Dashboard"

# Export tables as CSV
mysql -h localhost -P 3307 -u root -pUttam1234@ dummy_project -e "SELECT * FROM suppliers INTO OUTFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/suppliers.csv' FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\n';"
```

#### Import to Supabase:
1. In Supabase **Table Editor**
2. Select table → Click **Import data from CSV**
3. Upload your exported CSV file
4. Match columns
5. Click **Import**

---

## 🔧 STEP 3: Update Streamlit Cloud Secrets

1. Go to Streamlit Cloud app settings
2. Click **Manage app** → **Secrets**
3. Replace everything with:

```toml
SUPABASE_URL = "https://tgidccomqsaxrcqqarvz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRnaWRjY29tcXNheHJjcXFhcnZ6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NzEwOTM4NiwiZXhwIjoyMDgyNjg1Mzg2fQ.TgK3wKlKs17wlY_pPPfwcssfmklPLEthbEmNACnH0xI"
```

4. Click **Save**
5. App will auto-redeploy

---

## ✅ STEP 4: Test Locally (Optional)

```powershell
# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run app.py
```

---

## 🎉 Done!

Your app will now:
- ✅ Connect to Supabase using REST API
- ✅ No password needed
- ✅ No connection timeout errors
- ✅ Works perfectly on Streamlit Cloud

---

## 🔍 Verify in Supabase

1. Go to **Table Editor**
2. Check each table has data
3. Tables should be visible: suppliers, products_, shipments, stock_entries, reorders

---

## ⚠️ Important Notes

- ✅ Using **Service Role Key** (full access)
- ✅ No database password needed
- ✅ Works through REST API
- ✅ No connection pooling issues
- ✅ Better for Streamlit Cloud deployment

---

## 🆘 Troubleshooting

### "relation does not exist"
- Run the SQL script in Step 1 again

### "No data showing"
- Import data in Step 2

### "Connection failed"
- Check URL and key in secrets

---

## 📞 Quick Check

After setup, verify:
1. ✅ Tables created in Supabase
2. ✅ Data imported
3. ✅ Secrets updated in Streamlit Cloud
4. ✅ App deployed and working

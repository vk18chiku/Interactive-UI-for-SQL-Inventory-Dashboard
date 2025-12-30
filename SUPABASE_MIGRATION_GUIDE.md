# 🚀 SUPABASE MIGRATION GUIDE
## Complete Step-by-Step Instructions

---

## 📋 Overview
This guide will help you migrate your MySQL database to Supabase (PostgreSQL) without losing any data.

---

## ⚠️ IMPORTANT: Get Your Database Password

Before starting, you need to get your Supabase database password:

1. Go to your Supabase Dashboard: https://supabase.com/dashboard/project/tgidccomqsaxrcqqarvz
2. Click on **Settings** (⚙️ icon on left sidebar)
3. Click **Database**
4. Find **Connection String** or **Database Password**
5. Copy your password and save it securely

---

## 📝 STEP 1: Run SQL Scripts in Supabase

### 1.1 Open Supabase SQL Editor
1. Go to https://supabase.com/dashboard/project/tgidccomqsaxrcqqarvz
2. Click **SQL Editor** in the left sidebar
3. Click **New Query**

### 1.2 Create Schema
1. Open the file: `supabase_migration/1_schema_creation.sql`
2. Copy ALL the contents
3. Paste into Supabase SQL Editor
4. Click **RUN** (or press Ctrl+Enter)
5. Wait for "Success" message

### 1.3 Export Your MySQL Data (CRITICAL!)

#### Option A: Using MySQL Workbench (Easiest)
1. Open MySQL Workbench
2. Connect to your database (localhost:3307, dummy_project)
3. For each table, right-click → **Table Data Export Wizard**
4. Export: `suppliers`, `products_`, `shipments`, `stock_entries`, `reorders`
5. Save as CSV files

#### Option B: Using Command Line
```bash
# Run these commands in PowerShell
cd "C:\Users\hp\Downloads\Day 5-20250408T181523Z-001\Projects\Interactive UI for SQL Inventaroy Dashboard"

# Export each table
mysql -h localhost -P 3307 -u root -p dummy_project -e "SELECT * FROM suppliers" > suppliers.csv
mysql -h localhost -P 3307 -u root -p dummy_project -e "SELECT * FROM products_" > products.csv
mysql -h localhost -P 3307 -u root -p dummy_project -e "SELECT * FROM shipments" > shipments.csv
mysql -h localhost -P 3307 -u root -p dummy_project -e "SELECT * FROM stock_entries" > stock_entries.csv
mysql -h localhost -P 3307 -u root -p dummy_project -e "SELECT * FROM reorders" > reorders.csv
```

### 1.4 Import Your Data to Supabase

#### Option A: Use Supabase Table Editor (Recommended)
1. In Supabase Dashboard → **Table Editor**
2. Select each table (suppliers, products_, etc.)
3. Click **Insert** → **Import data from CSV**
4. Upload your CSV file
5. Map columns correctly
6. Click **Import**

#### Option B: Use SQL Editor
If you have SQL INSERT statements:
1. Open Supabase **SQL Editor**
2. Paste your INSERT statements
3. Click **RUN**

---

## 🔧 STEP 2: Update Local Secrets

Your `.streamlit/secrets.toml` file has been updated, but you need to add your password:

1. Open: `.streamlit/secrets.toml`
2. Find this line:
   ```toml
   SUPABASE_PASSWORD = "your_database_password_here"
   ```
3. Replace `your_database_password_here` with your actual Supabase database password
4. Save the file

---

## 🧪 STEP 3: Test Locally

1. Open PowerShell in your project folder
2. Activate virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
3. Install new dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. Run Streamlit:
   ```powershell
   streamlit run app.py
   ```
5. Test all features:
   - ✅ Basic Information page loads
   - ✅ All metrics show correct values
   - ✅ Add new product works
   - ✅ Product history works
   - ✅ Place reorder works
   - ✅ Receive reorder works

---

## ☁️ STEP 4: Deploy to Streamlit Cloud

### 4.1 Commit and Push Changes
```powershell
git add .
git commit -m "Migrate to Supabase PostgreSQL database"
git push origin main
```

### 4.2 Update Streamlit Cloud Secrets
1. Go to Streamlit Cloud: https://share.streamlit.io/
2. Click on your app
3. Click **Manage app** (bottom right)
4. Go to **Secrets** tab
5. Delete all old secrets
6. Add new secrets:

```toml
SUPABASE_HOST = "aws-0-ap-south-1.pooler.supabase.com"
SUPABASE_DB = "postgres"
SUPABASE_USER = "postgres.tgidccomqsaxrcqqarvz"
SUPABASE_PASSWORD = "YOUR_ACTUAL_PASSWORD_HERE"
SUPABASE_PORT = 5432

SUPABASE_URL = "https://tgidccomqsaxrcqqarvz.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRnaWRjY29tcXNheHJjcXFhcnZ6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjcxMDkzODYsImV4cCI6MjA4MjY4NTM4Nn0.TjrA8Ejp6VY6usqH9QALX9hkDxO36Ac03qQ3NkMiXr4"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRnaWRjY29tcXNheHJjcXFhcnZ6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NzEwOTM4NiwiZXhwIjoyMDgyNjg1Mzg2fQ.TgK3wKlKs17wlY_pPPfwcssfmklPLEthbEmNACnH0xI"
```

7. **Replace `YOUR_ACTUAL_PASSWORD_HERE`** with your real password
8. Click **Save**
9. App will auto-redeploy

---

## ✅ STEP 5: Verify Deployment

1. Wait for deployment to complete (2-3 minutes)
2. Open your Streamlit Cloud app
3. Check that:
   - ✅ No connection errors
   - ✅ Data displays correctly
   - ✅ All operations work
   - ✅ No data is missing

---

## 🔍 Troubleshooting

### Error: "connection failed"
- Check if you entered the correct password in secrets
- Verify Supabase project is active
- Check if all secrets are correctly copied

### Error: "relation does not exist"
- Make sure you ran `1_schema_creation.sql` completely
- Check if tables were created in Supabase Table Editor

### Error: "no data showing"
- Verify you imported data correctly from MySQL
- Check Supabase Table Editor to see if data exists
- Run sample data script if needed: `2_sample_data.sql`

### Data is missing
- Re-export from MySQL carefully
- Import again into Supabase
- Verify row counts match

---

## 📊 Verify Data Migration

Run this in Supabase SQL Editor to check data counts:

```sql
SELECT 'Suppliers' as table_name, COUNT(*) as count FROM suppliers
UNION ALL
SELECT 'Products', COUNT(*) FROM products_
UNION ALL
SELECT 'Shipments', COUNT(*) FROM shipments
UNION ALL
SELECT 'Stock Entries', COUNT(*) FROM stock_entries
UNION ALL
SELECT 'Reorders', COUNT(*) FROM reorders;
```

Compare these numbers with your MySQL database.

---

## 🎉 Migration Complete!

Once everything works:
1. Your app is now running on Supabase
2. No more timeout errors
3. Better performance
4. Free tier with 500MB database
5. Automatic backups

---

## 📞 Need Help?

If you encounter issues:
1. Check Streamlit Cloud logs (Manage app → Logs)
2. Check Supabase Dashboard → Database → Logs
3. Verify all secrets are correct
4. Make sure password doesn't have special characters that need escaping

---

## 🔐 Security Note

- Never commit `.streamlit/secrets.toml` to GitHub (already in .gitignore)
- Keep your Supabase password secure
- Don't share service role key publicly
- Use anon key for client-side applications only

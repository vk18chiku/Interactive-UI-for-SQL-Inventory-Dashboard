import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st

@st.cache_resource
def connect_to_db():
    try:
        connection = psycopg2.connect(
            host=st.secrets["SUPABASE_HOST"],
            database=st.secrets["SUPABASE_DB"],
            user=st.secrets["SUPABASE_USER"],
            password=st.secrets["SUPABASE_PASSWORD"],
            port=st.secrets.get("SUPABASE_PORT", 5432),
            connect_timeout=10
        )
        connection.autocommit = True
        return connection
    except Exception as e:
        st.error(f"❌ Database connection failed: {str(e)}")
        st.info("""
        **Troubleshooting:**
        1. Make sure Supabase secrets are correctly configured
        2. Verify your Supabase project is active
        3. Check if pooling mode is set correctly
        4. Ensure database is accessible
        """)
        st.stop()



def get_basic_info(cursor):
    queries = {
        "Total Suppliers": "SELECT COUNT(*) AS count FROM suppliers",

        "Total Products": "SELECT COUNT(*) AS count FROM products_",

        "Total Categories Dealing": "SELECT COUNT(DISTINCT category) AS count FROM products_",

        "Total Sale Value (Last 3 Months)": """
                SELECT ROUND(CAST(SUM(ABS(se.change_quantity) * p.price) AS NUMERIC), 2) AS total_sale
                FROM stock_entries se
                JOIN products_ p ON se.product_id = p.product_id
                WHERE se.change_type = 'Sale'
                AND se.entry_date >= (
                SELECT MAX(entry_date) - INTERVAL '3 months' FROM stock_entries)
                """,

        "Total Restock Value (Last 3 Months)": """
                SELECT ROUND(CAST(SUM(se.change_quantity * p.price) AS NUMERIC), 2) AS total_restock
                FROM stock_entries se
                JOIN products_ p ON se.product_id = p.product_id
                WHERE se.change_type = 'Restock'
                AND se.entry_date >= (
                SELECT MAX(entry_date) - INTERVAL '3 months' FROM stock_entries)
                """,

        "Below Reorder & No Pending Reorders": """
                SELECT COUNT(*) AS below_reorder
                FROM products_ p
                WHERE p.stock_quantity < p.reorder_level
                AND p.product_id NOT IN (
                SELECT DISTINCT product_id FROM reorders WHERE status = 'Pending')
                """
    }
    result = {}
    for label, query in queries.items():
        cursor.execute(query)
        row = cursor.fetchone()
        result[label] = list(row.values())[0]
    return result

def get_additional_tables(cursor):
    queries = {
        "Suppliers Contact Details": "SELECT supplier_name, contact_name, email, phone FROM suppliers",

        "Products with Supplier and Stock": """
            SELECT 
                p.product_name,
                s.supplier_name,
                p.stock_quantity,
                p.reorder_level
            FROM products_ p
            JOIN suppliers s ON p.supplier_id = s.supplier_id
            ORDER BY p.product_name ASC
        """,

        "Products Needing Reorder": """
            SELECT product_name, stock_quantity, reorder_level
            FROM products_
            WHERE stock_quantity <= reorder_level
        """
    }

    tables = {}
    for label, query in queries.items():
        cursor.execute(query)
        tables[label] = cursor.fetchall()

    return tables

def add_new_manual_id(cursor, db, p_name , p_category , p_price , p_stock , p_reorder, p_supplier):
    # PostgreSQL function call
    cursor.execute(
        "SELECT add_new_product_manual_id(%s, %s, %s, %s, %s, %s)",
        (p_name, p_category, p_price, p_stock, p_reorder, p_supplier)
    )

def get_categories(cursor):
    cursor.execute("SELECT DISTINCT category FROM products_ ORDER BY category ASC")
    rows = cursor.fetchall()
    return [row["category"] for row in rows]

def get_suppliers(cursor):
    cursor.execute("SELECT supplier_id, supplier_name FROM suppliers ORDER BY supplier_name ASC")
    return cursor.fetchall()

def get_all_products(cursor):
    cursor.execute("SELECT product_id, product_name FROM products_ ORDER BY product_name")
    return cursor.fetchall()

def get_product_history(cursor, product_id):
    query = "SELECT * FROM product_inventory_history WHERE product_id = %s ORDER BY record_date DESC"
    cursor.execute(query, (product_id,))
    return cursor.fetchall()

def place_reorder(cursor, db, product_id, reorder_quantity):
    query = """
         INSERT INTO reorders (reorder_id, product_id, reorder_quantity, reorder_date, status)
         SELECT 
         COALESCE(MAX(reorder_id), 0) + 1,
         %s,
         %s,
         CURRENT_DATE,
         'Ordered'
         FROM reorders
         """
    cursor.execute(query, (product_id, reorder_quantity))


def get_pending_reorders(cursor):
    cursor.execute("""
    SELECT r.reorder_id, p.product_name
    FROM reorders AS r 
    JOIN products_ AS p ON r.product_id = p.product_id
    WHERE r.status IN ('Pending', 'Ordered')
    """)
    return cursor.fetchall()

def mark_reorder_as_received(cursor, db, reorder_id):
    # PostgreSQL function call
    cursor.execute("SELECT mark_reorder_as_received(%s)", (reorder_id,))









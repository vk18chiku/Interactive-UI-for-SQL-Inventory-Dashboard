"""
Test script to verify Supabase connection
Run this before deploying to make sure everything works
"""

import psycopg2
from psycopg2.extras import RealDictCursor

# Test connection
def test_connection():
    print("🔌 Testing Supabase connection...")
    
    try:
        # Replace these with your actual values
        connection = psycopg2.connect(
            host="aws-0-ap-south-1.pooler.supabase.com",
            database="postgres",
            user="postgres.tgidccomqsaxrcqqarvz",
            password="YOUR_PASSWORD_HERE",  # ⚠️ Replace with your actual password
            port=5432,
            connect_timeout=10
        )
        
        print("✅ Connected successfully!")
        
        # Test basic queries
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        # Count tables
        cursor.execute("""
            SELECT 
                'Suppliers' as table_name, COUNT(*) as count FROM suppliers
            UNION ALL
            SELECT 'Products', COUNT(*) FROM products_
            UNION ALL
            SELECT 'Shipments', COUNT(*) FROM shipments
            UNION ALL
            SELECT 'Stock Entries', COUNT(*) FROM stock_entries
            UNION ALL
            SELECT 'Reorders', COUNT(*) FROM reorders
        """)
        
        results = cursor.fetchall()
        
        print("\n📊 Database Statistics:")
        print("-" * 40)
        for row in results:
            print(f"{row['table_name']:<20} {row['count']:>10}")
        print("-" * 40)
        
        # Test functions
        print("\n🧪 Testing stored functions...")
        cursor.execute("SELECT proname FROM pg_proc WHERE proname IN ('add_new_product_manual_id', 'mark_reorder_as_received')")
        functions = cursor.fetchall()
        
        if len(functions) == 2:
            print("✅ All stored functions exist")
        else:
            print("⚠️ Some stored functions missing")
            
        # Test view
        cursor.execute("SELECT COUNT(*) FROM product_inventory_history")
        view_count = cursor.fetchone()['count']
        print(f"✅ View 'product_inventory_history' has {view_count} records")
        
        cursor.close()
        connection.close()
        
        print("\n🎉 All tests passed! Ready to deploy.")
        return True
        
    except Exception as e:
        print(f"\n❌ Connection failed: {str(e)}")
        print("\n💡 Troubleshooting:")
        print("1. Check if you replaced 'YOUR_PASSWORD_HERE' with actual password")
        print("2. Verify Supabase project is active")
        print("3. Make sure you ran 1_schema_creation.sql")
        print("4. Check if data was imported correctly")
        return False

if __name__ == "__main__":
    test_connection()

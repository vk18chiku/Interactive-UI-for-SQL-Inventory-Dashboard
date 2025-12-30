import os
from supabase import create_client, Client
from datetime import datetime, timedelta

# Load secrets
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Please set SUPABASE_URL and SUPABASE_KEY environment variables")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 60)
print("DEBUG: Checking Stock Entries")
print("=" * 60)

# Get all stock entries
response = supabase.table("stock_entries").select("*").execute()
print(f"\nTotal stock entries: {len(response.data)}")
print("\nAll entries:")
for entry in response.data:
    print(f"  ID: {entry['entry_id']}, Product: {entry['product_id']}, "
          f"Type: {entry['change_type']}, Qty: {entry['change_quantity']}, Date: {entry['entry_date']}")

# Check restock entries specifically
print("\n" + "=" * 60)
print("DEBUG: Filtering Restock Entries")
print("=" * 60)

response = supabase.table("stock_entries").select("*").eq("change_type", "Restock").execute()
print(f"\nTotal RESTOCK entries: {len(response.data)}")
print("\nRestock entries:")
for entry in response.data:
    print(f"  ID: {entry['entry_id']}, Product: {entry['product_id']}, "
          f"Qty: {entry['change_quantity']}, Date: {entry['entry_date']}")

# Check sale entries
print("\n" + "=" * 60)
print("DEBUG: Filtering Sale Entries")
print("=" * 60)

response = supabase.table("stock_entries").select("*").eq("change_type", "Sale").execute()
print(f"\nTotal SALE entries: {len(response.data)}")
print("\nSale entries:")
for entry in response.data:
    print(f"  ID: {entry['entry_id']}, Product: {entry['product_id']}, "
          f"Qty: {entry['change_quantity']}, Date: {entry['entry_date']}")

# Get products with prices
print("\n" + "=" * 60)
print("DEBUG: Products with Prices")
print("=" * 60)

response = supabase.table("products_").select("product_id, product_name, price").execute()
print(f"\nTotal products: {len(response.data)}")
for prod in response.data:
    print(f"  ID: {prod['product_id']}, Name: {prod['product_name']}, Price: {prod['price']}")

# Calculate totals manually
print("\n" + "=" * 60)
print("DEBUG: Calculate Restock Value (Last 3 Months)")
print("=" * 60)

response = supabase.table("stock_entries").select("*").eq("change_type", "Restock").execute()
restock_entries = response.data

response = supabase.table("products_").select("product_id, price").execute()
products_map = {p["product_id"]: p["price"] for p in response.data}

three_months_ago = (datetime.now() - timedelta(days=90)).date()
print(f"\nThreshold date (3 months ago): {three_months_ago}")

total_restock_value = 0
for entry in restock_entries:
    entry_date = entry.get("entry_date")
    if entry_date:
        if isinstance(entry_date, str):
            entry_date = datetime.fromisoformat(entry_date.replace('Z', '+00:00')).date()
        
        product_id = entry.get("product_id")
        change_qty = abs(entry.get("change_quantity", 0))
        price = products_map.get(product_id, 0)
        
        value = change_qty * price
        total_restock_value += value
        
        print(f"  Entry ID: {entry['entry_id']}, Product: {product_id}, "
              f"Date: {entry_date}, Qty: {change_qty}, Price: {price}, Value: {value}, "
              f"In Range: {entry_date >= three_months_ago}")

print(f"\n✅ Total Restock Value (Last 3 Months): {total_restock_value}")

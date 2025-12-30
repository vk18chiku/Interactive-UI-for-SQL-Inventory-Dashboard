try:
    from supabase import create_client, Client
    from datetime import datetime, timedelta
    
    # Read secrets from .streamlit/secrets.toml
    try:
        import tomli
    except ImportError:
        import tomllib as tomli
    
    with open('.streamlit/secrets.toml', 'rb') as f:
        secrets = tomli.load(f)
    
    # Connect to database
    supabase = create_client(secrets['SUPABASE_URL'], secrets['SUPABASE_KEY'])
except Exception as e:
    print(f"Error loading: {e}")
    exit(1)

print("=" * 60)
print("CHECKING RESTOCK DATA")
print("=" * 60)

# Get all stock entries with Restock type
response = supabase.table("stock_entries").select("entry_id, product_id, change_quantity, change_type, entry_date").eq("change_type", "Restock").execute()

print(f"\nTotal Restock entries in database: {len(response.data)}")

if len(response.data) == 0:
    print("\n❌ NO RESTOCK ENTRIES FOUND IN DATABASE!")
    print("You need to add restock data to your stock_entries table.")
else:
    print("\nRestock entries found:")
    three_months_ago = (datetime.now() - timedelta(days=90)).date()
    print(f"Date threshold (3 months ago): {three_months_ago}")
    print(f"Current date: {datetime.now().date()}\n")
    
    # Get products with prices
    prod_response = supabase.table("products_").select("product_id, product_name, price").execute()
    products_map = {p["product_id"]: {"name": p["product_name"], "price": p["price"]} for p in prod_response.data}
    
    within_range_count = 0
    total_value = 0
    
    for entry in response.data:
        entry_date_str = entry.get("entry_date")
        entry_date = datetime.fromisoformat(entry_date_str.replace('Z', '+00:00')).date() if entry_date_str else None
        
        product_id = entry.get("product_id")
        product_info = products_map.get(product_id, {"name": "Unknown", "price": 0})
        change_qty = abs(entry.get("change_quantity", 0))
        value = change_qty * product_info["price"]
        
        in_range = entry_date >= three_months_ago if entry_date else False
        
        if in_range:
            within_range_count += 1
            total_value += value
        
        status = "✅ IN RANGE" if in_range else "❌ TOO OLD"
        print(f"{status} | Entry ID: {entry['entry_id']} | Product: {product_info['name']} (ID: {product_id}) | "
              f"Date: {entry_date} | Qty: {change_qty} | Price: {product_info['price']} | Value: {value:.2f}")
    
    print("\n" + "=" * 60)
    print(f"Restock entries within last 3 months: {within_range_count}")
    print(f"Total Restock Value (Last 3 Months): ${total_value:.2f}")
    print("=" * 60)

    if within_range_count == 0:
        print("\n⚠️ WARNING: All restock entries are older than 3 months!")
        print("This is why the Total Restock Value shows 0.")
        print("\nSolution: Run the sample data migration script again to get recent dates,")
        print("or add new restock entries through the app.")

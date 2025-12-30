import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def connect_to_db() -> Client:
    try:
        supabase: Client = create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"]
        )
        return supabase
    except Exception as e:
        st.error(f"❌ Database connection failed: {str(e)}")
        st.info("""
        **Troubleshooting:**
        1. Verify Supabase URL and Key in secrets
        2. Check if Supabase project is active
        3. Ensure tables exist in Supabase
        """)
        st.stop()


def get_basic_info(supabase: Client):
    result = {}
    
    try:
        # Total Suppliers
        response = supabase.table("suppliers").select("*", count="exact").execute()
        result["Total Suppliers"] = response.count
        
        # Total Products
        response = supabase.table("products_").select("*", count="exact").execute()
        result["Total Products"] = response.count
        
        # Total Categories
        response = supabase.table("products_").select("category").execute()
        categories = set(row['category'] for row in response.data if row['category'])
        result["Total Categories Dealing"] = len(categories)
        
        # For now, set default values for metrics that need RPC functions
        result["Total Sale Value (Last 3 Months)"] = 0
        result["Total Restock Value (Last 3 Months)"] = 0
        result["Below Reorder & No Pending Reorders"] = 0
        
    except Exception as e:
        st.error(f"Error fetching basic info: {str(e)}")
        # Return default values
        for key in ["Total Suppliers", "Total Products", "Total Categories Dealing", 
                    "Total Sale Value (Last 3 Months)", "Total Restock Value (Last 3 Months)", 
                    "Below Reorder & No Pending Reorders"]:
            if key not in result:
                result[key] = 0
    
    return result

def get_additional_tables(supabase: Client):
    tables = {}
    
    try:
        # Suppliers Contact Details
        response = supabase.table("suppliers").select("supplier_name, contact_name, email, phone").execute()
        tables["Suppliers Contact Details"] = response.data
        
        # Products with Supplier and Stock
        response = supabase.table("products_").select(
            "product_name, stock_quantity, reorder_level, suppliers(supplier_name)"
        ).order("product_name").execute()
        
        # Flatten the nested supplier data
        flattened = []
        for item in response.data:
            flattened.append({
                "product_name": item.get("product_name"),
                "supplier_name": item.get("suppliers", {}).get("supplier_name") if item.get("suppliers") else None,
                "stock_quantity": item.get("stock_quantity"),
                "reorder_level": item.get("reorder_level")
            })
        tables["Products with Supplier and Stock"] = flattened
        
        # Products Needing Reorder
        response = supabase.table("products_").select(
            "product_name, stock_quantity, reorder_level"
        ).filter("stock_quantity", "lte", "reorder_level").execute()
        tables["Products Needing Reorder"] = response.data
        
    except Exception as e:
        st.error(f"Error fetching tables: {str(e)}")
        tables = {
            "Suppliers Contact Details": [],
            "Products with Supplier and Stock": [],
            "Products Needing Reorder": []
        }
    
    return tables

def add_new_manual_id(supabase: Client, db, p_name, p_category, p_price, p_stock, p_reorder, p_supplier):
    try:
        # Get max product_id
        response = supabase.table("products_").select("product_id").order("product_id", desc=True).limit(1).execute()
        new_prod_id = (response.data[0]["product_id"] + 1) if response.data else 1
        
        # Insert new product
        from datetime import date
        supabase.table("products_").insert({
            "product_id": new_prod_id,
            "product_name": p_name,
            "category": p_category,
            "price": float(p_price),
            "stock_quantity": int(p_stock),
            "reorder_level": int(p_reorder),
            "supplier_id": int(p_supplier)
        }).execute()
        
        # Get max shipment_id
        response = supabase.table("shipments").select("shipment_id").order("shipment_id", desc=True).limit(1).execute()
        new_shipment_id = (response.data[0]["shipment_id"] + 1) if response.data else 1
        
        # Insert shipment
        supabase.table("shipments").insert({
            "shipment_id": new_shipment_id,
            "product_id": new_prod_id,
            "supplier_id": int(p_supplier),
            "quantity_received": int(p_stock),
            "shipment_date": date.today().isoformat()
        }).execute()
        
        # Get max entry_id
        response = supabase.table("stock_entries").select("entry_id").order("entry_id", desc=True).limit(1).execute()
        new_entry_id = (response.data[0]["entry_id"] + 1) if response.data else 1
        
        # Insert stock entry
        supabase.table("stock_entries").insert({
            "entry_id": new_entry_id,
            "product_id": new_prod_id,
            "change_quantity": int(p_stock),
            "change_type": "Restock",
            "entry_date": date.today().isoformat()
        }).execute()
        
    except Exception as e:
        raise Exception(f"Failed to add product: {str(e)}")

def get_categories(supabase: Client):
    try:
        response = supabase.table("products_").select("category").execute()
        categories = sorted(set(row['category'] for row in response.data if row['category']))
        return categories
    except Exception as e:
        st.error(f"Error fetching categories: {str(e)}")
        return []

def get_suppliers(supabase: Client):
    try:
        response = supabase.table("suppliers").select("supplier_id, supplier_name").order("supplier_name").execute()
        return response.data
    except Exception as e:
        st.error(f"Error fetching suppliers: {str(e)}")
        return []

def get_all_products(supabase: Client):
    try:
        response = supabase.table("products_").select("product_id, product_name").order("product_name").execute()
        return response.data
    except Exception as e:
        st.error(f"Error fetching products: {str(e)}")
        return []

def get_product_history(supabase: Client, product_id):
    try:
        response = supabase.table("product_inventory_history").select("*").eq(
            "product_id", product_id
        ).order("record_date", desc=True).execute()
        return response.data
    except Exception as e:
        st.error(f"Error fetching product history: {str(e)}")
        return []

def place_reorder(supabase: Client, db, product_id, reorder_quantity):
    try:
        # Get the max reorder_id
        response = supabase.table("reorders").select("reorder_id").order("reorder_id", desc=True).limit(1).execute()
        new_reorder_id = (response.data[0]["reorder_id"] + 1) if response.data else 1
        
        # Insert new reorder
        from datetime import date
        supabase.table("reorders").insert({
            "reorder_id": new_reorder_id,
            "product_id": product_id,
            "reorder_quantity": reorder_quantity,
            "reorder_date": date.today().isoformat(),
            "status": "Ordered"
        }).execute()
    except Exception as e:
        raise Exception(f"Failed to place reorder: {str(e)}")


def get_pending_reorders(supabase: Client):
    try:
        response = supabase.table("reorders").select(
            "reorder_id, products_(product_name)"
        ).in_("status", ["Pending", "Ordered"]).execute()
        
        # Flatten the nested product data
        flattened = []
        for item in response.data:
            flattened.append({
                "reorder_id": item.get("reorder_id"),
                "product_name": item.get("products_", {}).get("product_name") if item.get("products_") else None
            })
        return flattened
    except Exception as e:
        st.error(f"Error fetching pending reorders: {str(e)}")
        return []

def mark_reorder_as_received(supabase: Client, db, reorder_id):
    try:
        # Get reorder details
        response = supabase.table("reorders").select("product_id, reorder_quantity").eq("reorder_id", reorder_id).execute()
        if not response.data:
            raise Exception("Reorder not found")
        
        prod_id = response.data[0]["product_id"]
        qty = response.data[0]["reorder_quantity"]
        
        # Get supplier_id from products
        response = supabase.table("products_").select("supplier_id").eq("product_id", prod_id).execute()
        sup_id = response.data[0]["supplier_id"]
        
        # Update reorder status
        from datetime import datetime
        supabase.table("reorders").update({
            "status": "Received",
            "updated_at": datetime.now().isoformat()
        }).eq("reorder_id", reorder_id).execute()
        
        # Update product stock quantity
        response = supabase.table("products_").select("stock_quantity").eq("product_id", prod_id).execute()
        current_stock = response.data[0]["stock_quantity"]
        
        supabase.table("products_").update({
            "stock_quantity": current_stock + qty,
            "updated_at": datetime.now().isoformat()
        }).eq("product_id", prod_id).execute()
        
        # Add shipment record
        response = supabase.table("shipments").select("shipment_id").order("shipment_id", desc=True).limit(1).execute()
        new_shipment_id = (response.data[0]["shipment_id"] + 1) if response.data else 1
        
        from datetime import date
        supabase.table("shipments").insert({
            "shipment_id": new_shipment_id,
            "product_id": prod_id,
            "supplier_id": sup_id,
            "quantity_received": qty,
            "shipment_date": date.today().isoformat()
        }).execute()
        
        # Add stock entry
        response = supabase.table("stock_entries").select("entry_id").order("entry_id", desc=True).limit(1).execute()
        new_entry_id = (response.data[0]["entry_id"] + 1) if response.data else 1
        
        supabase.table("stock_entries").insert({
            "entry_id": new_entry_id,
            "product_id": prod_id,
            "change_quantity": qty,
            "change_type": "Restock",
            "entry_date": date.today().isoformat()
        }).execute()
        
    except Exception as e:
        raise Exception(f"Failed to mark reorder as received: {str(e)}")









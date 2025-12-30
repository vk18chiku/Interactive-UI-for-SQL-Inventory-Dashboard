-- PostgreSQL Functions for Supabase
-- These functions calculate the metrics for the dashboard

-- Function 1: Get Total Sale Value (Last 3 Months)
CREATE OR REPLACE FUNCTION get_total_sale_value_3months()
RETURNS DECIMAL AS $$
BEGIN
  RETURN (
    SELECT ROUND(CAST(SUM(ABS(se.change_quantity) * p.price) AS NUMERIC), 2)
    FROM stock_entries AS se
    JOIN products_ AS p ON p.product_id = se.product_id
    WHERE se.change_type = 'Sale'
    AND se.entry_date >= (
      SELECT MAX(entry_date) - INTERVAL '3 months'
      FROM stock_entries
    )
  );
END;
$$ LANGUAGE plpgsql;

-- Function 2: Get Total Restock Value (Last 3 Months)
CREATE OR REPLACE FUNCTION get_total_restock_value_3months()
RETURNS DECIMAL AS $$
BEGIN
  RETURN (
    SELECT ROUND(CAST(SUM(ABS(se.change_quantity) * p.price) AS NUMERIC), 2)
    FROM stock_entries AS se
    JOIN products_ AS p ON p.product_id = se.product_id
    WHERE se.change_type = 'Restock'
    AND se.entry_date >= (
      SELECT MAX(entry_date) - INTERVAL '3 months'
      FROM stock_entries
    )
  );
END;
$$ LANGUAGE plpgsql;

-- Function 3: Get Count of Products Below Reorder with No Pending Reorders
CREATE OR REPLACE FUNCTION get_below_reorder_no_pending()
RETURNS INTEGER AS $$
BEGIN
  RETURN (
    SELECT COUNT(*)
    FROM products_ AS p
    WHERE p.stock_quantity < p.reorder_level
    AND p.product_id NOT IN (
      SELECT DISTINCT product_id
      FROM reorders
      WHERE status IN ('Pending', 'Ordered')
    )
  );
END;
$$ LANGUAGE plpgsql;

-- Function 4: Get All Basic Info (Combined)
CREATE OR REPLACE FUNCTION get_all_basic_info()
RETURNS TABLE (
  metric_name VARCHAR,
  metric_value DECIMAL
) AS $$
BEGIN
  RETURN QUERY
  SELECT 'Total Suppliers'::VARCHAR, 
         COUNT(*)::DECIMAL FROM suppliers
  UNION ALL
  SELECT 'Total Products'::VARCHAR,
         COUNT(*)::DECIMAL FROM products_
  UNION ALL
  SELECT 'Total Categories Dealing'::VARCHAR,
         COUNT(DISTINCT category)::DECIMAL FROM products_
  UNION ALL
  SELECT 'Total Sale Value (Last 3 Months)'::VARCHAR,
         COALESCE(get_total_sale_value_3months(), 0)::DECIMAL
  UNION ALL
  SELECT 'Total Restock Value (Last 3 Months)'::VARCHAR,
         COALESCE(get_total_restock_value_3months(), 0)::DECIMAL
  UNION ALL
  SELECT 'Below Reorder & No Pending Reorders'::VARCHAR,
         get_below_reorder_no_pending()::DECIMAL;
END;
$$ LANGUAGE plpgsql;

-- Test the functions (optional)
-- SELECT * FROM get_all_basic_info();
-- SELECT get_total_sale_value_3months();
-- SELECT get_total_restock_value_3months();
-- SELECT get_below_reorder_no_pending();

-- Update entries to have dates within last 3 months based on max date in table
-- This will make your dashboard show actual values

-- First, find the max date in stock_entries table
DO $$
DECLARE
  max_date DATE;
  three_months_before DATE;
BEGIN
  -- Get the maximum date from stock_entries
  SELECT MAX(entry_date) INTO max_date FROM stock_entries;
  
  -- Calculate 3 months before max date
  three_months_before := max_date - INTERVAL '3 months';
  
  RAISE NOTICE 'Max date in table: %', max_date;
  RAISE NOTICE 'Three months before: %', three_months_before;
  
  -- Update 30 restock entries to have random dates between (max_date - 3 months) and max_date
  UPDATE stock_entries 
  SET entry_date = three_months_before + (RANDOM() * (max_date - three_months_before))::INTEGER
  WHERE change_type = 'Restock' 
  AND entry_id IN (
    SELECT entry_id 
    FROM stock_entries 
    WHERE change_type = 'Restock' 
    ORDER BY RANDOM()
    LIMIT 30
  );
  
  -- Update 30 sale entries to have random dates between (max_date - 3 months) and max_date
  UPDATE stock_entries 
  SET entry_date = three_months_before + (RANDOM() * (max_date - three_months_before))::INTEGER
  WHERE change_type = 'Sale' 
  AND entry_id IN (
    SELECT entry_id 
    FROM stock_entries 
    WHERE change_type = 'Sale' 
    ORDER BY RANDOM()
    LIMIT 30
  );
  
  RAISE NOTICE 'Updated entries successfully!';
END $$;

-- Verify the changes
SELECT 
  change_type,
  COUNT(*) as total_entries,
  COUNT(*) FILTER (WHERE entry_date >= (SELECT MAX(entry_date) - INTERVAL '3 months' FROM stock_entries)) as entries_in_last_3_months,
  MIN(entry_date) as earliest_date,
  MAX(entry_date) as latest_date
FROM stock_entries
GROUP BY change_type;

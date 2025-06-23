-- Average Rent by Ward
-- Calculate average rent statistics by Tokyo ward

SELECT 
    city as ward,
    property_type,
    COUNT(*) as property_count,
    AVG(rent) as avg_rent,
    MIN(rent) as min_rent,
    MAX(rent) as max_rent,
    APPROX_PERCENTILE(rent, 0.5) as median_rent,
    STDDEV(rent) as rent_stddev
FROM real_estate_db.tokyo_properties
WHERE rent > 0
    AND rent < 1000000  -- Filter out unrealistic values
GROUP BY city, property_type
HAVING COUNT(*) >= 5  -- Only show wards with at least 5 properties
ORDER BY avg_rent DESC;
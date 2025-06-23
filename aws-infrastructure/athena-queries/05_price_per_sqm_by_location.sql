-- Price per Square Meter by Location
-- Calculate rent per square meter statistics by ward to understand pricing efficiency

WITH price_per_sqm AS (
    SELECT 
        city as ward,
        property_type,
        property_id,
        rent,
        area,
        rent / area as rent_per_sqm
    FROM real_estate_db.tokyo_properties
    WHERE rent > 0 
        AND area > 10  -- Filter out unrealistically small areas
        AND rent < 1000000  -- Filter out unrealistic rents
)
SELECT 
    ward,
    property_type,
    COUNT(*) as property_count,
    ROUND(AVG(rent_per_sqm), 0) as avg_rent_per_sqm,
    ROUND(MIN(rent_per_sqm), 0) as min_rent_per_sqm,
    ROUND(MAX(rent_per_sqm), 0) as max_rent_per_sqm,
    ROUND(APPROX_PERCENTILE(rent_per_sqm, 0.25), 0) as q1_rent_per_sqm,
    ROUND(APPROX_PERCENTILE(rent_per_sqm, 0.5), 0) as median_rent_per_sqm,
    ROUND(APPROX_PERCENTILE(rent_per_sqm, 0.75), 0) as q3_rent_per_sqm
FROM price_per_sqm
WHERE rent_per_sqm < 10000  -- Filter out unrealistic values
GROUP BY ward, property_type
HAVING COUNT(*) >= 10  -- Only show wards with sufficient data
ORDER BY avg_rent_per_sqm DESC;
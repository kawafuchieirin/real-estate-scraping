-- Floor Plan Analysis
-- Analyze property distribution and pricing by floor plan type

SELECT 
    floor_plan,
    property_type,
    COUNT(*) as property_count,
    AVG(rent) as avg_rent,
    AVG(area) as avg_area_sqm,
    MIN(rent) as min_rent,
    MAX(rent) as max_rent,
    APPROX_PERCENTILE(rent, 0.5) as median_rent,
    AVG(rent / NULLIF(area, 0)) as avg_rent_per_sqm
FROM real_estate_db.tokyo_properties
WHERE floor_plan IS NOT NULL
    AND rent > 0
    AND area > 0
    AND rent < 1000000  -- Filter out unrealistic values
GROUP BY floor_plan, property_type
HAVING COUNT(*) >= 3  -- Only show floor plans with at least 3 properties
ORDER BY property_count DESC, avg_rent DESC
LIMIT 30;
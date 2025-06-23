-- Comprehensive Property Analysis
-- Multi-dimensional analysis combining location, size, age, and station distance

WITH property_metrics AS (
    SELECT 
        city as ward,
        property_type,
        floor_plan,
        -- Age grouping
        CASE 
            WHEN COALESCE(building_age, YEAR(CURRENT_DATE) - construction_year) <= 10 THEN 'New (≤10 years)'
            WHEN COALESCE(building_age, YEAR(CURRENT_DATE) - construction_year) <= 20 THEN 'Medium (11-20 years)'
            ELSE 'Old (>20 years)'
        END as age_group,
        -- Station distance grouping
        CASE 
            WHEN station_distance <= 10 THEN 'Near (≤10 min)'
            ELSE 'Far (>10 min)'
        END as station_proximity,
        -- Area size grouping
        CASE 
            WHEN area <= 25 THEN 'Small (≤25㎡)'
            WHEN area <= 40 THEN 'Medium (26-40㎡)'
            ELSE 'Large (>40㎡)'
        END as size_category,
        rent,
        area,
        rent / area as rent_per_sqm
    FROM real_estate_db.tokyo_properties
    WHERE rent > 0 
        AND area > 10
        AND station_distance IS NOT NULL
        AND (building_age IS NOT NULL OR construction_year IS NOT NULL)
)
SELECT 
    ward,
    property_type,
    age_group,
    station_proximity,
    size_category,
    COUNT(*) as property_count,
    ROUND(AVG(rent), 0) as avg_rent,
    ROUND(AVG(area), 1) as avg_area,
    ROUND(AVG(rent_per_sqm), 0) as avg_rent_per_sqm,
    ROUND(APPROX_PERCENTILE(rent, 0.5), 0) as median_rent
FROM property_metrics
GROUP BY 
    ward,
    property_type,
    age_group,
    station_proximity,
    size_category
HAVING COUNT(*) >= 3
ORDER BY 
    ward,
    property_type,
    avg_rent DESC;
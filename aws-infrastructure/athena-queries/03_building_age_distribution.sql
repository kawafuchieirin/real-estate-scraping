-- Building Age Distribution
-- Analyze property distribution and pricing by building age

WITH current_year AS (
    SELECT YEAR(CURRENT_DATE) as year
),
age_calculated AS (
    SELECT 
        property_id,
        rent,
        area,
        property_type,
        city,
        -- Calculate building age from construction year if not provided
        COALESCE(
            building_age,
            (SELECT year FROM current_year) - construction_year
        ) as calculated_age
    FROM real_estate_db.tokyo_properties
    WHERE rent > 0 
        AND area > 0
        AND (building_age IS NOT NULL OR construction_year IS NOT NULL)
)
SELECT 
    CASE 
        WHEN calculated_age <= 5 THEN '0-5 years (築浅)'
        WHEN calculated_age <= 10 THEN '6-10 years'
        WHEN calculated_age <= 15 THEN '11-15 years'
        WHEN calculated_age <= 20 THEN '16-20 years'
        WHEN calculated_age <= 30 THEN '21-30 years'
        ELSE '30+ years (築古)'
    END as age_range,
    COUNT(*) as property_count,
    AVG(rent) as avg_rent,
    AVG(area) as avg_area_sqm,
    AVG(rent / area) as avg_rent_per_sqm,
    APPROX_PERCENTILE(rent, 0.5) as median_rent
FROM age_calculated
WHERE calculated_age >= 0 
    AND calculated_age <= 100  -- Filter out unrealistic values
GROUP BY 
    CASE 
        WHEN calculated_age <= 5 THEN '0-5 years (築浅)'
        WHEN calculated_age <= 10 THEN '6-10 years'
        WHEN calculated_age <= 15 THEN '11-15 years'
        WHEN calculated_age <= 20 THEN '16-20 years'
        WHEN calculated_age <= 30 THEN '21-30 years'
        ELSE '30+ years (築古)'
    END
ORDER BY 
    CASE age_range
        WHEN '0-5 years (築浅)' THEN 1
        WHEN '6-10 years' THEN 2
        WHEN '11-15 years' THEN 3
        WHEN '16-20 years' THEN 4
        WHEN '21-30 years' THEN 5
        ELSE 6
    END;
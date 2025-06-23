-- Property Analysis by Station Distance
-- Analyze how walking distance to station affects rent and property characteristics

SELECT 
    CASE 
        WHEN station_distance <= 5 THEN '0-5 minutes'
        WHEN station_distance <= 10 THEN '6-10 minutes'
        WHEN station_distance <= 15 THEN '11-15 minutes'
        WHEN station_distance <= 20 THEN '16-20 minutes'
        ELSE '20+ minutes'
    END as distance_range,
    COUNT(*) as property_count,
    AVG(area) as avg_area_sqm,
    AVG(rent) as avg_rent,
    AVG(rent / NULLIF(area, 0)) as avg_rent_per_sqm,
    APPROX_PERCENTILE(rent, 0.5) as median_rent
FROM real_estate_db.tokyo_properties
WHERE station_distance IS NOT NULL
    AND station_distance >= 0
    AND station_distance <= 60  -- Filter out unrealistic values
    AND area > 0
    AND rent > 0
GROUP BY 
    CASE 
        WHEN station_distance <= 5 THEN '0-5 minutes'
        WHEN station_distance <= 10 THEN '6-10 minutes'
        WHEN station_distance <= 15 THEN '11-15 minutes'
        WHEN station_distance <= 20 THEN '16-20 minutes'
        ELSE '20+ minutes'
    END
ORDER BY 
    CASE distance_range
        WHEN '0-5 minutes' THEN 1
        WHEN '6-10 minutes' THEN 2
        WHEN '11-15 minutes' THEN 3
        WHEN '16-20 minutes' THEN 4
        ELSE 5
    END;
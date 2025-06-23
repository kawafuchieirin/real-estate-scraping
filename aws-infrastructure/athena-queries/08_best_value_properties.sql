-- Best Value Properties Analysis
-- Find properties that offer the best value based on multiple criteria

WITH property_scores AS (
    SELECT 
        property_id,
        title,
        city as ward,
        address,
        property_type,
        floor_plan,
        rent,
        area,
        station_distance,
        building_age,
        rent / area as rent_per_sqm,
        -- Calculate percentile ranks for each metric (lower is better for these metrics)
        PERCENT_RANK() OVER (PARTITION BY city ORDER BY rent / area) as rent_efficiency_rank,
        PERCENT_RANK() OVER (PARTITION BY city ORDER BY station_distance) as station_proximity_rank,
        PERCENT_RANK() OVER (PARTITION BY city ORDER BY building_age) as newness_rank
    FROM real_estate_db.tokyo_properties
    WHERE rent > 0 
        AND area > 15
        AND station_distance IS NOT NULL
        AND building_age IS NOT NULL
        AND rent < 500000  -- Focus on reasonably priced properties
),
scored_properties AS (
    SELECT 
        *,
        -- Calculate composite score (lower is better)
        (rent_efficiency_rank * 0.5 + 
         station_proximity_rank * 0.3 + 
         newness_rank * 0.2) as value_score
    FROM property_scores
)
SELECT 
    ward,
    property_id,
    title,
    address,
    property_type,
    floor_plan,
    rent,
    area,
    ROUND(rent_per_sqm, 0) as rent_per_sqm,
    station_distance as walk_to_station_min,
    building_age as building_age_years,
    ROUND(value_score * 100, 2) as value_score_pct,
    CASE 
        WHEN value_score <= 0.2 THEN 'Excellent Value'
        WHEN value_score <= 0.4 THEN 'Good Value'
        WHEN value_score <= 0.6 THEN 'Fair Value'
        ELSE 'Below Average Value'
    END as value_category
FROM scored_properties
WHERE value_score <= 0.4  -- Show only good and excellent value properties
ORDER BY ward, value_score
LIMIT 100;
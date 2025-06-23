-- Time Series Analysis
-- Analyze property trends over time using scraped_at timestamp

WITH monthly_stats AS (
    SELECT 
        DATE_TRUNC('month', scraped_at) as month,
        city as ward,
        property_type,
        COUNT(*) as property_count,
        AVG(rent) as avg_rent,
        AVG(area) as avg_area,
        AVG(rent / NULLIF(area, 0)) as avg_rent_per_sqm
    FROM real_estate_db.tokyo_properties
    WHERE rent > 0 
        AND area > 0
        AND scraped_at IS NOT NULL
    GROUP BY 
        DATE_TRUNC('month', scraped_at),
        city,
        property_type
)
SELECT 
    month,
    ward,
    property_type,
    property_count,
    ROUND(avg_rent, 0) as avg_rent,
    ROUND(avg_area, 1) as avg_area,
    ROUND(avg_rent_per_sqm, 0) as avg_rent_per_sqm,
    -- Calculate month-over-month changes
    LAG(avg_rent) OVER (PARTITION BY ward, property_type ORDER BY month) as prev_month_rent,
    ROUND(
        100.0 * (avg_rent - LAG(avg_rent) OVER (PARTITION BY ward, property_type ORDER BY month)) / 
        NULLIF(LAG(avg_rent) OVER (PARTITION BY ward, property_type ORDER BY month), 0), 
        2
    ) as rent_change_pct
FROM monthly_stats
WHERE property_count >= 5  -- Only include months with sufficient data
ORDER BY month DESC, ward, property_type;
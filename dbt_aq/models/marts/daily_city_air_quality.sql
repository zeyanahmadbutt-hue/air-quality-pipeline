select
    city,
    observed_date,
    count(*) as hours_observed,
    round(avg(pm25)::numeric, 1) as avg_pm25,
    max(pm25) as max_pm25,
    round(avg(us_aqi)::numeric, 0) as avg_aqi,
    max(us_aqi) as max_aqi,
    count(*) filter (where us_aqi > 100) as unhealthy_hours
from {{ ref('stg_air_quality') }}
group by city, observed_date

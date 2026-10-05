select
    city,
    observed_at,
    (observed_at at time zone 'Asia/Karachi')::date as observed_date,
    pm10,
    pm2_5 as pm25,
    us_aqi,
    case
        when us_aqi <= 50 then 'Good'
        when us_aqi <= 100 then 'Moderate'
        when us_aqi <= 150 then 'Unhealthy for Sensitive Groups'
        when us_aqi <= 200 then 'Unhealthy'
        when us_aqi <= 300 then 'Very Unhealthy'
        else 'Hazardous'
    end as aqi_category
from {{ source('raw', 'air_quality_hourly') }}

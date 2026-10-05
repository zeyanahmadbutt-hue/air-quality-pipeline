CREATE TABLE IF NOT EXISTS air_quality_hourly (
    city        TEXT        NOT NULL,
    observed_at TIMESTAMPTZ NOT NULL,
    pm10        DOUBLE PRECISION,
    pm2_5       DOUBLE PRECISION,
    us_aqi      INTEGER,
    loaded_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (city, observed_at)
);

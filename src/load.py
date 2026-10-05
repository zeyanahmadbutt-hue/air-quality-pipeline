import os
import pandas as pd
import psycopg
from dotenv import load_dotenv
load_dotenv()
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "sql", "schema.sql")
UPSERT_SQL = """
INSERT INTO air_quality_hourly (city, observed_at, pm10, pm2_5, us_aqi)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT (city, observed_at) DO UPDATE SET
    pm10 = EXCLUDED.pm10,
    pm2_5 = EXCLUDED.pm2_5,
    us_aqi = EXCLUDED.us_aqi,
    loaded_at = now()
"""
def get_conn():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )
def init_schema(conn):
    with open(SCHEMA_PATH, encoding="utf-8-sig") as f:
        conn.execute(f.read())
    conn.commit()
def _clean(value, cast):
    return None if pd.isna(value) else cast(value)
def upsert(conn, df):
    rows = [
        (
            r.city,
            r.observed_at.to_pydatetime(),
            _clean(r.pm10, float),
            _clean(r.pm2_5, float),
            _clean(r.us_aqi, int),
        )
        for r in df.itertuples(index=False)
    ]
    with conn.cursor() as cur:
        cur.executemany(UPSERT_SQL, rows)
    conn.commit()
    return len(rows)


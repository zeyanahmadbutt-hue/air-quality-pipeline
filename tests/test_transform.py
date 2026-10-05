import pandas as pd
from transform import transform
TZ = "Asia/Karachi"
def hour(offset):
    t = pd.Timestamp.now(tz=TZ).floor("h") + pd.Timedelta(hours=offset)
    return t.strftime("%Y-%m-%dT%H:%M")
def make_raw(rows, city="Testville"):
    return [{
        "city": city,
        "hourly": {
            "time": [r[0] for r in rows],
            "pm10": [r[1] for r in rows],
            "pm2_5": [r[2] for r in rows],
            "us_aqi": [r[3] for r in rows],
        },
    }]
def test_drops_future_rows():
    raw = make_raw([(hour(-2), 10, 5, 40), (hour(-1), 11, 6, 41),
                    (hour(3), 12, 7, 42)])
    clean, stats = transform(raw)
    assert len(clean) == 2
    assert stats["raw_rows"] == 3
def test_drops_all_null_rows():
    raw = make_raw([(hour(-2), 10, 5, 40), (hour(-1), None, None, None)])
    clean, _ = transform(raw)
    assert len(clean) == 1
def test_drops_invalid_values():
    raw = make_raw([(hour(-3), -5, 5, 40), (hour(-2), 10, 5, 600),
                    (hour(-1), 10, 5, 40)])
    clean, _ = transform(raw)
    assert len(clean) == 1
def test_removes_duplicates():
    raw = make_raw([(hour(-1), 10, 5, 40), (hour(-1), 10, 5, 40)])
    clean, _ = transform(raw)
    assert len(clean) == 1
def test_output_columns():
    raw = make_raw([(hour(-1), 10, 5, 40)])
    clean, _ = transform(raw)
    assert list(clean.columns) == ["city", "observed_at", "pm10", "pm2_5", "us_aqi"]

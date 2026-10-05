import pandas as pd
TZ = "Asia/Karachi"
def transform(raw):
    frames = []
    for item in raw:
        df = pd.DataFrame(item["hourly"])
        df["city"] = item["city"]
        frames.append(df)
    df = pd.concat(frames, ignore_index=True)
    df = df.rename(columns={"time": "observed_at"})
    df["observed_at"] = pd.to_datetime(df["observed_at"]).dt.tz_localize(TZ)
    stats = {"raw_rows": len(df)}
    now = pd.Timestamp.now(tz=TZ)
    df = df[df["observed_at"] <= now]
    stats["after_future_filter"] = len(df)
    df = df.dropna(subset=["pm10", "pm2_5", "us_aqi"], how="all")
    stats["after_null_filter"] = len(df)
    valid = (
        (df["pm10"].isna() | (df["pm10"] >= 0))
        & (df["pm2_5"].isna() | (df["pm2_5"] >= 0))
        & (df["us_aqi"].isna() | df["us_aqi"].between(0, 500))
    )
    df = df[valid]
    stats["after_validity_filter"] = len(df)
    df = df.drop_duplicates(subset=["city", "observed_at"])
    stats["final_rows"] = len(df)
    df = df[["city", "observed_at", "pm10", "pm2_5", "us_aqi"]]
    df = df.sort_values(["city", "observed_at"]).reset_index(drop=True)
    return df, stats
if __name__ == "__main__":
    from extract import extract_all
    clean, stats = transform(extract_all())
    print(stats)
    print(clean.groupby("city").size())
    print(clean.tail(3))

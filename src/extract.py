import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
log = logging.getLogger(__name__)
API_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
CITIES = {
    "Islamabad": (33.6844, 73.0479),
    "Lahore": (31.5497, 74.3436),
    "Karachi": (24.8607, 67.0011),
    "Faisalabad": (31.4504, 73.1350),
}
def make_session():
    retry = Retry(total=3, backoff_factor=2,
                  status_forcelist=[429, 500, 502, 503, 504])
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session
def fetch_city(session, city, lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "pm10,pm2_5,us_aqi",
        "timezone": "Asia/Karachi",
        "past_days": 2,
        "forecast_days": 1,
    }
    response = session.get(API_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    if "hourly" not in data:
        raise ValueError(f"no 'hourly' key in response for {city}")
    return {"city": city, "hourly": data["hourly"]}
def extract_all():
    session = make_session()
    results = []
    for city, (lat, lon) in CITIES.items():
        try:
            results.append(fetch_city(session, city, lat, lon))
            log.info("extracted %s", city)
        except (requests.RequestException, ValueError):
            log.exception("failed to extract %s", city)
    return results
if __name__ == "__main__":
    for result in extract_all():
        hourly = result["hourly"]
        print(result["city"], "| rows:", len(hourly["time"]),
              "| first:", hourly["time"][0],
              "| last pm2_5:", hourly["pm2_5"][-1])

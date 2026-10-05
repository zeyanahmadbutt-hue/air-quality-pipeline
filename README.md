# Air Quality Pipeline
An ETL pipeline that pulls hourly air quality data (PM10, PM2.5, US AQI) for Islamabad, Lahore, Karachi and Faisalabad from the free Open-Meteo API, cleans it, and loads it into PostgreSQL. It runs daily and is safe to re-run.
## Flow
Open-Meteo API -> extract.py -> transform.py -> load.py (upsert) -> PostgreSQL
## Design decisions
- **Idempotent loads:** primary key on (city, observed_at) plus INSERT ... ON CONFLICT DO UPDATE, so re-runs never create duplicates.
- **Forecast filtering:** the API returns future hours as forecasts; transform drops them so only observed data is stored.
- **Validation:** rows with all-null measurements, negative readings, or AQI outside 0-500 are dropped, and row counts at each stage are logged.
- **Failure handling:** API calls retry with backoff; one failing city does not stop the others (exit code 2 = partial run); a failed load returns exit code 1.
- **Tests:** pytest unit tests cover every transform rule.
## Setup
1. Install Python 3.11+ and PostgreSQL 16, then create a database named airquality.
2. Create .env in the project root:
        POSTGRES_USER=postgres
        POSTGRES_PASSWORD=your_password
        POSTGRES_DB=airquality
        POSTGRES_HOST=localhost
        POSTGRES_PORT=5432
3. Install and run:
        python -m venv .venv
        .venv\Scripts\Activate.ps1
        pip install -r requirements.txt
        python src\pipeline.py
        pytest
## Scheduling
Runs daily through Windows Task Scheduler, with logs written to logs/pipeline.log.
## Example query
    SELECT city, round(avg(pm2_5)::numeric, 1) AS avg_pm25
    FROM air_quality_hourly
    GROUP BY city
    ORDER BY avg_pm25 DESC;
## Next steps
Orchestration with Airflow, dbt models on top of the table, and a cloud warehouse.

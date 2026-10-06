from datetime import datetime, timedelta

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator

PROJECT = "/workspaces/air-quality-pipeline"
PY = "/home/codespace/pipe-venv/bin/python"
DBT = "/home/codespace/pipe-venv/bin/dbt"

default_args = {"retries": 2, "retry_delay": timedelta(minutes=2)}

with DAG(
    dag_id="air_quality_daily",
    start_date=datetime(2026, 10, 1),
    schedule="0 4 * * *",  # 04:00 UTC = 09:00 Pakistan time
    catchup=False,
    default_args=default_args,
    tags=["air-quality"],
) as dag:
    ingest = BashOperator(
        task_id="ingest",
        bash_command=f"cd {PROJECT} && {PY} src/pipeline.py",
    )
    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {PROJECT}/dbt_aq && {DBT} run --profiles-dir .",
    )
    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {PROJECT}/dbt_aq && {DBT} test --profiles-dir .",
    )

    ingest >> dbt_run >> dbt_test

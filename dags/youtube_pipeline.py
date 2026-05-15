import sys
sys.path.insert(0, '/opt/airflow')

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

from include.youtube_api import (
    extract_task,
    load_to_staging,
    transform_to_core,
)
from include.soda.quality_checks import run_soda_checks



def load_staging_task(**context):
    videos_data = context["ti"].xcom_pull(task_ids="extract")
    load_to_staging(videos_data)

with DAG(
        dag_id="youtube_pipeline",
        default_args=default_args,
        start_date=datetime(2024, 1, 1),
        schedule_interval="@daily",
        catchup=False,
        description="ELT pipeline for YouTube channel data",
) as dag:

    extract = PythonOperator(
        task_id="extract",
        python_callable=extract_task,
    )

    load_staging = PythonOperator(
        task_id="load_staging",
        python_callable=load_staging_task,
        provide_context=True,
    )

    transform_core = PythonOperator(
        task_id="transform_to_core",
        python_callable=transform_to_core,
    )

    quality_checks = PythonOperator(
        task_id="data_quality_checks",
        python_callable=run_soda_checks,
    )

    extract >> load_staging >> transform_core >> quality_checks
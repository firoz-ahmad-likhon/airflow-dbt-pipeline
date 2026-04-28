import os
from typing import Any

import pendulum

from airflow.exceptions import AirflowException
from airflow.models import DagRun
from airflow.sdk import Param, dag, task
from airflow.utils.types import DagRunType

DBT_PROJECT_DIR = os.getenv("DBT_PROJECT_DIR", "/opt/airflow/dbt")
DBT_PROFILES_DIR = os.getenv("DBT_PROFILES_DIR", "/opt/airflow/dbt")
DEFAULT_LOOKBACK_HOURS = 6
MIN_LOOKBACK_HOURS = 1
MAX_LOOKBACK_HOURS = 168


@dag(
    dag_id="wind_and_solar_power_transformation",
    schedule="10,40 * * * *",  # Run 5 minutes after the ingestion DAG
    start_date=pendulum.datetime(2025, 5, 10, 10, 50, 0, tz="UTC"),
    catchup=False,
    tags=["dbt", "half hourly"],
    default_args={
        "retries": 1,
        "retry_delay": pendulum.duration(minutes=5),
    },
    params={
        "lookback_hours": Param(
            default=DEFAULT_LOOKBACK_HOURS,
            type="integer",
            minimum=MIN_LOOKBACK_HOURS,
            maximum=MAX_LOOKBACK_HOURS,
            description="Number of recent hours to rebuild in the incremental dbt model.",
        ),
    },
    description="A dbt DAG for transforming raw wind and solar generation payloads into analytics models",
)
def wind_and_solar_power_transformation() -> None:
    """Dbt transformation DAG for wind and solar power generation data."""

    @task(task_display_name="Parameterize lookback", retries=0)
    def parameterize(params: dict[str, Any], dag_run: DagRun) -> dict[str, int]:
        """Validate dbt runtime parameters and return command arguments."""
        if dag_run.run_type == DagRunType.BACKFILL_JOB:
            raise AirflowException("Backfill runs are not supported for this dbt DAG")

        lookback_hours = params["lookback_hours"]

        if not isinstance(lookback_hours, int):
            raise AirflowException("lookback_hours must be an integer")

        if lookback_hours < MIN_LOOKBACK_HOURS or lookback_hours > MAX_LOOKBACK_HOURS:
            raise AirflowException(f"lookback_hours must be between {MIN_LOOKBACK_HOURS} and {MAX_LOOKBACK_HOURS}")

        return {
            "lookback_hours": lookback_hours,
        }

    @task.bash(task_display_name="Build dbt models")
    def build_dbt_models(p: dict[str, int]) -> str:
        """Run dbt Fusion to build the wind and solar models."""
        lookback_hours = p["lookback_hours"]

        return f"dbt build --project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR} --select tag:wind_solar --vars '{{\"lookback_hours\": {lookback_hours}}}'"

    parameterized = parameterize()  # type: ignore
    build_dbt_models(parameterized)


# Instantiate the DAG
wind_and_solar_power_transformation()

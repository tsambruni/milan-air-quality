from airflow.decorators import dag
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup
from cosmos.providers.dbt.core.operators import DbtRunOperator
import pendulum
# import pdb

# Define constants
today = pendulum.today(tz="local").format("YYYY-MM-DD")
# dbt needs
DBT_PROJECT = "dbt_air_quality"


@dag(
    start_date=pendulum.local(2023, 1, 1),
    max_active_runs=1,
    schedule=None,
    catchup=False,
    tags=["project", "gcp", "dbt"],
)
def dbt_air_data_dag():
    """
    """
    dbt_run = DbtRunOperator(
        task_id="dbt_run",
        project_dir=f"/usr/local/airflow/dbt/{DBT_PROJECT}",
        schema="air_quality_data",
        dbt_executable_path="/usr/local/airflow/dbt_venv/bin/dbt",
        conn_id="gcp-connection"
    )

    dbt_run


dbt_air_data_dag()

if __name__ == "__main__":
    dag.test()

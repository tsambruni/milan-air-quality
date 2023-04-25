from airflow.decorators import dag, task
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
import pandas as pd
import pendulum
# import requests
# import json


@dag(
        start_date=pendulum.local(2023, 1, 1),
        schedule=None,
        catchup=False,
        tags=["project", "gcp"]
        )
def milan_air_dag():
    """
    ### Add DAG info
    """

    @task()
    def get_daily_data(local_filename: str = "air_quality.parquet") -> str:
        """
        Gets City of Milan's 2023 air quality data.\n
        Data is shown for working days only and includes historical
        data since beginning of the year.\n
        Info url: https://dati.comune.milano.it/dataset/ds409-rilevazione-qualita-aria-2023\n
        Returns local path as string for further usage.
        """
        url = "https://dati.comune.milano.it/dataset/405ae1cd-0687-4449-baf2-6c9d993ed176/resource/781b1d03-5c4d-4c17-b10d-f9f74dbd7921/download/qaria_datoariagiornostazione_2023-01-01.json" # noqa
        df = pd.read_json(url)
        df['data'] = pd.to_datetime(df['data'])
        df['inquinante'] = df['inquinante'].astype(str)
        df.to_parquet(f"./data/{local_filename}", index=False)
        return local_filename

    @task()
    def get_station_data(local_filename: str = "stations.parquet") -> str:
        """
        Gets air quality stations.\n
        Info url: https://dati.comune.milano.it/dataset/ds409-rilevazione-qualita-aria-2023\n
        Returns local path as string for further usage.
        """
        url = "https://dati.comune.milano.it/dataset/d6960c75-0a02-4fda-a85f-3b1c4aa725d6/resource/b301f327-7504-4efc-8b4a-5f4a29f9d0ff/download/qaria_stazione.csv" # noqa
        df = pd.read_csv(url, sep=';')
        df['inizio_operativita'] = pd.to_datetime(df['inizio_operativita'])
        df['fine_operativita'] = pd.to_datetime(df['fine_operativita'])
        df['LONG_X_4326'] = df['LONG_X_4326'].astype(str)
        df['LAT_Y_4326'] = df['LAT_Y_4326'].astype(str)
        df = df.drop(columns='Location')
        df.to_parquet(f"./data/{local_filename}", index=False)
        return local_filename

    @task()
    def load_to_dwh() -> None:
        """
        Loads parquet file to data lake (Google Cloud Storage)
        """
        pass

    daily = get_daily_data()
    stations = get_station_data()

    load_to_datalake = LocalFilesystemToGCSOperator(
        gcp_conn_id="gcp-connection",
        task_id="load_to_datalake",
        src="/usr/local/airflow/data/*",
        dst="",
        bucket="milan-air-data-bucket"
    )

    [daily, stations] >> load_to_datalake >> load_to_dwh()


milan_air_dag()

if __name__ == "__main__":
    dag.test()

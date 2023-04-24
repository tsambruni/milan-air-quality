from airflow.decorators import dag, task
from airflow.operators.empty import EmptyOperator
from datetime import datetime
import pandas as pd
# import requests
# import json


@dag(
        start_date=datetime(2023, 1, 1),
        schedule=None,
        tags=["project", "gcp"]
        )
def milan_air_dag():
    """
    ### Add DAG info
    """

    @task()
    def get_daily_data() -> str:
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
        local_path = './data/air_quality.parquet'
        df.to_parquet(local_path, index=False)
        return local_path

    @task()
    def get_station_data() -> str:
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
        local_path = './data/stations.parquet'
        df.to_parquet(local_path, index=False)
        return local_path

    @task()
    def load_to_datalake(path: str) -> None:
        """
        Loads parquet file to data lake (Google Cloud Storage)
        """
        return None

    @task()
    def load_to_dwh(path: str) -> None:
        """
        Loads parquet file to data lake (Google Cloud Storage)
        """
        return None

    daily_path = get_daily_data()
    stations_path = get_station_data()
    status = load_to_datalake([daily_path, stations_path])
    load_to_dwh(status)


milan_air_dag()

if __name__ == "__main__":
    dag.test()

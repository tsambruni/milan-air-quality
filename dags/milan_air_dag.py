from airflow.decorators import dag, task
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator  # noqa
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator  # noqa
import requests
import json
import pandas as pd
import pendulum
# import pdb

# Define constants
GCP_CONN_ID = "gcp-connection"
BUCKET_ID = "milan-air-data-bucket"
today = pendulum.today(tz="local").format('YYYY-MM-DD')


@dag(
        start_date=pendulum.local(2023, 1, 1),
        schedule="40 6 * * 1-5",
        catchup=False,
        tags=["project", "gcp"]
        )
def milan_air_dag():
    """
    ### milan_air_dag
    1. Gets data from json and csv files
    2. Applies transformation via pandas
    3. Loadparquet files to Google Cloud Storage (keeps defined schema)
    4. Loads files from bucket to Big Query tables for further analysis.
    """

    @task()
    def extract_data():
        """
        1. Gets City of Milan's 2023 air quality data.
        2. Applies transformation to schema.s
        - Returns local path as string for further usage.
        - Data is shown for working days only and includes historical data
        since beginning of the year.
        - Info: https://dati.comune.milano.it/dataset/ds409-rilevazione-qualita-aria-2023 # noqa
        """
        daily_req = requests.get("https://dati.comune.milano.it/dataset/405ae1cd-0687-4449-baf2-6c9d993ed176/resource/781b1d03-5c4d-4c17-b10d-f9f74dbd7921/download/qaria_datoariagiornostazione_2023-01-01.json") # noqa
        daily_data = json.dumps(daily_req.json(), indent=4)

        # Writes file locally
        daily_file = open(f"./data/raw/{today}_air_quality.json", "w")
        daily_file.write(daily_data)
        daily_file.close()
        stations_req = requests.get("https://dati.comune.milano.it/dataset/d6960c75-0a02-4fda-a85f-3b1c4aa725d6/resource/b301f327-7504-4efc-8b4a-5f4a29f9d0ff/download/qaria_stazione.csv") # noqa

        # Writes file locally
        stations_file = open(f"./data/raw/{today}_stations.csv", "w")
        stations_file.write(stations_req.text)
        stations_file.close()

    @task()
    def transform_data():
        """
        """
        df_daily = pd.read_json(f"./data/raw/{today}_air_quality.json")
        df_daily['data'] = pd.to_datetime(df_daily['data'])
        df_daily['inquinante'] = df_daily['inquinante'].astype(str)
        df_daily.to_parquet(
            f"./data/staging/{today}_air_quality.parquet",
            index=False
        )
        df_stations = pd.read_csv(f"./data/raw/{today}_stations.csv", sep=';')
        df_stations['inizio_operativita'] = pd.to_datetime(df_stations['inizio_operativita'])
        df_stations['fine_operativita'] = pd.to_datetime(df_stations['fine_operativita'])
        df_stations['LONG_X_4326'] = df_stations['LONG_X_4326'].astype(str)
        df_stations['LAT_Y_4326'] = df_stations['LAT_Y_4326'].astype(str)
        df_stations = df_stations.drop(columns='Location')
        df_stations.to_parquet(
            f"./data/staging/{today}_stations.parquet",
            index=False
        )

    load_raw_data = LocalFilesystemToGCSOperator(
        gcp_conn_id=GCP_CONN_ID,
        task_id="load_raw_data",
        src="/usr/local/airflow/data/raw/*",
        dst="raw/",
        bucket=BUCKET_ID
    )

    load_staging_data = LocalFilesystemToGCSOperator(
        gcp_conn_id=GCP_CONN_ID,
        task_id="load_staging_data",
        src="/usr/local/airflow/data/staging/*",
        dst="staging/",
        bucket=BUCKET_ID
    )

    # Requires an operator for every load task, as it's not possible to map
    # different multiple files to different tables at once
    load_to_dwh_daily = GCSToBigQueryOperator(
        gcp_conn_id=GCP_CONN_ID,
        task_id='load_to_dwh_daily',
        source_objects=f"staging/{today}_air_quality.parquet",
        destination_project_dataset_table="air_quality_data.air_quality",
        source_format='PARQUET',
        autodetect=True,
        create_disposition='CREATE_IF_NEEDED',
        write_disposition='WRITE_TRUNCATE',
        bucket=BUCKET_ID
    )

    load_to_dwh_stations = GCSToBigQueryOperator(
        gcp_conn_id=GCP_CONN_ID,
        task_id='load_to_dwh_stations',
        source_objects=f"staging/{today}_stations.parquet",
        destination_project_dataset_table="air_quality_data.stations",
        source_format='PARQUET',
        autodetect=True,
        create_disposition='CREATE_IF_NEEDED',
        write_disposition='WRITE_TRUNCATE',
        bucket=BUCKET_ID
    )

    extract_data() >> load_raw_data >> transform_data() >> load_staging_data >> [load_to_dwh_daily, load_to_dwh_stations]


milan_air_dag()

if __name__ == "__main__":
    dag.test()

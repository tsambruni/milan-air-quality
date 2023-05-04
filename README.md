# Milan Air Quality

Hey, I'm building this data engineering project for self learning purposes.


## Project Contents

Source is open data from [City of milan 2023 Air Quality report](https://dati.comune.milano.it/dataset/ds409-rilevazione-qualita-aria-2023).

Basic description:
1. Extract 2023 air quality data.
> *Data is shown for working days only and includes historical data since beginning of the year. Includes also stations master data, needed for joining facts and add some complexity to DAG*

2. Load locally stored raw files to Google Cloud Storage
> *Create archive with raw data history*

3. Transform data and generate parquet files to keep schema edits

4. Store last transformed data in Google Cloud Storage (staging)

4. Load data from parquet to Google Big Query

5. Build model via dbt core

6. Analyze data

In order to experiment with Apache Airflow, I installed Astro CLI tools (which I **strongly** recommend if you want to speed up deployment of a local Airflow instance!) 😎
# Milan Air Quality

Hey, I'm building this data engineering project for self learning purposes.


## Project Contents

Source is open data from [City of milan 2023 Air Quality report](https://dati.comune.milano.it/dataset/ds409-rilevazione-qualita-aria-2023).

Basic description:
1. Get 2023 air quality data. `IN PROGRESS`
> *Data is shown for working days only and includes historical data since beginning of the year.*

2. Get air quality stations master data. `IN PROGRESS`
> *Not many stations available, used basically for joining facts and add some complexity to  to DAG.*

3. Load locally stored parquet data to Google Cloud Storage `TODO`
> *In order to keep schema edits to data file*

4. Load data from datalake to Google Big Query `TODO`

5. Analyze data `TODO`
> *I would probably build a quick app with Streamlit or Panel*



In order to experiment with Apache Airflow, I installed Astro CLI tools (which I **strongly** recommend if you want to speed up deployment of a local Airflow instance!) 😎
FROM quay.io/astronomer/astro-runtime:8.1.0

# install dbt into a virtual environment
# replace dbt-postgres with another supported adapter if you're using a different warehouse type
WORKDIR "/usr/local/airflow"
COPY dbt-requirements.txt ./
RUN python -m virtualenv dbt_venv && source dbt_venv/bin/activate && \
pip install --no-cache-dir -r dbt-requirements.txt && deactivate
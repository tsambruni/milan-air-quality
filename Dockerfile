FROM quay.io/astronomer/astro-runtime:8.0.0

# install dbt into a virtual environment
# replace dbt-postgres with another supported adapter if you're using a different warehouse type
RUN python -m venv dbt_venv && source dbt_venv/bin/activate && \
pip install --no-cache-dir dbt-bigquery && deactivate
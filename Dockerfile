# Apache Airflow image as the base
FROM apache/airflow:3.0.1 AS base

# Set workdir
WORKDIR /opt/airflow

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends bash git curl ca-certificates libpq5 \
    && rm -rf /var/lib/apt/lists/*

USER airflow

ARG DBT_FUSION_VERSION=2.0.0-preview.164

ENV PATH="/home/airflow/.local/bin:${PATH}" \
    DBT_PROJECT_DIR=/opt/airflow/dbt \
    DBT_PROFILES_DIR=/opt/airflow/dbt

RUN curl -fsSL https://public.cdn.getdbt.com/fs/install/install.sh | bash -s -- --update --version "${DBT_FUSION_VERSION}" \
    && dbt --version

# Install Python dependencies
COPY airflow/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY airflow/dags/ dags/
COPY airflow/pipelines/ pipelines/
COPY --chown=airflow:0 dbt/ dbt/
COPY alembic/ alembic/
COPY alembic.ini .

# Production stage
FROM base AS prod

EXPOSE 8080
CMD ["airflow", "api-server"]

# Development stage
FROM base AS dev

# Install dev-specific Python tools
COPY airflow/requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

EXPOSE 8080
CMD ["airflow", "api-server"]

#!/usr/bin/env python3
"""
Ukázka Airflow workflow pro orchestraci datové pipeline v Cloudera ekosystému.
Tento DAG demonstruje ETL proces s využitím Spark a Hive v Cloudera Data Platform.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.apache.hdfs.sensors.hdfs import HdfsSensor
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from airflow.hooks.base_hook import BaseHook

# Výchozí argumenty pro DAG
default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'email': ['datateam@example.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Proměnné pro konfiguraci
data_dir = Variable.get("cloudera_data_directory", default_var="/user/hive/data")
spark_master = Variable.get("spark_master", default_var="yarn")
hdfs_conn = BaseHook.get_connection("hdfs_default")
hdfs_host = hdfs_conn.host

# Definice DAG
dag = DAG(
    'cloudera_etl_workflow',
    default_args=default_args,
    description='ETL workflow v Cloudera ekosystému',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['cloudera', 'etl', 'iceberg'],
)

# 1. Kontrola dostupnosti vstupních dat v HDFS
check_input_data = HdfsSensor(
    task_id='check_input_data',
    filepath=f'{data_dir}/raw/products/{{{{ ds }}}}/data.csv',
    hdfs_conn_id='hdfs_default',
    poke_interval=60,
    timeout=600,
    dag=dag,
)

# 2. Příprava pracovního adresáře
prepare_workspace = BashOperator(
    task_id='prepare_workspace',
    bash_command=f'hdfs dfs -mkdir -p {data_dir}/processed/{{{{ ds }}}} && '
                 f'hdfs dfs -mkdir -p {data_dir}/reports/{{{{ ds }}}}',
    dag=dag,
)

# 3. Transformace dat pomocí Spark
transform_data = SparkSubmitOperator(
    task_id='transform_data',
    application='/opt/airflow/dags/scripts/transform_products.py',
    name='data_transformation',
    conn_id='spark_default',
    application_args=[
        '--input', f'{data_dir}/raw/products/{{{{ ds }}}}/data.csv',
        '--output', f'{data_dir}/processed/{{{{ ds }}}}/products.parquet',
        '--date', '{{ ds }}'
    ],
    conf={
        'spark.driver.memory': '2g',
        'spark.executor.memory': '2g',
        'spark.executor.cores': '2'
    },
    dag=dag,
)

# 4. Zpracování dat a uložení do Iceberg tabulky
load_to_iceberg = SparkSubmitOperator(
    task_id='load_to_iceberg',
    application='/opt/airflow/dags/scripts/load_to_iceberg.py',
    name='iceberg_loader',
    conn_id='spark_default',
    application_args=[
        '--input', f'{data_dir}/processed/{{{{ ds }}}}/products.parquet',
        '--table', 'db.products_catalog',
        '--date', '{{ ds }}'
    ],
    conf={
        'spark.sql.extensions': 'org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions',
        'spark.sql.catalog.spark_catalog': 'org.apache.iceberg.spark.SparkSessionCatalog',
        'spark.sql.catalog.spark_catalog.type': 'hadoop'
    },
    dag=dag,
)

# 5. Generování analytického reportu
generate_report = SparkSubmitOperator(
    task_id='generate_report',
    application='/opt/airflow/dags/scripts/generate_report.py',
    name='report_generator',
    conn_id='spark_default',
    application_args=[
        '--table', 'db.products_catalog',
        '--output', f'{data_dir}/reports/{{{{ ds }}}}/daily_report',
        '--date', '{{ ds }}'
    ],
    dag=dag,
)

# 6. Validace dat a monitorování kvality
validate_data = SparkSubmitOperator(
    task_id='validate_data',
    application='/opt/airflow/dags/scripts/data_quality.py',
    name='data_validator',
    conn_id='spark_default',
    application_args=[
        '--table', 'db.products_catalog',
        '--rules', '/opt/airflow/dags/config/validation_rules.json',
        '--date', '{{ ds }}'
    ],
    dag=dag,
)

# 7. Archivace původních dat
archive_raw_data = BashOperator(
    task_id='archive_raw_data',
    bash_command=f'hdfs dfs -mv {data_dir}/raw/products/{{{{ ds }}}} '
                 f'{data_dir}/archive/products/{{{{ ds }}}}',
    dag=dag,
)

# 8. Notifikace o dokončení
send_notification = BashOperator(
    task_id='send_notification',
    bash_command='echo "ETL pipeline dokončena: {{ ds }}" | mail -s "ETL Report" datateam@example.com',
    dag=dag,
)

# Definice závislostí mezi úlohami
check_input_data >> prepare_workspace >> transform_data >> load_to_iceberg
load_to_iceberg >> [generate_report, validate_data]
[generate_report, validate_data] >> archive_raw_data >> send_notification 
"""
Ukázkový DAG pro demonstraci základních konceptů Apache Airflow.
"""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator


# Defaultní argumenty pro DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Definice DAG
with DAG(
    'hello_world',
    default_args=default_args,
    description='Jednoduchý Hello World DAG',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2025, 4, 15),
    catchup=False,
    tags=['example'],
) as dag:

    # Task 1: BashOperator pro vypsání "Hello"
    task_hello = BashOperator(
        task_id='print_hello',
        bash_command='echo "Hello"',
    )
    
    # Funkce pro Python task
    def print_world():
        """Vypíše 'World!'."""
        print("World!")
        return "World!"
    
    # Task 2: PythonOperator pro vypsání "World!"
    task_world = PythonOperator(
        task_id='print_world',
        python_callable=print_world,
    )
    
    # Task 3: BashOperator pro vypsání data
    task_date = BashOperator(
        task_id='print_date',
        bash_command='date',
    )
    
    # Definice závislostí mezi tasky
    # task_hello běží první, pak task_world, a nakonec task_date
    task_hello >> task_world >> task_date 
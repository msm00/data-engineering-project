"""
Dynamické generování DAGů na základě konfiguračního souboru.
Tento skript demonstruje, jak lze dynamicky vytvářet DAGy na základě externí konfigurace.
"""
from datetime import datetime, timedelta
import os
import json

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

# Cesta ke konfiguračnímu souboru
CONFIG_DIR = '/opt/airflow/project/data'
CONFIG_FILE = os.path.join(CONFIG_DIR, 'dag_config.json')

# Zajistíme, že adresář existuje
os.makedirs(CONFIG_DIR, exist_ok=True)

# Vytvoříme konfigurační soubor, pokud neexistuje
if not os.path.exists(CONFIG_FILE):
    default_config = [
        {
            "dag_id": "dynamic_dag_1",
            "schedule": "0 0 * * *",
            "source_type": "csv",
            "source_path": "/opt/airflow/project/data/source1.csv",
            "target_table": "table_1",
            "transform_type": "basic"
        },
        {
            "dag_id": "dynamic_dag_2",
            "schedule": "0 12 * * *",
            "source_type": "json",
            "source_path": "/opt/airflow/project/data/source2.json",
            "target_table": "table_2",
            "transform_type": "advanced"
        },
        {
            "dag_id": "dynamic_dag_3",
            "schedule": None,  # Manuální spouštění
            "source_type": "api",
            "source_path": "https://api.example.com/data",
            "target_table": "table_3",
            "transform_type": "custom"
        }
    ]
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(default_config, f, indent=2)

# Načtení konfigurace
with open(CONFIG_FILE, 'r') as f:
    dag_configs = json.load(f)

# Defaultní argumenty pro všechny DAGy
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Funkce pro získání zdroje dat
def get_data(source_type, source_path, **kwargs):
    print(f"Získávání dat z {source_type} zdroje: {source_path}")
    return f"Data získána z {source_path}"

# Funkce pro transformaci dat
def transform_data(transform_type, **kwargs):
    ti = kwargs['ti']
    task_id = kwargs['task'].task_id
    dag_id = kwargs['dag'].dag_id
    
    # Získání dat z předchozího tasku pomocí XCom
    data = ti.xcom_pull(task_ids=f"get_data_{dag_id}")
    
    print(f"Aplikace {transform_type} transformace na data: {data}")
    return f"Data transformována pomocí {transform_type} metody"

# Funkce pro načtení dat
def load_data(target_table, **kwargs):
    ti = kwargs['ti']
    task_id = kwargs['task'].task_id
    dag_id = kwargs['dag'].dag_id
    
    # Získání dat z předchozího tasku pomocí XCom
    transformed_data = ti.xcom_pull(task_ids=f"transform_data_{dag_id}")
    
    print(f"Načítání dat do tabulky {target_table}: {transformed_data}")
    return f"Data načtena do tabulky {target_table}"

# Dynamické vytvoření DAGů na základě konfigurace
for config in dag_configs:
    dag_id = config['dag_id']
    schedule = config['schedule']
    source_type = config['source_type']
    source_path = config['source_path']
    target_table = config['target_table']
    transform_type = config['transform_type']
    
    # Vytvoření DAGu
    dag = DAG(
        dag_id=dag_id,
        default_args=default_args,
        description=f'Dynamicky vygenerovaný DAG pro {source_type} data',
        schedule_interval=schedule,
        start_date=datetime(2025, 4, 18),
        catchup=False,
        tags=['dynamic', source_type],
    )
    
    # Definice tasků pro tento DAG
    with dag:
        # Task 1: Získání dat
        get_data_task = PythonOperator(
            task_id=f'get_data_{dag_id}',
            python_callable=get_data,
            op_kwargs={
                'source_type': source_type,
                'source_path': source_path
            },
        )
        
        # Task 2: Transformace dat
        transform_task = PythonOperator(
            task_id=f'transform_data_{dag_id}',
            python_callable=transform_data,
            op_kwargs={
                'transform_type': transform_type
            },
        )
        
        # Task 3: Načtení dat
        load_task = PythonOperator(
            task_id=f'load_data_{dag_id}',
            python_callable=load_data,
            op_kwargs={
                'target_table': target_table
            },
        )
        
        # Task 4: Úklid po dokončení
        cleanup_task = BashOperator(
            task_id=f'cleanup_{dag_id}',
            bash_command=f'echo "Úklid po zpracování DAGu {dag_id}" && date',
        )
        
        # Definice závislostí
        get_data_task >> transform_task >> load_task >> cleanup_task
    
    # Registrace DAGu v globálním namespace
    globals()[dag_id] = dag 
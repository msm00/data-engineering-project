"""
DAG demonstrující pokročilé koncepty Airflow:
- XComs pro komunikaci mezi úlohami
- Sensors pro čekání na podmínky
- Branching pro podmíněné zpracování
- Dynamická parametrizace
- Error handling a retry mechanismy
"""
from datetime import datetime, timedelta
import os
import json
import random
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.sensors.filesystem import FileSensor
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.dummy import DummyOperator
from airflow.models.param import Param
from airflow.utils.trigger_rule import TriggerRule

# Cesty k datům
DATA_DIR = '/opt/airflow/project/data'
SENSOR_FILE = os.path.join(DATA_DIR, 'sensor_data.json')

# Defaultní argumenty pro DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,  # Zvýšený počet retries pro demonstraci
    'retry_delay': timedelta(seconds=30),  # Kratší interval pro demo účely
}

# Zajistíme, že adresář existuje
os.makedirs(DATA_DIR, exist_ok=True)

# Definice DAG
with DAG(
    'advanced_concepts',
    default_args=default_args,
    description='DAG demonstrující pokročilé koncepty Airflow',
    schedule_interval=None,  # Pouze manuální spouštění
    start_date=datetime(2025, 4, 18),
    catchup=False,
    tags=['demo', 'advanced'],
    params={
        'data_source': Param('sensor', type='string', enum=['sensor', 'api', 'database']),
        'processing_level': Param(1, type='integer', minimum=1, maximum=3),
        'debug_mode': Param(False, type='boolean'),
    },
) as dag:

    # Task 1: Generování testovacích dat pro sensor
    def generate_sensor_data(**kwargs):
        """Generuje testovací JSON data pro sensor."""
        ti = kwargs['ti']
        data_source = kwargs['params']['data_source']
        debug_mode = kwargs['params']['debug_mode']
        
        # Přidáme trochu náhodnosti pro demonstraci branching
        temperature = round(random.uniform(15.0, 35.0), 1)
        humidity = round(random.uniform(30.0, 80.0), 1)
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'source': data_source,
            'readings': {
                'temperature': temperature,
                'humidity': humidity,
                'pressure': round(random.uniform(990, 1020), 1)
            },
            'metadata': {
                'device_id': 'SENSOR-' + str(random.randint(1000, 9999)),
                'location': random.choice(['Prague', 'Brno', 'Ostrava', 'Plzen']),
                'debug_mode': debug_mode
            }
        }
        
        # Uložení dat pro FileSensor
        with open(SENSOR_FILE, 'w') as f:
            json.dump(data, f, indent=2)
            
        # Předání dat pomocí XCom
        ti.xcom_push(key='sensor_data', value=data)
        ti.xcom_push(key='temperature', value=temperature)
        ti.xcom_push(key='humidity', value=humidity)
        
        print(f"Vygenerovaná data: {json.dumps(data, indent=2)}")
        return f"Data byla vygenerována: teplota={temperature}°C, vlhkost={humidity}%"
        
    generate_data_task = PythonOperator(
        task_id='generate_sensor_data',
        python_callable=generate_sensor_data,
    )
    
    # Task 2: Čekání na dostupnost dat pomocí FileSensor
    wait_for_data = FileSensor(
        task_id='wait_for_sensor_data',
        filepath=SENSOR_FILE,
        fs_conn_id=None,  # Používáme absolutní cestu
        poke_interval=5,  # Kontroluje každých 5 sekund
        timeout=60,  # Timeout po 60 sekundách
        mode='poke',  # Blokuje slot, dokud soubor neexistuje
    )
    
    # Task 3: Zpracování dat a branching na základě hodnot
    def process_data_and_branch(**kwargs):
        """Zpracovává data a rozhoduje o dalším postupu na základě hodnot."""
        ti = kwargs['ti']
        processing_level = kwargs['params']['processing_level']
        
        # Získání dat z XCom
        temperature = ti.xcom_pull(task_ids='generate_sensor_data', key='temperature')
        humidity = ti.xcom_pull(task_ids='generate_sensor_data', key='humidity')
        
        print(f"Zpracování dat: teplota={temperature}°C, vlhkost={humidity}%, úroveň={processing_level}")
        
        # Logika pro rozhodování
        if temperature > 30:
            return 'handle_high_temperature'
        elif humidity > 70:
            return 'handle_high_humidity'
        else:
            return 'handle_normal_conditions'
            
    process_and_branch = BranchPythonOperator(
        task_id='process_and_branch',
        python_callable=process_data_and_branch,
    )
    
    # Task 4a: Zpracování vysoké teploty
    handle_high_temp = BashOperator(
        task_id='handle_high_temperature',
        bash_command='echo "VAROVÁNÍ: Vysoká teplota detekována! Zpracování speciálního případu..." && sleep 2',
    )
    
    # Task 4b: Zpracování vysoké vlhkosti
    handle_high_humidity = BashOperator(
        task_id='handle_high_humidity',
        bash_command='echo "UPOZORNĚNÍ: Vysoká vlhkost detekována! Zpracování speciálního případu..." && sleep 2',
    )
    
    # Task 4c: Zpracování normálních podmínek
    handle_normal = BashOperator(
        task_id='handle_normal_conditions',
        bash_command='echo "INFO: Normální podmínky, standardní zpracování..." && sleep 2',
    )
    
    # Task 5: Demonstrace zpracování chyb
    def potentially_failing_task(**kwargs):
        """Task, který může selhat na základě náhody pro demonstraci retry mechanismu."""
        ti = kwargs['ti']
        debug_mode = kwargs['params']['debug_mode']
        
        # V debug režimu vždy uspěje
        if debug_mode:
            print("Debug režim aktivní, task vždy uspěje")
            return "Task úspěšně dokončen (debug režim)"
        
        # Jinak 30% šance na selhání
        if random.random() < 0.3:
            print("Simulace selhání tasku pro demonstraci retry mechanismu")
            raise Exception("Simulované selhání tasku")
        
        return "Task úspěšně dokončen"
    
    error_demo_task = PythonOperator(
        task_id='error_handling_demo',
        python_callable=potentially_failing_task,
        trigger_rule=TriggerRule.ONE_SUCCESS,  # Spustí se, pokud alespoň jeden z předchozích tasků uspěje
    )
    
    # Task 6: Spuštění jiného DAGu na základě výsledků
    trigger_etl_task = TriggerDagRunOperator(
        task_id='trigger_etl_pipeline',
        trigger_dag_id='etl_pipeline',
        conf={'test_mode': True},  # Předání parametrů do spouštěného DAGu
        reset_dag_run=True,
        wait_for_completion=True,
        poke_interval=10,
    )
    
    # Task 7: Závěrečný task, který se spustí vždy, bez ohledu na výsledek předchozích tasků
    final_task = DummyOperator(
        task_id='finalize_processing',
        trigger_rule=TriggerRule.ALL_DONE,  # Spustí se vždy, i když některé tasky selhaly
    )
    
    # Definice workflow
    generate_data_task >> wait_for_data >> process_and_branch
    process_and_branch >> [handle_high_temp, handle_high_humidity, handle_normal] >> error_demo_task
    error_demo_task >> trigger_etl_task >> final_task 
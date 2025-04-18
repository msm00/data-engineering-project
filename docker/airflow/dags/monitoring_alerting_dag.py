"""
DAG demonstrující monitorování a alerting v Airflow.
"""
from datetime import datetime, timedelta
import os
import json
import random
import logging
import time
from typing import Dict, Any

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.sensors.time_sensor import TimeSensor
from airflow.hooks.base import BaseHook
from airflow.models import Variable, TaskInstance
from airflow.utils.email import send_email
from airflow.utils.state import State

# Konfigurace loggeru
logger = logging.getLogger(__name__)

# Defaultní argumenty pro DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['admin@example.com'],  # Email pro notifikace
    'email_on_failure': True,  # Poslat email při selhání
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=1),
}

# Pomocná funkce pro simulaci chyby
def simulate_error(error_rate=0.3):
    if random.random() < error_rate:
        raise Exception("Simulovaná chyba pro demonstraci alertingu")

# Pomocná funkce pro odeslání vlastní notifikace
def send_custom_alert(context):
    """Odešle vlastní notifikaci při selhání tasku."""
    task_instance = context['task_instance']
    task_id = task_instance.task_id
    dag_id = task_instance.dag_id
    execution_date = context['execution_date']
    exception = context.get('exception')
    
    # Log do Airflow
    logger.error(f"Task {task_id} v DAGu {dag_id} selhal: {exception}")
    
    # Zde by byla implementace odeslání alertu např. do Slacku, SMS, nebo jiného systému
    alert_message = f"""
    ALERT: Task {task_id} selhal!
    DAG: {dag_id}
    Execution date: {execution_date}
    Error: {exception}
    """
    
    print(f"Odesílání alertu: {alert_message}")
    
    # Pokud máme nastavené proměnné pro Slack webhook
    # slack_webhook = Variable.get("slack_webhook_url", default_var=None)
    # if slack_webhook:
    #     Zde by se použil slack_webhook pro odeslání zprávy
    
    # Odeslání emailu (je nastaveno již v default_args)
    # send_email(
    #     to=default_args['email'],
    #     subject=f"Airflow Alert: Task {task_id} v DAGu {dag_id} selhal",
    #     html_content=alert_message.replace("\n", "<br>")
    # )

# Definice DAG
with DAG(
    'monitoring_and_alerting',
    default_args=default_args,
    description='DAG demonstrující monitorování a alerting v Airflow',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2025, 4, 18),
    catchup=False,
    tags=['monitoring', 'alerting'],
    on_failure_callback=send_custom_alert,  # Globální callback pro celý DAG
) as dag:
    
    # Task 1: Simulace dlouho běžícího tasku
    def long_running_task(**kwargs):
        """Simuluje dlouho běžící task s průběžným logováním."""
        logger.info("Začátek dlouho běžícího tasku")
        
        total_steps = 5
        for step in range(1, total_steps + 1):
            # Zaznamenání průběhu
            logger.info(f"Krok {step}/{total_steps} začíná")
            
            # Simulace práce
            time.sleep(2)
            
            # Log o procentu dokončení
            completion = (step / total_steps) * 100
            logger.info(f"Průběh: {completion:.1f}% dokončeno")
            
        logger.info("Dlouho běžící task úspěšně dokončen")
        return "Task dokončen"
        
    long_task = PythonOperator(
        task_id='long_running_task',
        python_callable=long_running_task,
    )
    
    # Task 2: Monitor využití systémových zdrojů
    resource_monitor = BashOperator(
        task_id='monitor_resources',
        bash_command='echo "CPU využití:" && top -b -n 1 | head -n 12 && echo "Využití paměti:" && free -h',
    )
    
    # Task 3: Task, který může selhat pro demonstraci alertingu
    def potential_failure_task(**kwargs):
        """Task, který může selhat pro demonstraci alertingu."""
        ti = kwargs['ti']
        
        logger.info("Začátek potenciálně nestabilního tasku")
        
        # Získáme hodnotu pravděpodobnosti selhání z dag run conf nebo použijeme výchozí
        dag_run_conf = kwargs.get('dag_run').conf or {}
        failure_rate = dag_run_conf.get('failure_rate', 0.5)  # 50% šance na selhání
        
        logger.info(f"Pravděpodobnost selhání: {failure_rate * 100}%")
        
        # Simulace chyby
        if random.random() < failure_rate:
            logger.error("Nastala chyba v tasku!")
            raise Exception("Simulovaná chyba pro testování alertingu")
        
        logger.info("Task úspěšně dokončen bez chyb")
        return "Úspěch"
    
    failure_task = PythonOperator(
        task_id='potential_failure',
        python_callable=potential_failure_task,
        # Vlastní callback pro tento konkrétní task
        on_failure_callback=send_custom_alert,
        # Nastavení retry strategie
        retries=3,
        retry_delay=timedelta(seconds=10),
        # Pokusy o restartování tasku budou exponenciálně klesat
        retry_exponential_backoff=True,
        max_retry_delay=timedelta(minutes=10),
    )
    
    # Task 4: Čekání na specifický čas (pro demonstraci TimeSensor)
    wait_time = TimeSensor(
        task_id='wait_until_specific_time',
        target_time=datetime.combine(
            datetime.today() + timedelta(days=1),  # zítra
            datetime.strptime('01:00:00', '%H:%M:%S').time()  # v 1:00 ráno
        ),
        poke_interval=60,  # kontrolovat každou minutu
    )
    
    # Task 5: Kontrola stavu databáze
    def check_database_status(**kwargs):
        """Kontroluje stav databáze a loguje výsledky."""
        logger.info("Kontrola stavu databáze")
        
        # Zde by byla implementace skutečné kontroly databáze
        # Například s použitím PostgresHook nebo jiného hooku
        
        # Simulace kontroly s náhodným výsledkem
        db_status = random.choice(['healthy', 'degraded', 'critical'])
        response_time = random.uniform(0.1, 2.0)
        
        # Logování výsledku
        if db_status == 'healthy':
            logger.info(f"Databáze je zdravá. Doba odezvy: {response_time:.2f}s")
        elif db_status == 'degraded':
            logger.warning(f"Výkon databáze je zhoršený. Doba odezvy: {response_time:.2f}s")
        else:
            logger.critical(f"Kritický stav databáze! Doba odezvy: {response_time:.2f}s")
            # Zde by bylo odeslání kritického alertu
            
        # Vrátíme data do XCom
        result = {
            'status': db_status,
            'response_time': response_time,
            'timestamp': datetime.now().isoformat()
        }
        
        return result
        
    db_check = PythonOperator(
        task_id='check_database',
        python_callable=check_database_status,
    )
    
    # Task 6: Generování monitorovacího reportu
    def generate_monitoring_report(**kwargs):
        """Generuje souhrnný monitorovací report ze všech předchozích tasků."""
        ti = kwargs['ti']
        
        # Získání výsledků z ostatních tasků pomocí XCom
        db_status = ti.xcom_pull(task_ids='check_database')
        
        # Sestavení reportu
        report = {
            'timestamp': datetime.now().isoformat(),
            'database_status': db_status,
            'tasks_status': {
                'long_running_task': ti.xcom_pull(task_ids='long_running_task'),
                'potential_failure': ti.xcom_pull(task_ids='potential_failure', default='Task selhal') 
            }
        }
        
        # Logování reportu
        logger.info(f"Monitoring report: {json.dumps(report, indent=2)}")
        
        # Zde by byla implementace uložení reportu nebo jeho odeslání
        
        return "Report vygenerován"
        
    report_task = PythonOperator(
        task_id='generate_report',
        python_callable=generate_monitoring_report,
        trigger_rule='all_done',  # Spustit i když některé předchozí tasky selhaly
    )
    
    # Definice workflow
    long_task >> resource_monitor >> failure_task
    [failure_task, db_check] >> report_task 
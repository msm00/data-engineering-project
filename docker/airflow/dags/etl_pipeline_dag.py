"""
DAG pro spuštění ETL pipeline pro načítání produktů z CSV do PostgreSQL.
"""
from datetime import datetime, timedelta
import os

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.bash import BashOperator


# Importy z našeho projektu (dostupné díky namountovanému volume v docker-compose.yml)
import sys
sys.path.append('/opt/airflow/project')

from src.etl.extract.csv_extractor import CSVExtractor
from src.etl.transform.basic_transformer import BasicTransformer
from src.etl.transform.advanced_transformer import AdvancedTransformer
from src.etl.load.postgres_loader import PostgresLoader


# Defaultní argumenty pro DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Parametry pro databázové připojení - použití host.docker.internal pro přístup k host machine
DB_PARAMS = {
    'host': 'host.docker.internal',  # Speciální DNS název pro přístup k host machine z kontejneru
    'port': 5432,  # Port, na kterém běží původní PostgreSQL
    'database': 'ecommerce',
    'user': 'postgres',
    'password': 'postgres',
}

# Cesty k datům
DATA_DIR = '/opt/airflow/project/data'
CSV_FILE = os.path.join(DATA_DIR, 'products.csv')

# Definice DAG
with DAG(
    'etl_pipeline',
    default_args=default_args,
    description='ETL pipeline pro produktová data',
    schedule_interval='0 2 * * *',  # Spuštění každý den ve 2:00 ráno
    start_date=datetime(2025, 4, 15),
    catchup=False,
    tags=['etl', 'products'],
) as dag:

    # Přidání parametrů pomocí param metody
    dag.param('db_host', default='host.docker.internal')
    dag.param('db_port', default=5432)
    dag.param('db_name', default='ecommerce')
    dag.param('db_user', default='postgres')
    dag.param('db_password', default='postgres')
    dag.param('test_mode', default=False)  # Přidán parametr test_mode bez specifikace typu

    # Task 1: Kontrola dostupnosti vstupních dat
    check_data = BashOperator(
        task_id='check_data',
        bash_command=f'ls -la {CSV_FILE}',
    )
    
    # Funkce pro extrakci dat
    def extract_data(**kwargs):
        """Extrahuje data z CSV souboru."""
        extractor = CSVExtractor(data_dir=DATA_DIR)
        data = extractor.extract(os.path.basename(CSV_FILE))
        
        # Předání dat do dalšího tasku přes XComs
        kwargs['ti'].xcom_push(key='extracted_data', value=data.to_json())
        return "Extrakce dokončena"
    
    # Task 2: Extrakce dat
    extract_task = PythonOperator(
        task_id='extract_data',
        python_callable=extract_data,
    )
    
    # Funkce pro základní transformaci dat
    def transform_basic(**kwargs):
        """Provede základní transformaci dat."""
        import pandas as pd
        
        # Získání dat z předchozího tasku
        ti = kwargs['ti']
        json_data = ti.xcom_pull(task_ids='extract_data', key='extracted_data')
        data = pd.read_json(json_data)
        
        # Transformace pomocí BasicTransformer
        transformer = BasicTransformer()
        
        # Aplikace základních transformací
        transformed_data = data.copy()
        transformed_data = transformer.clean_column_names(transformed_data)
        transformed_data = transformer.drop_duplicates(transformed_data)
        transformed_data = transformer.handle_missing_values(
            transformed_data, 
            strategy={
                'price': 'mean',
                'category': 'mode',
                'description': 'empty_string'
            }
        )
        
        # Předání dat do dalšího tasku
        kwargs['ti'].xcom_push(key='basic_transformed_data', value=transformed_data.to_json())
        return "Základní transformace dokončena"
    
    # Task 3: Základní transformace
    transform_basic_task = PythonOperator(
        task_id='transform_basic',
        python_callable=transform_basic,
    )
    
    # Funkce pro pokročilou transformaci dat
    def transform_advanced(**kwargs):
        """Provede pokročilou transformaci dat."""
        import pandas as pd
        
        # Získání dat z předchozího tasku
        ti = kwargs['ti']
        json_data = ti.xcom_pull(task_ids='transform_basic', key='basic_transformed_data')
        data = pd.read_json(json_data)
        
        # Transformace
        transformer = AdvancedTransformer()
        transformed_data = transformer.apply_transformations(data)
        
        # Převod boolean sloupce is_expensive na číselný typ (1.0 nebo 0.0)
        if 'is_expensive' in transformed_data.columns:
            transformed_data['is_expensive'] = transformed_data['is_expensive'].astype(float)
            print(f"Převedení sloupce is_expensive na typ: {transformed_data['is_expensive'].dtype}")
        
        # Předání dat do dalšího tasku
        kwargs['ti'].xcom_push(key='advanced_transformed_data', value=transformed_data.to_json())
        return "Pokročilá transformace dokončena"
    
    # Task 4: Pokročilá transformace
    transform_advanced_task = PythonOperator(
        task_id='transform_advanced',
        python_callable=transform_advanced,
    )
    
    # Funkce pro načtení dat do databáze
    def load_data(**kwargs):
        """Načte data do PostgreSQL databáze."""
        import pandas as pd
        
        # Získání dat z předchozího tasku
        ti = kwargs['ti']
        json_data = ti.xcom_pull(task_ids='transform_advanced', key='advanced_transformed_data')
        data = pd.read_json(json_data)
        
        # Získání parametru test_mode
        test_mode = kwargs['dag_run'].conf.get('test_mode', False) if kwargs['dag_run'].conf else False
        
        # Určení cílové tabulky podle režimu
        target_table = 'products_airflow_test' if test_mode else 'products_airflow'
        
        # Použití globálně definovaných parametrů
        loader = PostgresLoader(
            host=DB_PARAMS['host'],
            port=DB_PARAMS['port'],
            database=DB_PARAMS['database'],
            user=DB_PARAMS['user'],
            password=DB_PARAMS['password'],
        )
        
        # Načtení dat
        success = loader.load_data(
            df=data,
            table_name=target_table,
            if_exists='replace'
        )
        
        # Předání informace o cílové tabulce dalším taskům
        kwargs['ti'].xcom_push(key='target_table', value=target_table)
        
        if success:
            return f"Data úspěšně nahrána do tabulky {target_table}"
        else:
            raise Exception(f"Chyba při nahrávání dat do tabulky {target_table}")
    
    # Task 5: Načtení dat do databáze
    load_task = PythonOperator(
        task_id='load_data',
        python_callable=load_data,
    )
    
    # Task 6: Ověření načtení dat
    verify_task = PostgresOperator(
        task_id='verify_data',
        postgres_conn_id='postgres_default',
        sql="""
        SELECT COUNT(*) FROM {{ ti.xcom_pull(task_ids='load_data', key='target_table') }};
        """,
    )
    
    # Definice závislostí mezi tasky
    check_data >> extract_task >> transform_basic_task >> transform_advanced_task >> load_task >> verify_task 
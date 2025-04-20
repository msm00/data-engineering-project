"""
Komplexní ETL Pipeline pro obohacení produktových dat o kurzové informace.

Tento DAG:
1. Extrahuje produktová data z CSV souborů
2. Získává aktuální směnné kurzy z API
3. Obohacuje produktová data o ceny v různých měnách
4. Ukládá výsledky do PostgreSQL databáze
5. Generuje report a notifikace
"""
from datetime import datetime, timedelta
import os
import json
import pandas as pd
import logging
from typing import Dict, List, Any, Optional

from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.utils.trigger_rule import TriggerRule
from airflow.models.param import Param

# Importy z našeho projektu (dostupné díky namountovanému volume v docker-compose.yml)
import sys
sys.path.append('/opt/airflow/project')

from src.etl.extract.csv_extractor import CSVExtractor
from src.etl.extract.api_extractor import ApiExtractor
from src.etl.transform.basic_transformer import BasicTransformer
from src.etl.transform.currency_transformer import CurrencyTransformer
from src.etl.load.postgres_loader import PostgresLoader

# Konfigurace loggeru
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Defaultní argumenty pro DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'email': ['admin@example.com'],
    'retries': 2,
    'retry_delay': timedelta(minutes=1),
}

# Parametry pro databázové připojení - použití host.docker.internal pro přístup k host machine
DB_PARAMS = {
    'host': 'host.docker.internal',  # Speciální DNS název pro přístup k host machine z kontejneru
    'port': 5432,  # Port, na kterém běží PostgreSQL
    'database': 'ecommerce',
    'user': 'postgres',
    'password': 'postgres',
}

# Cesty k datům
DATA_DIR = '/opt/airflow/project/data'
PRODUCTS_CSV = os.path.join(DATA_DIR, 'products.csv')
CURRENCY_API_BASE_URL = 'https://api.exchangerate.host'  # Veřejné API pro směnné kurzy

# Cílové měny pro převod
TARGET_CURRENCIES = ['USD', 'CZK', 'GBP', 'JPY']

# Definice DAG
with DAG(
    'currency_enriched_etl',
    default_args=default_args,
    description='Komplexní ETL Pipeline pro obohacení produktových dat o kurzové informace',
    schedule_interval='0 8 * * *',  # Spouští se každý den v 8:00
    start_date=datetime(2025, 4, 19),
    catchup=False,
    tags=['production', 'etl', 'currency'],
    params={
        'base_currency': Param('EUR', type='string'),
        'target_currencies': Param(TARGET_CURRENCIES, type='array'),
        'data_validation': Param('basic', type='string', enum=['none', 'basic', 'strict']),
        'output_table': Param('products_with_currency', type='string'),
        'notification_emails': Param(['admin@example.com'], type='array'),
        'api_cache_enabled': Param(True, type='boolean'),
    },
) as dag:
    
    # Task 1: Start pipeline
    start_pipeline = DummyOperator(task_id='start_pipeline')
    
    # Task 2: Kontrola dostupnosti vstupních dat
    def check_input_files(**kwargs):
        """Kontroluje dostupnost vstupních souborů."""
        # Kontrola existence souboru s produkty
        if not os.path.exists(PRODUCTS_CSV):
            raise FileNotFoundError(f"Soubor s produkty nenalezen: {PRODUCTS_CSV}")
            
        # Vrácení informací o souboru
        file_size = os.path.getsize(PRODUCTS_CSV)
        file_size_mb = file_size / (1024 * 1024)
        
        # Počet řádků v souboru
        line_count = sum(1 for _ in open(PRODUCTS_CSV))
        
        logger.info(f"Soubor s produkty nalezen: {PRODUCTS_CSV}")
        logger.info(f"Velikost: {file_size_mb:.2f} MB, počet řádků: {line_count}")
        
        # Uložíme informace o souboru do XCom
        kwargs['ti'].xcom_push(key='products_file_info', value={
            'path': PRODUCTS_CSV,
            'size_mb': file_size_mb,
            'line_count': line_count
        })
        
        return "Kontrola vstupních souborů úspěšná"
    
    check_files_task = PythonOperator(
        task_id='check_input_files',
        python_callable=check_input_files,
    )
    
    # Task 3: Extrakce produktových dat z CSV
    def extract_products(**kwargs):
        """Extrahuje produktová data z CSV souboru."""
        try:
            # Inicializace extraktoru
            extractor = CSVExtractor(data_dir=DATA_DIR)
            
            # Extrakce dat z CSV souboru
            products_df = extractor.extract(os.path.basename(PRODUCTS_CSV))
            
            # Log počtu načtených záznamů
            logger.info(f"Načteno {len(products_df)} produktů z CSV")
            
            # Uložení do XCom
            kwargs['ti'].xcom_push(key='products_data', value=products_df.to_json())
            
            return f"Extrakce produktů úspěšná: {len(products_df)} záznamů"
        except Exception as e:
            logger.error(f"Chyba při extrakci produktů: {str(e)}")
            raise
    
    extract_products_task = PythonOperator(
        task_id='extract_products',
        python_callable=extract_products,
    )
    
    # Task 4: Extrakce směnných kurzů z API
    def extract_currency_rates(**kwargs):
        """Získává aktuální směnné kurzy z API."""
        try:
            # Získání parametrů
            base_currency = kwargs['params']['base_currency']
            api_cache_enabled = kwargs['params']['api_cache_enabled']
            
            # Inicializace API extraktoru
            cache_dir = os.path.join(DATA_DIR, 'cache') if api_cache_enabled else None
            api_extractor = ApiExtractor(base_url=CURRENCY_API_BASE_URL, cache_dir=cache_dir)
            
            # Extrakce kurzů
            currency_rates = api_extractor.extract_currency_rates(base_currency=base_currency)
            
            # Log počtu získaných kurzů
            logger.info(f"Získáno {len(currency_rates)} kurzů měn s bází {base_currency}")
            
            # Uložení do XCom
            kwargs['ti'].xcom_push(key='currency_rates', value=currency_rates)
            
            return f"Extrakce kurzů měn úspěšná: {len(currency_rates)} měn"
        except Exception as e:
            logger.error(f"Chyba při extrakci kurzů měn: {str(e)}")
            raise
    
    extract_currency_task = PythonOperator(
        task_id='extract_currency_rates',
        python_callable=extract_currency_rates,
    )
    
    # Task 5: Základní transformace produktových dat
    def transform_products_basic(**kwargs):
        """Provádí základní transformaci produktových dat."""
        try:
            # Získání dat z XCom
            ti = kwargs['ti']
            products_json = ti.xcom_pull(task_ids='extract_products', key='products_data')
            products_df = pd.read_json(products_json)
            
            # Inicializace transformátoru
            transformer = BasicTransformer()
            
            # Aplikace základních transformací
            transformed_df = products_df.copy()
            
            # Čištění názvů sloupců
            transformed_df = transformer.clean_column_names(transformed_df)
            
            # Odstranění duplicit
            transformed_df = transformer.drop_duplicates(transformed_df)
            
            # Ošetření chybějících hodnot
            transformed_df = transformer.handle_missing_values(
                transformed_df, 
                strategy={
                    'price': 'mean',
                    'category': 'mode',
                    'description': 'empty_string'
                }
            )
            
            # Log o transformaci
            logger.info(f"Základní transformace dokončena: {len(transformed_df)} záznamů")
            
            # Uložení do XCom
            ti.xcom_push(key='basic_transformed_data', value=transformed_df.to_json())
            
            return f"Základní transformace dokončena: {len(transformed_df)} záznamů"
        except Exception as e:
            logger.error(f"Chyba při základní transformaci: {str(e)}")
            raise
    
    transform_basic_task = PythonOperator(
        task_id='transform_products_basic',
        python_callable=transform_products_basic,
    )
    
    # Task 6: Rozhodnutí o úrovni validace
    def branch_validation(**kwargs):
        """Rozhoduje o cestě pro validaci dat na základě parametru."""
        validation_level = kwargs['params']['data_validation']
        
        if validation_level == 'none':
            return 'skip_validation'
        elif validation_level == 'basic':
            return 'validate_data_basic'
        else:  # strict
            return 'validate_data_strict'
    
    validation_branch = BranchPythonOperator(
        task_id='branch_validation',
        python_callable=branch_validation,
    )
    
    # Task 7a: Přeskočení validace
    skip_validation = DummyOperator(task_id='skip_validation')
    
    # Task 7b: Základní validace dat
    def validate_data_basic(**kwargs):
        """Provádí základní validaci dat."""
        try:
            # Získání dat z XCom
            ti = kwargs['ti']
            products_json = ti.xcom_pull(task_ids='transform_products_basic', key='basic_transformed_data')
            products_df = pd.read_json(products_json)
            
            # Základní validace
            validation_errors = []
            
            # Kontrola, že ceny jsou kladné
            negative_prices = products_df[products_df['price'] < 0]
            if not negative_prices.empty:
                validation_errors.append(f"Nalezeno {len(negative_prices)} produktů se zápornou cenou")
            
            # Kontrola, že kategorie nejsou prázdné
            empty_categories = products_df[products_df['category'].isna() | (products_df['category'] == '')]
            if not empty_categories.empty:
                validation_errors.append(f"Nalezeno {len(empty_categories)} produktů s prázdnou kategorií")
            
            # Log výsledku validace
            if validation_errors:
                error_msg = "\n - ".join(["Validační chyby:"] + validation_errors)
                logger.warning(error_msg)
                
                # Uložení chyb do XCom
                ti.xcom_push(key='validation_errors', value=validation_errors)
                
                # Nezastavujeme pipeline při základní validaci, pouze logujeme chyby
                return f"Základní validace dokončena s {len(validation_errors)} chybami"
            else:
                logger.info("Základní validace úspěšná, žádné chyby nenalezeny")
                return "Základní validace úspěšná"
        except Exception as e:
            logger.error(f"Chyba při základní validaci: {str(e)}")
            raise
    
    validate_basic_task = PythonOperator(
        task_id='validate_data_basic',
        python_callable=validate_data_basic,
    )
    
    # Task 7c: Striktní validace dat
    def validate_data_strict(**kwargs):
        """Provádí striktní validaci dat s přísnějšími pravidly."""
        try:
            # Získání dat z XCom
            ti = kwargs['ti']
            products_json = ti.xcom_pull(task_ids='transform_products_basic', key='basic_transformed_data')
            products_df = pd.read_json(products_json)
            
            # Striktní validace
            validation_errors = []
            
            # Kontrola, že ceny jsou kladné a v rozumném rozsahu
            price_issues = products_df[(products_df['price'] <= 0) | (products_df['price'] > 10000)]
            if not price_issues.empty:
                validation_errors.append(f"Nalezeno {len(price_issues)} produktů s podezřelou cenou")
            
            # Kontrola, že všechny produkty mají neprázdné názvy
            name_issues = products_df[products_df['product_name'].isna() | (products_df['product_name'].str.len() < 3)]
            if not name_issues.empty:
                validation_errors.append(f"Nalezeno {len(name_issues)} produktů s chybějícím nebo příliš krátkým názvem")
            
            # Kontrola, že všechny produkty mají validní kategorii
            valid_categories = ['Electronics', 'Home Appliances', 'Sports', 'Home Decor', 'Clothing']
            category_issues = products_df[~products_df['category'].isin(valid_categories)]
            if not category_issues.empty:
                validation_errors.append(f"Nalezeno {len(category_issues)} produktů s neplatnou kategorií")
            
            # Log výsledku validace
            if validation_errors:
                error_msg = "\n - ".join(["Validační chyby (striktní režim):"] + validation_errors)
                logger.error(error_msg)
                
                # Uložení chyb do XCom
                ti.xcom_push(key='validation_errors', value=validation_errors)
                
                # Ve striktním režimu zastavíme pipeline při chybách
                raise ValueError(f"Striktní validace selhala s {len(validation_errors)} chybami")
            else:
                logger.info("Striktní validace úspěšná, žádné chyby nenalezeny")
                return "Striktní validace úspěšná"
        except Exception as e:
            logger.error(f"Chyba při striktní validaci: {str(e)}")
            raise
    
    validate_strict_task = PythonOperator(
        task_id='validate_data_strict',
        python_callable=validate_data_strict,
    )
    
    # Task 8: Join po validaci
    join_after_validation = DummyOperator(
        task_id='join_after_validation',
        trigger_rule=TriggerRule.ONE_SUCCESS  # Pokračujeme, pokud alespoň jedna validace byla úspěšná
    )
    
    # Task 9: Obohacení produktů o kurzové informace
    def enrich_products_with_currency(**kwargs):
        """Obohacuje produktová data o ceny v různých měnách."""
        try:
            # Získání dat z XCom
            ti = kwargs['ti']
            products_json = ti.xcom_pull(task_ids='transform_products_basic', key='basic_transformed_data')
            products_df = pd.read_json(products_json)
            currency_rates = ti.xcom_pull(task_ids='extract_currency_rates', key='currency_rates')
            
            # Získání parametrů
            base_currency = kwargs['params']['base_currency']
            requested_currencies = kwargs['params']['target_currencies']
            
            # Inicializace transformátoru
            transformer = EnhancedCurrencyTransformer(currency_rates=currency_rates, base_currency=base_currency)
            
            # Filtrování dostupných měn
            available_currencies = list(currency_rates.keys())
            logger.info(f"Dostupné měny z API: {available_currencies}")
            
            # Filtrovat pouze dostupné měny
            target_currencies = [currency for currency in requested_currencies if currency in available_currencies]
            
            # Ověřit, zda máme alespoň jednu měnu k dispozici
            if not target_currencies:
                logger.warning(f"Žádná z požadovaných měn {requested_currencies} není dostupná. Použijeme pouze základní měnu {base_currency}.")
                target_currencies = [base_currency]
            else:
                logger.info(f"Použité měny pro převod: {target_currencies}")
            
            # Transformace dat
            enriched_df = transformer.transform(
                df=products_df, 
                price_column='price', 
                target_currencies=target_currencies,
                add_currency_metadata=True
            )
            
            # Log o transformaci
            new_columns = len(enriched_df.columns) - len(products_df.columns)
            logger.info(f"Obohacení o kurzové informace dokončeno: {len(enriched_df)} záznamů, {new_columns} nových sloupců")
            
            # Uložení do XCom
            ti.xcom_push(key='enriched_data', value=enriched_df.to_json())
            
            return f"Obohacení dat o kurzové informace dokončeno"
        except Exception as e:
            logger.error(f"Chyba při obohacování dat o kurzové informace: {str(e)}")
            raise
    
    enrich_currency_task = PythonOperator(
        task_id='enrich_products_with_currency',
        python_callable=enrich_products_with_currency,
    )
    
    # Task 10: Uložení dat do databáze
    def load_to_postgres(**kwargs):
        """Ukládá obohacená data do PostgreSQL databáze."""
        try:
            # Získání dat z XCom
            ti = kwargs['ti']
            enriched_json = ti.xcom_pull(task_ids='enrich_products_with_currency', key='enriched_data')
            enriched_df = pd.read_json(enriched_json)
            
            # Získání parametrů
            output_table = kwargs['params']['output_table']
            
            # Inicializace loaderu
            loader = PostgresLoader(
                host=DB_PARAMS['host'],
                port=DB_PARAMS['port'],
                database=DB_PARAMS['database'],
                user=DB_PARAMS['user'],
                password=DB_PARAMS['password'],
            )
            
            # Uložení dat do databáze
            loader.load_data(
                df=enriched_df,
                table_name=output_table,
                if_exists='replace'  # Nahradíme existující tabulku
            )
            
            # Log o uložení
            logger.info(f"Data úspěšně uložena do tabulky {output_table}: {len(enriched_df)} záznamů")
            
            # Uložíme název tabulky do XCom pro ověření
            ti.xcom_push(key='output_table', value=output_table)
            
            return f"Data úspěšně uložena do {output_table}"
        except Exception as e:
            logger.error(f"Chyba při ukládání dat do PostgreSQL: {str(e)}")
            raise
    
    load_postgres_task = PythonOperator(
        task_id='load_to_postgres',
        python_callable=load_to_postgres,
    )
    
    # Task 11: Ověření nahrání dat
    def verify_data_loaded(**kwargs):
        """Ověřuje, že data byla úspěšně nahrána do databáze."""
        try:
            # Získání názvu tabulky z XCom
            ti = kwargs['ti']
            output_table = ti.xcom_pull(task_ids='load_to_postgres', key='output_table')
            
            # Použijeme přímo psycopg2 pro vytvoření spojení místo spoléhání na metody PostgresLoaderu
            import psycopg2
            conn = psycopg2.connect(
                host=DB_PARAMS['host'],
                port=DB_PARAMS['port'],
                database=DB_PARAMS['database'],
                user=DB_PARAMS['user'],
                password=DB_PARAMS['password']
            )
            
            # Ověření počtu záznamů přímým SQL dotazem
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {output_table}")
            row_count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            # Log o ověření
            logger.info(f"Ověření dokončeno: tabulka {output_table} obsahuje {row_count} záznamů")
            
            # Uložení počtu záznamů do XCom
            ti.xcom_push(key='row_count', value=row_count)
            
            return f"Ověření úspěšné: {row_count} záznamů"
        except Exception as e:
            logger.error(f"Chyba při ověřování dat: {str(e)}")
            raise
    
    verify_data_task = PythonOperator(
        task_id='verify_data_loaded',
        python_callable=verify_data_loaded,
    )
    
    # Task 12: Generování reportu
    def generate_report(**kwargs):
        """Generuje report o průběhu ETL procesu."""
        try:
            # Získání dat z XCom
            ti = kwargs['ti']
            
            # Informace o vstupním souboru
            file_info = ti.xcom_pull(task_ids='check_input_files', key='products_file_info')
            
            # Počet záznamů v databázi
            row_count = ti.xcom_pull(task_ids='verify_data_loaded', key='row_count')
            
            # Validační chyby, pokud existují
            validation_errors = ti.xcom_pull(task_ids=['validate_data_basic', 'validate_data_strict'], key='validation_errors')
            
            # Získání parametrů
            base_currency = kwargs['params']['base_currency']
            target_currencies = kwargs['params']['target_currencies']
            output_table = kwargs['params']['output_table']
            
            # Sestavení reportu
            report = {
                'timestamp': datetime.now().isoformat(),
                'input_file': {
                    'path': file_info.get('path') if file_info else 'N/A',
                    'size_mb': file_info.get('size_mb') if file_info else 'N/A',
                    'line_count': file_info.get('line_count') if file_info else 'N/A',
                },
                'currencies': {
                    'base_currency': base_currency,
                    'target_currencies': target_currencies,
                },
                'output': {
                    'table': output_table,
                    'row_count': row_count,
                },
                'validation': {
                    'errors': validation_errors if validation_errors else [],
                    'error_count': len(validation_errors) if validation_errors else 0,
                    'status': 'OK' if not validation_errors else 'WARNING'
                },
                'status': 'SUCCESS'
            }
            
            # Uložení reportu do souboru
            report_path = os.path.join(DATA_DIR, f'etl_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            # Log o reportu
            logger.info(f"Report vygenerován a uložen do: {report_path}")
            
            # Uložení reportu do XCom
            ti.xcom_push(key='report', value=report)
            ti.xcom_push(key='report_path', value=report_path)
            
            return f"Report vygenerován: {report_path}"
        except Exception as e:
            logger.error(f"Chyba při generování reportu: {str(e)}")
            raise
    
    generate_report_task = PythonOperator(
        task_id='generate_report',
        python_callable=generate_report,
        trigger_rule=TriggerRule.ALL_DONE  # Spustí se bez ohledu na výsledek předchozích tasků
    )
    
    # Task 13: Konec pipeline
    end_pipeline = DummyOperator(
        task_id='end_pipeline',
        trigger_rule=TriggerRule.ALL_DONE  # Spustí se bez ohledu na výsledek předchozích tasků
    )
    
    # Definice workflow
    start_pipeline >> check_files_task
    check_files_task >> [extract_products_task, extract_currency_task]
    extract_products_task >> transform_basic_task >> validation_branch
    validation_branch >> [skip_validation, validate_basic_task, validate_strict_task]
    [skip_validation, validate_basic_task, validate_strict_task] >> join_after_validation
    [join_after_validation, extract_currency_task] >> enrich_currency_task
    enrich_currency_task >> load_postgres_task >> verify_data_task
    verify_data_task >> generate_report_task >> end_pipeline 

# Inline úprava CurrencyTransformer pro zajištění kompatibility s API
# Vytvoříme vlastní odvozenou třídu s upraveným chováním
class EnhancedCurrencyTransformer(CurrencyTransformer):
    """Rozšířená třída CurrencyTransformer, která je tolerantnější k chybějícím měnám."""
    
    def enrich_products_with_currency_prices(self, 
                                         df: pd.DataFrame, 
                                         price_column: str = 'price', 
                                         target_currencies: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Obohatí DataFrame produktů o ceny v různých měnách.
        
        Args:
            df: DataFrame s produkty
            price_column: Název sloupce s cenou v základní měně
            target_currencies: Seznam cílových měn pro převod (None = všechny dostupné měny)
            
        Returns:
            DataFrame obohacený o ceny v různých měnách
        """
        if price_column not in df.columns:
            raise ValueError(f"Sloupec '{price_column}' neexistuje v DataFrame")
        
        # Pokud nejsou specifikovány cílové měny, použijeme všechny dostupné
        if target_currencies is None:
            target_currencies = list(self.currency_rates.keys())
        else:
            # Filtrujeme pouze dostupné měny, místo vyvolání výjimky
            available_currencies = list(self.currency_rates.keys())
            original_count = len(target_currencies)
            target_currencies = [currency for currency in target_currencies if currency in self.currency_rates]
            
            if not target_currencies:
                logger.warning(f"Žádná z požadovaných měn není dostupná. Použijeme pouze základní měnu {self.base_currency}")
                target_currencies = [self.base_currency]
            elif len(target_currencies) < original_count:
                logger.warning(f"Některé požadované měny nejsou dostupné. Použijeme pouze: {target_currencies}")
        
        # Vytvoření kopie DataFrame pro manipulaci
        result_df = df.copy()
        
        # Přidání sloupce s označením původní měny
        currency_col_name = f"{price_column}_currency"
        result_df[currency_col_name] = self.base_currency
        
        # Přidání sloupců s cenami v různých měnách
        for currency in target_currencies:
            if currency == self.base_currency:
                continue  # Přeskočíme základní měnu
                
            new_col_name = f"{price_column}_{currency}"
            
            # Použití vectorizované operace pro rychlý výpočet s bezpečným získáním hodnoty
            result_df[new_col_name] = (df[price_column] * self.currency_rates.get(currency, 1.0)).round(2)
            
            logger.debug(f"Přidán sloupec {new_col_name}")
        
        logger.info(f"DataFrame obohacen o ceny v {len(target_currencies)} měnách")
        return result_df
    
    def transform(self, df: pd.DataFrame, price_column: str = 'price', 
                 target_currencies: Optional[List[str]] = None,
                 add_currency_metadata: bool = True) -> pd.DataFrame:
        """
        Hlavní transformační metoda - obohatí data o měnové informace.
        Překrytí původní metody pro lepší odolnost vůči chybějícím měnám.
        
        Args:
            df: DataFrame s produkty
            price_column: Název sloupce s cenou v základní měně
            target_currencies: Seznam cílových měn pro převod (None = všechny dostupné měny)
            add_currency_metadata: Zda přidat metadata o měnách
            
        Returns:
            Transformovaný DataFrame
        """
        logger.info(f"Začátek transformace produktů s měnovými informacemi: {len(df)} záznamů")
        
        # Ověření, že DataFrame není prázdný
        if df.empty:
            logger.warning("Vstupní DataFrame je prázdný, transformace přeskočena")
            return df
            
        # Ověření, že cenový sloupec existuje a má správný datový typ
        if price_column not in df.columns:
            raise ValueError(f"Sloupec '{price_column}' neexistuje v DataFrame")
            
        # Zkusíme převést cenový sloupec na float, pokud ještě není
        try:
            df[price_column] = df[price_column].astype(float)
        except Exception as e:
            logger.error(f"Nepodařilo se převést sloupec '{price_column}' na float: {str(e)}")
            raise
        
        # Aplikovat transformace - použití naší vylepšené metody
        result_df = self.enrich_products_with_currency_prices(df, price_column, target_currencies)
        
        # Přidat metadata, pokud je to požadováno
        if add_currency_metadata:
            result_df = self.add_currency_info(result_df)
        
        logger.info(f"Transformace dokončena: {len(result_df)} záznamů, nové sloupce: {len(result_df.columns) - len(df.columns)}")
        return result_df 
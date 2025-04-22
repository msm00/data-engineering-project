# Best Practices pro Apache Spark

Tento dokument shrnuje osvědčené postupy a doporučení pro efektivní práci s Apache Spark v rámci našeho Spark-Airflow-Postgres stacku.

## 1. Optimalizace výkonu

### Partitioning
- Vždy používejte vhodný počet partitions podle velikosti dat a dostupných zdrojů
- Používejte `repartition()` pro zvýšení paralelismu, `coalesce()` pro jeho snížení
- Implementujte partitioning na základě sloupců, které se často používají ve filtrech a join operacích

```python
# Špatně - příliš málo partitions pro velký dataset
df = spark.read.parquet("/data/large_dataset.parquet")

# Správně - nastavení vhodného počtu partitions
df = spark.read.parquet("/data/large_dataset.parquet").repartition(100)

# Efektivní partitioning podle často používaného sloupce
df.write.partitionBy("date").parquet("/data/output/")
```

### Caching a persistence
- Používejte `cache()` nebo `persist()` pro datasety, které se opakovaně používají
- Volte správnou úroveň persistence podle paměťových nároků a charakteru úlohy
- Vždy uvolňujte cache pomocí `unpersist()`, když ji již nepotřebujete

```python
# Vhodné použití cache pro opakovaně použitý dataset
filtered_df = large_df.filter(col("value") > 100).cache()

# Provést několik operací nad cached dataframe
result1 = filtered_df.groupBy("category").count()
result2 = filtered_df.select("id", "value").filter(col("id") > 1000)

# Uvolnit cache, když už ji nepotřebujeme
filtered_df.unpersist()
```

### Optimalizace Shuffle operací
- Minimalizujte počet shuffle operací v pipeline
- Používejte broadcast joins pro malé tabulky
- Sledujte a optimalizujte operace, které způsobují shuffle:
  - `join`, `groupByKey`, `reduceByKey`, `repartition`

```python
# Broadcast join pro malou tabulku
from pyspark.sql.functions import broadcast
result = large_df.join(broadcast(small_df), "join_key")

# Použití map-side aggregace pro snížení dat přenášených při shuffle
from pyspark.sql.functions import count, sum
df.groupBy("key").agg(count("*"), sum("value"))
```

## 2. Správa a monitoring zdrojů

### Konfigurace Spark aplikace
- Nastavujte správně paměť a počet executorů podle charakteru úlohy a dostupných zdrojů
- Používejte dynamickou alokaci zdrojů v clusterovém prostředí
- Monitorujte využití zdrojů pomocí Spark UI

```bash
# Příklad konfigurace pro Spark submit
spark-submit \
  --master yarn \
  --deploy-mode cluster \
  --num-executors 10 \
  --executor-memory 4g \
  --executor-cores 2 \
  --conf spark.dynamicAllocation.enabled=true \
  --conf spark.dynamicAllocation.minExecutors=5 \
  --conf spark.dynamicAllocation.maxExecutors=20 \
  app.py
```

### Checkpoint a recovery
- Implementujte checkpointing pro dlouhotrvající aplikace a streaming úlohy
- Nastavte vhodné umístění pro checkpoint data

```python
# Nastavení checkpoint directory
sc.setCheckpointDir("hdfs:///checkpoint/directory")

# Použití checkpointu v pipeline
complex_rdd = input_rdd.map(...).filter(...).groupBy(...)
complex_rdd.checkpoint()
```

## 3. Datové formáty a schema management

### Optimální formáty
- Preferujte sloupcové formáty (Parquet, ORC) před řádkovými (CSV, JSON)
- Používejte kompresi (Snappy, GZip) podle potřeby poměru komprese/výkonu

```python
# Ukládání dat v optimálním formátu
df.write.mode("overwrite") \
  .option("compression", "snappy") \
  .parquet("/data/output/")
```

### Schema management
- Vždy explicitně definujte schema místo použití inferSchema
- Implementujte schema evoluce a migrace
- Dokumentujte změny schématu

```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

# Explicitní definice schématu
schema = StructType([
    StructField("id", IntegerType(), False),
    StructField("name", StringType(), True),
    StructField("value", IntegerType(), True)
])

df = spark.read.schema(schema).csv("/data/input.csv")
```

## 4. Error handling a validace dat

### Validace vstupních dat
- Vždy validujte vstupní data před zpracováním
- Implementujte data quality checks jako součást pipeline

```python
# Základní validace dat
def validate_df(df, min_rows=1):
    row_count = df.count()
    if row_count < min_rows:
        raise ValueError(f"DataFrame obsahuje pouze {row_count} řádků, očekáváno minimálně {min_rows}")
    
    # Kontrola null hodnot v klíčových sloupcích
    null_counts = df.select([count(when(col(c).isNull(), c)).alias(c) for c in df.columns]).collect()[0]
    for col_name in ["id", "timestamp", "value"]:
        if col_name in null_counts and null_counts[col_name] > 0:
            raise ValueError(f"Sloupec {col_name} obsahuje {null_counts[col_name]} null hodnot")
```

### Error handling
- Implementujte robustní error handling
- Logujte detaily chyb
- Zvažte implementaci "dead letter queue" pro nevalidní záznamy

```python
from pyspark.sql.functions import col, udf
from pyspark.sql.types import BooleanType
import logging

# UDF pro validaci dat s error handlingem
def validate_record(id, value):
    try:
        if id > 0 and value is not None:
            return True
        return False
    except Exception as e:
        logging.error(f"Chyba při validaci záznamu: {e}")
        return False

validate_udf = udf(validate_record, BooleanType())

# Separace validních a nevalidních záznamů
valid_records = df.filter(validate_udf(col("id"), col("value")))
invalid_records = df.filter(~validate_udf(col("id"), col("value")))

# Zpracování validních záznamů
valid_result = valid_records.groupBy("category").count()

# Uložení nevalidních záznamů pro pozdější analýzu
invalid_records.write.mode("append").parquet("/data/errors/invalid_records")
```

## 5. Integrace s Airflow

### Parametrizace Spark jobů
- Všechny Spark joby by měly být parametrizovatelné pro flexibilní použití v DAGu
- Používejte argparse nebo podobné knihovny pro předávání parametrů

```python
# V Spark skriptu
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--input_path", required=True, help="Input data path")
parser.add_argument("--output_path", required=True, help="Output data path")
parser.add_argument("--run_date", required=True, help="Processing date (YYYY-MM-DD)")
parser.add_argument("--filter_value", type=int, default=100, help="Filter threshold")

args = parser.parse_args()

# Použití parametrů
df = spark.read.parquet(args.input_path)
filtered_df = df.filter(col("value") > args.filter_value)
filtered_df.write.parquet(f"{args.output_path}/{args.run_date}")
```

```python
# V Airflow DAGu
spark_task = SparkSubmitOperator(
    task_id='process_data',
    application='/path/to/script.py',
    application_args=[
        '--input_path', '/data/input/{{ ds }}',
        '--output_path', '/data/output',
        '--run_date', '{{ ds }}',
        '--filter_value', '{{ params.filter_value }}'
    ],
    conf={'spark.executor.memory': '4g'},
    dag=dag
)
```

### Monitoring Spark úloh z Airflow
- Implementujte callback mechanismy pro hlášení stavu Spark úloh
- Ukládejte metriky výkonu a statistiky pro každý běh

```python
# V Airflow DAGu
def _process_spark_metrics(**context):
    """Zpracování metrik ze Spark jobu po jeho dokončení"""
    task_instance = context['task_instance']
    spark_app_id = task_instance.xcom_pull(task_ids='spark_job', key='application_id')
    
    # Zde můžete implementovat logiku pro získání a zpracování metrik
    # například pomocí Spark REST API nebo přímého přístupu k Spark History Server
    
    # Uložení metrik do XCom nebo externí databáze
    task_instance.xcom_push(key='job_metrics', value={
        'app_id': spark_app_id,
        'duration': 120,  # v sekundách
        'records_processed': 10000,
        'memory_used': '3.5 GB'
    })

process_metrics = PythonOperator(
    task_id='process_metrics',
    python_callable=_process_spark_metrics,
    provide_context=True,
    dag=dag
)

spark_job >> process_metrics
```

## 6. Testování Spark aplikací

### Unit testy
- Pište unit testy pro všechny transformace
- Používejte `pyspark.testing` pro testování transformací dat

```python
import unittest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
import your_module

class TestSparkTransformations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder \
            .master("local[2]") \
            .appName("SparkUnitTest") \
            .getOrCreate()
    
    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()
    
    def test_filter_transformation(self):
        # Vytvoření testovacího DataFrame
        schema = StructType([
            StructField("id", IntegerType(), False),
            StructField("value", IntegerType(), True)
        ])
        
        test_data = [(1, 100), (2, 50), (3, 200)]
        input_df = self.spark.createDataFrame(test_data, schema)
        
        # Aplikace testované transformace
        result_df = your_module.filter_high_values(input_df, threshold=100)
        
        # Ověření výsledku
        expected_data = [(1, 100), (3, 200)]
        expected_df = self.spark.createDataFrame(expected_data, schema)
        
        self.assertEqual(result_df.count(), 2)
        self.assertEqual(result_df.collect(), expected_df.collect())

if __name__ == "__main__":
    unittest.main()
```

### End-to-end testy
- Implementujte E2E testy pro celé Spark aplikace
- Používejte testovací data a prostředí podobné produkčnímu

## 7. Bezpečnost a compliance

### Správa citlivých dat
- Implementujte šifrování citlivých dat
- Dodržujte zásady pro manipulaci s různými úrovněmi citlivosti dat
- Implementujte masking a anonymizaci dat

```python
from pyspark.sql.functions import sha2, concat_ws

# Anonymizace PII dat
def anonymize_pii(df):
    return df.withColumn("hashed_email", sha2(col("email"), 256)) \
             .withColumn("hashed_name", sha2(concat_ws("", col("first_name"), col("last_name")), 256)) \
             .drop("email", "first_name", "last_name")
```

### Logování a audit
- Implementujte detailní logování všech operací
- Ukládejte auditní záznamy o přístupu k datům a prováděných operacích

```python
import logging
from datetime import datetime

# Inicializace loggeru
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"/logs/spark_job_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SparkJob")

# Logování operací
logger.info(f"Začátek zpracování datasetu: {input_path}")
logger.info(f"Počet vstupních záznamů: {df.count()}")

# Provedení transformace
result_df = transform_data(df)

logger.info(f"Počet výstupních záznamů: {result_df.count()}")
logger.info(f"Konec zpracování, data uložena do: {output_path}")
```

## 8. Dokumentace

### Dokumentace kódu
- Každý Spark job musí mít dokumentaci a docstringy
- Dokumentujte datový tok, schéma a transformace

```python
def transform_customer_data(customer_df, order_df):
    """
    Transformuje a obohacuje zákaznická data o informace z objednávek.
    
    Parametry:
    ----------
    customer_df : DataFrame
        DataFrame obsahující zákaznická data se schématem:
        - id (int): Unikátní ID zákazníka
        - name (string): Jméno zákazníka
        - email (string): Email zákazníka
        - registration_date (date): Datum registrace
    
    order_df : DataFrame
        DataFrame obsahující objednávky se schématem:
        - id (int): ID objednávky
        - customer_id (int): ID zákazníka (cizí klíč)
        - amount (double): Částka objednávky
        - order_date (date): Datum objednávky
    
    Vrací:
    ------
    DataFrame
        Obohacený DataFrame zákazníků s přidanými agregacemi z objednávek:
        - id, name, email, registration_date (původní sloupce)
        - total_orders (int): Celkový počet objednávek zákazníka
        - total_amount (double): Celková útrata zákazníka
        - avg_order_amount (double): Průměrná částka objednávky
        - last_order_date (date): Datum poslední objednávky
    """
    # Implementace transformace
    # ...
```

### Metadata v Airflow
- Využívejte Airflow UI pro dokumentaci datových toků
- Dokumentujte závislosti mezi DAGy a úlohami

```python
# Dokumentace DAGu v Airflow
dag = DAG(
    'customer_data_processing',
    default_args=default_args,
    description='Zpracování a obohacení zákaznických dat o informace z objednávek',
    schedule_interval='0 2 * * *',
    doc_md="""
    # Customer Data Processing Pipeline
    
    Tento DAG zpracovává denní data zákazníků a objednávek a vytváří agregované reporty.
    
    ## Vstupy
    - `/data/raw/customers/{{ ds }}/` - Denní export zákazníků
    - `/data/raw/orders/{{ ds }}/` - Denní export objednávek
    
    ## Výstupy
    - `/data/processed/customer_reports/{{ ds }}/` - Obohacená zákaznická data
    - `/data/processed/customer_kpis/{{ ds }}/` - KPI metriky zákazníků
    
    ## Závislosti
    - Tento DAG je závislý na úspěšném dokončení `raw_data_ingestion` DAGu
    - Výstupy tohoto DAGu jsou vstupem pro `customer_analytics` DAG
    """
)
```

## 9. Monitorování a troubleshooting

### Instrumentace kódu
- Přidejte metriky a monitorovací body do kódu
- Měřte dobu trvání klíčových operací

```python
import time
import logging

def measure_time(func):
    """Dekorátor pro měření času provádění funkce"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logging.info(f"Funkce {func.__name__} trvala {end_time - start_time:.2f} sekund")
        return result
    return wrapper

@measure_time
def process_large_dataset(df):
    # Zpracování dat
    return result_df
```

### Debugging a optimalizace
- Používejte Spark UI pro analýzu výkonu a identifikaci problémů
- Implementujte inkrementální optimalizace na základě metrických dat

```python
# Před optimalizací změřte výkon
start_time = time.time()
result1 = non_optimized_pipeline(df)
time1 = time.time() - start_time

# Optimalizovaná verze
start_time = time.time()
result2 = optimized_pipeline(df)
time2 = time.time() - start_time

# Logování zlepšení
improvement = (time1 - time2) / time1 * 100
logging.info(f"Optimalizace zlepšila výkon o {improvement:.2f}%")
```

## 10. Nasazení

### Verzování a dependency management
- Používejte verzování pro všechny Spark joby
- Explicitně specifikujte závislosti a jejich verze

```python
# requirements.txt
pyspark==3.2.1
delta-spark==1.1.0
pandas==1.4.2
numpy==1.22.3
great-expectations==0.15.8
```

### Prostředí a deployment
- Používejte kontejnerizaci pro konzistentní prostředí
- Implementujte CI/CD pipeline pro automatizované testy a deployment

```Dockerfile
# Dockerfile pro Spark aplikaci
FROM apache/spark:3.2.1-python3

# Instalace závislostí
COPY requirements.txt .
RUN pip install -r requirements.txt

# Kopírování kódu aplikace
COPY src/ /app/

# Výchozí příkaz při spuštění kontejneru
ENTRYPOINT ["/opt/spark/bin/spark-submit", "/app/main.py"]
```

---

## Souhrn klíčových bodů

1. **Výkon**: Optimalizujte partitioning, cache, a shuffle operace
2. **Zdroje**: Správně konfigurujte a monitorujte využití zdrojů
3. **Data**: Používejte optimální formáty a explicitní schémata
4. **Validace**: Implementujte data quality checks a error handling
5. **Integrace**: Parametrizujte joby a monitorujte je z Airflow
6. **Testování**: Pište unit testy a E2E testy
7. **Bezpečnost**: Šifrujte a anonymizujte citlivá data
8. **Dokumentace**: Detailně dokumentujte kód a datové toky
9. **Monitoring**: Instrumentujte kód pro snadné monitorování
10. **Nasazení**: Verzujte kód a používejte kontejnerizaci 
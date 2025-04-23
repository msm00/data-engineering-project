# 14denní intenzivní kurz datového inženýrství

# Technologický stack
•	Hadoop
	•	Spark
	•	AirFlow
	•	Apache Iceberg
	•	Atlas Metadata
	•	Cloudera
	•	Docker
	•	Python (s využitím pyenv a poetry)
	•	Postgres DB
	•	Schema Evolution
	•	Time Travel
  •	Hadoop
	•	+ další z big data oblasti

## Den 1-2: Základy a vývojové prostředí

### Den 1: Příprava prostředí
- **Dopoledne**: Instalace a konfigurace základních nástrojů
  - Nastavení pyenv pro správu verzí Pythonu
  - Konfigurace poetry pro správu závislostí
  - Instalace Docker a Docker Compose
  - Základní Git workflow pro datové projekty

- **Odpoledne**: Základy Docker kontejnerizace
  - Vytvoření prvního Dockerfile
  - Základní Docker příkazy a koncepty
  - Docker Compose pro multi-container aplikace
  - Vytvoření docker-compose.yml pro PostgreSQL

### Den 2: Python a PostgreSQL základy
- **Dopoledne**: Python pro datové zpracování
  - Práce s pandas a numpy
  - Základní ETL operace v Pythonu
  - Připojení k databázím pomocí SQLAlchemy

- **Odpoledne**: PostgreSQL a Schema Evolution koncept
  - Nastavení PostgreSQL v Dockeru
  - Základy schémového designu
  - Implementace jednoduchého Schema Evolution pomocí migrací
  - Praktická ukázka Time Travel konceptu

**Mini-projekt**: Vytvořte kontejnerizovanou aplikaci, která načítá CSV soubory, provádí základní transformace a ukládá výsledky do PostgreSQL. Implementujte jednoduchou verzi Schema Evolution s migrací schématu.

## Den 3-5: Orchestrace a workflow management

### Den 3: Apache Airflow - úvod
- **Dopoledne**: Základy Airflow
  - Architektura a komponenty
  - Instalace Airflow v Docker kontejneru
  - Základní koncepty: DAG, Task, Operator

- **Odpoledne**: Vytváření prvního workflows  - Definice DAG
  - Různé typy operátorů (PythonOperator, BashOperator)
  - Závislosti mezi úlohami
  - Plánování úloh

### Den 4: Pokročilé koncepty Airflow
- **Dopoledne**: Pokročilé funkce
  - XComs pro komunikaci mezi úlohami
  - Dynamické DAG generování
  - Parametrizace workflow
  - Sensors a triggers

- **Odpoledne**: Monitorování a error handling
  - Airflow UI
  - Logování
  - Retry mechanismy
  - Alerting

### Den 5: Praktická orchestrace ETL
- **Celodenní workshop**: Vytvoření komplexní datové pipeline
  - Stahování dat z externích zdrojů
  - Transformace dat pomocí Pythonu
  - Ukládání do PostgreSQL
  - Monitoring průběhu a reporting

**Mini-projekt**: Implementujte kompletní ETL pipeline pomocí Airflow, která pravidelně stahuje data, transformuje je a ukládá do databáze. Přidejte monitorování, error handling a notifikace při selhání.

## Den 6-9: Distribuované zpracování dat

### Den 6: Hadoop ekosystém
- **Dopoledne**: Úvod do Hadoop
  - Architektura HDFS
  - YARN a MapReduce koncepty
  - Spuštění Hadoop v Docker kontejneru
  - Základní operace s HDFS

- **Odpoledne**: Cloudera ekosystém
  - Úvod do Cloudera Data Platform
  - Docker konfigurace pro Cloudera komponenty
  - Základní administrace a monitoring

### Den 7: Apache Spark základy
- **Dopoledne**: Základy Spark
  - Architektura Spark
  - RDD koncept
  - Transformace a akce
  - Spuštění Spark v lokálním režimu a na YARN

- **Odpoledne**: Práce se Spark DataFrame
  - Spark SQL
  - DataFrame API
  - Základní transformace a agregace
  - Optimalizace výkonu

### Den 8: PySpark a MLlib
- **Dopoledne**: PySpark prakticky
  - Práce s DataFrame v Pythonu
  - ETL operace v PySpark
  - Integrace s pandas
  - UDF (User Defined Functions)

- **Odpoledne**: Základy MLlib
  - Preprocessing dat
  - Základní ML algoritmy
  - Pipeline koncept
  - Evaluace modelů

### Den 9: Spark Streaming a pokročilé techniky
- **Dopoledne**: Spark Streaming
  - Batch vs. Stream processing
  - Structured Streaming API
  - Windowing operace
  - Integrace s Kafka (koncept)

- **Odpoledne**: Spark optimalizace
  - Spark UI a monitoring
  - Optimalizace dotazů
  - Partitioning a bucketing
  - Caching a persistence

**Mini-projekt**: Vytvořte distribuovanou aplikaci pomocí Spark, která zpracovává větší datový set, provádí komplexní transformace a agregace, a ukládá výsledky do HDFS a PostgreSQL.

## Den 10-12: Pokročilé datové formáty a metadata management

### Den 10: Apache Iceberg
- **Dopoledne**: Úvod do Apache Iceberg
  - Tabulkové formáty overview (Iceberg, Delta Lake, Hudi)
  - Architektura a koncepty Iceberg
  - Výhody oproti tradičním formátům

- **Odpoledne**: Iceberg prakticky
  - Integrace s Spark
  - CRUD operace s Iceberg tabulkami
  - Schema Evolution v praxi
  - Time Travel dotazy

### Den 11: Metadata management s Atlas
- **Dopoledne**: Základy Atlas Metadata
  - Architektura a komponenty
  - Nastavení Atlas v Docker kontejneru
  - Základní koncepty: Entity, Klasifikace, Glosář

- **Odpoledne**: Praktická práce s Atlas
  - Definice entity typů
  - Sledování lineage
  - Integrace s Hadoop ekosystémem
  - Vyhledávání a discovery

### Den 12: Integrace komponent
- **Celodenní workshop**: Propojení všech technologií
  - Integrace Airflow, Spark, Iceberg a Atlas
  - End-to-end datový tok
  - Metadata tracking
  - Governance a kvalita dat

**Mini-projekt**: Vytvořte data lakehouse architekturu s využitím Apache Iceberg pro ukládání dat, integrujte Schema Evolution a Time Travel funkce, a propojte s Atlas pro správu metadat.

## Den 13-14: Enterprise řešení a dokončení projektu

### Den 13: Enterprise aspekty
- **Dopoledne**: Bezpečnost a governance
  - Autentizace a autorizace
  - Data masking a encryption
  - Audit a compliance
  - Best practices pro produkční nasazení

- **Odpoledne**: Monitoring a observabilita
  - Logging strategie
  - Metriky a KPI pro datové pipeline
  - Alerting a incident management
  - Dashboardy a reporty

### Den 14: Dokončení a prezentace projektu
- **Dopoledne**: Finalizace projektu
  - Integrace všech komponent
  - Testing a ladění
  - Dokumentace
  - Deployment a provoz

- **Odpoledne**: Prezentace a plán dalšího rozvoje
  - Demo finálního řešení
  - Diskuze o použitých technologiích
  - Identifikace oblastí pro další studium
  - Plán pro následující měsíc detailního učení

**Finální projekt**: Kompletní end-to-end datová platforma integrující všechny naučené technologie, se zaměřením na jeden vybraný use case (např. analýza e-commerce dat, IoT monitoring, nebo finanční analytika).

## Doporučené zdroje pro následující měsíc detailního studia

### Knihy:
- "Designing Data-Intensive Applications" by Martin Kleppmann
- "Learning Spark, 2nd Edition" by Jules Damji et al.
- "Hadoop: The Definitive Guide" by Tom White
- "Data Pipelines Pocket Reference" by James Densmore

### Online kurzy:
- Coursera: "Big Data Specialization" by UC San Diego
- Udemy: "Apache Airflow: The Hands-On Guide"
- Databricks Academy: "Apache Spark Programming"
- Cloudera Training: "Administrator Training for Apache Hadoop"

### Dokumentace:
- Apache Airflow Documentation
- Apache Spark Official Documentation
- Apache Iceberg Documentation
- Atlas Metadata Documentation
- PostgreSQL Documentation

### Praktické tipy pro další měsíc:
1. **Týden 1-2**: Hlubší studium Spark a Hadoop ekosystému
2. **Týden 3**: Pokročilé koncepty Airflow a orchestrace
3. **Týden 4**: Detailní práce s Iceberg a pokročilými datovými formáty

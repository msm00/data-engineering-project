# Cloudera Platform - Ukázkové Příklady

Tento adresář obsahuje demonstrační příklady pro práci s Cloudera ekosystémem a pro pochopení jeho klíčových komponent.

## Obsah adresáře

Tato složka obsahuje následující ukázkové skripty:

1. **spark_iceberg_demo.py** - Demonstrace práce s Apache Iceberg pro efektivní správu tabulkových dat v Cloudera, včetně ukázky Time Travel a Schema Evolution.

2. **airflow_workflow.py** - Ukázka Airflow DAG pro orchestraci komplexní datové pipeline v Cloudera prostředí s využitím Spark a Iceberg.

3. **atlas_metadata_demo.py** - Příklad práce s Apache Atlas pro metadata management, sledování data lineage a data governance v rámci Cloudera ekosystému.

## Architektura Cloudera Data Platform

Cloudera Data Platform (CDP) je moderní hybrid-cloud platforma, která poskytuje:

- **Jednotné prostředí** pro práci s daty napříč privátními, veřejnými a hybridními cloud prostředími
- **Škálovatelnost** pro zpracování velkých objemů dat
- **Bezpečnost a governance** prostřednictvím Shared Data Experience (SDX)
- **Podporu různých workload typů** od datového inženýrství po ML a AI

Klíčové komponenty, které jsou demonstrovány v ukázkách:

- **Spark** - Engine pro distribuované zpracování dat
- **Airflow** - Orchestrace datových pipeline
- **Iceberg** - Moderní formát tabulek s pokročilými funkcemi
- **Atlas** - Správa metadat a data governance

## Jak začít pracovat s příklady

### Prerekvizity

Pro spuštění těchto příkladů potřebujete:

- Přístup k Cloudera prostředí (CDP Public/Private Cloud nebo lokální Cloudera instance)
- Python 3.7+ s nainstalovanými balíčky (požadavky jsou v `requirements.txt`)
- Konfigurovaný přístup k Hadoop ekosystému

### Konfigurace prostředí

1. Nastavení proměnných prostředí:

```bash
export HADOOP_CONF_DIR=/etc/hadoop/conf
export SPARK_HOME=/opt/cloudera/parcels/CDH/lib/spark
export PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-*.zip:$PYTHONPATH
```

2. Instalace potřebných Python balíčků:

```bash
pip install -r requirements.txt
```

### Spuštění Spark Iceberg demo

Tento příklad demonstruje práci s Apache Iceberg v Cloudera:

```bash
python spark_iceberg_demo.py
```

Ukázka zahrnuje:
- Vytvoření Iceberg tabulky
- Přidání nových dat
- Schema Evolution (přidání nového sloupce)
- Time Travel (dotazování na předchozí verze dat)

### Nasazení Airflow workflow

Pro nasazení Airflow DAG:

1. Zkopírujte `airflow_workflow.py` do adresáře s DAGy ve vašem Airflow prostředí:

```bash
cp airflow_workflow.py /path/to/airflow/dags/
```

2. Zkontrolujte, že všechny závislosti jsou správně nakonfigurovány v Airflow:
   - Spark connection
   - HDFS connection
   - Potřebné proměnné

3. DAG bude automaticky načten Airflow a lze ho spustit přes UI nebo CLI.

### Spuštění Atlas metadata demo

Pro práci s metadaty v Apache Atlas:

```bash
python atlas_metadata_demo.py
```

Tato ukázka:
- Vyhledává existující Hive tabulky
- Zobrazuje detaily a lineage dat
- Vytváří novou entitu s metadaty a klasifikacemi

## Integrace s Cloudera SDX

Všechny ukázky demonstrují integraci s Cloudera Shared Data Experience (SDX), která poskytuje:

- **Jednotnou správu zabezpečení** - autentizace a autorizace
- **Sdílená metadata** - pomocí Apache Atlas
- **Governance** - klasifikace dat, audit, lineage
- **Katalogizaci dat** - vyhledávání a discovery

## Doporučené postupy

Při práci s ukázkami dodržujte tyto best practices:

1. **Data Quality** - Implementujte validaci dat v každém kroku pipeline
2. **Monitorování** - Využívejte Cloudera Manager pro monitoring procesů
3. **Governance** - Používejte Atlas pro sledování lineage a klasifikaci dat
4. **Verzování** - Využívejte funkce Iceberg pro Time Travel a Schema Evolution
5. **Partitioning** - Správně navrhujte partitioning pro optimální výkon

## Další zdroje

- [Cloudera Documentation](https://docs.cloudera.com/cdp/latest/index.html)
- [Apache Iceberg Documentation](https://iceberg.apache.org/)
- [Apache Atlas Documentation](https://atlas.apache.org/)
- [Apache Airflow Documentation](https://airflow.apache.org/) 
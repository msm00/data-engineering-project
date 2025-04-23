# Apache Hadoop Ekosystém - Praktické Příklady

Tento adresář obsahuje materiály a příklady pro pochopení moderního Hadoop ekosystému v rámci školení "Accelerated Data Engineering Course".

## Přehled Apache Hadoop Ekosystému

Apache Hadoop je open-source framework určený pro distribuované zpracování a ukládání velkých datových sad napříč clustery počítačů. Místo zastaralé Cloudera distribuce používáme oficiální Apache images, které poskytují všechny klíčové komponenty.

## Klíčové komponenty ekosystému

### 1. Hadoop Core
- **HDFS** - Distribuovaný souborový systém
- **YARN** - Resource Manager pro distribuované aplikace

### 2. Zpracování dat
- **Apache Spark** - Engine pro rychlé distribuované zpracování dat
- **Hue** - Webové rozhraní pro práci s Hadoop ekosystémem

## Architektura našeho demo prostředí

Naše demo prostředí se skládá z následujících kontejnerů:
- **namenode** - HDFS NameNode server
- **datanode** - HDFS DataNode server
- **resourcemanager** - YARN ResourceManager
- **nodemanager** - YARN NodeManager
- **spark-master** - Spark Master server
- **spark-worker** - Spark Worker node
- **hue** - Webové UI pro přístup k Hadoop

## Praktické příklady v tomto adresáři

1. **docker-compose-cloudera.yml** - Konfigurace Docker Compose pro spuštění Hadoop a Spark kontejnerů
2. **examples/hdfs_basics.py** - Ukázka základních operací s HDFS
3. **examples/spark_hadoop.py** - Demonstrace PySpark v Hadoop prostředí
4. **examples/hadoop_admin.sh** - Základní administrativní a monitorovací příkazy

## Jak začít pracovat s příklady

### Spuštění Hadoop kontejnerů

```bash
docker-compose -f docker-compose-cloudera.yml up -d
```

### Přístup k webovým rozhraním

- **HDFS NameNode**: http://localhost:9870
- **YARN ResourceManager**: http://localhost:8088
- **Spark Master**: http://localhost:8080
- **Spark Worker**: http://localhost:8081
- **Hue (Web UI)**: http://localhost:8888

### Spuštění příkladů

```bash
# Připojení do namenode kontejneru
docker exec -it hadoop-namenode bash

# Spuštění Python příkladů
cd /examples
python hdfs_basics.py

# Spuštění administračního skriptu
bash hadoop_admin.sh

# Připojení do Spark master kontejneru
docker exec -it spark-master bash

# Spuštění Spark příkladu
cd /examples
spark-submit --master spark://spark-master:7077 spark_hadoop.py
```

## Klíčové koncepty pro administraci

### 1. Sledování zdraví clusteru
- Kontrola využití HDFS
- Monitoring YARN aplikací
- Sledování zdrojů (CPU, RAM, diskový prostor)

### 2. Optimalizace výkonu
- Nastavení YARN konfigurací
- Spark konfigurace pro optimální výkon

### 3. Správa dat v HDFS
- Ukládání a načítání dat
- Správa replikace
- Záloha důležitých dat

### 4. Scaling a správa zdrojů
- Přidávání a odebírání uzlů
- Plánování zdrojů 
- Správa front YARN

## Doporučené zdroje pro další studium

- [Apache Hadoop Documentation](https://hadoop.apache.org/docs/)
- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [HDFS Architecture Guide](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html)
- [YARN Architecture](https://hadoop.apache.org/docs/stable/hadoop-yarn/hadoop-yarn-site/YARN.html)
- [Kniha: Hadoop: The Definitive Guide (Tom White)](https://www.oreilly.com/library/view/hadoop-the-definitive/9781491901687/) 
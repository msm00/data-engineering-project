# Praktický postup - Hadoop ekosystém

Tento dokument popisuje kroky pro praktické pochopení a procvičení Hadoop ekosystému.

## 1. Spuštění clusteru

Restartujeme cluster s opravenými konfiguracemi:

```bash
# Nejprve zastavíme existující kontejnery
docker-compose -f docker-compose-cloudera.yml down

# Nyní spustíme opravené kontejnery
docker-compose -f docker-compose-cloudera.yml up -d
```

## 2. Ověření stavu clusteru

Zkontrolujme, zda všechny komponenty běží správně:

```bash
# Kontrola běžících kontejnerů
docker ps

# Kontrola logů NameNode
docker logs hadoop-namenode

# Kontrola logů JupyterLab
docker logs jupyterlab
```

## 3. Základní operace s HDFS

### 3.1 Připojení do NameNode kontejneru

```bash
docker exec -it hadoop-namenode bash
```

### 3.2 Vytvoření adresářové struktury v HDFS

```bash
# Vytvoření adresářové struktury
hdfs dfs -mkdir -p /user/root/data
hdfs dfs -mkdir -p /user/root/output

# Kontrola adresářů
hdfs dfs -ls /user/root/
```

### 3.3 Nahrání testovacích dat do HDFS

```bash
# Vytvoření testovacího souboru
echo "1,Notebook,25000,10" > /tmp/products.csv
echo "2,Mobil,12000,25" >> /tmp/products.csv
echo "3,Tablet,8000,15" >> /tmp/products.csv
echo "4,Monitor,5000,20" >> /tmp/products.csv

# Nahrání do HDFS
hdfs dfs -put /tmp/products.csv /user/root/data/

# Ověření
hdfs dfs -cat /user/root/data/products.csv
```

## 4. Spark operace v JupyterLab

### 4.1 Přístup k JupyterLab

Otevřete si prohlížeč a jděte na adresu: http://localhost:8888

Poznámka: Pro první přihlášení do JupyterLab je potřeba token, který najdete v logu kontejneru:

```bash
docker logs jupyterlab
```

### 4.2 Vytvoření nového PySpark notebooku

1. V JupyterLab klikněte na "File" -> "New" -> "Notebook"
2. Vyberte "Python 3 (ipykernel)"
3. V první buňce zadejte následující kód pro inicializaci Spark:

```python
import findspark
findspark.init()

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, avg, desc

# Vytvoření SparkSession s propojením na HDFS
spark = SparkSession.builder \
    .appName("JupyterSparkDemo") \
    .config("spark.executor.memory", "1g") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:8020") \
    .getOrCreate()

# Informace o Spark kontextu
print(f"Spark version: {spark.version}")
print(f"Spark master: {spark.sparkContext.master}")
```

### 4.3 Práce s daty v PySpark

Přidejte další buňky s následujícím kódem:

```python
# Načtení CSV souboru do DataFrame
df = spark.read.csv("hdfs://namenode:8020/user/root/data/products.csv", 
                    inferSchema=True, 
                    header=False)

# Pojmenování sloupců
df = df.toDF("id", "nazev", "cena", "mnozstvi")

# Zobrazení dat
df.show()
```

```python
# Základní statistiky
df.describe().show()

# Výpočet celkové hodnoty skladu
df.withColumn("celkova_hodnota", col("cena") * col("mnozstvi")).show()
```

```python
# Uložení výsledků jako Parquet
df.write.mode("overwrite").parquet("hdfs://namenode:8020/user/root/output/products.parquet")

# Načtení dat zpět z Parquet
df_parquet = spark.read.parquet("hdfs://namenode:8020/user/root/output/products.parquet")
df_parquet.show()
```

## 5. Administrace a monitoring

### 5.1 Spuštění administračního skriptu

```bash
# V namenode kontejneru
docker exec -it hadoop-namenode bash
cd /examples
bash hadoop_admin.sh
```

### 5.2 Přístup k webovým rozhraním

Otevřete si prohlížeč a přistupte k následujícím rozhraním:

- HDFS NameNode: http://localhost:9870
- YARN ResourceManager: http://localhost:8088
- JupyterLab: http://localhost:8888

## 6. Vlastní úkoly pro procvičení

### Úkol 1: Analýza prodejů

1. Vytvořte CSV soubor s daty o prodejích (produkt, region, množství, cena)
2. Nahrajte ho do HDFS
3. Pomocí JupyterLab a PySpark:
   - Vypočítejte celkový obrat podle regionů
   - Identifikujte nejprodávanější produkty
   - Analyzujte průměrnou hodnotu objednávky

### Úkol 2: Optimalizace HDFS

1. Zkontrolujte aktuální konfiguraci HDFS (velikost bloku, replikační faktor)
2. Nastavte vhodné hodnoty pro větší dataset
3. Otestujte výkon při čtení/zápisu s různými konfiguracemi

### Úkol 3: Monitoring clusteru

1. Prozkoumejte webová rozhraní a identifikujte klíčové metriky
2. Vytvořte jednoduchý skript, který bude monitorovat vytížení clusteru
3. Simulujte zátěž a sledujte změny v metrikách

## 7. Úklid po dokončení

```bash
# Zastavení všech kontejnerů
docker-compose -f docker-compose-cloudera.yml down
``` 
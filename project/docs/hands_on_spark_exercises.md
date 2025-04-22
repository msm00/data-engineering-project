# Praktická cvičení s Apache Spark

Tento dokument obsahuje sadu praktických cvičení, která vám pomohou lépe pochopit a využít Apache Spark.

## Cvičení 1: Analýza produktových dat

### Cíl
Analyzovat dataset produktů a provést základní agregace a transformace.

### Postup

1. Vytvořte soubor `product_analysis.py` s následujícím kódem:

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, sum, count, desc, round

# Inicializace Spark session
spark = SparkSession.builder \
    .appName("ProductAnalysis") \
    .master("local[*]") \
    .getOrCreate()

# Nastavení logování (omezení verbosity)
spark.sparkContext.setLogLevel("WARN")

# Načtení dat
products_df = spark.read.csv("/data/products.csv", header=True, inferSchema=True)

# Zobrazení schématu
print("=== Schéma datasetu ===")
products_df.printSchema()

# Zobrazení prvních 5 řádků
print("\n=== Ukázka dat ===")
products_df.show(5)

# Základní statistiky
print("\n=== Základní statistiky ===")
products_df.describe().show()

# Počet produktů podle kategorie
print("\n=== Počet produktů podle kategorie ===")
products_df.groupBy("category") \
    .agg(count("*").alias("count")) \
    .orderBy(desc("count")) \
    .show()

# Průměrná cena podle kategorie
print("\n=== Průměrná cena podle kategorie ===")
products_df.groupBy("category") \
    .agg(round(avg("price"), 2).alias("avg_price")) \
    .orderBy(desc("avg_price")) \
    .show()

# Filtrování drahých produktů
print("\n=== Drahé produkty (cena > 100) ===")
expensive_products = products_df.filter(col("price") > 100)
expensive_products.show()

# Uložení výsledků do Parquet souboru
expensive_products.write.mode("overwrite").parquet("/data/output/expensive_products")

# Ukončení Spark session
spark.stop()
```

2. Vytvořte soubor produktových dat `products.csv`:

```csv
id,name,category,price,quantity
1,Smartphone XYZ,Electronics,599.99,50
2,Laptop Pro,Electronics,1299.99,30
3,Coffee Machine,Home,99.99,100
4,Bluetooth Speaker,Electronics,49.99,200
5,Office Chair,Furniture,129.99,40
6,Desk Lamp,Home,24.99,150
7,Tablet Mini,Electronics,299.99,75
8,Running Shoes,Clothing,89.99,120
9,Winter Jacket,Clothing,199.99,60
10,Smart Watch,Electronics,249.99,90
11,Yoga Mat,Sports,19.99,200
12,Protein Powder,Food,29.99,300
13,Gaming Console,Electronics,399.99,25
14,Dining Table,Furniture,349.99,15
15,Bookshelf,Furniture,159.99,35
```

3. Spusťte analýzu:

```bash
docker exec spark-master spark-submit /app/product_analysis.py
```

4. Prohlédněte si výsledky a zkuste modifikovat kód pro další analýzy

## Cvičení 2: Transformace a joins

### Cíl
Naučit se propojovat více datasetů a provádět složitější transformace

### Postup

1. Vytvořte soubor `sales_analysis.py` s následujícím kódem:

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, count, desc, round, concat, lit, when, udf
from pyspark.sql.types import StringType
import datetime

# Inicializace Spark session
spark = SparkSession.builder \
    .appName("SalesAnalysis") \
    .master("local[*]") \
    .getOrCreate()

# Nastavení logování
spark.sparkContext.setLogLevel("WARN")

# Načtení dat
products_df = spark.read.csv("/data/products.csv", header=True, inferSchema=True)
sales_df = spark.read.csv("/data/sales.csv", header=True, inferSchema=True)

# Kontrola dat
print("=== Ukázka dat: Produkty ===")
products_df.show(5)

print("=== Ukázka dat: Prodeje ===")
sales_df.show(5)

# Join produktů a prodejů
sales_products = sales_df.join(
    products_df,
    sales_df.product_id == products_df.id,
    "inner"
)

# Přidání sloupce s celkovou cenou
sales_products = sales_products.withColumn(
    "total_price", 
    round(col("quantity") * col("price"), 2)
)

# Ukázka spojeného datasetu
print("\n=== Spojený dataset ===")
sales_products.show(5)

# Agregace podle kategorie
print("\n=== Prodeje podle kategorie ===")
category_sales = sales_products.groupBy("category") \
    .agg(
        count("*").alias("num_sales"),
        round(sum("total_price"), 2).alias("total_revenue")
    ) \
    .orderBy(desc("total_revenue"))

category_sales.show()

# Vytvoření UDF pro kategorizaci cen
def price_category(price):
    if price < 50:
        return "Nízká"
    elif price < 200:
        return "Střední"
    else:
        return "Vysoká"

price_category_udf = udf(price_category, StringType())

# Přidání cenové kategorie
products_with_category = products_df.withColumn(
    "price_category", 
    price_category_udf(col("price"))
)

print("\n=== Produkty s cenovou kategorií ===")
products_with_category.show()

# Analýza podle měsíce
sales_products = sales_products.withColumn(
    "month", 
    sales_df.date.substr(6, 2)
)

print("\n=== Prodeje podle měsíce ===")
sales_products.groupBy("month") \
    .agg(
        count("*").alias("num_sales"),
        round(sum("total_price"), 2).alias("total_revenue")
    ) \
    .orderBy("month") \
    .show()

# Uložení výsledků
category_sales.write.mode("overwrite").parquet("/data/output/category_sales")

# Ukončení Spark session
spark.stop()
```

2. Vytvořte soubor prodejů `sales.csv`:

```csv
id,date,product_id,quantity,customer_id
1,2025-01-15,1,2,1001
2,2025-01-16,3,1,1002
3,2025-01-17,5,1,1003
4,2025-01-18,2,1,1004
5,2025-01-19,7,1,1001
6,2025-01-20,10,2,1005
7,2025-01-21,4,3,1006
8,2025-01-22,9,1,1007
9,2025-01-23,13,1,1008
10,2025-01-24,6,2,1009
11,2025-02-01,1,1,1010
12,2025-02-02,8,1,1001
13,2025-02-03,12,3,1003
14,2025-02-04,14,1,1005
15,2025-02-05,11,2,1002
16,2025-02-06,5,1,1007
17,2025-02-07,3,2,1008
18,2025-02-08,7,1,1004
19,2025-02-09,10,1,1006
20,2025-02-10,2,1,1009
```

3. Spusťte analýzu:

```bash
docker exec spark-master spark-submit /app/sales_analysis.py
```

4. Rozšiřte kód o další analýzy, například:
   - Top 3 nejprodávanější produkty
   - Průměrná velikost objednávky podle produktové kategorie
   - Porovnání prodejů mezi měsíci

## Cvičení 3: Word Count a práce s RDD

### Cíl
Pochopit základní paradigma MapReduce pomocí klasického Word Count příkladu

### Postup

1. Vytvořte soubor `word_count.py` s následujícím kódem:

```python
from pyspark.sql import SparkSession
import re

def normalize_text(text):
    # Odstranění speciálních znaků a převod na malá písmena
    return re.sub(r'[^\w\s]', '', text.lower())

# Inicializace Spark session
spark = SparkSession.builder \
    .appName("WordCount") \
    .master("local[*]") \
    .getOrCreate()

# Nastavení logování
spark.sparkContext.setLogLevel("WARN")

# Načtení textu jako RDD
text_file = spark.sparkContext.textFile("/data/sample_text.txt")

# Word count pomocí RDD transformací
word_counts = text_file \
    .map(normalize_text) \
    .flatMap(lambda line: line.split()) \
    .filter(lambda word: word != '') \
    .map(lambda word: (word, 1)) \
    .reduceByKey(lambda a, b: a + b) \
    .map(lambda x: (x[1], x[0])) \
    .sortByKey(False) \
    .map(lambda x: (x[1], x[0]))

# Ukázka výsledků
print("=== Nejčastější slova ===")
for word, count in word_counts.take(20):
    print(f"{word}: {count}")

# Uložení výsledků
word_counts.saveAsTextFile("/data/output/word_counts")

# Stejná úloha pomocí DataFrame API
text_df = spark.read.text("/data/sample_text.txt")

from pyspark.sql.functions import explode, split, lower, col, count, desc

words_df = text_df.select(
    explode(
        split(lower(col("value")), "\\W+")
    ).alias("word")
).filter(col("word") != "")

word_counts_df = words_df.groupBy("word").count().orderBy(desc("count"))

print("\n=== Nejčastější slova (DataFrame API) ===")
word_counts_df.show(20)

# Uložení výsledků z DataFrame API
word_counts_df.write.mode("overwrite").csv("/data/output/word_counts_df")

# Ukončení Spark session
spark.stop()
```

2. Vytvořte soubor s textem `sample_text.txt` obsahující libovolný delší text (např. úryvek z knihy)

3. Spusťte analýzu:

```bash
docker exec spark-master spark-submit /app/word_count.py
```

4. Porovnejte výsledky z obou přístupů (RDD vs DataFrame)

5. Rozšiřte kód o další funkcionalitu:
   - Filtrování "stop slov" (a, the, is, atd.)
   - Analýza četnosti n-gramů (dvojic nebo trojic slov)
   - Vizualizace nejčastějších slov

## Doporučení pro další cvičení

- **Streaming data**: Zkuste implementovat jednoduchý Spark Streaming příklad
- **Machine Learning**: Vyzkoušejte MLlib na klasické datové sadě (např. Iris dataset)
- **Zpracování grafů s GraphX**: Implementujte jednoduchý algoritmus nad grafovými daty
- **SparkR nebo PySpark**: Prozkoumejte integraci Spark s R nebo Python ekosystémem
- **Optimalizace výkonu**: Experimentujte s různými konfiguracemi a měřte výkon

## Pokročilá témata k vyzkoušení

1. **Integrace s Kafka**: Streaming dat z Kafka do Spark
2. **Spark a HDFS**: Práce s daty uloženými v HDFS
3. **Delta Lake**: Implementace transakcí a schéma evoluce nad Spark daty
4. **Spark UI**: Analýza výkonu pomocí Spark UI
5. **Structured Streaming**: Implementace real-time analytických dotazů 
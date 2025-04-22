# Architektura Apache Spark

## Úvod do Apache Spark

Apache Spark je vysoce výkonný distribuovaný výpočetní framework pro zpracování velkých objemů dat. Umožňuje provádět výpočty v paměti (in-memory), což výrazně zvyšuje výkon oproti tradičnímu MapReduce modelu používanému v Hadoop.

## Klíčové vlastnosti Spark

1. **Rychlost**: Spark může být až 100× rychlejší než Hadoop MapReduce díky zpracování v paměti
2. **Všestrannost**: Podporuje různé typy zpracování (batch processing, streaming, machine learning, graph processing)
3. **Snadné použití**: API v jazycích Java, Scala, Python a R
4. **Unifikovaný framework**: Jednotný engine pro různé typy zpracování dat

## Hlavní komponenty architektury Spark

![Architektura Spark](https://spark.apache.org/docs/latest/img/cluster-overview.png)

### 1. Spark Core

Jádro Spark poskytuje základní funkcionalitu, jako je plánování úloh, správa paměti, zotavení po chybách a interakce s úložným systémem. Hlavní abstrakce v Spark Core jsou:

- **RDD (Resilient Distributed Dataset)**: Základní datová struktura, která reprezentuje kolekci objektů rozdělených přes cluster
- **DAG (Directed Acyclic Graph)**: Reprezentace výpočetního grafu, který určuje, jak budou transformace aplikovány na data

### 2. Spark SQL

Modul pro práci se strukturovanými daty pomocí SQL dotazů. Hlavní abstrakce:

- **DataFrame**: Distribuovaná kolekce dat organizovaná do pojmenovaných sloupců
- **Dataset**: Typově bezpečná verze DataFrame (dostupná v Javě a Scale)
- **SparkSession**: Vstupní bod pro práci se Spark SQL

### 3. Spark Streaming & Structured Streaming

Moduly pro zpracování dat v reálném čase:

- **DStream (Discretized Stream)**: Reprezentace kontinuálního toku dat
- **Strukturované streamy**: Streamované verze DataFrame API s podporou pro windowing operace

### 4. MLlib

Knihovna pro strojové učení, která poskytuje:

- Běžné ML algoritmy (klasifikace, regrese, clustering)
- Feature transformace
- Pipeline API pro skládání ML workflow
- Nástroje pro evaluaci modelů

### 5. GraphX

Komponenta pro zpracování grafů a paralelní výpočty nad grafy:

- Grafy a operace nad grafy
- Algoritmy jako PageRank, Connected Components, Triangle Counting

## Architektura clusteru Spark

Spark používá master-slave architekturu s následujícími komponenty:

### 1. Driver Program (Master)

- Spouští hlavní funkci aplikace
- Vytváří SparkContext/SparkSession
- Převádí uživatelský kód na úlohy (tasks)
- Plánuje úlohy pro vykonání na executorech
- Koordinuje vykonávání aplikace

### 2. Cluster Manager

Alokuje zdroje v clusteru. Spark podporuje několik cluster managerů:

- **Standalone**: Vlastní cluster manager Sparku
- **YARN**: Hadoop cluster manager
- **Mesos**: Obecný cluster manager
- **Kubernetes**: Kontejnerový orchestrátor

### 3. Worker Nodes (Slaves)

- Provádějí výpočetní práci
- Hostují executory

### 4. Executors

- Jsou spuštěny na worker nodech
- Provádějí výpočty a ukládají data
- Každá aplikace Spark má své vlastní executory
- Komunikují jen s Driver programem

## Zpracování úloh v Spark

1. **Lazy Evaluation**: Transformace na RDD/DataFrame jsou vyhodnocovány lazy (nejsou provedeny okamžitě, ale vytvoří se plán)
2. **Action Triggering**: Akce (jako count(), collect(), save()) spouští vykonání transformací
3. **Optimalizace**: Catalyst Optimizer optimalizuje dotazy pro DataFrame/Dataset
4. **Task Scheduling**: Plánovač úloh rozdělí práci na menší úkoly pro executory
5. **Data Locality**: Spark se snaží zpracovávat data na nodech, kde jsou fyzicky uložená

## Klíčové koncepty výkonu

### Partitioning

- Data v RDD/DataFrame jsou rozdělena na partitions
- Každá partition je zpracována jedním úkolem (task)
- Správné partitioning je klíčové pro výkon (partitioning by key, repartitioning)

### Caching/Persistence

- RDD/DataFrame mohou být uloženy v paměti pomocí `cache()` nebo `persist()`
- Různé úrovně persistence (pouze paměť, paměť+disk, pouze disk)
- Vhodné pro data, která se opakovaně používají v různých operacích

### Shuffle

- Přesun dat mezi partitions (např. při operacích join, groupBy, repartition)
- Náročná operace, která často zahrnuje zápis na disk
- Měla by být minimalizována pro dosažení lepšího výkonu

### Broadcast Variables

- Mechanismus pro efektivní distribuci velkých read-only proměnných z Driver programu do executors
- Redukuje množství dat přenášených přes síť

## Praktické ukázky kódu

### Příklad 1: Vytvoření SparkSession

```python
from pyspark.sql import SparkSession

# Vytvoření SparkSession
spark = SparkSession.builder \
    .appName("SparkArchitectureDemo") \
    .master("local[*]") \
    .getOrCreate()
```

### Příklad 2: Práce s DataFrame

```python
# Načtení dat
df = spark.read.csv("data.csv", header=True, inferSchema=True)

# Transformace
filtered_df = df.filter(df.age > 25).select("name", "age", "city")

# Zobrazení výsledků
filtered_df.show()
```

### Příklad 3: RDD transformace a akce

```python
# Vytvoření RDD
rdd = spark.sparkContext.parallelize([1, 2, 3, 4, 5])

# Transformace
mapped_rdd = rdd.map(lambda x: x * 2)
filtered_rdd = mapped_rdd.filter(lambda x: x > 5)

# Akce
result = filtered_rdd.collect()
print(result)  # [6, 8, 10]
```

## Shrnutí

Apache Spark je výkonný distribuovaný výpočetní framework, který díky zpracování v paměti poskytuje vysoký výkon pro různé typy datových úloh. Jeho unifikovaná architektura a bohaté API v různých jazycích z něj činí všestranný nástroj pro moderní datové inženýrství.

---

## Doporučené zdroje pro další studium

- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [Learning Spark, 2nd Edition](https://pages.databricks.com/rs/094-YMS-629/images/LearningSpark2.0.pdf) (O'Reilly)
- [Databricks Academy](https://www.databricks.com/learn/training)
- [Spark: The Definitive Guide](https://www.oreilly.com/library/view/spark-the-definitive/9781491912201/) (O'Reilly) 
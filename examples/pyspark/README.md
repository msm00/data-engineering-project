# PySpark analýza prodejů

## Návod k použití

1. Spusť JupyterLab přes webový prohlížeč:
   - Přejdi na http://localhost:8888
   - Použij token z výstupu příkazu `docker logs jupyterlab | grep token`

2. V JupyterLab vytvořte nový PySpark notebook a zkopíruj do něj následující kód:

```python
# Import potřebných knihoven
from pyspark.sql import SparkSession
from pyspark.sql.functions import sum as spark_sum, avg, count, col, desc

# Vytvoření Spark session
spark = SparkSession.builder \
    .appName("Analýza prodejů") \
    .getOrCreate()

# Nastavení úrovně logování
spark.sparkContext.setLogLevel("WARN")

# Cesta k vstupním datům
INPUT_FILE = "/home/jovyan/data/testdata/prodeje.csv"

# Načtení dat
print("Načítání dat z:", INPUT_FILE)
df = spark.read.csv(INPUT_FILE, header=True, inferSchema=True)

# Zobrazení schématu
print("\nSchéma dat:")
df.printSchema()

# Zobrazení prvních pár řádků
print("\nUkázka dat:")
df.show(5)

# Analýza podle kategorií
print("\nAnalýza podle kategorií:")
df_kategorie = df.groupBy("kategorie") \
    .agg(
        count("id").alias("pocet_polozek"),
        spark_sum("mnozstvi").alias("celkem_prodano"),
        spark_sum(col("cena") * col("mnozstvi")).alias("celkovy_obrat")
    ) \
    .orderBy(desc("celkovy_obrat"))

df_kategorie.show()

# Analýza podle regionů
print("\nAnalýza podle regionů:")
df_regiony = df.groupBy("region") \
    .agg(
        count("id").alias("pocet_polozek"),
        spark_sum("mnozstvi").alias("celkem_prodano"),
        spark_sum(col("cena") * col("mnozstvi")).alias("celkovy_obrat"),
        avg("cena").alias("prumerna_cena")
    ) \
    .orderBy(desc("celkovy_obrat"))

df_regiony.show()
```

3. Spusť kód a analyzuj výsledky

4. Alternativně můžeš spustit Python skript přímo v kontejneru:

```bash
docker exec -it jupyterlab python /home/jovyan/examples/pyspark/analyza_prodeje.py
``` 
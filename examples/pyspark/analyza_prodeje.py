#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Příklad analýzy prodejů pomocí PySpark
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import sum as spark_sum, avg, count, col, desc, month, year, lit
import matplotlib.pyplot as plt
import os

# Vytvoření Spark session
spark = SparkSession.builder \
    .appName("Analýza prodejů") \
    .config("spark.ui.port", "4050") \
    .getOrCreate()

# Nastavení úrovně logování
spark.sparkContext.setLogLevel("WARN")

# Cesta k vstupním datům
INPUT_FILE = "/home/jovyan/data/testdata/prodeje.csv"

def main():
    # Načtení dat
    print("Načítání dat z:", INPUT_FILE)
    df = spark.read.csv(INPUT_FILE, header=True, inferSchema=True)
    
    # Zobrazení schématu
    print("\nSchéma dat:")
    df.printSchema()
    
    # Zobrazení prvních pár řádků
    print("\nUkázka dat:")
    df.show(5)
    
    # Základní statistiky
    print("\nStatistiky prodejů:")
    df.select("cena", "mnozstvi").describe().show()
    
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
    
    # Uložení výsledků do CSV souborů
    output_dir = "/home/jovyan/data/testdata/results"
    os.makedirs(output_dir, exist_ok=True)
    
    df_kategorie.coalesce(1).write.mode("overwrite").csv(f"{output_dir}/kategorie", header=True)
    df_regiony.coalesce(1).write.mode("overwrite").csv(f"{output_dir}/regiony", header=True)
    
    print(f"\nVýsledky byly uloženy do: {output_dir}")
    
    # Ukončení Spark session
    spark.stop()

if __name__ == "__main__":
    main() 
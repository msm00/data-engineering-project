#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Pokročilá analýza prodejů pomocí PySpark
----------------------------------------
Tento skript demonstruje použití Apache Spark v rámci Hadoop ekosystému
pro pokročilou analýzu dat s využitím SQL, DataFrame API a ML knihovny.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as spark_sum, avg, count, desc, month, year, dayofweek
from pyspark.sql.functions import when, concat, lit, expr, datediff, to_date, current_date
from pyspark.sql.types import DoubleType, IntegerType
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator
import matplotlib.pyplot as plt
import pandas as pd
import os
import time

# Vytvoření Spark session s podporou Hive
spark = SparkSession.builder \
    .appName("Pokročilá analýza prodejů") \
    .config("spark.sql.warehouse.dir", "/user/hive/warehouse") \
    .config("hive.metastore.uris", "thrift://hive-metastore:9083") \
    .enableHiveSupport() \
    .getOrCreate()

# Nastavení úrovně logování
spark.sparkContext.setLogLevel("WARN")

def main():
    print("Spouštím pokročilou analýzu dat pomocí PySpark...")
    
    # 1. Načtení dat z HDFS
    print("\n1. Načítání dat z HDFS...")
    try:
        # Přímé načtení z CSV souborů v HDFS
        prodeje_df = spark.read.csv("hdfs://namenode:8020/data/raw/prodeje/prodeje_2024.csv", 
                                    header=True, inferSchema=True)
        zakaznici_df = spark.read.csv("hdfs://namenode:8020/data/raw/zakaznici/zakaznici.csv", 
                                     header=True, inferSchema=True)
        
        # Alternativně lze načíst data z Hive
        # prodeje_df = spark.sql("SELECT * FROM prodeje_db.prodeje")
        # zakaznici_df = spark.sql("SELECT * FROM prodeje_db.zakaznici")
    
        print(f"Načteno {prodeje_df.count()} záznamů prodejů a {zakaznici_df.count()} záznamů zákazníků")
    except Exception as e:
        print(f"Chyba při načítání dat: {e}")
        return
    
    # Registrace DataFrame jako dočasné pohledy pro SQL
    prodeje_df.createOrReplaceTempView("prodeje")
    zakaznici_df.createOrReplaceTempView("zakaznici")
    
    # 2. Základní analýza pomocí DataFrame API
    print("\n2. Základní statistiky prodejů podle kategorií...")
    kategorie_stats = prodeje_df.groupBy("kategorie") \
        .agg(
            count("id").alias("pocet_transakci"),
            spark_sum("mnozstvi").alias("celkem_prodano"),
            spark_sum(col("cena") * col("mnozstvi")).alias("celkovy_obrat"),
            avg("cena").alias("prumerna_cena")
        ) \
        .orderBy(desc("celkovy_obrat"))
    
    kategorie_stats.show()
    
    # 3. Analýza pomocí Spark SQL
    print("\n3. Analýza prodejů podle času (měsíc)...")
    mesicni_prodeje = spark.sql("""
        SELECT 
            YEAR(datum) as rok,
            MONTH(datum) as mesic,
            SUM(cena * mnozstvi) as celkovy_obrat,
            COUNT(*) as pocet_transakci
        FROM prodeje
        GROUP BY YEAR(datum), MONTH(datum)
        ORDER BY rok, mesic
    """)
    
    mesicni_prodeje.show()
    
    # 4. Join DataFrame a pokročilá analýza
    print("\n4. Analýza prodejů podle segmentu zákazníků...")
    # Join prodejů a zákazníků
    joined_df = prodeje_df.join(zakaznici_df, prodeje_df.zakaznik_id == zakaznici_df.id)
    
    # Analýza podle segmentu
    segment_analysis = joined_df.groupBy("segment") \
        .agg(
            count("produkt").alias("pocet_transakci"),
            spark_sum(col("cena") * col("mnozstvi")).alias("celkovy_obrat"),
            avg("cena").alias("prumerna_cena"),
            avg("vek").alias("prumerny_vek")
        ) \
        .orderBy(desc("celkovy_obrat"))
    
    segment_analysis.show()
    
    # 5. Analýza podle věkových skupin
    print("\n5. Analýza podle věkových skupin zákazníků...")
    vekove_skupiny = joined_df \
        .withColumn("vekova_skupina", 
                   when(col("vek") < 30, "18-29")
                   .when((col("vek") >= 30) & (col("vek") < 40), "30-39")
                   .when((col("vek") >= 40) & (col("vek") < 50), "40-49")
                   .otherwise("50+")) \
        .groupBy("vekova_skupina") \
        .agg(
            count("produkt").alias("pocet_transakci"),
            spark_sum(col("cena") * col("mnozstvi")).alias("celkovy_obrat"),
            avg("cena").alias("prumerna_cena")
        ) \
        .orderBy("vekova_skupina")
    
    vekove_skupiny.show()
    
    # 6. Prediktivní analýza - jednoduchý lineární regresní model
    print("\n6. Prediktivní analýza - predikce ceny na základě věku zákazníka a množství...")
    
    # Příprava dat pro ML
    ml_data = joined_df.select(
        col("cena").cast(DoubleType()).alias("cena"),
        col("mnozstvi").cast(IntegerType()).alias("mnozstvi"),
        col("vek").cast(IntegerType()).alias("vek"),
        when(col("segment") == "Premium", 1).otherwise(0).alias("premium_flag")
    ).na.drop()
    
    # Rozdělení na trénovací a testovací data
    train_data, test_data = ml_data.randomSplit([0.8, 0.2], seed=42)
    
    # Příprava feature vektoru
    assembler = VectorAssembler(
        inputCols=["mnozstvi", "vek", "premium_flag"],
        outputCol="features"
    )
    
    # Trénování modelu
    train_data = assembler.transform(train_data)
    test_data = assembler.transform(test_data)
    
    lr = LinearRegression(featuresCol="features", labelCol="cena")
    lr_model = lr.fit(train_data)
    
    # Vyhodnocení modelu
    predictions = lr_model.transform(test_data)
    evaluator = RegressionEvaluator(labelCol="cena", predictionCol="prediction", metricName="rmse")
    rmse = evaluator.evaluate(predictions)
    
    print(f"Model koeficienty: {lr_model.coefficients}")
    print(f"Model intercept: {lr_model.intercept}")
    print(f"RMSE: {rmse}")
    print(f"R2: {lr_model.summary.r2}")
    
    # 7. Uložení výsledků analýzy do HDFS
    print("\n7. Ukládání výsledků analýzy do HDFS...")
    
    # Uložení výsledků analýzy podle kategorií
    hdfs_output_dir = "hdfs://namenode:8020/data/processed"
    try:
        kategorie_stats.write.mode("overwrite").csv(f"{hdfs_output_dir}/kategorie_stats", header=True)
        mesicni_prodeje.write.mode("overwrite").csv(f"{hdfs_output_dir}/mesicni_prodeje", header=True)
        segment_analysis.write.mode("overwrite").csv(f"{hdfs_output_dir}/segment_analysis", header=True)
        vekove_skupiny.write.mode("overwrite").csv(f"{hdfs_output_dir}/vekove_skupiny", header=True)
        
        print(f"Výsledky byly uloženy do: {hdfs_output_dir}")
    except Exception as e:
        print(f"Chyba při ukládání výsledků: {e}")
    
    # Ukončení Spark session
    print("\nAnalýza byla úspěšně dokončena.")
    spark.stop()

if __name__ == "__main__":
    start_time = time.time()
    main()
    print(f"Celkový čas zpracování: {time.time() - start_time:.2f} sekund") 
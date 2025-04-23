#!/usr/bin/env python3
"""
Základní příklad pro práci se Spark v Cloudera ekosystému.
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, avg, desc

def spark_demo():
    """Ukázka základních Spark operací v Cloudera."""
    # Vytvoření SparkSession s napojením na Cloudera
    spark = SparkSession.builder \
        .appName("ClouderaSparkDemo") \
        .config("spark.master", "yarn") \
        .config("spark.submit.deployMode", "client") \
        .enableHiveSupport() \
        .getOrCreate()
    
    # Vytvoření testovacích dat
    data = [
        {"id": 1, "region": "Praha", "produkt": "Notebook", "mnozstvi": 10, "cena": 25000},
        {"id": 2, "region": "Brno", "produkt": "Mobil", "mnozstvi": 15, "cena": 10000},
        {"id": 3, "region": "Ostrava", "produkt": "Tablet", "mnozstvi": 5, "cena": 8000},
        {"id": 4, "region": "Praha", "produkt": "Mobil", "mnozstvi": 20, "cena": 12000},
        {"id": 5, "region": "Brno", "produkt": "Notebook", "mnozstvi": 8, "cena": 22000},
        {"id": 6, "region": "Ostrava", "produkt": "Mobil", "mnozstvi": 12, "cena": 9500},
        {"id": 7, "region": "Praha", "produkt": "Tablet", "mnozstvi": 18, "cena": 7500},
        {"id": 8, "region": "Brno", "produkt": "Tablet", "mnozstvi": 10, "cena": 8200},
    ]
    
    # Převod na DataFrame
    df = spark.createDataFrame(data)
    
    # Uložení do HDFS v Parquet formátu
    df.write.mode("overwrite").parquet("/user/cloudera/demo/prodeje.parquet")
    
    # Načtení z Parquet
    df_loaded = spark.read.parquet("/user/cloudera/demo/prodeje.parquet")
    
    print("Schéma načtených dat:")
    df_loaded.printSchema()
    
    print("\nUkázka dat:")
    df_loaded.show()
    
    # Provedení několika transformací
    print("\nCelkové množství prodaných produktů podle regionu:")
    df_loaded.groupBy("region") \
        .agg(sum("mnozstvi").alias("celkem_prodano")) \
        .orderBy(desc("celkem_prodano")) \
        .show()
    
    print("\nPrůměrná cena produktů podle typu:")
    df_loaded.groupBy("produkt") \
        .agg(avg("cena").alias("prumerna_cena")) \
        .orderBy(desc("prumerna_cena")) \
        .show()
    
    print("\nCelková hodnota zboží na skladě podle regionu:")
    df_loaded.withColumn("hodnota", col("mnozstvi") * col("cena")) \
        .groupBy("region") \
        .agg(sum("hodnota").alias("celkova_hodnota")) \
        .orderBy(desc("celkova_hodnota")) \
        .show()
    
    # Uložení výsledků do Hive tabulky
    df_loaded.write.mode("overwrite").saveAsTable("prodeje")
    
    print("\nUkazka přístupu k datům přes Hive:")
    spark.sql("SELECT * FROM prodeje LIMIT 5").show()
    
    # Cleanup
    spark.stop()

if __name__ == "__main__":
    print("===== Demonstrace Spark v Cloudera ekosystému =====")
    spark_demo()
    print("===== Konec demonstrace =====") 
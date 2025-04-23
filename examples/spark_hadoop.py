#!/usr/bin/env python3
"""
Základní příklad pro práci se Spark v Hadoop ekosystému.
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, avg, desc

def spark_demo():
    """Ukázka základních Spark operací v Hadoop."""
    # Vytvoření SparkSession s napojením na Hadoop
    spark = SparkSession.builder \
        .appName("SparkHadoopDemo") \
        .master("spark://spark-master:7077") \
        .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:8020") \
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
    
    print("Vytvářím testovací data...")
    
    # Převod na DataFrame
    df = spark.createDataFrame(data)
    
    print("Ukládám data do HDFS v Parquet formátu...")
    
    # Uložení do HDFS v Parquet formátu
    try:
        df.write.mode("overwrite").parquet("hdfs://namenode:8020/user/root/demo/prodeje.parquet")
        print("Data úspěšně uložena")
    except Exception as e:
        print(f"Chyba při ukládání dat: {e}")
        print("Pokračuji s lokálními daty...")
    
    # Načtení z Parquet
    try:
        df_loaded = spark.read.parquet("hdfs://namenode:8020/user/root/demo/prodeje.parquet")
        print("Data úspěšně načtena z HDFS")
    except Exception as e:
        print(f"Chyba při čtení dat z HDFS: {e}")
        print("Používám lokální data...")
        df_loaded = df
    
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
    
    # Export výsledků do CSV
    try:
        result = df_loaded.withColumn("hodnota", col("mnozstvi") * col("cena"))
        result.write.mode("overwrite").csv("hdfs://namenode:8020/user/root/demo/prodeje_export.csv", header=True)
        print("\nExportovaná data uložena do HDFS jako CSV")
    except Exception as e:
        print(f"Chyba při exportu do CSV: {e}")
    
    # Cleanup
    spark.stop()

if __name__ == "__main__":
    print("===== Demonstrace Spark v Hadoop ekosystému =====")
    spark_demo()
    print("===== Konec demonstrace =====") 
#!/usr/bin/env python3
"""
Ukázka práce s Apache Iceberg v Cloudera ekosystému.
Tento skript demonstruje základní operace s tabulkami Iceberg,
včetně Time Travel a Schema Evolution.
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType, DoubleType

def iceberg_demo():
    """Demonstrace práce s Apache Iceberg v Cloudera Data Platform."""
    # Vytvoření SparkSession s podporou Iceberg
    spark = SparkSession.builder \
        .appName("IcebergDemo") \
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkSessionCatalog") \
        .config("spark.sql.catalog.spark_catalog.type", "hive") \
        .config("spark.sql.catalog.local", "org.apache.iceberg.spark.SparkCatalog") \
        .config("spark.sql.catalog.local.type", "hadoop") \
        .config("spark.sql.catalog.local.warehouse", "hdfs://namenode:8020/user/hive/warehouse") \
        .enableHiveSupport() \
        .getOrCreate()
    
    # Definice schématu pro naši tabulku
    schema = StructType([
        StructField("id", IntegerType(), False),
        StructField("produkt", StringType(), True),
        StructField("kategorie", StringType(), True),
        StructField("mnozstvi", IntegerType(), True),
        StructField("cena", DoubleType(), True),
        StructField("timestamp", TimestampType(), True)
    ])
    
    # Vytvoření testovacích dat
    data1 = [
        (1, "Notebook Dell", "Elektronika", 10, 25000.0, current_timestamp()),
        (2, "iPhone 13", "Mobilní telefony", 15, 22000.0, current_timestamp()),
        (3, "Samsung Galaxy Tab", "Tablety", 5, 12000.0, current_timestamp())
    ]
    
    # Vytvoření DataFrame
    df1 = spark.createDataFrame(data1, schema)
    
    # Uložení DataFrame jako Iceberg tabulky
    print("Vytváření Iceberg tabulky...")
    df1.writeTo("local.db.produkty_iceberg") \
        .tableProperty("format-version", "2") \
        .create()
    
    print("První verze tabulky vytvořena.")
    
    # Zobrazení obsahu tabulky
    print("\nObsah Iceberg tabulky (verze 1):")
    spark.read.table("local.db.produkty_iceberg").show()
    
    # Získání historie tabulky
    print("\nHistorie tabulky po prvním zápisu:")
    spark.sql("SELECT * FROM local.db.produkty_iceberg.history").show(truncate=False)
    
    # Přidání nových dat (druhá verze tabulky)
    data2 = [
        (4, "MacBook Pro", "Elektronika", 8, 45000.0, current_timestamp()),
        (5, "iPad Pro", "Tablety", 12, 18000.0, current_timestamp())
    ]
    df2 = spark.createDataFrame(data2, schema)
    
    print("\nPřidání nových dat do Iceberg tabulky...")
    df2.writeTo("local.db.produkty_iceberg").append()
    
    print("Druhá verze tabulky vytvořena.")
    
    # Zobrazení obsahu tabulky po aktualizaci
    print("\nObsah Iceberg tabulky po přidání dat:")
    spark.read.table("local.db.produkty_iceberg").show()
    
    # Ukázka Schema Evolution - přidání nového sloupce
    print("\nSchema Evolution - přidání nového sloupce 'sleva'...")
    
    # Aktualizace dat s novým sloupcem
    data3 = [
        (1, "Notebook Dell", "Elektronika", 10, 25000.0, current_timestamp(), 0.1),
        (2, "iPhone 13", "Mobilní telefony", 15, 22000.0, current_timestamp(), 0.05),
        (3, "Samsung Galaxy Tab", "Tablety", 5, 12000.0, current_timestamp(), 0.15),
        (4, "MacBook Pro", "Elektronika", 8, 45000.0, current_timestamp(), 0.0),
        (5, "iPad Pro", "Tablety", 12, 18000.0, current_timestamp(), 0.1)
    ]
    
    # Rozšířené schéma
    schema_extended = StructType([
        StructField("id", IntegerType(), False),
        StructField("produkt", StringType(), True),
        StructField("kategorie", StringType(), True),
        StructField("mnozstvi", IntegerType(), True),
        StructField("cena", DoubleType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("sleva", DoubleType(), True)
    ])
    
    df3 = spark.createDataFrame(data3, schema_extended)
    
    # Přidání nového sloupce do schématu a aktualizace dat
    df3.writeTo("local.db.produkty_iceberg").overwritePartitions()
    
    print("Třetí verze tabulky vytvořena (s novým sloupcem).")
    
    # Zobrazení aktualizovaného schématu
    print("\nAktualizované schéma tabulky:")
    spark.read.table("local.db.produkty_iceberg").printSchema()
    
    # Zobrazení aktualizovaných dat
    print("\nAktualizovaná data:")
    spark.read.table("local.db.produkty_iceberg").show()
    
    # Time Travel - zobrazení dat z konkrétní verze
    print("\nTime Travel - zobrazení dat z první verze tabulky:")
    spark.read.option("as-of-version", "1") \
        .table("local.db.produkty_iceberg") \
        .show()
    
    # Time Travel - zobrazení dat k určitému času
    print("\nTime Travel - zobrazení dat k určitému časovému okamžiku:")
    # Získání timestamp z historie
    history_df = spark.sql("SELECT * FROM local.db.produkty_iceberg.history")
    history_df.show(truncate=False)
    
    # Clean up
    spark.stop()

if __name__ == "__main__":
    print("===== Demonstrace Apache Iceberg v Cloudera Data Platform =====")
    iceberg_demo()
    print("===== Konec demonstrace =====") 
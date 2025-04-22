#!/usr/bin/env python3

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, count, avg, desc, month, year, round as spark_round, countDistinct, when, lit
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, DateType
import os
import datetime

def create_spark_session():
    """
    Vytvoření Spark session s JDBC driverem pro PostgreSQL
    """
    spark = SparkSession.builder \
        .appName("Sales Analysis") \
        .config("spark.jars", "/opt/spark/jars/postgresql-42.6.0.jar") \
        .getOrCreate()
    
    print("Spark session vytvořena!")
    return spark

def load_data(spark, customers_file, sales_file):
    """
    Načtení dat z CSV souborů
    """
    # Schéma pro zákazníky
    customer_schema = StructType([
        StructField("customer_id", IntegerType(), False),
        StructField("first_name", StringType(), True),
        StructField("last_name", StringType(), True),
        StructField("email", StringType(), True),
        StructField("region", StringType(), True),
        StructField("country", StringType(), True),
        StructField("registration_date", DateType(), True)
    ])
    
    # Schéma pro prodeje
    sales_schema = StructType([
        StructField("sale_id", StringType(), False),
        StructField("customer_id", IntegerType(), False),
        StructField("sale_date", DateType(), True),
        StructField("category", StringType(), True),
        StructField("product", StringType(), True),
        StructField("quantity", IntegerType(), True),
        StructField("price", DoubleType(), True),
        StructField("total", DoubleType(), True),
        StructField("payment_method", StringType(), True)
    ])
    
    # Načtení dat
    customers_df = spark.read.csv(customers_file, header=True, schema=customer_schema)
    sales_df = spark.read.csv(sales_file, header=True, schema=sales_schema)
    
    print(f"Načteno {customers_df.count()} zákazníků a {sales_df.count()} prodejů")
    return customers_df, sales_df

def analyze_data(customers_df, sales_df):
    """
    Provedení komplexních analýz
    """
    # 1. Statistika prodejů podle kategorií
    print("Provádím analýzu prodejů podle kategorií...")
    category_stats = sales_df.groupBy("category") \
        .agg(
            count("sale_id").alias("number_of_sales"),
            sum("total").alias("total_sales_amount"),
            avg("price").alias("average_price"),
            sum("quantity").alias("total_quantity")
        ) \
        .orderBy(desc("total_sales_amount"))
    
    # 2. Statistika zákazníků podle regionů
    print("Provádím analýzu zákazníků podle regionů...")
    region_stats = customers_df.join(sales_df, "customer_id") \
        .groupBy("region") \
        .agg(
            countDistinct("customer_id").alias("number_of_customers"),
            count("sale_id").alias("number_of_sales"),
            sum("total").alias("total_sales_amount"),
            (sum("total") / countDistinct("customer_id")).alias("average_per_customer")
        ) \
        .orderBy(desc("total_sales_amount"))
    
    # 3. Top 10 nejlepších zákazníků
    print("Identifikuji top 10 zákazníků...")
    top_customers = sales_df.groupBy("customer_id") \
        .agg(
            count("sale_id").alias("number_of_purchases"),
            sum("total").alias("total_spent")
        ) \
        .orderBy(desc("total_spent")) \
        .limit(10) \
        .join(customers_df, "customer_id") \
        .select(
            "customer_id", 
            "first_name", 
            "last_name", 
            "email", 
            "region", 
            "country", 
            "number_of_purchases", 
            "total_spent"
        )
    
    # 4. Časová analýza prodejů podle měsíců
    print("Provádím časovou analýzu prodejů...")
    time_analysis = sales_df \
        .withColumn("year", year("sale_date")) \
        .withColumn("month", month("sale_date")) \
        .groupBy("year", "month") \
        .agg(
            count("sale_id").alias("number_of_sales"),
            sum("total").alias("total_sales_amount"),
            avg("total").alias("average_sale_value")
        ) \
        .orderBy("year", "month")
    
    # 5. Analýza platebních metod
    print("Provádím analýzu platebních metod...")
    payment_analysis = sales_df.groupBy("payment_method") \
        .agg(
            count("sale_id").alias("number_of_sales"),
            sum("total").alias("total_amount"),
            avg("total").alias("average_amount")
        ) \
        .orderBy(desc("total_amount"))
    
    # 6. Komplexní analýza prodejů podle zemí a kategorií
    print("Provádím komplexní analýzu podle zemí a kategorií...")
    country_category_analysis = customers_df.join(sales_df, "customer_id") \
        .groupBy("country", "category") \
        .agg(
            count("sale_id").alias("number_of_sales"),
            sum("total").alias("total_sales"),
            avg("price").alias("average_price")
        ) \
        .orderBy("country", desc("total_sales"))
    
    return {
        "category_stats": category_stats,
        "region_stats": region_stats,
        "top_customers": top_customers,
        "time_analysis": time_analysis,
        "payment_analysis": payment_analysis,
        "country_category_analysis": country_category_analysis
    }

def save_to_hdfs(spark, results, output_dir):
    """
    Uložení výsledků do HDFS
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base_path = f"{output_dir}/{timestamp}"
    
    print(f"Ukládám výsledky do HDFS: {base_path}")
    
    for name, df in results.items():
        path = f"{base_path}/{name}"
        print(f"Ukládám {name} do {path}")
        
        # Přidání časového razítka pro auditní účely
        df_with_timestamp = df.withColumn("analysis_date", lit(timestamp))
        
        # Uložení ve formátu Parquet
        df_with_timestamp.write.mode("overwrite").parquet(path)
    
    print("Všechny výsledky byly uloženy do HDFS!")

def save_to_postgres(results, jdbc_url, properties):
    """
    Uložení výsledků do PostgreSQL
    """
    print("Ukládám výsledky do PostgreSQL...")
    
    for name, df in results.items():
        table_name = f"sales_analysis_{name}"
        print(f"Ukládám {name} do tabulky {table_name}")
        
        # Uložení do PostgreSQL
        df.write \
            .jdbc(url=jdbc_url, table=table_name, mode="overwrite", properties=properties)
    
    print("Všechny výsledky byly uloženy do PostgreSQL!")

def main():
    """
    Hlavní funkce aplikace
    """
    # Nastavení cesty k datům
    input_dir = "/app/data"
    customers_file = f"{input_dir}/customers.csv"
    sales_file = f"{input_dir}/sales.csv"
    
    # HDFS výstupní adresář
    hdfs_output_dir = "hdfs://namenode:9000/data/sales_analysis"
    
    # PostgreSQL připojení
    jdbc_url = "jdbc:postgresql://postgres:5434/dataengineering"
    properties = {
        "user": "postgres",
        "password": "postgres",
        "driver": "org.postgresql.Driver"
    }
    
    # Vytvoření Spark session
    spark = create_spark_session()
    
    try:
        # Načtení dat
        customers_df, sales_df = load_data(spark, customers_file, sales_file)
        
        # Cache pro lepší výkon
        customers_df.cache()
        sales_df.cache()
        
        # Analýza dat
        results = analyze_data(customers_df, sales_df)
        
        # Uložení výsledků do HDFS
        save_to_hdfs(spark, results, hdfs_output_dir)
        
        # Uložení výsledků do PostgreSQL
        save_to_postgres(results, jdbc_url, properties)
        
    finally:
        # Uvolnění cache a ukončení session
        spark.stop()
        print("Spark session ukončena!")

if __name__ == "__main__":
    main() 
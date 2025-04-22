// Nastavení logování
import org.apache.log4j.{Level, Logger}
Logger.getLogger("org").setLevel(Level.WARN)

// Cesta k datům v HDFS
val dataPath = "hdfs://namenode:9000/data/sales_analysis/20250422_141355/top_customers"

// Načtení dat z Parquet souboru
val topCustomers = spark.read.parquet(dataPath)

// Zobrazení dat
println("=== TOP 10 ZÁKAZNÍKŮ ===")
topCustomers.show(false)

// Výpis schématu
println("=== SCHÉMA DAT ===")
topCustomers.printSchema()

// Ukončení
System.exit(0) 
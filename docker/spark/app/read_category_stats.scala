// Nastavení logování
import org.apache.log4j.{Level, Logger}
Logger.getLogger("org").setLevel(Level.WARN)

// Cesta k datům v HDFS
val dataPath = "hdfs://namenode:9000/data/sales_analysis/20250422_141355/category_stats"

// Načtení dat z Parquet souboru
val categoryStats = spark.read.parquet(dataPath)

// Zobrazení dat
println("=== STATISTIKA PRODEJŮ PODLE KATEGORIÍ ===")
categoryStats.show(false)

// Výpis schématu
println("=== SCHÉMA DAT ===")
categoryStats.printSchema()

// Ukončení
System.exit(0) 
// Nastavení logování
import org.apache.log4j.{Level, Logger}
Logger.getLogger("org").setLevel(Level.WARN)

// Cesta k datům v HDFS
val dataPath = "hdfs://namenode:9000/data/sales_analysis/20250422_141355/region_stats"

// Načtení dat z Parquet souboru
val regionStats = spark.read.parquet(dataPath)

// Zobrazení dat
println("=== STATISTIKA PRODEJŮ PODLE REGIONŮ ===")
regionStats.show(false)

// Výpis schématu
println("=== SCHÉMA DAT ===")
regionStats.printSchema()

// Ukončení
System.exit(0) 
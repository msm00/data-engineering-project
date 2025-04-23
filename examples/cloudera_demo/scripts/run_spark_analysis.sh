#!/bin/bash

# Skript pro spuštění PySpark analýzy
# Tento skript demonstruje použití Apache Spark v rámci Hadoop ekosystému

echo "Připojuji se k Spark clusteru..."

# Vytvoření adresáře pro výstupy v HDFS
echo "Vytvářím adresář pro výstupy v HDFS..."
docker exec -it namenode hdfs dfs -mkdir -p /data/processed

# Spuštění PySpark analýzy
echo "Spouštím pokročilou analýzu dat pomocí PySpark..."
docker exec -it spark-master bash -c "cd /data/examples/cloudera_demo/spark && python advanced_analysis.py"

# Kontrola výsledků v HDFS
echo "Kontrola výsledků v HDFS:"
docker exec -it namenode hdfs dfs -ls -R /data/processed

echo "Spark analýza dokončena." 
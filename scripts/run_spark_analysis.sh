#!/bin/bash

# Skript pro spuštění PySpark analýzy
# Tento skript demonstruje použití Apache Spark v rámci Hadoop ekosystému

echo "Připojuji se k Spark clusteru..."

# Vytvoření adresáře pro výstupy v HDFS
echo "Vytvářím adresář pro výstupy v HDFS..."
docker exec -it namenode hdfs dfs -mkdir -p /data/processed

# Kopírování PySpark skriptu do kontejneru
echo "Kopíruji PySpark skript do Spark master kontejneru..."
docker cp ../spark/advanced_analysis.py spark-master:/tmp/advanced_analysis.py

# Instalace potřebných Python balíčků do kontejneru
echo "Instaluji potřebné Python balíčky..."
docker exec -it spark-master pip install pandas matplotlib

# Spuštění PySpark analýzy
echo "Spouštím pokročilou analýzu dat pomocí PySpark..."
docker exec -it spark-master bash -c "cd /tmp && python advanced_analysis.py"

# Kontrola výsledků v HDFS
echo "Kontrola výsledků v HDFS:"
docker exec -it namenode hdfs dfs -ls -R /data/processed

echo "Spark analýza dokončena." 
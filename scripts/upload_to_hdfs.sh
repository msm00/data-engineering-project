#!/bin/bash

# Skript pro nahrání dat do HDFS (Hadoop Distributed File System)
# Tento skript demonstruje základní práci s HDFS v rámci Hadoop ekosystému

echo "Připojuji se k Hadoop HDFS..."

# Kopírování CSV souborů do kontejneru
echo "Kopíruji CSV soubory do namenode kontejneru..."
docker cp ../data/prodeje_2024.csv namenode:/tmp/prodeje_2024.csv
docker cp ../data/zakaznici.csv namenode:/tmp/zakaznici.csv

# Vytvoření adresářové struktury v HDFS
docker exec -it namenode hdfs dfs -mkdir -p /data/raw/prodeje
docker exec -it namenode hdfs dfs -mkdir -p /data/raw/zakaznici

# Nahrání CSV souborů do HDFS
echo "Nahrávám data o prodejích do HDFS..."
docker exec -it namenode hdfs dfs -put /tmp/prodeje_2024.csv /data/raw/prodeje/

echo "Nahrávám data o zákaznících do HDFS..."
docker exec -it namenode hdfs dfs -put /tmp/zakaznici.csv /data/raw/zakaznici/

# Kontrola nahraných dat
echo "Kontrola struktury HDFS:"
docker exec -it namenode hdfs dfs -ls -R /data

echo "Zobrazení části dat o prodejích:"
docker exec -it namenode hdfs dfs -cat /data/raw/prodeje/prodeje_2024.csv | head -5

echo "Zobrazení části dat o zákaznících:"
docker exec -it namenode hdfs dfs -cat /data/raw/zakaznici/zakaznici.csv | head -5

echo "Data byla úspěšně nahrána do HDFS." 
#!/bin/bash

# Nastavení proměnných
INPUT_DIR="/app/data"
HDFS_DIR="/data/sales_analysis"
CSV_DIR="/project/data/spark"

echo "Spark Analýza prodejů - Start"

# Vytvoření adresáře pro data
mkdir -p ${INPUT_DIR}

# Kontrola existence dat v HDFS
echo "Kontroluji existenci adresáře ${HDFS_DIR} v HDFS..."
if hdfs dfs -test -d ${HDFS_DIR}; then
    echo "Adresář ${HDFS_DIR} již existuje v HDFS"
else
    echo "Vytvářím adresář ${HDFS_DIR} v HDFS..."
    hdfs dfs -mkdir -p ${HDFS_DIR}
fi

# Kopírování CSV dat do kontejneru
echo "Kopíruji CSV soubory do kontejneru..."
cp ${CSV_DIR}/*.csv ${INPUT_DIR}/

# Spuštění Spark analýzy
echo "Spouštím Spark analýzu..."
python3 /app/sales_analysis.py

echo "Spark Analýza prodejů - Konec" 
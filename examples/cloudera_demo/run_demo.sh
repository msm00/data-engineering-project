#!/bin/bash

# Hlavní skript pro demonstraci Cloudera-like Big Data workflow
# Tento skript postupně spustí všechny kroky Big Data zpracování
# v rámci Hadoop ekosystému

echo "============================================================"
echo "      CLOUDERA DEMO - Big Data Processing Workflow"
echo "============================================================"
echo ""

# 1. Nahrání dat do HDFS
echo "KROK 1: Nahrání dat do HDFS"
echo "------------------------------------------------------------"
cd scripts
bash upload_to_hdfs.sh
echo ""

# 2. Hive analýza - SQL a datový sklad
echo "KROK 2: Hive analýza - SQL a datový sklad"
echo "------------------------------------------------------------"
bash run_hive_queries.sh
echo ""

# 3. Spark analýza - ML a pokročilé zpracování dat
echo "KROK 3: Spark analýza - ML a pokročilé zpracování dat"
echo "------------------------------------------------------------"
bash run_spark_analysis.sh
echo ""

echo "============================================================"
echo "            DEMO DOKONČENO ÚSPĚŠNĚ"
echo "============================================================"
echo ""
echo "WebUI přístupy:"
echo "- HDFS NameNode: http://localhost:9870"
echo "- YARN ResourceManager: http://localhost:8088"
echo "- Spark Master: http://localhost:8080"
echo "- Hue: http://localhost:8889"
echo "- Jupyter: http://localhost:8890"
echo ""
echo "Doporučené další kroky:"
echo "1. Prohlédnout výsledky v Hue rozhraní"
echo "2. Prozkoumat možnosti interaktivní analýzy v Jupyter Notebooku"
echo "3. Podívat se na monitoring úloh v YARN a Spark UI" 
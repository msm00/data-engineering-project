#!/bin/bash

# Čekání na dostupnost NameNode (port 9000)
echo "Čekám na dostupnost NameNode..."
while ! nc -z namenode 9000; do
  sleep 3
done
echo "NameNode je dostupný, spouštím DataNode..."

# Spuštění datanode
$HADOOP_HOME/bin/hdfs --daemon start datanode

# Udržení kontejneru spuštěného
echo "DataNode spuštěn, ponechávám kontejner běžet..."
tail -f /data/logs/* $HADOOP_HOME/logs/* 
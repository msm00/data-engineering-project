#!/bin/bash

# Čekání na dostupnost ResourceManager (port 8088)
echo "Čekám na dostupnost ResourceManager..."
while ! nc -z resourcemanager 8088; do
  sleep 3
done
echo "ResourceManager je dostupný, spouštím NodeManager..."

# Spuštění NodeManager
$HADOOP_HOME/bin/yarn --daemon start nodemanager

# Udržení kontejneru spuštěného
echo "NodeManager spuštěn, ponechávám kontejner běžet..."
tail -f $HADOOP_HOME/logs/* 
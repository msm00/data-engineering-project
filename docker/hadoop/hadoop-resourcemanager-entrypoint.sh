#!/bin/bash

# Čekání na dostupnost NameNode (port 9000)
echo "Čekám na dostupnost NameNode..."
while ! nc -z namenode 9000; do
  sleep 3
done
echo "NameNode je dostupný, spouštím ResourceManager..."

# Spuštění ResourceManager
$HADOOP_HOME/bin/yarn --daemon start resourcemanager

# Udržení kontejneru spuštěného
echo "ResourceManager spuštěn, ponechávám kontejner běžet..."
tail -f $HADOOP_HOME/logs/* 
#!/bin/bash

# Kontrola, zda je namenode adresář prázdný
if [ -z "$(ls -A /data/namenode)" ]; then
    echo "Inicializuji namenode..."
    # Formátování HDFS při prvním spuštění
    $HADOOP_HOME/bin/hdfs namenode -format -force
fi

# Spuštění namenode
$HADOOP_HOME/bin/hdfs --daemon start namenode
# Spuštění HTTP serveru pro monitoring
$HADOOP_HOME/bin/hdfs --daemon start httpfs

# Udržení kontejneru spuštěného
echo "NameNode spuštěn, ponechávám kontejner běžet..."
tail -f /data/logs/* $HADOOP_HOME/logs/* 
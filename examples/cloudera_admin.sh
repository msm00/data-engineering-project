#!/bin/bash
# Základní administrace a monitoring Cloudera

# Nastavení proměnných
HADOOP_HOME=/usr/lib/hadoop
HDFS_HOME=/usr/lib/hadoop-hdfs
HIVE_HOME=/usr/lib/hive
SPARK_HOME=/usr/lib/spark

echo "===== Cloudera administrace a monitoring ====="

echo -e "\n1. Kontrola stavu HDFS:"
$HADOOP_HOME/bin/hdfs dfsadmin -report | head -20

echo -e "\n2. Kontrola stavu YARN:"
$HADOOP_HOME/bin/yarn node -list

echo -e "\n3. Kontrola aktivních YARN aplikací:"
$HADOOP_HOME/bin/yarn application -list

echo -e "\n4. Kontrola Hive metastore:"
$HIVE_HOME/bin/hive --service metatool -listFSRoot

echo -e "\n5. Kontrola stavu HDFS souborového systému:"
$HADOOP_HOME/bin/hdfs dfs -df -h

echo -e "\n6. Diagnostika HDFS zdraví:"
$HADOOP_HOME/bin/hdfs fsck / | grep -i corrupt

echo -e "\n7. Kontrola HDFS safe mode:"
$HADOOP_HOME/bin/hdfs dfsadmin -safemode get

echo -e "\n8. Výpis běžících Spark aplikací:"
$SPARK_HOME/bin/spark-submit --status

echo -e "\n9. Kontrola využití diskového prostoru:"
df -h

echo -e "\n10. Kontrola vytížení systému:"
top -b -n 1 | head -15

echo "===== Konec administrace a monitoringu =====" 
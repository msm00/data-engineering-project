#!/bin/bash
# Základní administrace a monitoring Apache Hadoop

echo "===== Apache Hadoop administrace a monitoring ====="

echo -e "\n1. Kontrola stavu HDFS:"
hdfs dfsadmin -report | head -20

echo -e "\n2. Kontrola stavu YARN clusteru:"
yarn node -list

echo -e "\n3. Kontrola aktivních YARN aplikací:"
yarn application -list

echo -e "\n4. Kontrola stavu HDFS souborového systému:"
hdfs dfs -df -h

echo -e "\n5. Kontrola HDFS adresářů:"
hdfs dfs -ls /

echo -e "\n6. Diagnostika HDFS zdraví:"
hdfs fsck / | grep -i corrupt

echo -e "\n7. Kontrola HDFS safe mode:"
hdfs dfsadmin -safemode get

echo -e "\n8. Informace o konfiguraci HDFS:"
hdfs getconf -confKey dfs.replication
hdfs getconf -confKey dfs.blocksize

echo -e "\n9. Kontrola běžících Java procesů:"
jps

echo -e "\n10. Informace o všech uzlech clusteru:"
hdfs dfsadmin -printTopology

echo -e "\n11. Kontrola dostupného diskového prostoru:"
df -h

echo -e "\n12. Kontrola vytížení systému:"
top -b -n 1 | head -15

echo "===== Konec administrace a monitoringu =====" 
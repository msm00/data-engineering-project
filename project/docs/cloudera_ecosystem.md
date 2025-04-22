# Cloudera Data Platform - Ekosystém

## Úvod do Cloudera Data Platform (CDP)

Cloudera Data Platform (CDP) je integrovaná datová platforma, která kombinuje nejlepší open-source technologie pro zpracování dat v celém jejich životním cyklu. CDP poskytuje jednotné řešení pro sběr, zpracování, analýzu a správu dat napříč on-premise infrastrukturou i veřejnými cloudy.

### Klíčové komponenty CDP

1. **CDP Private Cloud Base**
   - On-premise nasazení postavené na distribuci Hadoop
   - Zahrnuje Cloudera Runtime (HDFS, YARN, Hive, HBase, Spark, Kafka, atd.)
   - Integrovaná správa a zabezpečení

2. **CDP Private Cloud Data Services**
   - Kontejnerizované služby pro analýzu dat, ML a streaming
   - Škálovatelná architektura postavená na Kubernetes
   - Samoobslužný přístup pro datové týmy

3. **CDP Public Cloud**
   - Datové služby běžící v AWS, Azure a Google Cloud
   - Automatické škálování a správa zdrojů
   - Jednotná správa zabezpečení a governance

### Architektura CDP

CDP je postavena na následujících vrstvách:

1. **Datová vrstva (Storage)**
   - HDFS, S3, ADLS, Cloud Storage
   - Objektové úložiště s podporou strukturovaných i nestrukturovaných dat

2. **Výpočetní vrstva (Compute)**
   - Spark, MapReduce, Tez, Impala
   - Oddělená od datové vrstvy pro lepší škálování

3. **Analytická vrstva (Analytics)**
   - Hive, Impala, Kudu pro SQL analýzy
   - NiFi pro datovou ingesi
   - Spark a Hadoop pro batch processing
   - Kafka a Flink pro stream processing
   - HBase, Phoenix pro NoSQL databáze

4. **ML a AI vrstva**
   - Cloudera Machine Learning (CML)
   - Podpora Jupyter, R Studio, TensorFlow, PyTorch
   - MLOps funkce pro nasazení a monitoring modelů

5. **Governance a Security vrstva**
   - Atlas pro metadata management
   - Ranger pro řízení přístupu
   - Navigator pro audit a data lineage
   - Knox pro autentizaci

## Docker konfigurace pro Cloudera komponenty

### Lokální vývojové prostředí s Docker

Pro účely vývoje a testování lze využít Docker kontejnery simulující Cloudera ekosystém. Níže je příklad docker-compose konfigurace pro základní Cloudera komponenty:

```yaml
version: '3'

services:
  # HDFS NameNode
  namenode:
    image: cloudera/quickstart:latest
    hostname: namenode
    container_name: namenode
    ports:
      - "8020:8020"  # HDFS
      - "50070:50070"  # NameNode Web UI
    environment:
      - CLUSTER_NAME=cdp-dev-cluster
    volumes:
      - namenode_data:/var/lib/hadoop-hdfs/cache/hdfs/dfs/name
    command: /etc/bootstrap.sh -d

  # HDFS DataNode
  datanode:
    image: cloudera/quickstart:latest
    hostname: datanode
    container_name: datanode
    depends_on:
      - namenode
    ports:
      - "50075:50075"  # DataNode Web UI
    volumes:
      - datanode_data:/var/lib/hadoop-hdfs/cache/hdfs/dfs/data
    command: /etc/bootstrap.sh -d

  # YARN ResourceManager
  resourcemanager:
    image: cloudera/quickstart:latest
    hostname: resourcemanager
    container_name: resourcemanager
    depends_on:
      - namenode
    ports:
      - "8088:8088"  # ResourceManager Web UI
      - "8032:8032"  # ResourceManager
    command: /etc/bootstrap.sh -d

  # Hive Server
  hive:
    image: cloudera/quickstart:latest
    hostname: hive
    container_name: hive
    depends_on:
      - namenode
      - resourcemanager
    ports:
      - "10000:10000"  # HiveServer2
      - "10002:10002"  # HiveServer2 Web UI
    command: /etc/bootstrap.sh -d

  # Spark History Server
  spark:
    image: cloudera/quickstart:latest
    hostname: spark
    container_name: spark
    depends_on:
      - namenode
      - resourcemanager
    ports:
      - "4040:4040"  # Spark UI
      - "18080:18080"  # Spark History Server
    command: /etc/bootstrap.sh -d

volumes:
  namenode_data:
  datanode_data:
```

### Vlastní konfigurace CDP komponent

Pro pokročilejší scénáře lze vytvořit vlastní Dockerfile pro CDP komponenty:

```Dockerfile
FROM centos:7

# Instalace závislostí
RUN yum -y install java-1.8.0-openjdk java-1.8.0-openjdk-devel wget curl which

# Nastavení Java
ENV JAVA_HOME /usr/lib/jvm/java-1.8.0-openjdk
ENV PATH $PATH:$JAVA_HOME/bin

# Stažení a instalace Hadoop
ENV HADOOP_VERSION 3.1.1
ENV HADOOP_URL https://archive.apache.org/dist/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz
ENV HADOOP_HOME /opt/hadoop

RUN mkdir -p /opt/hadoop && \
    wget -q $HADOOP_URL && \
    tar -xzf hadoop-$HADOOP_VERSION.tar.gz -C /opt && \
    rm hadoop-$HADOOP_VERSION.tar.gz && \
    mv /opt/hadoop-$HADOOP_VERSION/* $HADOOP_HOME && \
    rmdir /opt/hadoop-$HADOOP_VERSION

# Konfigurace Hadoop
COPY config/hdfs-site.xml $HADOOP_HOME/etc/hadoop/
COPY config/core-site.xml $HADOOP_HOME/etc/hadoop/
COPY config/mapred-site.xml $HADOOP_HOME/etc/hadoop/
COPY config/yarn-site.xml $HADOOP_HOME/etc/hadoop/

# Nastavení Hadoop proměnných
ENV PATH $PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
ENV HADOOP_CONF_DIR $HADOOP_HOME/etc/hadoop

# Instalace Hive
ENV HIVE_VERSION 3.1.2
ENV HIVE_URL https://archive.apache.org/dist/hive/hive-$HIVE_VERSION/apache-hive-$HIVE_VERSION-bin.tar.gz
ENV HIVE_HOME /opt/hive

RUN mkdir -p /opt/hive && \
    wget -q $HIVE_URL && \
    tar -xzf apache-hive-$HIVE_VERSION-bin.tar.gz -C /opt && \
    rm apache-hive-$HIVE_VERSION-bin.tar.gz && \
    mv /opt/apache-hive-$HIVE_VERSION-bin/* $HIVE_HOME && \
    rmdir /opt/apache-hive-$HIVE_VERSION-bin

# Konfigurace Hive
COPY config/hive-site.xml $HIVE_HOME/conf/

# Nastavení Hive proměnných
ENV PATH $PATH:$HIVE_HOME/bin
ENV HIVE_CONF_DIR $HIVE_HOME/conf

# Instalace Spark
ENV SPARK_VERSION 3.1.2
ENV SPARK_URL https://archive.apache.org/dist/spark/spark-$SPARK_VERSION/spark-$SPARK_VERSION-bin-hadoop3.2.tgz
ENV SPARK_HOME /opt/spark

RUN mkdir -p /opt/spark && \
    wget -q $SPARK_URL && \
    tar -xzf spark-$SPARK_VERSION-bin-hadoop3.2.tgz -C /opt && \
    rm spark-$SPARK_VERSION-bin-hadoop3.2.tgz && \
    mv /opt/spark-$SPARK_VERSION-bin-hadoop3.2/* $SPARK_HOME && \
    rmdir /opt/spark-$SPARK_VERSION-bin-hadoop3.2

# Konfigurace Spark
COPY config/spark-defaults.conf $SPARK_HOME/conf/
COPY config/hive-site.xml $SPARK_HOME/conf/

# Nastavení Spark proměnných
ENV PATH $PATH:$SPARK_HOME/bin
ENV SPARK_CONF_DIR $SPARK_HOME/conf

# Vstupní skript
COPY scripts/entrypoint.sh /
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
```

## Základní administrace a monitoring

### Administrace CDP

#### 1. Cloudera Manager

Cloudera Manager je centralizovaný nástroj pro správu a monitoring celého CDP ekosystému:

- **Instalace a konfigurace služeb**
  - Průvodce instalací nových služeb
  - Správa konfiguračních souborů s validací
  - Distribuce konfigurací na všechny nody

- **Správa clusteru**
  - Start/stop/restart služeb
  - Rolling upgrade s minimálním výpadkem
  - Přidávání a odebírání nodů
  - Balancování zatížení

- **Správa uživatelů a oprávnění**
  - Integrace s LDAP/Active Directory
  - Role-based access control (RBAC)
  - Delegování administrace

#### 2. Kerberos integrace

CDP podporuje Kerberos autentizaci pro zabezpečení clusteru:

```bash
# Instalace Kerberos server
sudo apt-get install krb5-kdc krb5-admin-server

# Konfigurace Kerberos pro CDP
sudo kadmin.local -q "addprinc -randkey hdfs/namenode.example.com@EXAMPLE.COM"
sudo kadmin.local -q "addprinc -randkey yarn/resourcemanager.example.com@EXAMPLE.COM"
sudo kadmin.local -q "addprinc -randkey hive/hiveserver.example.com@EXAMPLE.COM"

# Export keytab souborů
sudo kadmin.local -q "ktadd -k /etc/hadoop/hdfs.keytab hdfs/namenode.example.com@EXAMPLE.COM"
```

#### 3. Ranger pro řízení přístupu

Apache Ranger poskytuje centralizovanou správu politik pro řízení přístupu:

- Definice politik pro HDFS, Hive, HBase, Kafka, atd.
- Řízení přístupu na úrovni sloupců a řádků
- Audit všech přístupů k datům

### Monitoring CDP

#### 1. Cloudera Manager Monitoring

Cloudera Manager nabízí komplexní monitoring:

- **Zdraví systému**
  - Status služeb a jejich komponent
  - Automatická detekce problémů a alerting
  - Diagnostické nástroje pro řešení problémů

- **Výkonnostní metriky**
  - Využití CPU, paměti, disku a sítě
  - HDFS využití a zdraví
  - Metriky specifické pro jednotlivé služby

- **Logování**
  - Centralizovaný sběr logů
  - Vyhledávání a analýza logů
  - Korelace událostí mezi službami

#### 2. Implementace vlastního monitoringu

Pro specifické potřeby lze implementovat vlastní monitoring pomocí Prometheus a Grafana:

```yaml
version: '3'

services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'

  grafana:
    image: grafana/grafana:latest
    depends_on:
      - prometheus
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false

volumes:
  grafana_data:
```

Příklad konfigurace `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'hadoop'
    static_configs:
      - targets: ['namenode:9870', 'datanode:9864', 'resourcemanager:8088']

  - job_name: 'spark'
    static_configs:
      - targets: ['spark:18080']

  - job_name: 'hive'
    static_configs:
      - targets: ['hive:10002']
```

#### 3. Alerting

Nastavení alertů v Cloudera Manager:

- **Kritické alerty**
  - Nedostatek místa na HDFS
  - Selhání NameNode nebo DataNode
  - Vysoké zatížení systému

- **Varovné alerty**
  - Nízká replikace HDFS bloků
  - Dlouhotrvající Spark úlohy
  - Abnormální využití paměti nebo CPU

## Praktické cvičení

### Cvičení 1: Nasazení CDP Mini-Clusteru pomocí Dockeru

1. Vytvořte adresářovou strukturu pro konfigurační soubory:

```bash
mkdir -p cdp-docker/{config,scripts,data}
cd cdp-docker
```

2. Vytvořte `docker-compose.yml` s základními CDP komponentami (HDFS, YARN, Hive, Spark)

3. Nakonfigurujte jednotlivé komponenty a spusťte cluster:

```bash
docker-compose up -d
```

4. Otestujte funkčnost clusteru:

```bash
# Přístup k HDFS
docker exec -it namenode hdfs dfs -ls /

# Spuštění Spark aplikace
docker exec -it spark spark-submit --class org.apache.spark.examples.SparkPi \
    --master yarn \
    --deploy-mode cluster \
    $SPARK_HOME/examples/jars/spark-examples*.jar 10
```

### Cvičení 2: Implementace Data Pipeline v CDP

1. Vytvořte jednoduchou ETL pipeline s využitím různých CDP komponent:
   - Příjem dat pomocí NiFi nebo Kafka
   - Zpracování pomocí Spark
   - Uložení do Hive
   - Vizualizace pomocí Superset

2. Otestujte výkon a škálovatelnost řešení

### Cvičení 3: Zabezpečení a Governance

1. Nakonfigurujte Ranger politiky pro přístup k datům
2. Implementujte Kerberos autentizaci
3. Nastavte Atlas pro správu metadat a lineage

## Souhrn

Cloudera Data Platform poskytuje komplexní řešení pro datové inženýrství, vědu o datech a analýzu. Výhodou CDP je:

1. **Jednotná platforma** pro celý životní cyklus dat
2. **Hybridní přístup** podporující on-premise i cloudová nasazení
3. **Integrované zabezpečení a governance** prostřednictvím SDX
4. **Škálovatelnost** od malých nasazení po enterprise clustery
5. **Otevřené standardy** založené na populárních open-source projektech

CDP je ideální volbou pro organizace, které potřebují zpracovávat velké objemy dat, zajistit jejich bezpečnost a compliance, a poskytovat datové služby různým týmům napříč organizací.

## Doporučené zdroje

- [Oficiální dokumentace Cloudera](https://docs.cloudera.com/)
- [Cloudera Community](https://community.cloudera.com/)
- [CDP Reference Architecture](https://www.cloudera.com/content/dam/www/marketing/resources/reference-architectures/cloudera-data-platform-reference-architecture.pdf) 
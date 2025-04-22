FROM openjdk:8-jdk-slim

# Nastavení proměnných prostředí
ENV HADOOP_VERSION=3.3.4
ENV HADOOP_HOME=/opt/hadoop
ENV HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

# Instalace základních nástrojů
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget \
    curl \
    gnupg \
    procps \
    netcat \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Stažení a instalace Hadoop z archivního serveru
RUN wget -q https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz && \
    tar -xzf hadoop-${HADOOP_VERSION}.tar.gz -C /opt/ && \
    mv /opt/hadoop-${HADOOP_VERSION} $HADOOP_HOME && \
    rm hadoop-${HADOOP_VERSION}.tar.gz

# Vytvoření adresářů pro HDFS
RUN mkdir -p /data/namenode /data/datanode /data/logs

# Kopírování konfiguračních souborů
COPY config/* $HADOOP_HOME/etc/hadoop/

# Nastavení pracovního adresáře
WORKDIR $HADOOP_HOME

# Defaultní port HDFS Web UI
EXPOSE 9870 9864 8088

CMD ["/bin/bash"] 
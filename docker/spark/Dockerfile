FROM openjdk:11-slim

# Nastavení proměnných prostředí
ENV SPARK_VERSION=3.3.2
ENV HADOOP_VERSION=3
ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:$SPARK_HOME/bin

# Instalace základních nástrojů a Python
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget \
    python3 \
    python3-pip \
    python3-setuptools \
    && rm -rf /var/lib/apt/lists/*

# Instalace PySpark závislostí
RUN pip3 install --no-cache-dir pyspark==${SPARK_VERSION} numpy pandas

# Stažení a instalace Spark
RUN wget -q https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
    tar -xzf spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz -C /opt/ && \
    mv /opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} $SPARK_HOME && \
    rm spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz

# Stažení ovladače JDBC pro Postgres
RUN wget -q https://jdbc.postgresql.org/download/postgresql-42.6.0.jar -O $SPARK_HOME/jars/postgresql-42.6.0.jar

# Vytvoření pracovního adresáře
WORKDIR /app

# Spark porty
EXPOSE 4040 8080 7077

CMD ["bash"] 
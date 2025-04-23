# Cloudera Ekosystém - Praktické Příklady

Tento adresář obsahuje materiály a příklady pro pochopení Cloudera ekosystému v rámci školení "Accelerated Data Engineering Course".

## Co je Cloudera?

Cloudera je společnost poskytující enterprise distribuci Hadoop a souvisejících projektů. Cloudera Data Platform (CDP) je komplexní cloudová platforma pro správu dat, která integruje nástroje pro analýzu, zpracování a správu velkých dat.

## Klíčové komponenty Cloudera ekosystému

### 1. Hadoop Core
- **HDFS** - Distribuovaný souborový systém
- **YARN** - Resource Manager pro distribuované aplikace
- **MapReduce** - Framework pro distribuované zpracování

### 2. Zpracování dat
- **Apache Spark** - Engine pro rychlé distribuované zpracování dat
- **Apache Hive** - Data warehouse poskytující SQL rozhraní
- **Apache Impala** - MPP (massively parallel processing) SQL engine

### 3. Správa a Monitoring
- **Cloudera Manager** - Centralizovaná správa celého clusteru
- **Monitoring** - Nástroje pro sledování výkonu a stavu clusteru

### 4. Bezpečnost
- **Apache Ranger** - Správa autorizací a přístupových práv
- **Apache Atlas** - Metadata management a data governance
- **Kerberos** - Autentizace

## Praktické příklady v tomto adresáři

1. **docker-compose-cloudera.yml** - Konfigurace Docker Compose pro spuštění Cloudera QuickStart Container
2. **examples/hdfs_basics.py** - Ukázka základních operací s HDFS
3. **examples/spark_cloudera.py** - Demonstrace PySpark v Cloudera prostředí
4. **examples/cloudera_admin.sh** - Základní administrativní a monitorovací příkazy

## Jak začít pracovat s příklady

### Spuštění Cloudera kontejneru

```bash
docker-compose -f docker-compose-cloudera.yml up
```

### Přístup k webovým rozhraním

- **HDFS NameNode**: http://localhost:50070
- **YARN ResourceManager**: http://localhost:8088
- **Spark History Server**: http://localhost:18080
- **Hue (Web UI)**: http://localhost:8888

### Spuštění příkladů

```bash
# Připojení do kontejneru
docker exec -it cloudera-quickstart /bin/bash

# Spuštění Python příkladů
cd /examples
python hdfs_basics.py
python spark_cloudera.py

# Spuštění administračního skriptu
bash cloudera_admin.sh
```

## Klíčové koncepty pro administraci

### 1. Sledování zdraví clusteru
- Kontrola využití HDFS
- Monitoring YARN aplikací
- Sledování zdrojů (CPU, RAM, diskový prostor)

### 2. Optimalizace výkonu
- Nastavení YARN konfigurací
- Spark konfigurace pro optimální výkon
- Hive optimalizace

### 3. Bezpečnost
- Kerberos autentizace
- HDFS ACL (Access Control Lists)
- Šifrování dat

### 4. Scaling a správa zdrojů
- Přidávání a odebírání uzlů
- Plánování zdrojů a QoS (Quality of Service)
- Dynamická alokace zdrojů

## Doporučené zdroje pro další studium

- [Cloudera Documentation](https://docs.cloudera.com/)
- [Apache Hadoop Documentation](https://hadoop.apache.org/docs/)
- [Cloudera Community Forums](https://community.cloudera.com/)
- [Cloudera YouTube Channel](https://www.youtube.com/user/clouderahadoop)
- [Kniha: Hadoop: The Definitive Guide (Tom White)](https://www.oreilly.com/library/view/hadoop-the-definitive/9781491901687/) 
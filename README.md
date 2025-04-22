# E-commerce Data Analytics Platform

Komplexní řešení pro sběr, zpracování a analýzu e-commerce dat využívající moderní big data technologie.

## Technologický stack

- Apache Hadoop & HDFS
- Apache Spark
- Apache Airflow
- Apache Iceberg
- Atlas Metadata
- PostgreSQL
- Docker & Docker Compose
- Python (pyenv, poetry)

## Rychlý start

1. Klonujte repozitář
2. Nastavte prostředí: `poetry install`
3. Spusťte kontejnery: `docker-compose up -d`
4. Otevřete Airflow UI: http://localhost:8080

### Spuštění Hadoop clusteru

Pro spuštění Hadoop clusteru použijte:

```bash
cd docker/hadoop
docker-compose -f docker-compose.hadoop.yml up -d
```

Po spuštění jsou dostupná následující rozhraní:
- HDFS NameNode UI: http://localhost:9870
- YARN ResourceManager UI: http://localhost:8088
- NodeManager UI: http://localhost:8042

## Dokumentace

Kompletní dokumentace je dostupná ve složce `docs/`.
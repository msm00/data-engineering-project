# Architektura řešení

## Přehled

Tato dokumentace popisuje architekturu naší E-commerce Data Analytics Platform. Systém je navržen pro sběr, zpracování a analýzu velkých objemů dat z e-commerce prostředí s důrazem na škálovatelnost, spolehlivost a flexibilitu.

## Komponenty systému

### Datové úložiště
- **HDFS** - distribuovaný souborový systém pro uložení velkých objemů dat
- **PostgreSQL** - relační databáze pro strukturovaná data a metadata
- **Apache Iceberg** - formát tabulek pro zajištění ACID transakcí nad daty v HDFS

### Zpracování dat
- **Apache Spark** - engine pro distribuované zpracování velkých objemů dat
- **Apache Airflow** - orchestrace a plánování ETL procesů

### Metadata management
- **Atlas Metadata** - centrální repozitář pro metadata a datovou linealitu

## Architektonické principy

1. **Oddělení úložiště a výpočetních zdrojů** - umožňuje nezávislé škálování
2. **Datové pipeline jako kód** - všechny transformace a ETL procesy jsou verzovány v Gitu
3. **Idempotence** - procesy lze bezpečně opakovat bez nežádoucích vedlejších efektů
4. **Monitorování** - všechny komponenty jsou monitorovány
5. **Automatizace** - CI/CD pipeline pro automatické nasazení změn

## Datové toky

1. Data jsou extrahována z různých zdrojů (API, databáze, soubory)
2. Zpracována pomocí Spark jobů
3. Uložena v datovém jezeře (HDFS) ve formátu Iceberg
4. Metadata jsou zaznamenána v Atlas
5. Data jsou dostupná pro analytické dotazy a reporting

## Diagramy

*(Zde budou umístěny diagramy architektury)*

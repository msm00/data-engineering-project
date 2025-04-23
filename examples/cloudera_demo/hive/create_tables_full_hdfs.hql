-- Vytvoření databáze
CREATE DATABASE IF NOT EXISTS prodeje_db;
USE prodeje_db;

-- Vytvoření tabulky prodeje
DROP TABLE IF EXISTS prodeje;
CREATE EXTERNAL TABLE prodeje (
    id INT,
    datum DATE,
    produkt STRING,
    kategorie STRING,
    cena DOUBLE,
    mnozstvi INT,
    region STRING,
    zakaznik_id INT
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION 'hdfs://namenode:8020/data/raw/prodeje/'
TBLPROPERTIES ('skip.header.line.count'='1');

-- Vytvoření tabulky zákazníci
DROP TABLE IF EXISTS zakaznici;
CREATE EXTERNAL TABLE zakaznici (
    id INT,
    jmeno STRING,
    prijmeni STRING,
    email STRING,
    vek INT,
    segment STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION 'hdfs://namenode:8020/data/raw/zakaznici/'
TBLPROPERTIES ('skip.header.line.count'='1');

-- Vytvoření optimalizované tabulky prodeje (ORC formát)
DROP TABLE IF EXISTS prodeje_orc;
CREATE TABLE prodeje_orc (
    id INT,
    datum DATE,
    produkt STRING,
    kategorie STRING,
    cena DOUBLE,
    mnozstvi INT,
    region STRING,
    zakaznik_id INT
)
STORED AS ORC
TBLPROPERTIES ('orc.compress'='SNAPPY');

INSERT OVERWRITE TABLE prodeje_orc
SELECT * FROM prodeje;

-- Vytvoření optimalizované tabulky zákazníci (ORC formát)
DROP TABLE IF EXISTS zakaznici_orc;
CREATE TABLE zakaznici_orc (
    id INT,
    jmeno STRING,
    prijmeni STRING,
    email STRING,
    vek INT,
    segment STRING
)
STORED AS ORC
TBLPROPERTIES ('orc.compress'='SNAPPY');

INSERT OVERWRITE TABLE zakaznici_orc
SELECT * FROM zakaznici;

-- Vytvoření tabulky měsíční prodeje (agregace)
DROP TABLE IF EXISTS mesicni_prodeje;
CREATE TABLE mesicni_prodeje
STORED AS ORC
AS
SELECT 
    YEAR(datum) as rok,
    MONTH(datum) as mesic,
    kategorie,
    region,
    COUNT(*) as pocet_transakci,
    SUM(mnozstvi) as celkem_prodano,
    SUM(cena * mnozstvi) as celkovy_obrat
FROM prodeje
GROUP BY YEAR(datum), MONTH(datum), kategorie, region;

-- Kontrolní dotaz - zobrazení obsahu tabulek
SELECT * FROM prodeje LIMIT 10;
SELECT * FROM zakaznici LIMIT 10;
SELECT * FROM mesicni_prodeje LIMIT 10; 
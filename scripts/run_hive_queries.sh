#!/bin/bash

# Skript pro spuštění Hive dotazů
# Tento skript demonstruje použití Apache Hive v rámci Hadoop ekosystému

echo "Připojuji se k Hive serveru..."

# Kopírování HQL souboru do kontejneru
echo "Kopíruji HQL soubor do Hive serveru..."
docker cp ../hive/create_tables.hql hive-server:/tmp/create_tables.hql

# Vytvoření tabulek a import dat
echo "Vytvářím tabulky a importuji data z HDFS..."
docker exec -it hive-server bash -c "cd /tmp && hive -f create_tables.hql"

# Analýza dat pomocí Hive QL
echo "Provádím analýzu dat pomocí Hive QL..."

echo "1. Top 5 nejprodávanějších produktů podle celkového obratu:"
docker exec -it hive-server bash -c "hive -e \"
USE prodeje_db;
SELECT 
    produkt, 
    SUM(cena * mnozstvi) as celkovy_obrat,
    SUM(mnozstvi) as celkem_prodano
FROM prodeje_orc
GROUP BY produkt
ORDER BY celkovy_obrat DESC
LIMIT 5;
\""

echo "2. Průměrný věk zákazníků podle segmentu:"
docker exec -it hive-server bash -c "hive -e \"
USE prodeje_db;
SELECT 
    segment, 
    AVG(vek) as prumerny_vek,
    COUNT(*) as pocet_zakazniku
FROM zakaznici_orc
GROUP BY segment;
\""

echo "3. Analýza prodejů podle regionu a měsíce:"
docker exec -it hive-server bash -c "hive -e \"
USE prodeje_db;
SELECT 
    region,
    rok,
    mesic,
    SUM(celkovy_obrat) as celkovy_obrat,
    SUM(celkem_prodano) as celkem_prodano
FROM mesicni_prodeje
GROUP BY region, rok, mesic
ORDER BY region, rok, mesic;
\""

echo "4. Join prodejů a zákazníků - analýza prodejů podle segmentu zákazníků:"
docker exec -it hive-server bash -c "hive -e \"
USE prodeje_db;
SELECT 
    z.segment,
    p.kategorie,
    SUM(p.cena * p.mnozstvi) as celkovy_obrat,
    COUNT(DISTINCT p.zakaznik_id) as pocet_zakazniku
FROM prodeje_orc p
JOIN zakaznici_orc z ON p.zakaznik_id = z.id
GROUP BY z.segment, p.kategorie
ORDER BY z.segment, celkovy_obrat DESC;
\""

echo "5. Prodeje podle dne v týdnu:"
docker exec -it hive-server bash -c "hive -e \"
USE prodeje_db;
SELECT 
    CASE
        WHEN DAYOFWEEK(datum) = 1 THEN 'Neděle'
        WHEN DAYOFWEEK(datum) = 2 THEN 'Pondělí'
        WHEN DAYOFWEEK(datum) = 3 THEN 'Úterý'
        WHEN DAYOFWEEK(datum) = 4 THEN 'Středa'
        WHEN DAYOFWEEK(datum) = 5 THEN 'Čtvrtek'
        WHEN DAYOFWEEK(datum) = 6 THEN 'Pátek'
        WHEN DAYOFWEEK(datum) = 7 THEN 'Sobota'
    END as den,
    COUNT(*) as pocet_transakci,
    SUM(cena * mnozstvi) as celkovy_obrat
FROM prodeje_orc
GROUP BY DAYOFWEEK(datum)
ORDER BY DAYOFWEEK(datum);
\""

echo "Hive analýza dokončena." 
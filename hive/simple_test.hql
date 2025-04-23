-- Jednoduchý test
CREATE DATABASE IF NOT EXISTS test_db;
USE test_db;

-- Vytvoření jednoduché tabulky
DROP TABLE IF EXISTS test_table;
CREATE TABLE test_table (
    id INT,
    name STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ',';

-- Vložení testovacích dat
INSERT INTO test_table VALUES (1, 'test1');
INSERT INTO test_table VALUES (2, 'test2');

-- Kontrolní dotaz
SELECT * FROM test_table; 
#!/usr/bin/env python3

import sys

# Mapper načítá data ze stdin (vstup z HDFS)
for line in sys.stdin:
    # Odstraníme whitespace a převedeme na lowercase
    line = line.strip().lower()
    
    # Rozdělíme řádek na slova
    words = line.split()
    
    # Vypíšeme každé slovo s počátečním počtem 1
    # Formát: slovo\t1
    for word in words:
        print(f"{word}\t1") 
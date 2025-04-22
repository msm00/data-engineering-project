#!/usr/bin/env python3

import sys

current_word = None
current_count = 0
word = None

# Reducer načítá data ze stdin (výstup mapperů)
for line in sys.stdin:
    # Odstraníme whitespace
    line = line.strip()
    
    # Rozložíme vstupní řádek na slovo a počet
    word, count = line.split('\t', 1)
    
    # Převedeme počet na int
    try:
        count = int(count)
    except ValueError:
        continue
    
    # Pokud zpracováváme stejné slovo jako předtím, přičteme počet
    if current_word == word:
        current_count += count
    else:
        # Pokud máme nové slovo a nějaké předchozí slovo bylo zpracováno,
        # vypíšeme výsledek předchozího slova
        if current_word:
            print(f"{current_word}\t{current_count}")
        
        # Nastavíme nové aktuální slovo a jeho počáteční počet
        current_count = count
        current_word = word

# Nezapomeneme vypsat poslední slovo
if current_word == word:
    print(f"{current_word}\t{current_count}") 
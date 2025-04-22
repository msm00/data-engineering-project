"""
Jednoduchý příklad MapReduce WordCount úlohy pro Hadoop.

Tento skript implementuje klasickou "Hello World" úlohu MapReduce - počítání slov.
"""
import os
import logging
import subprocess
import tempfile
from typing import Dict

# Nastavení loggeru
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_mapper() -> str:
    """
    Vytvoří mapper skript pro WordCount úlohu.
    
    Returns:
        Cesta k vytvořenému mapper skriptu
    """
    mapper_content = """#!/usr/bin/env python

import sys

# Mapper čte standardní vstup řádek po řádku
for line in sys.stdin:
    # Odstranění bílých znaků
    line = line.strip()
    
    # Rozdělení řádku na slova
    words = line.split()
    
    # Výstup ve formátu klíč-hodnota (slovo, 1)
    for word in words:
        # Výstup ve formátu: slovo\t1
        # Tabulátor je výchozí oddělovač v Hadoop Streaming
        print('%s\\t%s' % (word.lower(), 1))
"""
    
    fd, path = tempfile.mkstemp(suffix=".py", prefix="mapper_")
    with os.fdopen(fd, 'w') as f:
        f.write(mapper_content)
    
    # Nastavení oprávnění pro spuštění
    os.chmod(path, 0o755)
    logger.info(f"Vytvořen mapper skript: {path}")
    return path


def create_reducer() -> str:
    """
    Vytvoří reducer skript pro WordCount úlohu.
    
    Returns:
        Cesta k vytvořenému reducer skriptu
    """
    reducer_content = """#!/usr/bin/env python

import sys

current_word = None
current_count = 0
word = None

# Reducer čte standardní vstup řádek po řádku
for line in sys.stdin:
    # Odstranění bílých znaků
    line = line.strip()
    
    # Parsování vstupu (předpokládáme formát "slovo\tpočet")
    word, count = line.split('\\t', 1)
    
    # Převod počtu na číslo
    try:
        count = int(count)
    except ValueError:
        # V případě chyby pokračujeme s dalším řádkem
        continue
    
    # Pokud zpracováváme stejné slovo, přičteme počet
    if current_word == word:
        current_count += count
    else:
        # Pokud už jsme zpracovali nějaké slovo, vypíšeme výsledek
        if current_word:
            print('%s\\t%s' % (current_word, current_count))
        # Přepneme na nové slovo
        current_count = count
        current_word = word

# Nezapomeneme vypsat poslední slovo
if current_word == word:
    print('%s\\t%s' % (current_word, current_count))
"""
    
    fd, path = tempfile.mkstemp(suffix=".py", prefix="reducer_")
    with os.fdopen(fd, 'w') as f:
        f.write(reducer_content)
    
    # Nastavení oprávnění pro spuštění
    os.chmod(path, 0o755)
    logger.info(f"Vytvořen reducer skript: {path}")
    return path


def create_input_file(content: str) -> str:
    """
    Vytvoří vstupní soubor s textem pro WordCount.
    
    Args:
        content: Obsah souboru
        
    Returns:
        Cesta k vytvořenému souboru
    """
    fd, path = tempfile.mkstemp(suffix=".txt", prefix="input_")
    with os.fdopen(fd, 'w') as f:
        f.write(content)
    
    logger.info(f"Vytvořen vstupní soubor: {path}")
    return path


def upload_to_hdfs(local_path: str, hdfs_path: str) -> bool:
    """
    Nahraje soubor do HDFS.
    
    Args:
        local_path: Cesta k lokálnímu souboru
        hdfs_path: Cesta v HDFS
        
    Returns:
        True při úspěchu, jinak False
    """
    try:
        cmd = ["hdfs", "dfs", "-mkdir", "-p", os.path.dirname(hdfs_path)]
        subprocess.run(cmd, check=True, capture_output=True)
        
        cmd = ["hdfs", "dfs", "-put", local_path, hdfs_path]
        subprocess.run(cmd, check=True, capture_output=True)
        
        logger.info(f"Soubor nahrán do HDFS: {hdfs_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Chyba při nahrávání do HDFS: {e.stderr.decode('utf-8')}")
        return False


def run_hadoop_streaming(input_path: str, output_path: str, mapper_path: str, reducer_path: str) -> bool:
    """
    Spustí Hadoop Streaming úlohu pro WordCount.
    
    Args:
        input_path: Vstupní cesta v HDFS
        output_path: Výstupní cesta v HDFS
        mapper_path: Cesta k mapper skriptu
        reducer_path: Cesta k reducer skriptu
        
    Returns:
        True při úspěchu, jinak False
    """
    try:
        # Odstranění výstupního adresáře, pokud existuje
        cmd = ["hdfs", "dfs", "-rm", "-r", "-skipTrash", output_path]
        subprocess.run(cmd, capture_output=True)
        
        # Sestavení příkazu pro spuštění Hadoop Streaming
        hadoop_streaming_jar = "$HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar"
        cmd = [
            "hadoop", "jar", hadoop_streaming_jar,
            "-files", f"{mapper_path},{reducer_path}",
            "-mapper", f"python {os.path.basename(mapper_path)}",
            "-reducer", f"python {os.path.basename(reducer_path)}",
            "-input", input_path,
            "-output", output_path
        ]
        
        # Spuštění úlohy
        subprocess.run(cmd, check=True, capture_output=True)
        logger.info(f"MapReduce úloha úspěšně dokončena, výstup: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Chyba při spuštění MapReduce úlohy: {e.stderr.decode('utf-8')}")
        return False


def download_result(hdfs_output_path: str) -> Dict[str, int]:
    """
    Stáhne a zpracuje výsledky MapReduce úlohy.
    
    Args:
        hdfs_output_path: Cesta k výstupnímu adresáři v HDFS
        
    Returns:
        Slovník s počty slov
    """
    try:
        # Stažení výsledků
        result_file = f"{hdfs_output_path}/part-00000"
        temp_result = tempfile.mktemp(suffix=".txt", prefix="result_")
        
        cmd = ["hdfs", "dfs", "-get", result_file, temp_result]
        subprocess.run(cmd, check=True, capture_output=True)
        
        # Načtení a parsování výsledků
        word_counts = {}
        with open(temp_result, 'r') as f:
            for line in f:
                word, count = line.strip().split('\t')
                word_counts[word] = int(count)
        
        os.remove(temp_result)
        logger.info(f"Načteny výsledky, nalezeno {len(word_counts)} unikátních slov")
        return word_counts
    except (subprocess.CalledProcessError, IOError) as e:
        logger.error(f"Chyba při stahování výsledků: {str(e)}")
        return {}


if __name__ == "__main__":
    # Příklad použití
    # 1. Vytvoření skriptů a vstupních dat
    mapper_script = create_mapper()
    reducer_script = create_reducer()
    
    sample_text = """
    Apache Hadoop je framework, který umožňuje distribuované zpracování velkých datových sad napříč clustery počítačů.
    Je navržen tak, aby škáloval od jednoho serveru až po tisíce strojů.
    Hadoop implementuje výpočetní paradigma zvané MapReduce, kde je úloha rozdělena na mnoho malých částí, které mohou běžet paralelně.
    Hadoop také poskytuje distribuovaný souborový systém (HDFS), který ukládá data na uzly clusteru.
    HDFS poskytuje vysokou propustnost přístupu k datům a je vhodný pro aplikace s velkými datovými sadami.
    """
    
    input_file = create_input_file(sample_text)
    
    # 2. Nahrání vstupních dat do HDFS
    hdfs_input_dir = "/wordcount/input"
    hdfs_input_path = f"{hdfs_input_dir}/input.txt"
    hdfs_output_dir = "/wordcount/output"
    
    if upload_to_hdfs(input_file, hdfs_input_path):
        # 3. Spuštění MapReduce úlohy
        if run_hadoop_streaming(hdfs_input_dir, hdfs_output_dir, mapper_script, reducer_script):
            # 4. Zobrazení výsledků
            results = download_result(hdfs_output_dir)
            
            print("\nVýsledky počítání slov:")
            for word, count in sorted(results.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"{word}: {count}")
    
    # 5. Úklid
    os.remove(mapper_script)
    os.remove(reducer_script)
    os.remove(input_file)
    logger.info("Demo dokončeno!") 
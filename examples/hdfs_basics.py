#!/usr/bin/env python3
"""
Základní příklad pro práci s HDFS v Apache Hadoop prostředí.
"""
import os
import subprocess

def run_cmd(cmd):
    """Spustí příkaz a vrátí výstup."""
    print(f"Spouštím: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Chyba: {result.stderr}")
        return None
    return result.stdout.strip()

def hdfs_demo():
    """Ukázka základních HDFS operací."""
    # 1. Vytvoření adresáře v HDFS
    run_cmd("hdfs dfs -mkdir -p /user/root/demo")
    
    # 2. Vytvoření testovacího souboru
    with open("/tmp/test_data.txt", "w") as f:
        f.write("Toto je testovací soubor pro HDFS.\n")
        f.write("Hadoop ekosystém poskytuje mnoho nástrojů pro Big Data.\n")
    
    # 3. Nahrání souboru do HDFS
    run_cmd("hdfs dfs -put /tmp/test_data.txt /user/root/demo/")
    
    # 4. Výpis obsahu adresáře
    print("\nObsah HDFS adresáře:")
    contents = run_cmd("hdfs dfs -ls /user/root/demo/")
    print(contents)
    
    # 5. Čtení souboru z HDFS
    print("\nObsah souboru z HDFS:")
    file_content = run_cmd("hdfs dfs -cat /user/root/demo/test_data.txt")
    print(file_content)
    
    # 6. Informace o souboru
    print("\nInformace o souboru:")
    file_info = run_cmd("hdfs dfs -stat '%o %r %F' /user/root/demo/test_data.txt")
    print(file_info)
    
    # 7. Smazání souboru
    run_cmd("hdfs dfs -rm /user/root/demo/test_data.txt")
    print("\nSoubor byl smazán.")

if __name__ == "__main__":
    print("===== Demonstrace základních HDFS operací v Apache Hadoop =====")
    hdfs_demo()
    print("===== Konec demonstrace =====") 
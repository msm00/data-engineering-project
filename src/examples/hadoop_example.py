"""
Jednoduchý příklad pro interakci s Hadoop HDFS pomocí Python API.
"""
import os
import subprocess
import logging
from typing import List, Optional

# Nastavení loggeru
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class HadoopClient:
    """Třída pro interakci s Hadoop HDFS."""
    
    def __init__(self, namenode_host: str = "namenode", namenode_port: int = 9000):
        """
        Inicializace Hadoop klienta.
        
        Args:
            namenode_host: Hostname nebo IP adresa NameNode
            namenode_port: Port NameNode
        """
        self.hdfs_uri = f"hdfs://{namenode_host}:{namenode_port}"
        logger.info(f"Inicializován HDFS klient pro URI: {self.hdfs_uri}")
    
    def mkdir(self, hdfs_path: str) -> bool:
        """
        Vytvoří adresář v HDFS.
        
        Args:
            hdfs_path: Cesta k adresáři v HDFS
            
        Returns:
            True pokud adresář byl vytvořen, jinak False
        """
        try:
            cmd = ["hdfs", "dfs", "-mkdir", "-p", f"{self.hdfs_uri}{hdfs_path}"]
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Vytvořen adresář: {hdfs_path}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Chyba při vytváření adresáře {hdfs_path}: {e.stderr.decode('utf-8')}")
            return False
    
    def put(self, local_path: str, hdfs_path: str) -> bool:
        """
        Nahraje soubor do HDFS.
        
        Args:
            local_path: Cesta k lokálnímu souboru
            hdfs_path: Cílová cesta v HDFS
            
        Returns:
            True pokud soubor byl nahrán, jinak False
        """
        try:
            cmd = ["hdfs", "dfs", "-put", local_path, f"{self.hdfs_uri}{hdfs_path}"]
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Nahrán soubor {local_path} do HDFS: {hdfs_path}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Chyba při nahrávání souboru do HDFS: {e.stderr.decode('utf-8')}")
            return False
    
    def get(self, hdfs_path: str, local_path: str) -> bool:
        """
        Stáhne soubor z HDFS.
        
        Args:
            hdfs_path: Cesta souboru v HDFS
            local_path: Cílová lokální cesta
            
        Returns:
            True pokud soubor byl stažen, jinak False
        """
        try:
            cmd = ["hdfs", "dfs", "-get", f"{self.hdfs_uri}{hdfs_path}", local_path]
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Stažen soubor z HDFS {hdfs_path} do: {local_path}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Chyba při stahování souboru z HDFS: {e.stderr.decode('utf-8')}")
            return False
    
    def ls(self, hdfs_path: str) -> Optional[List[str]]:
        """
        Vypíše obsah adresáře v HDFS.
        
        Args:
            hdfs_path: Cesta k adresáři v HDFS
            
        Returns:
            Seznam souborů a adresářů, nebo None při chybě
        """
        try:
            cmd = ["hdfs", "dfs", "-ls", f"{self.hdfs_uri}{hdfs_path}"]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            lines = result.stdout.strip().split("\n")
            # Odfiltrování prvního řádku a prázdných řádků
            files = [line.split()[-1].replace(f"{self.hdfs_uri}", "") for line in lines[1:] if line.strip()]
            logger.info(f"Výpis adresáře {hdfs_path}: {len(files)} položek")
            return files
        except subprocess.CalledProcessError as e:
            logger.error(f"Chyba při výpisu adresáře HDFS: {e.stderr}")
            return None
    
    def rm(self, hdfs_path: str, recursive: bool = False) -> bool:
        """
        Odstraní soubor nebo adresář z HDFS.
        
        Args:
            hdfs_path: Cesta k souboru nebo adresáři v HDFS
            recursive: Zda odstranit rekurzivně (pro adresáře)
            
        Returns:
            True pokud byl soubor/adresář odstraněn, jinak False
        """
        try:
            cmd = ["hdfs", "dfs", "-rm"]
            if recursive:
                cmd.append("-r")
            cmd.append(f"{self.hdfs_uri}{hdfs_path}")
            
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Odstraněn {'adresář' if recursive else 'soubor'}: {hdfs_path}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Chyba při odstraňování z HDFS: {e.stderr.decode('utf-8')}")
            return False


def create_sample_file(filename: str, content: str) -> bool:
    """
    Vytvoří vzorový soubor pro nahrání do HDFS.
    
    Args:
        filename: Název souboru
        content: Obsah souboru
        
    Returns:
        True pokud byl soubor vytvořen, jinak False
    """
    try:
        with open(filename, 'w') as f:
            f.write(content)
        logger.info(f"Vytvořen vzorový soubor: {filename}")
        return True
    except IOError as e:
        logger.error(f"Chyba při vytváření souboru: {str(e)}")
        return False


if __name__ == "__main__":
    # Příklad použití
    client = HadoopClient()
    
    # Vytvoření vzorového souboru
    sample_file = "sample_data.txt"
    sample_content = "Toto je testovací soubor pro Hadoop HDFS.\nObsahuje několik řádků textu.\n"
    
    if create_sample_file(sample_file, sample_content):
        # Vytvoření adresáře v HDFS
        client.mkdir("/user/example")
        
        # Nahrání souboru do HDFS
        client.put(sample_file, "/user/example/sample_data.txt")
        
        # Výpis obsahu adresáře
        files = client.ls("/user/example")
        if files:
            logger.info(f"Soubory v HDFS: {files}")
        
        # Stažení souboru z HDFS
        client.get("/user/example/sample_data.txt", "downloaded_sample.txt")
        
        # Úklid
        os.remove(sample_file)
        client.rm("/user/example", recursive=True)
        logger.info("Demo dokončeno!") 
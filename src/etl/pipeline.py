"""
Základní ETL pipeline, která demonstruje použití jednotlivých komponent.
"""
import argparse
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from src.etl.extract.csv_extractor import CSVExtractor
from src.etl.transform.basic_transformer import BasicTransformer
from src.etl.load.postgres_loader import PostgresLoader

# Načtení proměnných z .env souboru
load_dotenv()

# Nastavení loggeru
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run_etl_pipeline(data_dir: str, file_name: str, table_name: str) -> bool:
    """
    Spustí ETL pipeline - extrakce, transformace, načtení.
    
    Args:
        data_dir: Adresář s CSV soubory
        file_name: Název CSV souboru ke zpracování
        table_name: Název cílové tabulky v databázi
        
    Returns:
        True pokud pipeline proběhla úspěšně, jinak False
    """
    try:
        # 1. Extrakce
        logger.info("Začínám extrakci dat.")
        extractor = CSVExtractor(data_dir)
        df = extractor.extract(file_name)
        
        if df is None:
            logger.error("Extrakce dat selhala.")
            return False
            
        # 2. Transformace
        logger.info("Začínám transformaci dat.")
        transformer = BasicTransformer()
        df = transformer.clean_column_names(df)
        df = transformer.drop_duplicates(df)
        
        # Příklad zpracování chybějících hodnot
        missing_strategy = {
            "price": "median",
            "category": "mode",
            "description": "empty_string"
        }
        df = transformer.handle_missing_values(df, missing_strategy)
        
        # 3. Načtení do databáze
        logger.info("Začínám načítání dat do databáze.")
        loader = PostgresLoader(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 5432)),
            database=os.getenv("DB_NAME", "datawarehouse"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres"),
        )
        
        if not loader.connect():
            logger.error("Připojení k databázi selhalo.")
            return False
            
        success = loader.load_data(df, table_name, if_exists="append")
        
        if success:
            logger.info("ETL pipeline dokončena úspěšně.")
            return True
        else:
            logger.error("Načítání dat do databáze selhalo.")
            return False
    
    except Exception as e:
        logger.error(f"ETL pipeline selhala s chybou: {e}")
        return False


def main():
    """
    Hlavní funkce pro spuštění ETL pipeline z příkazové řádky.
    """
    parser = argparse.ArgumentParser(description="Spustí ETL pipeline pro CSV soubor.")
    parser.add_argument("--data-dir", type=str, required=True, help="Adresář s daty")
    parser.add_argument("--file", type=str, required=True, help="Název CSV souboru")
    parser.add_argument("--table", type=str, required=True, help="Název cílové tabulky")
    
    args = parser.parse_args()
    
    success = run_etl_pipeline(args.data_dir, args.file, args.table)
    
    if not success:
        exit(1)


if __name__ == "__main__":
    main() 
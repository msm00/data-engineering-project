"""
ETL pipeline pro načítání, transformaci a ukládání dat s pokročilými transformacemi.
"""
import argparse
import logging
import os
from pathlib import Path
from typing import Optional

import pandas as pd
from dotenv import load_dotenv

from src.etl.extract.csv_extractor import CSVExtractor
from src.etl.load.postgres_loader import PostgresLoader
from src.etl.transform.advanced_transformer import AdvancedTransformer

# Načtení proměnných prostředí
load_dotenv()

# Nastavení loggeru
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run_pipeline(
    data_dir: str,
    file_name: str,
    table_name: str,
    db_host: Optional[str] = None,
    db_port: Optional[int] = None,
    db_name: Optional[str] = None,
    db_user: Optional[str] = None,
    db_password: Optional[str] = None,
    if_exists: str = "append",
) -> bool:
    """
    Spustí ETL pipeline s pokročilými transformacemi.
    
    Args:
        data_dir: Adresář s daty
        file_name: Název souboru
        table_name: Název cílové tabulky
        db_host: Hostitel databáze
        db_port: Port databáze
        db_name: Název databáze
        db_user: Uživatelské jméno
        db_password: Heslo
        if_exists: Strategie pro existující tabulku
        
    Returns:
        True pokud pipeline proběhla úspěšně, jinak False
    """
    try:
        # Vytvoření cesty k souboru
        file_path = Path(data_dir) / file_name
        
        # 1. Extract - načtení dat z CSV
        logger.info("Začínám extrakci dat.")
        extractor = CSVExtractor()
        data = extractor.extract(str(file_path))
        
        if data is None or data.empty:
            logger.error("Extrakce dat selhala nebo jsou data prázdná.")
            return False
        
        # 2. Transform - pokročilé transformace dat
        logger.info("Začínám transformaci dat s pokročilými transformacemi.")
        transformer = AdvancedTransformer()
        transformed_data = transformer.apply_transformations(data)
        
        # 3. Load - uložení do databáze
        logger.info("Začínám načítání dat do databáze.")
        loader = PostgresLoader(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password,
        )
        
        success = loader.load_data(
            df=transformed_data,
            table_name=table_name,
            if_exists=if_exists,
        )
        
        if success:
            logger.info("ETL pipeline dokončena úspěšně.")
        else:
            logger.error("ETL pipeline selhala při načítání dat do databáze.")
        
        return success
        
    except Exception as e:
        logger.exception(f"ETL pipeline selhala s chybou: {e}")
        return False


if __name__ == "__main__":
    # Parsování argumentů
    parser = argparse.ArgumentParser(description="Pokročilá ETL pipeline pro zpracování dat")
    parser.add_argument("--data-dir", help="Adresář s daty", default="./data")
    parser.add_argument("--file", help="Název souboru", required=True)
    parser.add_argument("--table", help="Název cílové tabulky", required=True)
    parser.add_argument("--if-exists", help="Strategie pro existující tabulku", choices=["fail", "replace", "append"], default="append")
    
    args = parser.parse_args()
    
    # Spuštění pipeline
    run_pipeline(
        data_dir=args.data_dir,
        file_name=args.file,
        table_name=args.table,
        if_exists=args.if_exists,
    ) 
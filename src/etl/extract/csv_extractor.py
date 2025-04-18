"""
CSV data extractor pro načítání dat ze souborů.
"""
import logging
from pathlib import Path
from typing import Dict, Optional, Union

import pandas as pd

# Nastavení loggeru
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class CSVExtractor:
    """
    Třída pro extrakci dat z CSV souborů.
    
    Umožňuje načítat data z CSV souborů s různými parametry
    a poskytuje základní validaci.
    """

    def __init__(self, data_dir: Union[str, Path]):
        """
        Inicializace extractoru.
        
        Args:
            data_dir: Adresář s CSV soubory
        """
        self.data_dir = Path(data_dir)
        if not self.data_dir.exists():
            logger.warning(f"Adresář {self.data_dir} neexistuje, bude vytvořen.")
            self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def extract(
        self, 
        filename: str, 
        **csv_options: Dict
    ) -> Optional[pd.DataFrame]:
        """
        Načte data z CSV souboru.
        
        Args:
            filename: Název souboru v data_dir
            csv_options: Další parametry pro pd.read_csv
            
        Returns:
            DataFrame s načtenými daty nebo None v případě chyby
        """
        file_path = self.data_dir / filename
        
        if not file_path.exists():
            logger.error(f"Soubor {file_path} neexistuje.")
            return None
        
        try:
            logger.info(f"Načítám data z {file_path}")
            df = pd.read_csv(file_path, **csv_options)
            logger.info(f"Úspěšně načteno {len(df)} řádků.")
            return df
        except Exception as e:
            logger.error(f"Chyba při načítání souboru {file_path}: {e}")
            return None
    
    def validate_data(self, df: pd.DataFrame, required_columns: list) -> bool:
        """
        Validuje, zda DataFrame obsahuje požadované sloupce.
        
        Args:
            df: DataFrame k validaci
            required_columns: Seznam povinných sloupců
            
        Returns:
            True pokud validace proběhla úspěšně, jinak False
        """
        if df is None:
            logger.error("Nelze validovat prázdný DataFrame.")
            return False
            
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.error(f"Chybějící sloupce: {missing_columns}")
            return False
        
        logger.info("Validace dat proběhla úspěšně.")
        return True 
"""
Základní transformer pro zpracování dat.
"""
import logging
from typing import Dict, List, Optional

import pandas as pd

# Nastavení loggeru
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class BasicTransformer:
    """
    Třída poskytující základní transformace pro datové DataFrame.
    """

    @staticmethod
    def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
        """
        Vyčistí názvy sloupců - odstraní mezery, převede na lowercase.
        
        Args:
            df: Vstupní DataFrame
            
        Returns:
            DataFrame s vyčištěnými názvy sloupců
        """
        if df is None or df.empty:
            logger.warning("Prázdný DataFrame, nelze čistit názvy sloupců.")
            return df
            
        df_copy = df.copy()
        df_copy.columns = df_copy.columns.str.strip().str.lower().str.replace(' ', '_')
        logger.info(f"Názvy sloupců byly vyčištěny: {list(df_copy.columns)}")
        return df_copy
    
    @staticmethod
    def drop_duplicates(
        df: pd.DataFrame, 
        subset: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Odstraní duplicitní řádky z DataFrame.
        
        Args:
            df: Vstupní DataFrame
            subset: Seznam sloupců pro kontrolu duplicit
            
        Returns:
            DataFrame bez duplicit
        """
        if df is None or df.empty:
            logger.warning("Prázdný DataFrame, nelze odstranit duplicity.")
            return df
            
        original_count = len(df)
        df_copy = df.copy()
        df_copy = df_copy.drop_duplicates(subset=subset)
        new_count = len(df_copy)
        
        if original_count > new_count:
            logger.info(f"Odstraněno {original_count - new_count} duplicitních řádků.")
        else:
            logger.info("Žádné duplicity nebyly nalezeny.")
            
        return df_copy
    
    @staticmethod
    def handle_missing_values(
        df: pd.DataFrame, 
        strategy: Dict[str, str]
    ) -> pd.DataFrame:
        """
        Zpracuje chybějící hodnoty podle zadané strategie.
        
        Args:
            df: Vstupní DataFrame
            strategy: Slovník mapující názvy sloupců na strategie
                      (např. {"price": "mean", "category": "mode", "desc": "drop"})
                      
        Returns:
            DataFrame se zpracovanými chybějícími hodnotami
        """
        if df is None or df.empty:
            logger.warning("Prázdný DataFrame, nelze zpracovat chybějící hodnoty.")
            return df
            
        df_copy = df.copy()
        
        for column, method in strategy.items():
            if column not in df_copy.columns:
                logger.warning(f"Sloupec {column} neexistuje v DataFrame.")
                continue
                
            missing_count = df_copy[column].isna().sum()
            if missing_count == 0:
                logger.info(f"Sloupec {column} nemá žádné chybějící hodnoty.")
                continue
                
            if method == "drop":
                df_copy = df_copy.dropna(subset=[column])
                logger.info(f"Odstraněno {missing_count} řádků s chybějícími hodnotami ve sloupci {column}.")
            elif method == "mean":
                if pd.api.types.is_numeric_dtype(df_copy[column]):
                    df_copy[column] = df_copy[column].fillna(df_copy[column].mean())
                    logger.info(f"Chybějící hodnoty ve sloupci {column} nahrazeny průměrem.")
                else:
                    logger.warning(f"Sloupec {column} není numerický, nelze použít metodu 'mean'.")
            elif method == "median":
                if pd.api.types.is_numeric_dtype(df_copy[column]):
                    df_copy[column] = df_copy[column].fillna(df_copy[column].median())
                    logger.info(f"Chybějící hodnoty ve sloupci {column} nahrazeny mediánem.")
                else:
                    logger.warning(f"Sloupec {column} není numerický, nelze použít metodu 'median'.")
            elif method == "mode":
                df_copy[column] = df_copy[column].fillna(df_copy[column].mode()[0])
                logger.info(f"Chybějící hodnoty ve sloupci {column} nahrazeny nejčastější hodnotou.")
            elif method == "zero":
                df_copy[column] = df_copy[column].fillna(0)
                logger.info(f"Chybějící hodnoty ve sloupci {column} nahrazeny nulou.")
            elif method == "empty_string":
                df_copy[column] = df_copy[column].fillna("")
                logger.info(f"Chybějící hodnoty ve sloupci {column} nahrazeny prázdným řetězcem.")
            else:
                logger.warning(f"Neznámá metoda '{method}' pro sloupec {column}.")
                
        return df_copy 
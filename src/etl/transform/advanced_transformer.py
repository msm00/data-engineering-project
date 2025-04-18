"""
Modul pro pokročilé transformace dat s využitím pandas a numpy.
"""
import logging
from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd

# Nastavení loggeru
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class AdvancedTransformer:
    """
    Třída pro pokročilé transformace dat s využitím pandas a numpy.
    """
    
    def __init__(self):
        """
        Inicializace transformeru.
        """
        logger.info("Inicializace pokročilého transformeru.")
    
    def apply_transformations(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplikuje všechny transformace na DataFrame.
        
        Args:
            df: Vstupní DataFrame
            
        Returns:
            Transformovaný DataFrame
        """
        if df is None or df.empty:
            logger.warning("Prázdný DataFrame, nelze aplikovat transformace.")
            return df
        
        # Kopírujeme DataFrame, abychom neměnili originál
        result_df = df.copy()
        
        # Aplikujeme jednotlivé transformace
        result_df = self.normalize_numeric_columns(result_df)
        result_df = self.handle_outliers(result_df)
        result_df = self.generate_features(result_df)
        
        logger.info(f"Aplikovány všechny transformace na DataFrame s {len(result_df)} řádky.")
        return result_df
    
    def normalize_numeric_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalizuje numerické sloupce v DataFrame pomocí min-max normalizace.
        
        Args:
            df: Vstupní DataFrame
            
        Returns:
            DataFrame s normalizovanými numerickými sloupci
        """
        result_df = df.copy()
        numeric_columns = result_df.select_dtypes(include=['number']).columns
        
        for column in numeric_columns:
            # Přeskočíme sloupce, které jsou primárními klíči nebo identifikátory
            if column.endswith('_id') or column == 'id':
                continue
                
            # Min-max normalizace: (x - min) / (max - min)
            min_val = result_df[column].min()
            max_val = result_df[column].max()
            
            # Kontrola, zda nemáme konstantní sloupec
            if max_val > min_val:
                # Vytvoříme nový sloupec s normalizovanými hodnotami
                norm_col_name = f"{column}_normalized"
                result_df[norm_col_name] = (result_df[column] - min_val) / (max_val - min_val)
                logger.info(f"Sloupec {column} normalizován jako {norm_col_name}")
                
        return result_df
    
    def handle_outliers(self, df: pd.DataFrame, method: str = 'iqr', threshold: float = 1.5) -> pd.DataFrame:
        """
        Detekuje a ošetřuje odlehlé hodnoty v numerických sloupcích.
        
        Args:
            df: Vstupní DataFrame
            method: Metoda pro detekci odlehlých hodnot ('iqr' nebo 'zscore')
            threshold: Práh pro detekci odlehlých hodnot
            
        Returns:
            DataFrame s ošetřenými odlehlými hodnotami
        """
        result_df = df.copy()
        numeric_columns = result_df.select_dtypes(include=['number']).columns
        
        for column in numeric_columns:
            # Přeskočíme sloupce, které jsou primárními klíči nebo identifikátory
            if column.endswith('_id') or column == 'id':
                continue
            
            # Vytvoříme masku pro odlehlé hodnoty podle zvolené metody
            if method == 'iqr':
                # IQR metoda
                Q1 = result_df[column].quantile(0.25)
                Q3 = result_df[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                outliers = (result_df[column] < lower_bound) | (result_df[column] > upper_bound)
            else:
                # Z-score metoda
                z_scores = np.abs((result_df[column] - result_df[column].mean()) / result_df[column].std())
                outliers = z_scores > threshold
            
            # Spočítáme počet odlehlých hodnot
            outlier_count = outliers.sum()
            if outlier_count > 0:
                # Nahradíme odlehlé hodnoty mediánem
                median_value = result_df[column].median()
                result_df.loc[outliers, column] = median_value
                logger.info(f"Nahrazeno {outlier_count} odlehlých hodnot v sloupci {column} mediánem ({median_value})")
                
                # Vytvoříme indikační sloupec pro odlehlé hodnoty
                result_df[f"{column}_outlier"] = outliers
        
        return result_df
    
    def generate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generuje nové features pro analýzu.
        
        Args:
            df: Vstupní DataFrame
            
        Returns:
            DataFrame s novými features
        """
        result_df = df.copy()
        
        # Příklad 1: Vytvoření binárních kategorií pro ceny (drahé/levné)
        if 'price' in result_df.columns:
            median_price = result_df['price'].median()
            result_df['is_expensive'] = result_df['price'] > median_price
            logger.info(f"Vytvořen nový feature 'is_expensive' s mediánovou hranicí {median_price}")
        
        # Příklad 2: Extrakce informací z textových polí
        if 'description' in result_df.columns:
            # Počet slov v popisu
            result_df['description_word_count'] = result_df['description'].str.split().str.len()
            logger.info("Vytvořen nový feature 'description_word_count'")
        
        # Příklad 3: Kombinace kategorií a cen pro analytické účely
        if 'category' in result_df.columns and 'price' in result_df.columns:
            # Průměrná cena kategorie
            category_avg_prices = result_df.groupby('category')['price'].transform('mean')
            result_df['category_avg_price'] = category_avg_prices
            
            # Poměr ceny produktu k průměrné ceně kategorie
            result_df['price_to_category_avg'] = result_df['price'] / category_avg_prices
            logger.info("Vytvořeny nové features 'category_avg_price' a 'price_to_category_avg'")
        
        return result_df 
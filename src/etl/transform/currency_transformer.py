"""
Transformátor pro obohacení produktových dat o kurzové informace.
"""
import logging
import pandas as pd
from typing import Dict, List, Any, Optional, Union

# Konfigurace loggeru
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CurrencyTransformer:
    """Třída pro transformaci produktových dat s přidáním kurzových informací."""
    
    def __init__(self, currency_rates: Dict[str, float], base_currency: str = 'EUR'):
        """
        Inicializace Currency transformátoru.
        
        Args:
            currency_rates: Slovník směnných kurzů ve formátu {'USD': 1.1, 'CZK': 25.5, ...}
            base_currency: Základní měna pro kurzy (výchozí EUR)
        """
        self.currency_rates = currency_rates
        self.base_currency = base_currency
        
        # Přidání kurzu 1.0 pro základní měnu, pokud neexistuje
        if base_currency not in self.currency_rates:
            self.currency_rates[base_currency] = 1.0
            
        logger.info(f"CurrencyTransformer inicializován s {len(currency_rates)} měnami, základ: {base_currency}")
    
    def calculate_price_in_currency(self, price: float, target_currency: str) -> float:
        """
        Vypočítá cenu v cílové měně.
        
        Args:
            price: Cena v základní měně
            target_currency: Cílová měna pro převod
            
        Returns:
            Cena v cílové měně
            
        Raises:
            ValueError: Pokud cílová měna není v dostupných kurzech
        """
        if target_currency not in self.currency_rates:
            available_currencies = ", ".join(self.currency_rates.keys())
            raise ValueError(f"Měna {target_currency} není dostupná. Dostupné měny: {available_currencies}")
        
        # Převod ceny z základní měny na cílovou měnu
        converted_price = price * self.currency_rates[target_currency]
        return round(converted_price, 2)
    
    def enrich_products_with_currency_prices(self, 
                                             df: pd.DataFrame, 
                                             price_column: str = 'price', 
                                             target_currencies: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Obohatí DataFrame produktů o ceny v různých měnách.
        
        Args:
            df: DataFrame s produkty
            price_column: Název sloupce s cenou v základní měně
            target_currencies: Seznam cílových měn pro převod (None = všechny dostupné měny)
            
        Returns:
            DataFrame obohacený o ceny v různých měnách
        """
        if price_column not in df.columns:
            raise ValueError(f"Sloupec '{price_column}' neexistuje v DataFrame")
        
        # Pokud nejsou specifikovány cílové měny, použijeme všechny dostupné
        if target_currencies is None:
            target_currencies = list(self.currency_rates.keys())
        else:
            # Ověřit, že všechny požadované měny jsou dostupné
            for currency in target_currencies:
                if currency not in self.currency_rates:
                    available_currencies = ", ".join(self.currency_rates.keys())
                    raise ValueError(f"Měna {currency} není dostupná. Dostupné měny: {available_currencies}")
        
        # Vytvoření kopie DataFrame pro manipulaci
        result_df = df.copy()
        
        # Přidání sloupce s označením původní měny
        currency_col_name = f"{price_column}_currency"
        result_df[currency_col_name] = self.base_currency
        
        # Přidání sloupců s cenami v různých měnách
        for currency in target_currencies:
            if currency == self.base_currency:
                continue  # Přeskočíme základní měnu
                
            new_col_name = f"{price_column}_{currency}"
            
            # Použití vectorizované operace pro rychlý výpočet
            result_df[new_col_name] = (df[price_column] * self.currency_rates[currency]).round(2)
            
            logger.debug(f"Přidán sloupec {new_col_name}")
        
        logger.info(f"DataFrame obohacen o ceny v {len(target_currencies)} měnách")
        return result_df
    
    def add_currency_info(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Přidá informace o dostupných měnách a kurzech do DataFrame.
        
        Args:
            df: DataFrame s produkty
            
        Returns:
            DataFrame obohacený o informace o měnách
        """
        # Vytvoření kopie DataFrame
        result_df = df.copy()
        
        # Přidání sloupce s informacemi o měnách
        result_df['available_currencies'] = str(list(self.currency_rates.keys()))
        result_df['base_currency'] = self.base_currency
        
        # Přidání sloupce s informacemi o aktuálním datu kurzů - všechny řádky stejné
        import datetime
        result_df['currency_rates_date'] = datetime.datetime.now().strftime("%Y-%m-%d")
        
        return result_df
    
    def transform(self, df: pd.DataFrame, price_column: str = 'price', 
                  target_currencies: Optional[List[str]] = None,
                  add_currency_metadata: bool = True) -> pd.DataFrame:
        """
        Hlavní transformační metoda - obohatí data o měnové informace.
        
        Args:
            df: DataFrame s produkty
            price_column: Název sloupce s cenou v základní měně
            target_currencies: Seznam cílových měn pro převod (None = všechny dostupné měny)
            add_currency_metadata: Zda přidat metadata o měnách
            
        Returns:
            Transformovaný DataFrame
        """
        logger.info(f"Začátek transformace produktů s měnovými informacemi: {len(df)} záznamů")
        
        # Ověření, že DataFrame není prázdný
        if df.empty:
            logger.warning("Vstupní DataFrame je prázdný, transformace přeskočena")
            return df
            
        # Ověření, že cenový sloupec existuje a má správný datový typ
        if price_column not in df.columns:
            raise ValueError(f"Sloupec '{price_column}' neexistuje v DataFrame")
            
        # Zkusíme převést cenový sloupec na float, pokud ještě není
        try:
            df[price_column] = df[price_column].astype(float)
        except Exception as e:
            logger.error(f"Nepodařilo se převést sloupec '{price_column}' na float: {str(e)}")
            raise
        
        # Aplikovat transformace
        result_df = self.enrich_products_with_currency_prices(df, price_column, target_currencies)
        
        # Přidat metadata, pokud je to požadováno
        if add_currency_metadata:
            result_df = self.add_currency_info(result_df)
        
        logger.info(f"Transformace dokončena: {len(result_df)} záznamů, nové sloupce: {len(result_df.columns) - len(df.columns)}")
        return result_df 
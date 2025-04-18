"""
Loader pro ukládání dat do PostgreSQL databáze.
"""
import logging
import os
from typing import Dict, Optional, Union

import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

# Nastavení loggeru
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class PostgresLoader:
    """
    Třída pro načítání dat do PostgreSQL databáze.
    """
    
    def __init__(
        self,
        host: str = None,
        port: int = None,
        database: str = None,
        user: str = None,
        password: str = None,
    ):
        """
        Inicializace loaderu.
        
        Args:
            host: Hostitel databázového serveru
            port: Port databázového serveru
            database: Název databáze
            user: Uživatelské jméno
            password: Heslo
        """
        # Načtení konfigurace z proměnných prostředí s předností před parametry
        self.host = host or os.environ.get("DB_HOST", "localhost")
        self.port = port or int(os.environ.get("DB_PORT", 5432))
        self.database = database or os.environ.get("DB_NAME", "datawarehouse")
        self.user = user or os.environ.get("DB_USER", "dataeng")
        self.password = password or os.environ.get("DB_PASSWORD", "dataeng")
        
        logger.info(f"Inicializace PostgreSQL loaderu pro databázi {self.database} na {self.host}:{self.port}")
        
        self.connection_string = (
            f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        )
        self.engine: Optional[Engine] = None
        self.db_params = {
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "user": self.user,
            "password": self.password
        }
        
    def connect(self) -> bool:
        """
        Vytvoří připojení k databázi.
        
        Returns:
            True pokud připojení bylo úspěšné, jinak False
        """
        try:
            self.engine = create_engine(self.connection_string)
            # Test připojení
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Úspěšně připojeno k PostgreSQL databázi.")
            return True
        except Exception as e:
            logger.error(f"Chyba při připojování k databázi: {e}")
            self.engine = None
            return False
    
    def load_data(
        self, 
        df: pd.DataFrame, 
        table_name: str, 
        if_exists: str = "append",
        **kwargs: Dict
    ) -> bool:
        """
        Nahraje data do specifikované tabulky.
        
        Args:
            df: DataFrame k nahrání
            table_name: Název cílové tabulky
            if_exists: Strategie pro existující tabulku ('fail', 'replace', 'append')
            **kwargs: Další parametry pro pd.to_sql
            
        Returns:
            True pokud nahrání bylo úspěšné, jinak False
        """
        if df is None or df.empty:
            logger.warning("Prázdný DataFrame, nelze nahrát data.")
            return False
        
        try:
            logger.info(f"Nahrávám {len(df)} řádků do tabulky {table_name}.")
            # Vytvoříme SQL pro tabulku, pokud neexistuje
            columns = df.columns
            column_defs = []
            
            # Jednoduché mapování pandas typů na PostgreSQL typy
            for col in columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    if pd.api.types.is_integer_dtype(df[col]):
                        column_defs.append(f'"{col}" INTEGER')
                    else:
                        column_defs.append(f'"{col}" FLOAT')
                else:
                    column_defs.append(f'"{col}" TEXT')
            
            # Vytvoříme připojení k databázi - pro admin operace zkusíme schema public
            conn = psycopg2.connect(**self.db_params)
            conn.autocommit = True  # Zapneme autocommit pro DDL operace
            cursor = conn.cursor()
            
            schema_name = 'public'
            
            # Pokud tabulka neexistuje, vytvoříme ji v public schema
            try:
                if if_exists == "replace":
                    cursor.execute(f'DROP TABLE IF EXISTS {schema_name}."{table_name}"')
                    
                if if_exists != "append":
                    create_sql = f'CREATE TABLE IF NOT EXISTS {schema_name}."{table_name}" ({", ".join(column_defs)})'
                    cursor.execute(create_sql)
                    
                # Přidáme oprávnění pro aktuálního uživatele
                cursor.execute(f'GRANT ALL PRIVILEGES ON TABLE {schema_name}."{table_name}" TO {self.db_params["user"]}')
            except Exception as e:
                logger.warning(f"Nelze upravit tabulku: {e}. Zkusíme pokračovat s vkládáním dat.")
            
            # Přepneme na běžné transakce pro vkládání dat
            conn.autocommit = False
            
            # Vložíme data po řádcích
            for _, row in df.iterrows():
                placeholders = ", ".join(["%s"] * len(columns))
                column_names = ", ".join([f'"{col}"' for col in columns])
                insert_sql = f'INSERT INTO {schema_name}."{table_name}" ({column_names}) VALUES ({placeholders})'
                values = [row[col] for col in columns]
                cursor.execute(insert_sql, values)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info("Data byla úspěšně nahrána.")
            return True
        except Exception as e:
            logger.error(f"Chyba při nahrávání dat do tabulky {table_name}: {e}")
            return False
    
    def execute_query(self, query: str) -> Optional[pd.DataFrame]:
        """
        Provede SQL dotaz a vrátí výsledky jako DataFrame.
        
        Args:
            query: SQL dotaz k provedení
            
        Returns:
            DataFrame s výsledky nebo None v případě chyby
        """
        if self.engine is None:
            logger.warning("Není vytvořeno připojení k databázi.")
            if not self.connect():
                return None
                
        try:
            logger.info(f"Provádím dotaz: {query[:100]}...")
            return pd.read_sql(query, self.engine)
        except Exception as e:
            logger.error(f"Chyba při provádění dotazu: {e}")
            return None 
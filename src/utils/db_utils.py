"""
Database utility functions for PostgreSQL connection and operations.
"""
import os
from contextlib import contextmanager
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Načtení .env proměnných
load_dotenv()

def get_connection_string(
    user: Optional[str] = None,
    password: Optional[str] = None,
    host: Optional[str] = None,
    port: Optional[str] = None,
    database: Optional[str] = None,
) -> str:
    """
    Vytvoří connection string pro PostgreSQL.
    Pokud není parametr zadán, použije se hodnota z .env souboru.
    """
    user = user or os.getenv("DB_USER", "dataeng")
    password = password or os.getenv("DB_PASSWORD", "dataeng")
    host = host or os.getenv("DB_HOST", "localhost")
    port = port or os.getenv("DB_PORT", "5432")
    database = database or os.getenv("DB_NAME", "datawarehouse")

    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


def create_db_engine(conn_string: Optional[str] = None) -> Engine:
    """
    Vytvoří SQLAlchemy engine pro připojení k databázi.
    """
    if conn_string is None:
        conn_string = get_connection_string()
    
    return create_engine(conn_string)


@contextmanager
def get_db_connection(engine: Optional[Engine] = None) -> Connection:
    """
    Context manager pro správu databázového spojení.
    """
    if engine is None:
        engine = create_db_engine()
    
    connection = engine.connect()
    try:
        yield connection
    finally:
        connection.close()


def execute_query(query: str, params: Optional[Dict] = None, engine: Optional[Engine] = None) -> None:
    """
    Vykoná SQL dotaz bez vracení výsledků.
    """
    if engine is None:
        engine = create_db_engine()
    
    with get_db_connection(engine) as conn:
        conn.execute(text(query), params or {})
        conn.commit()


def fetch_all(query: str, params: Optional[Dict] = None, engine: Optional[Engine] = None) -> List[Tuple]:
    """
    Vykoná SELECT dotaz a vrátí všechny výsledky jako list n-tic.
    """
    if engine is None:
        engine = create_db_engine()
    
    with get_db_connection(engine) as conn:
        result = conn.execute(text(query), params or {})
        return result.fetchall()


def fetch_as_df(query: str, params: Optional[Dict] = None, engine: Optional[Engine] = None) -> pd.DataFrame:
    """
    Vykoná SELECT dotaz a vrátí výsledky jako pandas DataFrame.
    """
    if engine is None:
        engine = create_db_engine()
    
    # Správná interakce s pandas a SQLAlchemy
    with engine.connect() as connection:
        result = connection.execute(text(query), params or {})
        df = pd.DataFrame(result.fetchall())
        if df.empty:
            return pd.DataFrame()
        df.columns = result.keys()
        return df


def insert_df(
    df: pd.DataFrame, 
    table_name: str, 
    schema: str = "staging",
    if_exists: str = "append", 
    engine: Optional[Engine] = None
) -> None:
    """
    Vloží pandas DataFrame do specifikované tabulky.
    
    Args:
        df: DataFrame k vložení
        table_name: Název cílové tabulky
        schema: Schéma, ve kterém se tabulka nachází
        if_exists: Co dělat, pokud tabulka existuje ('fail', 'replace', 'append')
        engine: SQLAlchemy engine (volitelný)
    """
    if engine is None:
        engine = create_db_engine()
    
    fully_qualified_table = f"{schema}.{table_name}" if schema else table_name
    df.to_sql(
        name=table_name,
        schema=schema,
        con=engine,
        if_exists=if_exists,
        index=False,
        chunksize=1000,  # Vkládání po blocích pro větší objemy dat
    )


def test_connection() -> bool:
    """
    Test připojení k databázi.
    """
    try:
        engine = create_db_engine()
        with get_db_connection(engine) as conn:
            result = conn.execute(text("SELECT 1")).fetchone()
            return result[0] == 1
    except SQLAlchemyError as e:
        print(f"Chyba připojení k databázi: {e}")
        return False


if __name__ == "__main__":
    # Test připojení při přímém spuštění souboru
    if test_connection():
        print("Připojení k databázi je funkční.")
        
        # Základní informace o databázi
        query = """
        SELECT 
            schema_name 
        FROM 
            information_schema.schemata 
        WHERE 
            schema_name NOT IN ('pg_catalog', 'information_schema')
        ORDER BY 
            schema_name;
        """
        try:
            result = fetch_as_df(query)
            print("Dostupná schémata v databázi:")
            print(result)
        except Exception as e:
            print(f"Chyba při načítání schémat: {e}")
            
            # Zkusíme se připojit k PostgreSQL systémové databázi
            print("\nZkoušíme připojení k PostgreSQL systémové databázi...")
            postgres_conn = get_connection_string(
                user=os.getenv("POSTGRES_USER", "postgres"),
                password=os.getenv("POSTGRES_PASSWORD", "postgres"),
                database=os.getenv("POSTGRES_DB", "postgres")
            )
            postgres_engine = create_db_engine(postgres_conn)
            try:
                with postgres_engine.connect() as conn:
                    print("Připojení k systémové PostgreSQL databázi je funkční.")
                    
                    # Zkusíme získat seznam schémat pomocí upravené funkce
                    query = """
                    SELECT 
                        schema_name 
                    FROM 
                        information_schema.schemata 
                    WHERE 
                        schema_name NOT IN ('pg_catalog', 'information_schema')
                    ORDER BY 
                        schema_name;
                    """
                    result = conn.execute(text(query))
                    rows = result.fetchall()
                    print("Dostupná schémata v databázi (přímo přes SQLAlchemy):")
                    for row in rows:
                        print(f"  - {row[0]}")
            except SQLAlchemyError as e:
                print(f"Chyba připojení k systémové databázi: {e}")
    else:
        print("Připojení k databázi selhalo.") 
"""
Skript pro demonstraci aktualizace produktů a funkce Time Travel.
"""
import logging
import os
import random
import time
from datetime import datetime, timedelta

import pandas as pd
import psycopg2
from dotenv import load_dotenv

# Načtení proměnných prostředí
load_dotenv()

# Nastavení loggeru
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_db_connection():
    """
    Vytvoří připojení k databázi.
    
    Returns:
        Connection objekt pro databázi
    """
    host = os.environ.get("DB_HOST", "localhost")
    port = int(os.environ.get("DB_PORT", 5432))
    database = os.environ.get("DB_NAME", "ecommerce")
    user = os.environ.get("DB_USER", "postgres")
    password = os.environ.get("DB_PASSWORD", "postgres")
    
    return psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )


def get_products():
    """
    Získá všechny produkty z databáze.
    
    Returns:
        DataFrame s produkty
    """
    with get_db_connection() as conn:
        query = "SELECT * FROM products"
        return pd.read_sql(query, conn)


def update_product_price(product_id, new_price):
    """
    Aktualizuje cenu produktu.
    
    Args:
        product_id: ID produktu
        new_price: Nová cena
        
    Returns:
        True pokud aktualizace proběhla úspěšně, jinak False
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE products SET price = %s WHERE product_id = %s",
                (new_price, product_id)
            )
            
            conn.commit()
            
            logger.info(f"Produkt {product_id} byl aktualizován s cenou {new_price}")
            return True
            
    except Exception as e:
        logger.error(f"Chyba při aktualizaci produktu {product_id}: {e}")
        return False


def update_product_stock(product_id, new_stock):
    """
    Aktualizuje skladové zásoby produktu.
    
    Args:
        product_id: ID produktu
        new_stock: Nové množství na skladě
        
    Returns:
        True pokud aktualizace proběhla úspěšně, jinak False
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE products SET stock_quantity = %s WHERE product_id = %s",
                (new_stock, product_id)
            )
            
            conn.commit()
            
            logger.info(f"Produkt {product_id} byl aktualizován s množstvím {new_stock}")
            return True
            
    except Exception as e:
        logger.error(f"Chyba při aktualizaci produktu {product_id}: {e}")
        return False


def get_product_history(product_id):
    """
    Získá historii změn produktu.
    
    Args:
        product_id: ID produktu
        
    Returns:
        DataFrame s historií změn
    """
    with get_db_connection() as conn:
        query = """
        SELECT 
            product_id, 
            version, 
            price, 
            stock_quantity, 
            valid_from, 
            valid_to,
            operation
        FROM products_history
        WHERE product_id = %s
        ORDER BY valid_from DESC
        """
        
        return pd.read_sql(query, conn, params=(product_id,))


def get_product_at_timestamp(product_id, timestamp):
    """
    Získá stav produktu v určitém časovém bodu.
    
    Args:
        product_id: ID produktu
        timestamp: Časový bod
        
    Returns:
        DataFrame s produktem v daném časovém bodu
    """
    with get_db_connection() as conn:
        query = """
        SELECT * FROM get_product_at_timestamp(%s, %s)
        """
        
        return pd.read_sql(query, conn, params=(product_id, timestamp))


def simulate_price_changes():
    """
    Simuluje změny cen produktů v průběhu času.
    """
    products = get_products()
    
    if products.empty:
        logger.error("Žádné produkty v databázi.")
        return
    
    logger.info(f"Nalezeno {len(products)} produktů.")
    
    # Pro každý produkt provedeme několik aktualizací ceny
    for _, product in products.iterrows():
        product_id = product['product_id']
        original_price = float(product['price'])
        
        # Simulujeme 5 změn ceny
        for i in range(5):
            # Náhodná změna ceny (+/- 10%)
            price_change = random.uniform(-0.1, 0.1)
            new_price = round(original_price * (1 + price_change), 2)
            
            # Aktualizace ceny
            update_product_price(product_id, new_price)
            
            # Náhodná změna skladových zásob
            new_stock = random.randint(10, 100)
            update_product_stock(product_id, new_stock)
            
            # Pauza mezi aktualizacemi
            time.sleep(1)
        
        # Zobrazení historie změn
        history = get_product_history(product_id)
        logger.info(f"Historie změn produktu {product_id}:")
        logger.info(history)
        
        # Ukázka Time Travel - zobrazení stavu produktu před 2 aktualizacemi
        if len(history) >= 3:
            timestamp = history.iloc[2]['valid_from']
            product_in_past = get_product_at_timestamp(product_id, timestamp)
            logger.info(f"Produkt {product_id} v čase {timestamp}:")
            logger.info(product_in_past)


if __name__ == "__main__":
    # Nejdříve se ujistíme, že máme migrace aplikované
    logger.info("Kontrola, zda jsou migrace aplikované...")
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Kontrola existence sloupce version v tabulce products
            cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name = 'products' AND column_name = 'version'
            )
            """)
            
            has_version_column = cursor.fetchone()[0]
            
            if not has_version_column:
                logger.error("Sloupec 'version' v tabulce 'products' neexistuje. Je potřeba spustit migrace.")
                logger.error("Použijte: python -m src.db.cli migrate")
                exit(1)
            
            # Kontrola existence tabulky products_history
            cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'products_history'
            )
            """)
            
            has_history_table = cursor.fetchone()[0]
            
            if not has_history_table:
                logger.error("Tabulka 'products_history' neexistuje. Je potřeba spustit migrace.")
                logger.error("Použijte: python -m src.db.cli migrate")
                exit(1)
                
    except Exception as e:
        logger.error(f"Chyba při kontrole migrací: {e}")
        exit(1)
    
    # Simulace změn cen
    logger.info("Simulace změn cen produktů...")
    simulate_price_changes()
    logger.info("Simulace dokončena.") 
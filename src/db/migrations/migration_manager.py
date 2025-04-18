"""
Správce migrací pro Schema Evolution.
"""
import hashlib
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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


class MigrationManager:
    """
    Správce migrací pro Schema Evolution v PostgreSQL.
    """
    
    def __init__(
        self,
        migrations_dir: str = "src/db/migrations/scripts",
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
    ):
        """
        Inicializace správce migrací.
        
        Args:
            migrations_dir: Adresář s migračními skripty
            host: Hostitel databáze
            port: Port databáze
            database: Název databáze
            user: Uživatelské jméno
            password: Heslo
        """
        self.migrations_dir = Path(migrations_dir)
        
        # Načtení konfigurace z proměnných prostředí s předností před parametry
        self.host = host or os.environ.get("DB_HOST", "localhost")
        self.port = port or int(os.environ.get("DB_PORT", 5432))
        self.database = database or os.environ.get("DB_NAME", "ecommerce")
        self.user = user or os.environ.get("DB_USER", "postgres")
        self.password = password or os.environ.get("DB_PASSWORD", "postgres")
        
        # Vytvoříme adresář pro migrační skripty, pokud neexistuje
        os.makedirs(self.migrations_dir, exist_ok=True)
        
        # Připojovací parametry
        self.db_params = {
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "user": self.user,
            "password": self.password
        }
        
        logger.info(f"Inicializace správce migrací pro databázi {self.database} na {self.host}:{self.port}")
    
    def initialize_schema_history(self) -> bool:
        """
        Inicializuje schéma a tabulku pro sledování historie migrací.
        
        Returns:
            True pokud inicializace proběhla úspěšně, jinak False
        """
        try:
            with psycopg2.connect(**self.db_params) as conn:
                conn.autocommit = True
                cursor = conn.cursor()
                
                # Vytvoříme schéma migrations, pokud neexistuje
                cursor.execute("CREATE SCHEMA IF NOT EXISTS migrations")
                
                # Vytvoříme tabulku schema_history, pokud neexistuje
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS migrations.schema_history (
                    id SERIAL PRIMARY KEY,
                    version VARCHAR(50) NOT NULL,
                    description TEXT NOT NULL,
                    type VARCHAR(20) NOT NULL,
                    script VARCHAR(1000) NOT NULL,
                    checksum VARCHAR(100) NOT NULL,
                    installed_by VARCHAR(100) NOT NULL,
                    installed_on TIMESTAMP NOT NULL DEFAULT now(),
                    execution_time INTEGER NOT NULL,
                    success BOOLEAN NOT NULL
                )
                """)
                
                # Vytvoříme index pro rychlejší vyhledávání
                cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_schema_history_version 
                ON migrations.schema_history(version)
                """)
                
                logger.info("Schéma a tabulka pro sledování migrací byly úspěšně inicializovány.")
                return True
                
        except Exception as e:
            logger.error(f"Chyba při inicializaci schématu a tabulky: {e}")
            return False
    
    def get_applied_migrations(self) -> List[str]:
        """
        Získá seznam již aplikovaných migrací.
        
        Returns:
            Seznam verzí aplikovaných migrací
        """
        applied_migrations = []
        
        try:
            with psycopg2.connect(**self.db_params) as conn:
                cursor = conn.cursor()
                
                # Zjistíme, zda tabulka existuje
                cursor.execute("""
                SELECT EXISTS (
                   SELECT FROM information_schema.tables 
                   WHERE table_schema = 'migrations'
                   AND table_name = 'schema_history'
                )
                """)
                
                table_exists = cursor.fetchone()[0]
                
                if not table_exists:
                    logger.warning("Tabulka migrations.schema_history neexistuje.")
                    return applied_migrations
                
                # Získáme seznam aplikovaných migrací
                cursor.execute("""
                SELECT version FROM migrations.schema_history
                WHERE success = true
                ORDER BY version
                """)
                
                for row in cursor.fetchall():
                    applied_migrations.append(row[0])
                
                logger.info(f"Nalezeno {len(applied_migrations)} již aplikovaných migrací.")
                return applied_migrations
                
        except Exception as e:
            logger.error(f"Chyba při získávání aplikovaných migrací: {e}")
            return applied_migrations
    
    def get_pending_migrations(self) -> List[Tuple[str, str, str]]:
        """
        Získá seznam čekajících migrací.
        
        Returns:
            Seznam čekajících migrací (verze, popis, cesta k souboru)
        """
        # Získání seznamu již aplikovaných migrací
        applied_migrations = self.get_applied_migrations()
        
        # Získání seznamu všech migračních skriptů
        migration_files = []
        
        # Nejprve zkontrolujeme, zda adresář existuje
        logger.info(f"Hledám migrační soubory v: {self.migrations_dir}")
        if not os.path.exists(self.migrations_dir):
            logger.warning(f"Adresář {self.migrations_dir} neexistuje!")
            return []
            
        # Výpis všech souborů v adresáři pro debugging
        all_files = os.listdir(self.migrations_dir)
        logger.info(f"Nalezené soubory v adresáři: {all_files}")
        
        # Hledání migračních souborů
        for file_name in all_files:
            # Přeskočíme __init__.py a další soubory, které nejsou migrační skripty
            if file_name.startswith('V') and file_name.endswith('.sql'):
                migration_files.append(os.path.join(self.migrations_dir, file_name))
        
        # Seřazení souborů podle názvu
        migration_files.sort()
        logger.info(f"Nalezené migrační soubory: {migration_files}")
        
        # Filtrování čekajících migrací
        pending_migrations = []
        
        for file_path in migration_files:
            # Parsování názvu souboru: V<version>__<description>.<extension>
            file_name = os.path.basename(file_path)
            parts = file_name.split('__', 1)
            
            if len(parts) != 2:
                logger.warning(f"Neplatný formát názvu souboru: {file_name}")
                continue
            
            version = parts[0][1:]  # Odstraníme počáteční 'V'
            description_with_ext = parts[1]
            description = os.path.splitext(description_with_ext)[0].replace('_', ' ')
            
            # Kontrola, zda migrace již byla aplikována
            if version not in applied_migrations:
                pending_migrations.append((version, description, str(file_path)))
        
        logger.info(f"Nalezeno {len(pending_migrations)} čekajících migrací.")
        return pending_migrations
    
    def calculate_checksum(self, file_path: str) -> str:
        """
        Vypočítá kontrolní součet souboru.
        
        Args:
            file_path: Cesta k souboru
            
        Returns:
            Kontrolní součet souboru (SHA-256)
        """
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.sha256(content).hexdigest()
        except Exception as e:
            logger.error(f"Chyba při výpočtu kontrolního součtu: {e}")
            return ""
    
    def execute_migration(self, version: str, description: str, file_path: str) -> bool:
        """
        Provede jednu migraci.
        
        Args:
            version: Verze migrace
            description: Popis migrace
            file_path: Cesta k souboru s migrací
            
        Returns:
            True pokud migrace proběhla úspěšně, jinak False
        """
        logger.info(f"Provádím migraci {version}: {description}")
        
        # Načtení obsahu SQL souboru
        try:
            with open(file_path, 'r') as f:
                sql_content = f.read()
        except Exception as e:
            logger.error(f"Chyba při čtení souboru {file_path}: {e}")
            return False
        
        # Výpočet kontrolního součtu
        checksum = self.calculate_checksum(file_path)
        
        try:
            with psycopg2.connect(**self.db_params) as conn:
                # Vypnutí autocommit pro transakce
                conn.autocommit = False
                cursor = conn.cursor()
                
                # Začátek měření času
                start_time = time.time()
                
                try:
                    # Provedení migrace
                    cursor.execute(sql_content)
                    
                    # Výpočet doby trvání
                    execution_time = int((time.time() - start_time) * 1000)
                    
                    # Záznam o úspěšné migraci
                    cursor.execute("""
                    INSERT INTO migrations.schema_history (
                        version, description, type, script, checksum, 
                        installed_by, installed_on, execution_time, success
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        version, description, 'SQL', os.path.basename(file_path), checksum,
                        self.user, datetime.now(), execution_time, True
                    ))
                    
                    # Potvrzení transakce
                    conn.commit()
                    logger.info(f"Migrace {version} byla úspěšně provedena (trvání: {execution_time} ms).")
                    return True
                    
                except Exception as e:
                    # Rollback transakce v případě chyby
                    conn.rollback()
                    
                    # Záznam o neúspěšné migraci
                    try:
                        conn.autocommit = True
                        execution_time = int((time.time() - start_time) * 1000)
                        cursor.execute("""
                        INSERT INTO migrations.schema_history (
                            version, description, type, script, checksum, 
                            installed_by, installed_on, execution_time, success
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            version, description, 'SQL', os.path.basename(file_path), checksum,
                            self.user, datetime.now(), execution_time, False
                        ))
                    except Exception as insert_error:
                        logger.error(f"Chyba při záznamu neúspěšné migrace: {insert_error}")
                    
                    logger.error(f"Chyba při provádění migrace {version}: {e}")
                    return False
                    
        except Exception as e:
            logger.error(f"Chyba při připojování k databázi: {e}")
            return False
    
    def migrate(self) -> bool:
        """
        Provede všechny čekající migrace.
        
        Returns:
            True pokud všechny migrace proběhly úspěšně, jinak False
        """
        # Inicializace schématu pro sledování migrací
        if not self.initialize_schema_history():
            logger.error("Nepodařilo se inicializovat schéma pro sledování migrací.")
            return False
        
        # Získání seznamu čekajících migrací
        pending_migrations = self.get_pending_migrations()
        
        if not pending_migrations:
            logger.info("Žádné čekající migrace.")
            return True
        
        # Provedení migrací
        success = True
        for version, description, file_path in pending_migrations:
            if not self.execute_migration(version, description, file_path):
                success = False
                # Pokračujeme v dalších migracích i v případě chyby
        
        if success:
            logger.info("Všechny migrace byly úspěšně provedeny.")
        else:
            logger.warning("Některé migrace selhaly.")
        
        return success
    
    def create_migration(self, description: str, content: str) -> Optional[str]:
        """
        Vytvoří novou migraci.
        
        Args:
            description: Popis migrace
            content: SQL obsah migrace
            
        Returns:
            Cesta k vytvořenému souboru nebo None v případě chyby
        """
        try:
            # Formátování popisu pro název souboru
            formatted_description = description.replace(' ', '_').lower()
            
            # Generování verze na základě aktuálního času (YYYYMMDDHHmmss)
            version = datetime.now().strftime("%Y%m%d%H%M%S")
            
            # Vytvoření názvu souboru
            file_name = f"V{version}__{formatted_description}.sql"
            file_path = self.migrations_dir / file_name
            
            # Zápis obsahu do souboru
            with open(file_path, 'w') as f:
                f.write(content)
            
            logger.info(f"Vytvořena nová migrace: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Chyba při vytváření migrace: {e}")
            return None


if __name__ == "__main__":
    # Příklad použití
    manager = MigrationManager()
    manager.migrate() 
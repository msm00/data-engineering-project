"""
CLI nástroj pro správu databázového schématu a migrací.
"""
import argparse
import logging
import os
import sys
from typing import Optional

from dotenv import load_dotenv

from src.db.migrations.migration_manager import MigrationManager

# Načtení proměnných prostředí
load_dotenv()

# Nastavení loggeru
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run_migrate(args):
    """
    Spustí migrace databázového schématu.
    """
    migration_manager = MigrationManager(
        migrations_dir=args.migrations_dir,
        host=args.host,
        port=args.port,
        database=args.database,
        user=args.user,
        password=args.password,
    )
    
    success = migration_manager.migrate()
    
    if success:
        logger.info("Migrace byly úspěšně provedeny.")
        return 0
    else:
        logger.error("Migrace selhaly.")
        return 1


def create_migration(args):
    """
    Vytvoří novou migraci.
    """
    if not args.description:
        logger.error("Musíte zadat popis migrace.")
        return 1
    
    migration_manager = MigrationManager(
        migrations_dir=args.migrations_dir,
        host=args.host,
        port=args.port,
        database=args.database,
        user=args.user,
        password=args.password,
    )
    
    # Načtení obsahu SQL souboru, pokud byl zadán
    content = ""
    if args.sql_file:
        try:
            with open(args.sql_file, 'r') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Chyba při čtení souboru {args.sql_file}: {e}")
            return 1
    
    # Vytvoření migrace
    file_path = migration_manager.create_migration(args.description, content)
    
    if file_path:
        logger.info(f"Migrace byla úspěšně vytvořena: {file_path}")
        return 0
    else:
        logger.error("Vytvoření migrace selhalo.")
        return 1


def show_migrations(args):
    """
    Zobrazí seznam migrací.
    """
    migration_manager = MigrationManager(
        migrations_dir=args.migrations_dir,
        host=args.host,
        port=args.port,
        database=args.database,
        user=args.user,
        password=args.password,
    )
    
    # Získání seznamu aplikovaných migrací
    applied_migrations = migration_manager.get_applied_migrations()
    
    # Získání seznamu čekajících migrací
    pending_migrations = migration_manager.get_pending_migrations()
    
    # Výpis aplikovaných migrací
    if applied_migrations:
        print("\nAplikované migrace:")
        print("-------------------")
        for version in applied_migrations:
            print(f"  {version}")
    else:
        print("\nŽádné aplikované migrace.")
    
    # Výpis čekajících migrací
    if pending_migrations:
        print("\nČekající migrace:")
        print("----------------")
        for version, description, file_path in pending_migrations:
            print(f"  {version}: {description}")
    else:
        print("\nŽádné čekající migrace.")
    
    return 0


def main():
    """
    Hlavní funkce CLI nástroje.
    """
    parser = argparse.ArgumentParser(description="Nástroj pro správu databázového schématu")
    
    # Společné parametry
    parser.add_argument("--migrations-dir", help="Adresář s migračními skripty", default="src/db/migrations/scripts")
    parser.add_argument("--host", help="Hostitel databáze", default=None)
    parser.add_argument("--port", help="Port databáze", type=int, default=None)
    parser.add_argument("--database", help="Název databáze", default=None)
    parser.add_argument("--user", help="Uživatelské jméno", default=None)
    parser.add_argument("--password", help="Heslo", default=None)
    
    # Podpříkazy
    subparsers = parser.add_subparsers(help="Příkazy")
    
    # Podpříkaz 'migrate'
    migrate_parser = subparsers.add_parser("migrate", help="Spustí migrace")
    migrate_parser.set_defaults(func=run_migrate)
    
    # Podpříkaz 'create'
    create_parser = subparsers.add_parser("create", help="Vytvoří novou migraci")
    create_parser.add_argument("description", help="Popis migrace")
    create_parser.add_argument("--sql-file", help="SQL soubor s obsahem migrace")
    create_parser.set_defaults(func=create_migration)
    
    # Podpříkaz 'show'
    show_parser = subparsers.add_parser("show", help="Zobrazí seznam migrací")
    show_parser.set_defaults(func=show_migrations)
    
    # Parsování argumentů
    args = parser.parse_args()
    
    # Kontrola, zda byl zadán podpříkaz
    if not hasattr(args, "func"):
        parser.print_help()
        return 1
    
    # Spuštění funkce příslušného podpříkazu
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main()) 
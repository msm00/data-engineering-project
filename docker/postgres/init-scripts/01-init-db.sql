-- Původní vytvoření uživatele pro aplikaci s omezenými právy již není potřeba,
-- protože budeme používat existujícího uživatele 'postgres'

-- Vytvoření databáze pro datový projekt (pokud už neexistuje)
-- Nejprve zkontrolujeme, zda databáze existuje
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ecommerce') THEN
        -- PostgreSQL proměnná prostředí POSTGRES_DB již vytvoří databázi, ale pro jistotu
        CREATE DATABASE ecommerce 
        WITH OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TEMPLATE = template0;
    END IF;
END
$$;

-- Připojení k vytvořené databázi
\connect ecommerce

-- Nastavení práv pro uživatele postgres (superuser, takže toto je jen pro úplnost)
GRANT ALL PRIVILEGES ON DATABASE ecommerce TO postgres;
GRANT ALL PRIVILEGES ON SCHEMA public TO postgres;

-- Vytvoření schématu pro správu verzování databáze
CREATE SCHEMA IF NOT EXISTS migrations;
GRANT ALL PRIVILEGES ON SCHEMA migrations TO postgres;

-- Vytvoření tabulky pro sledování migrací
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
);

-- Vytvoření indexu pro rychlejší vyhledávání
CREATE INDEX IF NOT EXISTS idx_schema_history_version ON migrations.schema_history(version);

-- Komentáře pro dokumentaci
COMMENT ON SCHEMA public IS 'Hlavní schema pro e-commerce data';
COMMENT ON SCHEMA migrations IS 'Metadata o databázových migracích';

-- Vytvoření rozšíření pro pokročilé funkce
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- Poznámka: Další rozšíření by vyžadovala použití speciálního PostgreSQL image s těmito rozšířeními

-- Nastavení vyhledávací cesty pro schémata
ALTER ROLE postgres SET search_path TO public; 
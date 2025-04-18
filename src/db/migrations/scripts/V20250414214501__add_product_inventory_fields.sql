-- Migrace: Přidání sloupců pro sledování skladových zásob produktů
-- Tato migrace demonstruje Schema Evolution v akci

-- Pro Time Travel schopnost přidáme sloupec s verzí
ALTER TABLE products ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1;

-- Přidání sloupců pro skladové zásoby
ALTER TABLE products ADD COLUMN IF NOT EXISTS stock_quantity INTEGER DEFAULT 0;
ALTER TABLE products ADD COLUMN IF NOT EXISTS reorder_level INTEGER DEFAULT 10;
ALTER TABLE products ADD COLUMN IF NOT EXISTS reorder_quantity INTEGER DEFAULT 20;

-- Přidání sloupce pro sledování dodavatele
ALTER TABLE products ADD COLUMN IF NOT EXISTS supplier_id INTEGER;

-- Přidání sloupce pro označení, zda je produkt aktivní
ALTER TABLE products ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

-- Přidání sloupce pro sledování změn
ALTER TABLE products ADD COLUMN IF NOT EXISTS last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Vytvoření triggeru pro automatickou aktualizaci verzí a časového razítka
CREATE OR REPLACE FUNCTION update_product_version_and_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.version = OLD.version + 1;
    NEW.last_updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Vytvoření triggeru
DROP TRIGGER IF EXISTS products_version_trigger ON products;
CREATE TRIGGER products_version_trigger
BEFORE UPDATE ON products
FOR EACH ROW
EXECUTE FUNCTION update_product_version_and_timestamp();

-- Komentáře k novým sloupcům pro lepší dokumentaci
COMMENT ON COLUMN products.version IS 'Verze záznamu pro Time Travel';
COMMENT ON COLUMN products.stock_quantity IS 'Aktuální množství na skladě';
COMMENT ON COLUMN products.reorder_level IS 'Množství, při kterém by měl být produkt objednán znovu';
COMMENT ON COLUMN products.reorder_quantity IS 'Standardní množství pro objednání';
COMMENT ON COLUMN products.supplier_id IS 'ID dodavatele produktu';
COMMENT ON COLUMN products.is_active IS 'Indikátor, zda je produkt aktivní/dostupný';
COMMENT ON COLUMN products.last_updated_at IS 'Čas poslední aktualizace záznamu'; 
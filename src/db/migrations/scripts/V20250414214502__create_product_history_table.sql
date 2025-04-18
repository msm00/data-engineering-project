-- Migrace: Vytvoření history tabulky pro Time Travel v products
-- Tato migrace demonstruje implementaci Time Travel pomocí history tabulky

-- Vytvoření tabulky pro history (ukládání změn)
CREATE TABLE IF NOT EXISTS products_history (
    history_id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    price DECIMAL(10, 2) NOT NULL,
    description TEXT,
    
    -- Nové sloupce přidané v předchozí migraci
    version INTEGER NOT NULL,
    stock_quantity INTEGER,
    reorder_level INTEGER,
    reorder_quantity INTEGER,
    supplier_id INTEGER,
    is_active BOOLEAN,
    
    -- Timestamp sloupce
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    last_updated_at TIMESTAMP,
    
    -- Metadata history záznamu
    valid_from TIMESTAMP NOT NULL,
    valid_to TIMESTAMP,
    operation CHAR(1) NOT NULL,  -- I=Insert, U=Update, D=Delete
    changed_by VARCHAR(100) NOT NULL
);

-- Vytvoření indexů pro rychlejší vyhledávání v history tabulce
CREATE INDEX idx_products_history_product_id ON products_history(product_id);
CREATE INDEX idx_products_history_valid_from ON products_history(valid_from);
CREATE INDEX idx_products_history_valid_to ON products_history(valid_to);

-- Trigger funkce pro automatické ukládání změn do history tabulky
CREATE OR REPLACE FUNCTION product_history_trigger_function()
RETURNS TRIGGER AS $$
DECLARE
    current_user_name VARCHAR(100);
BEGIN
    -- Získání aktuálního uživatele, který provedl změnu
    SELECT current_user INTO current_user_name;
    
    -- Pro INSERT operaci
    IF (TG_OP = 'INSERT') THEN
        INSERT INTO products_history (
            product_id, product_name, category, price, description,
            version, stock_quantity, reorder_level, reorder_quantity,
            supplier_id, is_active, created_at, updated_at, last_updated_at,
            valid_from, valid_to, operation, changed_by
        ) VALUES (
            NEW.product_id, NEW.product_name, NEW.category, NEW.price, NEW.description,
            NEW.version, NEW.stock_quantity, NEW.reorder_level, NEW.reorder_quantity,
            NEW.supplier_id, NEW.is_active, NEW.created_at, NEW.updated_at, NEW.last_updated_at,
            CURRENT_TIMESTAMP, NULL, 'I', current_user_name
        );
        RETURN NEW;
    
    -- Pro UPDATE operaci
    ELSIF (TG_OP = 'UPDATE') THEN
        -- Uzavřeme předchozí záznam
        UPDATE products_history 
        SET valid_to = CURRENT_TIMESTAMP 
        WHERE product_id = OLD.product_id 
        AND valid_to IS NULL;
        
        -- Vytvoříme nový záznam
        INSERT INTO products_history (
            product_id, product_name, category, price, description,
            version, stock_quantity, reorder_level, reorder_quantity,
            supplier_id, is_active, created_at, updated_at, last_updated_at,
            valid_from, valid_to, operation, changed_by
        ) VALUES (
            NEW.product_id, NEW.product_name, NEW.category, NEW.price, NEW.description,
            NEW.version, NEW.stock_quantity, NEW.reorder_level, NEW.reorder_quantity,
            NEW.supplier_id, NEW.is_active, NEW.created_at, NEW.updated_at, NEW.last_updated_at,
            CURRENT_TIMESTAMP, NULL, 'U', current_user_name
        );
        RETURN NEW;
    
    -- Pro DELETE operaci
    ELSIF (TG_OP = 'DELETE') THEN
        -- Uzavřeme předchozí záznam
        UPDATE products_history 
        SET valid_to = CURRENT_TIMESTAMP 
        WHERE product_id = OLD.product_id 
        AND valid_to IS NULL;
        
        -- Vytvoříme záznam o smazání
        INSERT INTO products_history (
            product_id, product_name, category, price, description,
            version, stock_quantity, reorder_level, reorder_quantity,
            supplier_id, is_active, created_at, updated_at, last_updated_at,
            valid_from, valid_to, operation, changed_by
        ) VALUES (
            OLD.product_id, OLD.product_name, OLD.category, OLD.price, OLD.description,
            OLD.version, OLD.stock_quantity, OLD.reorder_level, OLD.reorder_quantity,
            OLD.supplier_id, OLD.is_active, OLD.created_at, OLD.updated_at, OLD.last_updated_at,
            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'D', current_user_name
        );
        RETURN OLD;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Vytvoření triggeru pro všechny operace na tabulce products
DROP TRIGGER IF EXISTS products_history_trigger ON products;
CREATE TRIGGER products_history_trigger
AFTER INSERT OR UPDATE OR DELETE ON products
FOR EACH ROW
EXECUTE FUNCTION product_history_trigger_function();

-- Pohled pro snadné dotazování na produkty v určitém časovém bodu
CREATE OR REPLACE VIEW products_at_timestamp AS
SELECT p.product_id, p.product_name, p.category, p.price, p.description,
       p.version, p.stock_quantity, p.reorder_level, p.reorder_quantity,
       p.supplier_id, p.is_active, p.created_at, p.updated_at, p.last_updated_at,
       p.valid_from, p.valid_to
FROM products_history p;

-- Funkce pro získání produktu v určitém časovém bodu
CREATE OR REPLACE FUNCTION get_product_at_timestamp(p_product_id INTEGER, p_timestamp TIMESTAMP)
RETURNS TABLE (
    product_id INTEGER,
    product_name VARCHAR(255),
    category VARCHAR(100),
    price DECIMAL(10, 2),
    description TEXT,
    version INTEGER,
    stock_quantity INTEGER,
    reorder_level INTEGER,
    reorder_quantity INTEGER,
    supplier_id INTEGER,
    is_active BOOLEAN,
    valid_from TIMESTAMP,
    valid_to TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT p.product_id, p.product_name, p.category, p.price, p.description,
           p.version, p.stock_quantity, p.reorder_level, p.reorder_quantity,
           p.supplier_id, p.is_active, p.valid_from, p.valid_to
    FROM products_history p
    WHERE p.product_id = p_product_id
    AND p.valid_from <= p_timestamp
    AND (p.valid_to IS NULL OR p.valid_to > p_timestamp)
    ORDER BY p.valid_from DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql; 
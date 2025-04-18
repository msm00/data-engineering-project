# Schema Evolution a Time Travel v PostgreSQL

Tento modul implementuje správu databázového schématu s podporou **Schema Evolution** a **Time Travel** funkcionalit.

## Hlavní komponenty

1. **Migrační framework**
   - Správa verzí databázového schématu
   - Sledování aplikovaných migrací
   - CLI nástroj pro správu migrací

2. **Time Travel** implementace
   - Historie změn produktů
   - Možnost dotazování na stav dat v minulosti
   - Verzování záznamů s automatickými triggery

## Použití migračního nástroje

### Zobrazení migrací
```bash
python -m src.db.cli show
```

### Spuštění migračních skriptů
```bash
python -m src.db.cli migrate
```

### Vytvoření nové migrace
```bash
python -m src.db.cli create "popis migrace"
```

## Time Travel příklady

### Aktualizace produktů pro demonstraci
```bash
python -m src.examples.update_products
```

### Získání produktu v určitém čase
```sql
SELECT * FROM get_product_at_timestamp(product_id, timestamp);
```

### Získání historie změn produktu
```sql
SELECT * FROM products_history WHERE product_id = ? ORDER BY valid_from DESC;
```

## Důležité součásti implementace

1. **Migrační tabulka**
   - `migrations.schema_history` sleduje všechny aplikované migrace
   - Kontrolní součty pro detekci změn
   - Záznamy o úspěšnosti migrace

2. **Historie produktů**
   - `products_history` ukládá všechny změny produktů
   - Zachycuje stav před a po každé změně
   - Umožňuje dotazování na historická data

3. **Triggery**
   - Automatická aktualizace verzí při změnách
   - Zaznamenávání časů změn
   - Aktualizace historie produktů

## Schéma databáze

### Tabulka products
```
- product_id (PK)
- product_name
- category
- price
- description
- created_at
- updated_at
- version
- stock_quantity
- reorder_level
- reorder_quantity
- supplier_id
- is_active
- last_updated_at
```

### Tabulka products_history
```
- history_id (PK)
- product_id (FK)
- ... (všechny sloupce z products)
- valid_from
- valid_to
- operation
- changed_by
```

## Návrhové vzory a best practices

1. **Event Sourcing** - ukládáme historii změn, ne pouze aktuální stav
2. **Immutable Data** - záznamy v historii se nemění, vytváří se nové
3. **Version Control** - každý záznam má svou verzi
4. **Temporal Data** - každý záznam má časové rozmezí platnosti 
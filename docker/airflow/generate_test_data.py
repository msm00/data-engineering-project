#!/usr/bin/env python3
"""
Skript pro generování testovacích produktových dat
Vytvoří CSV soubor s náhodnými produkty pro testování ETL pipeline
"""

import pandas as pd
import numpy as np
import os
import random
from datetime import datetime

# Konstanty pro generování dat
NUM_PRODUCTS = 100
CATEGORIES = ['Electronics', 'Home Appliances', 'Sports', 'Home Decor', 'Clothing']
PRODUCT_PREFIXES = ['Smart', 'Pro', 'Ultra', 'Mega', 'Super', 'Eco', 'Digital', 'Premium', 'Basic', 'Advanced']
PRODUCT_TYPES = ['Phone', 'TV', 'Laptop', 'Watch', 'Camera', 'Speaker', 'Headphones', 'Tablet', 
                'Refrigerator', 'Microwave', 'Blender', 'Vacuum', 'Toaster', 
                'Ball', 'Racket', 'Shoes', 'Jersey', 'Bike', 
                'Lamp', 'Rug', 'Curtains', 'Pillow', 'Frame',
                'Shirt', 'Pants', 'Jacket', 'Hat', 'Socks']

# Zajistí, že adresář data existuje
DATA_DIR = '../project/data'
os.makedirs(DATA_DIR, exist_ok=True)

def generate_random_product():
    """Generuje náhodný produkt s realistickými atributy."""
    product_id = random.randint(1000, 9999)
    
    # Generování jména produktu
    prefix = random.choice(PRODUCT_PREFIXES)
    product_type = random.choice(PRODUCT_TYPES)
    product_name = f"{prefix} {product_type} {random.randint(1, 10)}"
    
    # Určení kategorie na základě typu produktu
    if product_type in ['Phone', 'TV', 'Laptop', 'Watch', 'Camera', 'Speaker', 'Headphones', 'Tablet']:
        category = 'Electronics'
    elif product_type in ['Refrigerator', 'Microwave', 'Blender', 'Vacuum', 'Toaster']:
        category = 'Home Appliances'
    elif product_type in ['Ball', 'Racket', 'Shoes', 'Jersey', 'Bike']:
        category = 'Sports'
    elif product_type in ['Lamp', 'Rug', 'Curtains', 'Pillow', 'Frame']:
        category = 'Home Decor'
    elif product_type in ['Shirt', 'Pants', 'Jacket', 'Hat', 'Socks']:
        category = 'Clothing'
    else:
        category = random.choice(CATEGORIES)
    
    # Generování ceny - s realistickým rozložením podle kategorie
    if category == 'Electronics':
        price = round(random.uniform(100, 2000), 2)
    elif category == 'Home Appliances':
        price = round(random.uniform(50, 800), 2)
    elif category == 'Sports':
        price = round(random.uniform(20, 300), 2)
    elif category == 'Home Decor':
        price = round(random.uniform(10, 200), 2)
    else:  # Clothing
        price = round(random.uniform(15, 150), 2)
    
    # Některé produkty nemají popis (simulace chybějících dat)
    if random.random() < 0.15:  # 15% produktů nemá popis
        description = None
    else:
        description = f"The {product_name} is a high-quality {product_type.lower()} suitable for all your {category.lower()} needs."
    
    # Množství na skladě
    stock = random.randint(0, 500)
    
    # Datum přidání produktu
    days_ago = random.randint(1, 365)
    current_date = datetime.now()
    date_added = current_date - pd.Timedelta(days=days_ago)
    date_added_str = date_added.strftime('%Y-%m-%d')
    
    # Některé produkty nemají rating nebo počet hodnocení (simulace chybějících dat)
    if random.random() < 0.2:  # 20% produktů nemá rating
        rating = None
    else:
        rating = round(random.uniform(1, 5), 1)
    
    if random.random() < 0.2 or rating is None:  # 20% produktů nemá počet hodnocení
        review_count = None
    else:
        review_count = random.randint(0, 500)
    
    # Status (in stock, low stock, out of stock)
    if stock == 0:
        status = 'Out of Stock'
    elif stock < 10:
        status = 'Low Stock'
    else:
        status = 'In Stock'
    
    # Pro simulaci duplicit, přidáme duplikáty s mírně pozměněnými daty
    is_duplicate = False
    if random.random() < 0.05:  # 5% šance na duplicitu
        is_duplicate = True
    
    return {
        'product_id': product_id,
        'product_name': product_name,
        'category': category,
        'price': price,
        'description': description,
        'stock': stock,
        'date_added': date_added_str,
        'rating': rating,
        'review_count': review_count,
        'status': status,
        'is_duplicate': is_duplicate
    }

def generate_products_dataframe(num_products):
    """Generuje DataFrame s náhodnými produkty."""
    products = []
    
    for _ in range(num_products):
        product = generate_random_product()
        products.append(product)
        
        # Pokud je produkt označen jako duplikát, přidáme ho ještě jednou s malými změnami
        if product['is_duplicate']:
            duplicate = product.copy()
            # Mírně změníme název (např. přidáme mezeru)
            duplicate['product_name'] = duplicate['product_name'].replace(' ', '  ')
            # Mírně upravíme cenu
            duplicate['price'] = round(duplicate['price'] * (1 + random.uniform(-0.05, 0.05)), 2)
            products.append(duplicate)
    
    # Vytvoření DataFrame
    df = pd.DataFrame(products)
    
    # Odstranění pomocného sloupce is_duplicate
    df = df.drop('is_duplicate', axis=1)
    
    return df

def main():
    """Hlavní funkce pro generování a ukládání testovacích dat."""
    print(f"Generuji {NUM_PRODUCTS} náhodných produktů...")
    
    # Generování DataFrame s náhodnými produkty
    products_df = generate_products_dataframe(NUM_PRODUCTS)
    
    # Ukládání do CSV
    csv_path = os.path.join(DATA_DIR, 'products.csv')
    products_df.to_csv(csv_path, index=False)
    
    print(f"Testovací data byla vygenerována a uložena do {csv_path}")
    print(f"Počet řádků: {len(products_df)}")
    print(f"Sloupce: {', '.join(products_df.columns)}")
    
    # Zobrazení několika ukázkových řádků
    print("\nUkázka dat:")
    print(products_df.head(3).to_string())

if __name__ == "__main__":
    main() 
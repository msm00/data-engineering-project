#!/usr/bin/env python3

import csv
import random
import os
from datetime import datetime, timedelta
import uuid

# Konstanty
NUM_CUSTOMERS = 1000
NUM_SALES = 10000
PRODUCT_CATEGORIES = ["Electronics", "Clothing", "Books", "Home", "Sports", "Food", "Beauty", "Toys", "Automotive", "Garden"]
PRODUCTS = {
    "Electronics": ["Laptop", "Smartphone", "Tablet", "Headphones", "TV", "Camera", "Speaker"],
    "Clothing": ["T-Shirt", "Jeans", "Dress", "Jacket", "Shoes", "Hat", "Socks"],
    "Books": ["Fiction", "Non-Fiction", "Science", "History", "Biography", "Fantasy", "Self-Help"],
    "Home": ["Sofa", "Table", "Chair", "Lamp", "Bed", "Desk", "Cabinet"],
    "Sports": ["Bicycle", "Tennis Racket", "Football", "Basketball", "Treadmill", "Yoga Mat", "Weights"],
    "Food": ["Coffee", "Tea", "Chocolate", "Pasta", "Rice", "Snacks", "Cereal"],
    "Beauty": ["Shampoo", "Conditioner", "Soap", "Perfume", "Makeup", "Facial Cream", "Lotion"],
    "Toys": ["Action Figure", "Board Game", "LEGO", "Doll", "Puzzle", "Plush Toy", "Remote Control Car"],
    "Automotive": ["Car Parts", "Oil", "Accessories", "Tools", "Car Care", "Electronics", "Tires"],
    "Garden": ["Plants", "Seeds", "Tools", "Furniture", "Decorations", "Pots", "Soil"]
}
REGIONS = ["North", "South", "East", "West", "Central"]
COUNTRIES = ["CZ", "SK", "DE", "PL", "AT", "FR", "IT", "ES", "UK", "US"]

# Adresář pro data
DATA_DIR = os.path.join("project", "data", "spark")
os.makedirs(DATA_DIR, exist_ok=True)

# Generování zákazníků
def generate_customers():
    customers = []
    for i in range(1, NUM_CUSTOMERS + 1):
        customer_id = i
        first_name = f"First{i}"
        last_name = f"Last{i}"
        email = f"customer{i}@example.com"
        region = random.choice(REGIONS)
        country = random.choice(COUNTRIES)
        registration_date = (datetime.now() - timedelta(days=random.randint(1, 1000))).strftime("%Y-%m-%d")
        
        customers.append({
            "customer_id": customer_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "region": region,
            "country": country,
            "registration_date": registration_date
        })
    
    return customers

# Generování prodejů
def generate_sales(customers):
    sales = []
    for i in range(1, NUM_SALES + 1):
        sale_id = str(uuid.uuid4())
        customer_id = random.choice(customers)["customer_id"]
        sale_date = (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d")
        
        category = random.choice(PRODUCT_CATEGORIES)
        product = random.choice(PRODUCTS[category])
        
        quantity = random.randint(1, 5)
        price = round(random.uniform(10, 1000), 2)
        total = round(quantity * price, 2)
        
        payment_method = random.choice(["Credit Card", "PayPal", "Bank Transfer", "Cash", "Crypto"])
        
        sales.append({
            "sale_id": sale_id,
            "customer_id": customer_id,
            "sale_date": sale_date,
            "category": category,
            "product": product,
            "quantity": quantity,
            "price": price,
            "total": total,
            "payment_method": payment_method
        })
    
    return sales

# Uložení dat do CSV
def save_to_csv(data, filename):
    file_path = os.path.join(DATA_DIR, filename)
    with open(file_path, 'w', newline='') as csvfile:
        if data:
            writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
    
    print(f"Soubor {filename} byl vytvořen s {len(data)} řádky.")

# Hlavní funkce
def main():
    print("Generuji data pro Spark aplikaci...")
    customers = generate_customers()
    sales = generate_sales(customers)
    
    save_to_csv(customers, "customers.csv")
    save_to_csv(sales, "sales.csv")
    
    print("Generování dat dokončeno!")

if __name__ == "__main__":
    main() 
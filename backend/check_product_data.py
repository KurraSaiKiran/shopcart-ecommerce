from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import json

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(url)

with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM amazon_products LIMIT 3")).fetchall()
    columns = conn.execute(text("SELECT * FROM amazon_products LIMIT 1")).keys()
    
    print("=== Product Data Sample ===\n")
    print("Columns:", list(columns))
    print("\n")
    
    for row in result:
        product = dict(zip(columns, row))
        print(f"ASIN: {product.get('asin')}")
        print(f"Title: {product.get('title')[:50]}...")
        print(f"Price: {product.get('price')}")
        print(f"Image URL: {product.get('img_url') or product.get('imgUrl') or 'MISSING'}")
        print(f"Stars: {product.get('stars')}")
        print(f"Reviews: {product.get('reviews')}")
        print("-" * 60)

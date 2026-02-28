from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import time

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(url)

print("Testing query...")
start = time.time()

with engine.connect() as conn:
    sql = """
        SELECT 
            asin, title, stars, reviews, price, category_id,
            imgUrl as img_url
        FROM amazon_products 
        LIMIT 20
    """
    result = conn.execute(text(sql)).fetchall()
    print(f"Query took: {time.time() - start:.2f}s")
    print(f"Returned {len(result)} products")
    
    if result:
        print(f"\nFirst product:")
        print(f"  ASIN: {result[0][0]}")
        print(f"  Title: {result[0][1][:50]}...")
        print(f"  Image: {result[0][6]}")

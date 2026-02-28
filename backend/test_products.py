from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

from urllib.parse import quote_plus
encoded_password = quote_plus(DB_PASSWORD)
url = f"mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(url)

print("Testing products query...")
with engine.connect() as conn:
    # First check what columns exist
    columns = conn.execute(text("SHOW COLUMNS FROM amazon_products")).fetchall()
    print("\nAvailable columns:")
    for col in columns:
        print(f"  - {col[0]}")
    
    # Try query without imgUrl
    sql = """
        SELECT *
        FROM amazon_products 
        LIMIT 2
    """
    result = conn.execute(text(sql)).fetchall()
    print(f"\nFound {len(result)} products")
    if result:
        print(f"First product ASIN: {result[0][0]}")

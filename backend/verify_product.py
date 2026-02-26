import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(url)

with engine.connect() as conn:
    print("Finding the 'dress' product...")
    result = conn.execute(text("SELECT asin, title, price, img_url FROM amazon_products WHERE title LIKE '%dress%' OR asin = '5464647745'"))
    rows = [dict(row._mapping) for row in result]
    if rows:
        for row in rows:
            # Print title and price, truncate image URL for display
            img_status = "Available" if row['img_url'] else "Missing"
            print(f"ASIN: {row['asin']} | Title: {row['title']} | Price: ${row['price']} | Image: {img_status}")
    else:
        print("Product not found in database yet.")

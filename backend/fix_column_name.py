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
    print("Renaming imgUrl to img_url for consistency...")
    try:
        conn.execute(text("ALTER TABLE amazon_products CHANGE imgUrl img_url LONGTEXT"))
        print("Success: Column renamed.")
    except Exception as e:
        print(f"Error: {e}")

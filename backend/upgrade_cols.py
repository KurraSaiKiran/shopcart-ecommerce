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
    print("Upgrading columns to LONGTEXT to support large media data...")
    try:
        conn.execute(text("ALTER TABLE amazon_products MODIFY COLUMN imgUrl LONGTEXT"))
        conn.execute(text("ALTER TABLE amazon_products MODIFY COLUMN video_url LONGTEXT"))
        print("Success: Columns upgraded.")
    except Exception as e:
        print(f"Error: {e}")

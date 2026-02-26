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
    print("Adding video_url column...")
    try:
        conn.execute(text("ALTER TABLE amazon_products ADD COLUMN video_url TEXT"))
        print("✓ video_url column added.")
    except Exception as e:
        print(f"Error adding video_url: {e}")

    print("Note: img_url will be mapped to imgUrl in the API code.")

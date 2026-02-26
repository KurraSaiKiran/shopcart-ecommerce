import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(url)

params = {"limit": 20, "offset": 0}
sql = """
    SELECT 
        asin, title, stars, reviews, price, category_id,
        img_url, video_url
    FROM amazon_products 
    LIMIT :limit OFFSET :offset
"""

try:
    with engine.connect() as conn:
        df = pd.read_sql(text(sql), conn, params=params)
    print("SUCCESS")
    print(f"Count: {len(df)}")
    print(df.head())
except Exception as e:
    print(f"FAILED: {e}")

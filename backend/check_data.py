import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
url = f'mysql+pymysql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}'
engine = create_engine(url)
with engine.connect() as conn:
    cat_count = conn.execute(text("SELECT COUNT(*) FROM amazon_categories")).scalar()
    cat_names = conn.execute(text("SELECT category_name FROM amazon_categories LIMIT 5")).fetchall()
    prod_count = conn.execute(text("SELECT COUNT(*) FROM amazon_products")).scalar()

print(f"Categories: {cat_count}")
print(f"Sample: {cat_names}")
print(f"Products: {prod_count}")

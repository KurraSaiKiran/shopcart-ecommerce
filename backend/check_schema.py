import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

load_dotenv()
url = f'mysql+pymysql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}'
engine = create_engine(url)
insp = inspect(engine)
print(f"Categories columns: {[c['name'] for c in insp.get_columns('amazon_categories')]}")
print(f"Products columns: {[c['name'] for c in insp.get_columns('amazon_products')]}")

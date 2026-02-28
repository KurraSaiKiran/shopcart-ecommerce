from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/"
engine = create_engine(url)

print("=== Checking all databases and tables ===\n")

with engine.connect() as conn:
    # Get all databases
    dbs = conn.execute(text("SHOW DATABASES")).fetchall()
    print("Available databases:")
    for db in dbs:
        print(f"  - {db[0]}")
    
    print("\n=== Checking database1 tables ===")
    conn.execute(text("USE database1"))
    
    # Get all tables
    tables = conn.execute(text("SHOW TABLES")).fetchall()
    print(f"\nTables in database1:")
    for table in tables:
        table_name = table[0]
        count = conn.execute(text(f"SELECT COUNT(*) FROM `{table_name}`")).scalar()
        print(f"  - {table_name}: {count:,} rows")

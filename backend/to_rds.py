"""
Load amazon_categories.csv and amazon_products.csv into MySQL RDS.

- amazon_categories  →  small file, loaded all at once
- amazon_products    →  large file (~367 MB), loaded in chunks to save memory

"""

import pandas as pd
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv
import os
import logging

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ── Configuration ──────────────────────────────────────────────────────────────
load_dotenv()

DB_HOST     = os.getenv("DB_HOST",     "your-rds-endpoint.rds.amazonaws.com")
DB_PORT     = int(os.getenv("DB_PORT", 3306))
DB_NAME     = os.getenv("DB_NAME",     "your_database")
DB_USER     = os.getenv("DB_USER",     "your_username")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_password")

# File paths
CATEGORIES_CSV  = os.getenv("CATEGORIES_CSV",  "amazon_categories.csv")
PRODUCTS_CSV    = os.getenv("PRODUCTS_CSV",    "amazon_products.csv")

# Target table names in MySQL
CATEGORIES_TABLE = os.getenv("CATEGORIES_TABLE", "amazon_categories")
PRODUCTS_TABLE   = os.getenv("PRODUCTS_TABLE",   "amazon_products")

# How to handle existing tables
IF_EXISTS  = os.getenv("IF_EXISTS", "replace")

# Rows per chunk when reading the large products file
READ_CHUNK_SIZE  = int(os.getenv("READ_CHUNK_SIZE", 50000))
WRITE_CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))


# ── Engine ─────────────────────────────────────────────────────────────────────

def build_engine():
    # Step 1 — Connect WITHOUT database to create it if needed
    base_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/"
    temp_engine = create_engine(base_url, pool_pre_ping=True)

    with temp_engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`"))
        logger.info(f"  ✓ Database '{DB_NAME}' ready")
    temp_engine.dispose()

    # Step 2 — Reconnect WITH the database
    url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(url, pool_pre_ping=True)


def table_exists(engine, table_name: str) -> bool:
    return table_name in inspect(engine).get_table_names()


# ── Load Categories (small file) ───────────────────────────────────────────────

def load_categories(engine):
    logger.info(f"── Loading '{CATEGORIES_CSV}' ──")
    df = pd.read_csv(CATEGORIES_CSV)

    logger.info(f"  Rows: {len(df):,}  |  Columns: {list(df.columns)}")
    logger.info(f"  Preview:\n{df.head(3)}\n")

    # ── Basic cleaning ──
    # Strip whitespace from string columns
    str_cols = df.select_dtypes(include="object").columns
    df[str_cols] = df[str_cols].apply(lambda c: c.str.strip())

    # Drop duplicate rows
    df = df.drop_duplicates()

    df.to_sql(
        name=CATEGORIES_TABLE,
        con=engine,
        if_exists=IF_EXISTS,
        index=False,
        chunksize=WRITE_CHUNK_SIZE,
        method="multi",
    )

    count = engine.connect().execute(
        text(f"SELECT COUNT(*) FROM `{CATEGORIES_TABLE}`")
    ).scalar()
    logger.info(f"  ✓ '{CATEGORIES_TABLE}' loaded — {count:,} rows in DB\n")


# ── Load Products (large file — chunked) ───────────────────────────────────────

def load_products(engine):
    logger.info(f"── Loading '{PRODUCTS_CSV}' (large file — chunked) ──")

    total_rows = 0
    first_chunk = True

    # pd.read_csv with chunksize returns an iterator — only one chunk
    # is in memory at a time, so this is safe for large files.
    for chunk_df in pd.read_csv(PRODUCTS_CSV, chunksize=READ_CHUNK_SIZE):

        # ── Basic cleaning per chunk ──
        str_cols = chunk_df.select_dtypes(include="object").columns
        chunk_df[str_cols] = chunk_df[str_cols].apply(lambda c: c.str.strip())
        chunk_df = chunk_df.drop_duplicates()

        # ── Optional type fixes — uncomment / edit as needed ──
        # chunk_df["price"]  = pd.to_numeric(chunk_df["price"],  errors="coerce")
        # chunk_df["rating"] = pd.to_numeric(chunk_df["rating"], errors="coerce")
        # chunk_df["date"]   = pd.to_datetime(chunk_df["date"],  errors="coerce")

        # First chunk: honour IF_EXISTS setting (replace or append).
        # Subsequent chunks: always append so we don't wipe previous data.
        mode = IF_EXISTS if first_chunk else "append"

        chunk_df.to_sql(
            name=PRODUCTS_TABLE,
            con=engine,
            if_exists=mode,
            index=False,
            chunksize=WRITE_CHUNK_SIZE,
            method="multi",
        )

        total_rows += len(chunk_df)
        logger.info(f"  Written so far: {total_rows:,} rows ...")
        first_chunk = False

    count = engine.connect().execute(
        text(f"SELECT COUNT(*) FROM `{PRODUCTS_TABLE}`")
    ).scalar()
    logger.info(f"  ✓ '{PRODUCTS_TABLE}' loaded — {count:,} rows in DB\n")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    logger.info("Connecting to RDS MySQL ...")
    engine = build_engine()

    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    logger.info("  ✓ Connection successful\n")

    # Load both tables
    load_categories(engine)
    load_products(engine)

    # Final summary
    logger.info("── Summary ──")
    for table in [CATEGORIES_TABLE, PRODUCTS_TABLE]:
        with engine.connect() as conn:
            count = conn.execute(text(f"SELECT COUNT(*) FROM `{table}`")).scalar()
        logger.info(f"  {table}: {count:,} rows")

    engine.dispose()
    logger.info("\nAll done ✓")


if __name__ == "__main__":
    main()
"""
Generate and load dummy data for a Recommendation Engine into MySQL RDS.

Tables created:
  - users               → user profiles
  - user_interactions   → views, clicks, purchases (implicit feedback)
  - product_ratings     → star ratings (explicit feedback)

Requirements:
    pip install pandas sqlalchemy pymysql python-dotenv faker
"""

import random
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from faker import Faker
import os
import logging

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

fake = Faker()
random.seed(42)

# ── Config ─────────────────────────────────────────────────────────────────────
load_dotenv()

DB_HOST     = os.getenv("DB_HOST")
DB_PORT     = int(os.getenv("DB_PORT", 3306))
DB_NAME     = os.getenv("DB_NAME")
DB_USER     = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

NUM_USERS        = 5_000    # number of fake users to generate
NUM_INTERACTIONS = 100_000  # number of interaction events (views/clicks/purchases)
NUM_RATINGS      = 30_000   # number of explicit star ratings

IF_EXISTS = "replace"


# ── Engine ─────────────────────────────────────────────────────────────────────

def build_engine():
    url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(url, pool_pre_ping=True)


# ── Fetch existing product IDs from DB ─────────────────────────────────────────

def get_product_ids(engine):
    logger.info("Fetching product IDs from amazon_products ...")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT asin FROM amazon_products LIMIT 50000"))
        ids = [row[0] for row in result]
    logger.info(f"  → {len(ids):,} product IDs loaded")
    return ids


# ── Generate Users ─────────────────────────────────────────────────────────────

def generate_users(n: int) -> pd.DataFrame:
    logger.info(f"Generating {n:,} users ...")

    genders    = ["M", "F", "Other"]
    age_groups = ["18-24", "25-34", "35-44", "45-54", "55+"]

    users = []
    for i in range(1, n + 1):
        users.append({
            "user_id":    i,
            "name":       fake.name(),
            "email":      fake.unique.email(),
            "age_group":  random.choice(age_groups),
            "gender":     random.choice(genders),
            "country":    fake.country(),
            "created_at": fake.date_time_between(start_date="-3y", end_date="now"),
        })

    df = pd.DataFrame(users)
    logger.info(f"  → {len(df):,} users generated")
    return df


# ── Generate User Interactions (implicit feedback) ─────────────────────────────

def generate_interactions(n: int, user_ids: list, product_ids: list) -> pd.DataFrame:
    logger.info(f"Generating {n:,} interactions ...")

    event_types   = ["view", "view", "view", "click", "click", "add_to_cart", "purchase"]
    # 'view' is more common, so it appears multiple times in the list

    interactions = []
    for i in range(1, n + 1):
        event = random.choice(event_types)
        interactions.append({
            "interaction_id": i,
            "user_id":        random.choice(user_ids),
            "product_id":     random.choice(product_ids),
            "event_type":     event,
            "session_id":     fake.uuid4(),
            "timestamp":      fake.date_time_between(start_date="-1y", end_date="now"),
        })

    df = pd.DataFrame(interactions)
    logger.info(f"  → {len(df):,} interactions generated")
    return df


# ── Generate Product Ratings (explicit feedback) ───────────────────────────────

def generate_ratings(n: int, user_ids: list, product_ids: list) -> pd.DataFrame:
    logger.info(f"Generating {n:,} ratings ...")

    ratings = []
    seen = set()  # avoid duplicate user+product combinations

    attempts = 0
    while len(ratings) < n and attempts < n * 3:
        attempts += 1
        uid = random.choice(user_ids)
        pid = random.choice(product_ids)
        key = (uid, pid)

        if key in seen:
            continue
        seen.add(key)

        # Slightly skew ratings towards higher values (realistic)
        rating = random.choices([1, 2, 3, 4, 5], weights=[5, 8, 15, 35, 37])[0]

        ratings.append({
            "rating_id":  len(ratings) + 1,
            "user_id":    uid,
            "product_id": pid,
            "rating":     rating,
            "review":     fake.sentence(nb_words=random.randint(5, 20)) if random.random() > 0.4 else None,
            "rated_at":   fake.date_time_between(start_date="-1y", end_date="now"),
        })

    df = pd.DataFrame(ratings)
    logger.info(f"  → {len(df):,} ratings generated")
    return df


# ── Upload to DB ───────────────────────────────────────────────────────────────

def upload(df: pd.DataFrame, engine, table: str):
    logger.info(f"Uploading to '{table}' ...")
    df.to_sql(
        name=table,
        con=engine,
        if_exists=IF_EXISTS,
        index=False,
        chunksize=1000,
        method="multi",
    )
    with engine.connect() as conn:
        count = conn.execute(text(f"SELECT COUNT(*) FROM `{table}`")).scalar()
    logger.info(f"  ✓ '{table}' — {count:,} rows in DB")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    engine = build_engine()

    # Test connection
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    logger.info("✓ Connected to RDS\n")

    # Fetch real product IDs from existing table
    product_ids = get_product_ids(engine)

    # Generate all data
    users_df        = generate_users(NUM_USERS)
    user_ids        = users_df["user_id"].tolist()

    interactions_df = generate_interactions(NUM_INTERACTIONS, user_ids, product_ids)
    ratings_df      = generate_ratings(NUM_RATINGS, user_ids, product_ids)

    # Upload to DB
    upload(users_df,        engine, "users")
    upload(interactions_df, engine, "user_interactions")
    upload(ratings_df,      engine, "product_ratings")

    # Final summary
    logger.info("\n── Final Summary ──")
    for table in ["amazon_categories", "amazon_products", "users", "user_interactions", "product_ratings"]:
        with engine.connect() as conn:
            count = conn.execute(text(f"SELECT COUNT(*) FROM `{table}`")).scalar()
        logger.info(f"  {table}: {count:,} rows")

    engine.dispose()
    logger.info("\nAll done ✓")


if __name__ == "__main__":
    main()
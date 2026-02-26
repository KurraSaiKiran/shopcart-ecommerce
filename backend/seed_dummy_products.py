import os
import random
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from faker import Faker

load_dotenv()
fake = Faker()

DB_HOST     = os.getenv("DB_HOST")
DB_PORT     = int(os.getenv("DB_PORT", 3306))
DB_NAME     = os.getenv("DB_NAME")
DB_USER     = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(url)

def seed_products():
    with engine.connect() as conn:
        # Get existing categories
        cats = conn.execute(text("SELECT id FROM amazon_categories LIMIT 20")).fetchall()
        cat_ids = [c[0] for c in cats]
        
        if not cat_ids:
            print("No categories found. Run load_categories first.")
            return

        print(f"Seeding 10 products into {DB_NAME}...")
        for _ in range(10):
            asin = fake.bothify(text='B0#########')
            title = fake.sentence(nb_words=6)
            price = round(random.uniform(10, 500), 2)
            stars = round(random.uniform(3.5, 5.0), 1)
            reviews = random.randint(50, 5000)
            category_id = random.choice(cat_ids)
            img_url = f"https://picsum.photos/seed/{asin}/400/400"
            
            sql = text("""
                INSERT INTO amazon_products (asin, title, price, stars, reviews, category_id, imgUrl)
                VALUES (:asin, :title, :price, :stars, :reviews, :category_id, :imgUrl)
                ON DUPLICATE KEY UPDATE title=title
            """)
            conn.execute(sql, {
                "asin": asin,
                "title": title,
                "price": price,
                "stars": stars,
                "reviews": reviews,
                "category_id": category_id,
                "imgUrl": img_url
            })
            conn.commit()
    print("✓ Done seeding.")

if __name__ == "__main__":
    seed_products()

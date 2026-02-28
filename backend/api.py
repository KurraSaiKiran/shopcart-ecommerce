import os
print(f"DEBUG: Executing api.py from: {os.path.abspath(__file__)}")
"""
FastAPI Amazon Product API (Recommendation Engine Removed)

Endpoints:
  GET  /health                              → API + DB status
  GET  /users/{user_id}/profile             → User info + ratings
  GET  /stats                               → Overall system stats
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from dotenv import load_dotenv
import pandas as pd
import logging
from datetime import datetime
import os
from recommendation_engine import RecommendationEngine

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

# ── FastAPI App ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Amazon Product API",
    description="""
    Core Product and User API. Recommendation Engine has been decommissioned.
    """,
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global State ───────────────────────────────────────────────────────────────
state = {
    "engine":            None,
    "ready":             False,
    "recommender":       None,
}

# ── Configuration ──────────────────────────────────────────────────────────────
DB_HOST     = os.getenv("DB_HOST")
DB_PORT     = int(os.getenv("DB_PORT", 3306))
DB_NAME     = os.getenv("DB_NAME")
DB_USER     = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# ── Helper: Run SQL and return DataFrame ───────────────────────────────────────

def query_db(sql: str, params: dict = {}) -> pd.DataFrame:
    with state["engine"].connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)

def build_engine():
    from sqlalchemy import create_engine
    from urllib.parse import quote_plus
    
    # URL-encode the password to handle special characters like @
    encoded_password = quote_plus(DB_PASSWORD)
    url = f"mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(url, pool_pre_ping=True)

# ── Startup: Connect DB ──────────────────────────────────────────

@app.on_event("startup")
def startup():
    logger.info(f"Starting up API from {os.path.abspath(__file__)} ...")
    engine = build_engine()
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    logger.info("✓ Connected to RDS")

    state["engine"]            = engine
    state["recommender"]       = RecommendationEngine(engine)
    state["ready"]             = True
    logger.info("✓ API ready")
    logger.info("✓ Recommendation engine initialized")


# ══════════════════════════════════════════════════════════════════════════════
# 1. HEALTH CHECK
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/health", tags=["General"])
def health_check():
    """Check if API and DB are running."""
    try:
        with state["engine"].connect() as conn:
            conn.execute(text("SELECT 1"))
        return {
            "status":      "ok",
            "db_connected": True,
            "timestamp":   datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")


# ══════════════════════════════════════════════════════════════════════════════
# 2. PRODUCTS (CRUD)
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/products/search", tags=["Products"])
def search_products(
    q: str = Query(default="", description="Search query"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    category_id: int = Query(default=None),
    min_price: float = Query(default=None),
    max_price: float = Query(default=None),
    min_rating: float = Query(default=None),
):
    """Search products with filters."""
    offset = (page - 1) * limit
    where_clauses = []
    params = {"limit": limit, "offset": offset}
    
    if q:
        where_clauses.append("(title LIKE :search OR asin LIKE :search)")
        params["search"] = f"%{q}%"
    
    if category_id:
        where_clauses.append("category_id = :cat_id")
        params["cat_id"] = category_id
    
    if min_price is not None:
        where_clauses.append("price >= :min_price")
        params["min_price"] = min_price
    
    if max_price is not None:
        where_clauses.append("price <= :max_price")
        params["max_price"] = max_price
    
    if min_rating is not None:
        where_clauses.append("stars >= :min_rating")
        params["min_rating"] = min_rating
    
    where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    
    sql = f"""
        SELECT 
            asin, title, stars, reviews, price, category_id, img_url
        FROM amazon_products 
        {where_clause} 
        LIMIT :limit OFFSET :offset
    """
    
    count_sql = f"SELECT COUNT(*) FROM amazon_products {where_clause}"
    
    try:
        with state["engine"].connect() as conn:
            count_params = {k: v for k, v in params.items() if k not in ['limit', 'offset']}
            total = conn.execute(text(count_sql), count_params).scalar()
            df = pd.read_sql(text(sql), conn, params=params)
        
        products = df.fillna("N/A").to_dict(orient="records")
        for product in products:
            if product.get('price') and product['price'] != 'N/A':
                import random
                discount_factor = random.uniform(1.2, 1.5)
                product['original_price'] = round(float(product['price']) * discount_factor, 2)
        
        return {
            "page": page,
            "limit": limit,
            "total_results": int(total),
            "query": q,
            "products": products
        }
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return {"page": page, "limit": limit, "total_results": 0, "query": q, "products": []}

@app.get("/products", tags=["Products"])
def get_products(
    page:  int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    category_id: int = Query(default=None),
):
    """List products with pagination and optional category filter."""
    offset = (page - 1) * limit
    where_clause = ""
    params = {"limit": limit, "offset": offset}
    
    if category_id:
        where_clause = "WHERE category_id = :cat_id"
        params["cat_id"] = category_id

    sql = f"""
        SELECT 
            asin, title, stars, reviews, price, category_id, img_url
        FROM amazon_products 
        {where_clause} 
        LIMIT :limit OFFSET :offset
    """
    
    count_sql = f"SELECT COUNT(*) FROM amazon_products {where_clause}"
    
    try:
        with state["engine"].connect() as conn:
            total = conn.execute(text(count_sql), {k: v for k, v in params.items() if k == "cat_id"}).scalar()
            df = pd.read_sql(text(sql), conn, params=params)
        
        products = df.fillna("N/A").to_dict(orient="records")
        for product in products:
            if product.get('price') and product['price'] != 'N/A':
                import random
                discount_factor = random.uniform(1.2, 1.5)
                product['original_price'] = round(float(product['price']) * discount_factor, 2)
        
        return {
            "page": page,
            "limit": limit,
            "total_results": int(total),
            "products": products
        }
    except Exception as e:
        logger.error(f"Products query failed: {e}")
        return {"page": page, "limit": limit, "total_results": 0, "products": []}

@app.get("/products/{asin}", tags=["Products"])
def get_product(asin: str):
    """Get a single product by ASIN."""
    sql = "SELECT * FROM amazon_products WHERE asin = :asin"
    df = query_db(sql, {"asin": asin})
    if df.empty:
        raise HTTPException(status_code=404, detail="Product not found")
    return df.fillna("N/A").to_dict(orient="records")[0]

@app.post("/products", tags=["Products"])
def create_product(product: dict):
    """Create a new product."""
    required = ["asin", "title", "category_id"]
    for field in required:
        if field not in product:
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
            
    try:
        with state["engine"].begin() as conn:
            cols = ", ".join(product.keys())
            placeholders = ", ".join([f":{k}" for k in product.keys()])
            sql = text(f"INSERT INTO amazon_products ({cols}) VALUES ({placeholders})")
            conn.execute(sql, product)
        return {"message": "Product created successfully", "asin": product["asin"]}
    except Exception as e:
        logger.error(f"Create product failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/products/{asin}", tags=["Products"])
def update_product(asin: str, product: dict):
    """Update an existing product."""
    params = {**product}
    if "asin" in params:
        del params["asin"]

    try:
        with state["engine"].begin() as conn:
            updates = ", ".join([f"{k} = :{k}" for k in params.keys()])
            sql = text(f"UPDATE amazon_products SET {updates} WHERE asin = :target_asin")
            conn.execute(sql, {**params, "target_asin": asin})
        return {"message": "Product updated successfully"}
    except Exception as e:
        logger.error(f"Update product failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/products/{asin}", tags=["Products"])
def delete_product(asin: str):
    """Delete a product."""
    try:
        with state["engine"].begin() as conn:
            conn.execute(text("DELETE FROM amazon_products WHERE asin = :asin"), {"asin": asin})
        return {"message": "Product deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════════════════════════════════════
# 3. CATEGORIES
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/categories", tags=["General"])
def get_categories():
    """List all categories."""
    df = query_db("SELECT * FROM amazon_categories ORDER BY category_name")
    return df.to_dict(orient="records")


# ══════════════════════════════════════════════════════════════════════════════
# 4. USER PROFILE
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/users/{user_id}/profile", tags=["Users"])
def get_user_profile(user_id: int):
    """
    Full user profile:
    - User info (name, age group, country)
    - Products they have rated
    """
    user_df = query_db("SELECT * FROM users WHERE user_id = :uid", {"uid": user_id})
    if user_df.empty:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found.")

    ratings_df = query_db("""
        SELECT
            r.product_id,
            r.rating,
            r.rated_at,
            p.title   AS product_name,
            p.price,
            c.category_name
        FROM product_ratings r
        LEFT JOIN amazon_products   p ON r.product_id  = p.asin
        LEFT JOIN amazon_categories c ON p.category_id = c.id
        WHERE r.user_id = :uid
        ORDER BY r.rating DESC
    """, {"uid": user_id})

    return {
        "user":                  user_df.fillna("N/A").to_dict(orient="records")[0],
        "total_ratings":         len(ratings_df),
        "ratings":               ratings_df.fillna("N/A").to_dict(orient="records"),
    }


# ══════════════════════════════════════════════════════════════════════════════
# 5. OVERALL STATS
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/stats", tags=["General"])
def get_stats():
    """High-level stats about the system."""
    stats = {}

    queries = {
        "total_users":           "SELECT COUNT(*) FROM users",
        "total_products":        "SELECT COUNT(*) FROM amazon_products",
        "total_categories":      "SELECT COUNT(*) FROM amazon_categories",
        "total_ratings":         "SELECT COUNT(*) FROM product_ratings",
    }

    with state["engine"].connect() as conn:
        for key, sql in queries.items():
            result = conn.execute(text(sql)).scalar()
            stats[key] = float(result) if result is not None else 0

    return stats


# ══════════════════════════════════════════════════════════════════════════════
# 6. RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/recommendations/collaborative/{user_id}", tags=["Recommendations"])
def get_collaborative_recommendations(user_id: int, limit: int = Query(default=10, ge=1, le=50)):
    """
    Collaborative Filtering: "Users like you bought this"
    Recommends products based on similar users' preferences.
    """
    try:
        recommendations = state["recommender"].collaborative_filtering(user_id, top_n=limit)
        return {
            "user_id": user_id,
            "method": "collaborative_filtering",
            "description": "Users like you bought this",
            "recommendations": recommendations
        }
    except Exception as e:
        logger.error(f"Collaborative filtering failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/recommendations/similar/{product_id}", tags=["Recommendations"])
def get_similar_products(product_id: str, limit: int = Query(default=10, ge=1, le=50)):
    """
    Content-Based Filtering: "Similar products to this one"
    Recommends products similar to the given product.
    """
    try:
        recommendations = state["recommender"].content_based_filtering(product_id, top_n=limit)
        return {
            "product_id": product_id,
            "method": "content_based_filtering",
            "description": "Similar products to this one",
            "recommendations": recommendations
        }
    except Exception as e:
        logger.error(f"Content-based filtering failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/recommendations/hybrid/{user_id}", tags=["Recommendations"])
def get_hybrid_recommendations(
    user_id: int,
    product_id: str = Query(default=None),
    limit: int = Query(default=10, ge=1, le=50)
):
    """
    Hybrid Recommendations: Combines collaborative and content-based filtering.
    Provides the best of both worlds.
    """
    try:
        recommendations = state["recommender"].hybrid_recommendations(
            user_id, product_id, top_n=limit
        )
        return {
            "user_id": user_id,
            "product_id": product_id,
            "method": "hybrid",
            "description": "Personalized recommendations combining multiple techniques",
            "recommendations": recommendations
        }
    except Exception as e:
        logger.error(f"Hybrid recommendations failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recommendations/similarity", tags=["Recommendations"])
def calculate_product_similarity(product_ids: list[str]):
    """
    Calculate cosine similarity matrix for given products.
    Shows mathematical similarity between products.
    """
    try:
        if len(product_ids) < 2:
            raise HTTPException(status_code=400, detail="Need at least 2 products")
        
        if len(product_ids) > 20:
            raise HTTPException(status_code=400, detail="Maximum 20 products allowed")
        
        result = state["recommender"].product_similarity_matrix(product_ids)
        
        if result is None:
            raise HTTPException(status_code=404, detail="Products not found")
        
        return {
            "method": "cosine_similarity",
            "description": "Mathematical similarity calculation between products",
            "products": result['products'],
            "similarity_matrix": result['similarity_matrix']
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Similarity calculation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Run ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8005, reload=True)

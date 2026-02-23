"""
FastAPI Recommendation API

Imports core logic from recommendation_engine.py (must be in same folder).

Endpoints:
  GET  /health                              → API + DB status
  GET  /recommend/{user_id}                 → Saved recommendations from DB
  GET  /recommend/{user_id}/top             → Best single recommendation
  GET  /recommend/{user_id}/category        → Filter recommendations by category
  GET  /recommend/{user_id}/live            → Re-compute recommendations on the fly
  GET  /similar-users/{user_id}             → Most similar users
  GET  /products/top-recommended            → Most recommended products globally
  GET  /products/{product_id}/recommended-to → Which users got this product
  GET  /users/{user_id}/profile             → User info + ratings + recommendations
  GET  /stats                               → Overall system stats
  POST /model/reload                        → Reload similarity model from DB
  POST /recommendations/generate            → Trigger batch generation

"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from sqlalchemy import text
from dotenv import load_dotenv
import pandas as pd
import logging
from datetime import datetime

# ── Import everything needed from recommendation_engine.py ────────────────────
from recommendation_engine import (
    build_engine,
    load_model,
    get_recommendations,
    enrich_with_product_details,
    save_recommendations,
    batch_generate,
)

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

# ── FastAPI App ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Amazon Recommendation API",
    description="""
    Collaborative Filtering Recommendation Engine using Cosine Similarity.
    Reads pre-computed recommendations from DB and also supports live computation.
    """,
    version="2.0.0",
)

# ── Global State ───────────────────────────────────────────────────────────────
state = {
    "engine":            None,
    "matrix":            None,
    "similarity_matrix": None,
    "ready":             False,
}


# ── Helper: Run SQL and return DataFrame ───────────────────────────────────────

def query_db(sql: str, params: dict = {}) -> pd.DataFrame:
    with state["engine"].connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)


# ── Startup: Connect DB + Load Model ──────────────────────────────────────────

@app.on_event("startup")
def startup():
    logger.info("Starting up API ...")
    engine = build_engine()
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    logger.info("✓ Connected to RDS")

    matrix, similarity_matrix = load_model(engine)

    state["engine"]            = engine
    state["matrix"]            = matrix
    state["similarity_matrix"] = similarity_matrix
    state["ready"]             = True
    logger.info("✓ API ready")


# ══════════════════════════════════════════════════════════════════════════════
# 1. HEALTH CHECK
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/health", tags=["General"])
def health_check():
    """Check if API, DB and model are all running."""
    try:
        with state["engine"].connect() as conn:
            conn.execute(text("SELECT 1"))
        return {
            "status":      "ok",
            "model_ready": state["ready"],
            "users":       int(state["matrix"].shape[0]) if state["ready"] else 0,
            "products":    int(state["matrix"].shape[1]) if state["ready"] else 0,
            "timestamp":   datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")


# ══════════════════════════════════════════════════════════════════════════════
# 2. GET SAVED RECOMMENDATIONS FOR A USER (from DB)
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/recommend/{user_id}", tags=["Recommendations"])
def get_saved_recommendations(
    user_id: int,
    top_n:   int = Query(default=10, ge=1, le=50, description="Number of results to return"),
):
    """
    Fetch pre-computed recommendations for a user from the DB.
    Includes product name, price, category, and predicted rating.
    """
    sql = """
        SELECT
            r.`rank`,
            r.product_id,
            r.predicted_rating,
            r.generated_at,
            p.title           AS product_name,
            p.price,
            p.stars           AS avg_rating,
            p.reviews         AS total_reviews,
            c.category_name
        FROM recommendations r
        LEFT JOIN amazon_products   p ON r.product_id  = p.asin
        LEFT JOIN amazon_categories c ON p.category_id = c.id
        WHERE r.user_id = :user_id
        ORDER BY r.`rank`
        LIMIT :top_n
    """
    df = query_db(sql, {"user_id": user_id, "top_n": top_n})

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No saved recommendations for user {user_id}. Run batch generation first."
        )

    return {
        "user_id":         user_id,
        "total_results":   len(df),
        "recommendations": df.fillna("N/A").to_dict(orient="records"),
    }


# ══════════════════════════════════════════════════════════════════════════════
# 3. TOP #1 RECOMMENDATION FOR A USER
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/recommend/{user_id}/top", tags=["Recommendations"])
def get_top_recommendation(user_id: int):
    """
    Returns only the single best (rank=1) recommendation for a user.
    Useful for showing one featured product on a homepage.
    """
    sql = """
        SELECT
            r.`rank`,
            r.product_id,
            r.predicted_rating,
            p.title   AS product_name,
            p.price,
            p.stars   AS avg_rating,
            c.category_name
        FROM recommendations r
        LEFT JOIN amazon_products   p ON r.product_id  = p.asin
        LEFT JOIN amazon_categories c ON p.category_id = c.id
        WHERE r.user_id = :user_id AND r.`rank` = 1
    """
    df = query_db(sql, {"user_id": user_id})

    if df.empty:
        raise HTTPException(status_code=404, detail=f"No recommendation found for user {user_id}.")

    return {
        "user_id":            user_id,
        "top_recommendation": df.fillna("N/A").to_dict(orient="records")[0],
    }


# ══════════════════════════════════════════════════════════════════════════════
# 4. FILTER RECOMMENDATIONS BY CATEGORY
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/recommend/{user_id}/category", tags=["Recommendations"])
def get_recommendations_by_category(
    user_id:       int,
    category_name: str = Query(..., description="Category to filter by e.g. 'Clothing'"),
    top_n:         int = Query(default=10, ge=1, le=50),
):
    """
    Recommendations for a user filtered by product category.
    Useful when the user is browsing a specific section of the store.
    """
    sql = """
        SELECT
            r.`rank`,
            r.product_id,
            r.predicted_rating,
            p.title   AS product_name,
            p.price,
            p.stars   AS avg_rating,
            c.category_name
        FROM recommendations r
        LEFT JOIN amazon_products   p ON r.product_id  = p.asin
        LEFT JOIN amazon_categories c ON p.category_id = c.id
        WHERE r.user_id = :user_id
          AND c.category_name LIKE :category
        ORDER BY r.`rank`
        LIMIT :top_n
    """
    df = query_db(sql, {"user_id": user_id, "category": f"%{category_name}%", "top_n": top_n})

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No recommendations for user {user_id} in category '{category_name}'."
        )

    return {
        "user_id":         user_id,
        "category_filter": category_name,
        "total_results":   len(df),
        "recommendations": df.fillna("N/A").to_dict(orient="records"),
    }


# ══════════════════════════════════════════════════════════════════════════════
# 5. LIVE RECOMMENDATIONS (re-compute on the fly, don't read from DB)
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/recommend/{user_id}/live", tags=["Recommendations"])
def get_live_recommendations(
    user_id: int,
    top_n:   int  = Query(default=10, ge=1, le=50),
    save:    bool = Query(default=False, description="Save result to DB after computing"),
):
    """
    Re-compute recommendations live using the in-memory model.
    Slower than /recommend/{user_id} but always fresh.
    Use save=true to also persist results to DB.
    """
    if not state["ready"]:
        raise HTTPException(status_code=503, detail="Model not ready yet.")

    rec_df = get_recommendations(
        user_id,
        state["matrix"],
        state["similarity_matrix"],
        top_n=top_n
    )

    if rec_df.empty:
        raise HTTPException(status_code=404, detail=f"No recommendations found for user {user_id}.")

    rec_df = enrich_with_product_details(rec_df, state["engine"])

    if save:
        save_recommendations(user_id, rec_df, state["engine"])

    return {
        "user_id":         user_id,
        "source":          "live_computed",
        "total_results":   len(rec_df),
        "recommendations": rec_df.fillna("N/A").to_dict(orient="records"),
    }


# ══════════════════════════════════════════════════════════════════════════════
# 6. SIMILAR USERS
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/similar-users/{user_id}", tags=["Users"])
def get_similar_users(
    user_id: int,
    top_n:   int = Query(default=10, ge=1, le=50),
):
    """
    Find users most similar to the given user based on cosine similarity.
    Shows similarity score and how many products each user has rated.
    """
    import numpy as np

    if not state["ready"]:
        raise HTTPException(status_code=503, detail="Model not ready.")

    matrix            = state["matrix"]
    similarity_matrix = state["similarity_matrix"]

    if user_id not in matrix.index:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found in model.")

    user_idx         = matrix.index.get_loc(user_id)
    user_similarities = similarity_matrix[user_idx]
    similar_indices  = np.argsort(user_similarities)[::-1][1:top_n + 1]

    results = [
        {
            "user_id":          int(matrix.index[i]),
            "similarity_score": round(float(user_similarities[i]), 4),
            "products_rated":   int((matrix.iloc[i] > 0).sum()),
        }
        for i in similar_indices
    ]

    return {"user_id": user_id, "similar_users": results}


# ══════════════════════════════════════════════════════════════════════════════
# 7. TOP RECOMMENDED PRODUCTS (across all users)
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/products/top-recommended", tags=["Products"])
def get_top_recommended_products(
    top_n: int = Query(default=10, ge=1, le=100),
):
    """
    Products recommended most frequently across all users.
    These are the globally trending products in the recommendation system.
    """
    sql = """
        SELECT
            r.product_id,
            p.title                  AS product_name,
            p.price,
            p.stars                  AS avg_rating,
            p.reviews                AS total_reviews,
            c.category_name,
            COUNT(r.user_id)         AS recommended_to_users,
            ROUND(AVG(r.predicted_rating), 3) AS avg_predicted_rating
        FROM recommendations r
        LEFT JOIN amazon_products   p ON r.product_id  = p.asin
        LEFT JOIN amazon_categories c ON p.category_id = c.id
        GROUP BY r.product_id, p.title, p.price, p.stars, p.reviews, c.category_name
        ORDER BY recommended_to_users DESC, avg_predicted_rating DESC
        LIMIT :top_n
    """
    df = query_db(sql, {"top_n": top_n})

    if df.empty:
        raise HTTPException(status_code=404, detail="No recommendation data found in DB.")

    return {
        "total_results": len(df),
        "top_products":  df.fillna("N/A").to_dict(orient="records"),
    }


# ══════════════════════════════════════════════════════════════════════════════
# 8. WHICH USERS WERE RECOMMENDED A SPECIFIC PRODUCT
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/products/{product_id}/recommended-to", tags=["Products"])
def get_users_recommended_product(
    product_id: str,
    top_n:      int = Query(default=20, ge=1, le=100),
):
    """
    See which users were recommended a specific product.
    Useful for understanding the reach of a product.
    """
    sql = """
        SELECT
            r.user_id,
            r.`rank`,
            r.predicted_rating,
            r.generated_at,
            u.name      AS user_name,
            u.age_group,
            u.country
        FROM recommendations r
        LEFT JOIN users u ON r.user_id = u.user_id
        WHERE r.product_id = :product_id
        ORDER BY r.predicted_rating DESC
        LIMIT :top_n
    """
    df = query_db(sql, {"product_id": product_id, "top_n": top_n})

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Product '{product_id}' has not been recommended to any user."
        )

    return {
        "product_id":     product_id,
        "total_users":    len(df),
        "recommended_to": df.fillna("N/A").to_dict(orient="records"),
    }


# ══════════════════════════════════════════════════════════════════════════════
# 9. USER PROFILE
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/users/{user_id}/profile", tags=["Users"])
def get_user_profile(user_id: int):
    """
    Full user profile:
    - User info (name, age group, country)
    - Products they have rated
    - Their saved recommendations
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

    recs_df = query_db("""
        SELECT
            r.`rank`,
            r.product_id,
            r.predicted_rating,
            p.title   AS product_name,
            p.price,
            c.category_name
        FROM recommendations r
        LEFT JOIN amazon_products   p ON r.product_id  = p.asin
        LEFT JOIN amazon_categories c ON p.category_id = c.id
        WHERE r.user_id = :uid
        ORDER BY r.`rank`
    """, {"uid": user_id})

    return {
        "user":                  user_df.fillna("N/A").to_dict(orient="records")[0],
        "total_ratings":         len(ratings_df),
        "ratings":               ratings_df.fillna("N/A").to_dict(orient="records"),
        "total_recommendations": len(recs_df),
        "recommendations":       recs_df.fillna("N/A").to_dict(orient="records"),
    }


# ══════════════════════════════════════════════════════════════════════════════
# 10. OVERALL STATS
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/stats", tags=["General"])
def get_stats():
    """High-level stats about the entire recommendation system."""
    stats = {}

    queries = {
        "total_users":           "SELECT COUNT(*) FROM users",
        "total_products":        "SELECT COUNT(*) FROM amazon_products",
        "total_categories":      "SELECT COUNT(*) FROM amazon_categories",
        "total_ratings":         "SELECT COUNT(*) FROM product_ratings",
        "total_recommendations": "SELECT COUNT(*) FROM recommendations",
        "users_with_recs":       "SELECT COUNT(DISTINCT user_id) FROM recommendations",
        "avg_predicted_rating":  "SELECT ROUND(AVG(predicted_rating), 3) FROM recommendations",
    }

    with state["engine"].connect() as conn:
        for key, sql in queries.items():
            result = conn.execute(text(sql)).scalar()
            stats[key] = float(result) if result is not None else 0

    stats["model_users"]    = int(state["matrix"].shape[0]) if state["ready"] else 0
    stats["model_products"] = int(state["matrix"].shape[1]) if state["ready"] else 0

    return stats


# ══════════════════════════════════════════════════════════════════════════════
# 11. RELOAD MODEL
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/model/reload", tags=["Admin"])
def reload_model():
    """
    Reload the similarity model from DB.
    Use this after new ratings have been added.
    """
    matrix, similarity_matrix = load_model(state["engine"])
    state["matrix"]            = matrix
    state["similarity_matrix"] = similarity_matrix
    state["ready"]             = True
    return {
        "message":   "Model reloaded successfully.",
        "users":     int(matrix.shape[0]),
        "products":  int(matrix.shape[1]),
        "reloaded_at": datetime.now().isoformat(),
    }


# ══════════════════════════════════════════════════════════════════════════════
# 12. BATCH GENERATE RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/recommendations/generate", tags=["Admin"])
def generate_recommendations(
    background_tasks: BackgroundTasks,
    sample_users: int = Query(default=500, ge=1, description="Number of users to generate for"),
):
    """
    Trigger batch generation of recommendations for N users.
    Runs in background — check the recommendations table once complete.
    """
    if not state["ready"]:
        raise HTTPException(status_code=503, detail="Model not ready.")

    background_tasks.add_task(
        batch_generate,
        state["matrix"],
        state["similarity_matrix"],
        state["engine"],
        sample_users,
    )

    return {
        "message":    f"Batch generation started for {sample_users} users.",
        "status":     "running in background",
        "tip":        "Call GET /stats to check progress once complete.",
    }


# ── Run ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=False)
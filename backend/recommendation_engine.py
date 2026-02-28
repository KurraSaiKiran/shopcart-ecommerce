"""
E-Commerce Recommendation Engine

Implements three recommendation techniques:
1. Collaborative Filtering - "Users like you bought this"
2. Content-Based Filtering - "Similar products to this one"
3. Cosine Similarity - Mathematical similarity calculation
"""

import numpy as np
import pandas as pd
from sqlalchemy import text
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class RecommendationEngine:
    def __init__(self, engine):
        self.engine = engine
        self.user_item_matrix = None
        self.product_features = None
        self.tfidf_matrix = None
        
    # ═══════════════════════════════════════════════════════════════════════
    # 1. COLLABORATIVE FILTERING - "Users like you bought this"
    # ═══════════════════════════════════════════════════════════════════════
    
    def collaborative_filtering(self, user_id, top_n=10):
        """
        Recommend products based on similar users' preferences.
        Uses user-item interaction matrix and cosine similarity.
        """
        try:
            # Build user-item matrix from ratings/interactions (limit to recent data)
            with self.engine.connect() as conn:
                query = """
                    SELECT user_id, product_id, rating
                    FROM product_ratings
                    LIMIT 5000
                """
                df = pd.read_sql(text(query), conn)
            
            if df.empty:
                return []
            
            # Create user-item matrix (users x products)
            user_item_matrix = df.pivot_table(
                index='user_id',
                columns='product_id',
                values='rating',
                fill_value=0
            )
            
            # Find similar users using cosine similarity
            if user_id not in user_item_matrix.index:
                return []
            
            user_vector = user_item_matrix.loc[user_id].values.reshape(1, -1)
            similarities = cosine_similarity(user_vector, user_item_matrix.values)[0]
            
            # Get top similar users (excluding self)
            similar_users_idx = np.argsort(similarities)[::-1][1:11]
            similar_users = user_item_matrix.index[similar_users_idx]
            
            # Get products rated highly by similar users
            recommendations = defaultdict(float)
            user_rated_products = set(df[df['user_id'] == user_id]['product_id'])
            
            for idx, sim_user in enumerate(similar_users):
                sim_score = similarities[similar_users_idx[idx]]
                sim_user_ratings = df[df['user_id'] == sim_user]
                
                for _, row in sim_user_ratings.iterrows():
                    product_id = row['product_id']
                    if product_id not in user_rated_products:
                        recommendations[product_id] += row['rating'] * sim_score
            
            # Sort and get top N
            top_products = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)[:top_n]
            product_ids = [p[0] for p in top_products]
            
            # Fetch product details
            return self._fetch_product_details(product_ids)
            
        except Exception as e:
            logger.error(f"Collaborative filtering error: {e}")
            return []
    
    # ═══════════════════════════════════════════════════════════════════════
    # 2. CONTENT-BASED FILTERING - "Similar products to this one"
    # ═══════════════════════════════════════════════════════════════════════
    
    def content_based_filtering(self, product_id, top_n=10):
        """
        Recommend products similar to a given product.
        Uses product features (title, category, price range) and TF-IDF.
        """
        try:
            # First get the target product's category
            with self.engine.connect() as conn:
                target_query = """
                    SELECT category_id FROM amazon_products WHERE asin = :pid
                """
                target_df = pd.read_sql(text(target_query), conn, params={'pid': product_id})
                
                if target_df.empty:
                    return []
                
                category_id = target_df.iloc[0]['category_id']
                
                # Fetch products from same category only (much smaller dataset)
                query = """
                    SELECT 
                        p.asin,
                        p.title,
                        p.price,
                        p.stars,
                        c.category_name
                    FROM amazon_products p
                    LEFT JOIN amazon_categories c ON p.category_id = c.id
                    WHERE p.category_id = :cat_id
                    LIMIT 500
                """
                df = pd.read_sql(text(query), conn, params={'cat_id': category_id})
            
            if df.empty or product_id not in df['asin'].values:
                return []
            
            # Create combined feature text
            df['features'] = (
                df['title'].fillna('') + ' ' +
                df['category_name'].fillna('') + ' ' +
                df['price'].astype(str)
            )
            
            # Create TF-IDF matrix with reduced features
            tfidf = TfidfVectorizer(max_features=100, stop_words='english')
            tfidf_matrix = tfidf.fit_transform(df['features'])
            
            # Find the product index
            product_idx = df[df['asin'] == product_id].index[0]
            
            # Calculate cosine similarity
            product_vector = tfidf_matrix[product_idx]
            similarities = cosine_similarity(product_vector, tfidf_matrix)[0]
            
            # Get top similar products (excluding self)
            similar_indices = np.argsort(similarities)[::-1][1:top_n+1]
            similar_products = df.iloc[similar_indices]['asin'].tolist()
            
            return self._fetch_product_details(similar_products)
            
        except Exception as e:
            logger.error(f"Content-based filtering error: {e}")
            return []
    
    # ═══════════════════════════════════════════════════════════════════════
    # 3. COSINE SIMILARITY - Mathematical similarity calculation
    # ═══════════════════════════════════════════════════════════════════════
    
    def calculate_cosine_similarity(self, vector_a, vector_b):
        """
        Calculate cosine similarity between two vectors.
        
        Formula: cos(θ) = (A · B) / (||A|| × ||B||)
        
        Returns: Similarity score between 0 and 1
        """
        # Dot product
        dot_product = np.dot(vector_a, vector_b)
        
        # Magnitudes
        magnitude_a = np.linalg.norm(vector_a)
        magnitude_b = np.linalg.norm(vector_b)
        
        # Avoid division by zero
        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0
        
        # Cosine similarity
        similarity = dot_product / (magnitude_a * magnitude_b)
        
        return similarity
    
    def product_similarity_matrix(self, product_ids):
        """
        Create a similarity matrix for given products.
        Returns a matrix showing similarity between all product pairs.
        """
        try:
            with self.engine.connect() as conn:
                placeholders = ','.join([f"'{pid}'" for pid in product_ids])
                query = f"""
                    SELECT 
                        p.asin,
                        p.title,
                        p.price,
                        p.stars,
                        c.category_name
                    FROM amazon_products p
                    LEFT JOIN amazon_categories c ON p.category_id = c.id
                    WHERE p.asin IN ({placeholders})
                """
                df = pd.read_sql(text(query), conn)
            
            if df.empty:
                return None
            
            # Create feature vectors
            df['features'] = (
                df['title'].fillna('') + ' ' +
                df['category_name'].fillna('')
            )
            
            tfidf = TfidfVectorizer(max_features=100, stop_words='english')
            feature_matrix = tfidf.fit_transform(df['features'])
            
            # Calculate similarity matrix
            similarity_matrix = cosine_similarity(feature_matrix)
            
            return {
                'products': df['asin'].tolist(),
                'similarity_matrix': similarity_matrix.tolist()
            }
            
        except Exception as e:
            logger.error(f"Similarity matrix error: {e}")
            return None
    
    # ═══════════════════════════════════════════════════════════════════════
    # HYBRID RECOMMENDATION - Combine all techniques
    # ═══════════════════════════════════════════════════════════════════════
    
    def hybrid_recommendations(self, user_id, product_id=None, top_n=10):
        """
        Combine collaborative and content-based filtering for better results.
        """
        recommendations = []
        
        # Get collaborative filtering recommendations
        collab_recs = self.collaborative_filtering(user_id, top_n=top_n)
        
        # Get content-based recommendations if product_id provided
        if product_id:
            content_recs = self.content_based_filtering(product_id, top_n=top_n)
            
            # Merge and deduplicate
            seen = set()
            for rec in collab_recs + content_recs:
                if rec['asin'] not in seen:
                    recommendations.append(rec)
                    seen.add(rec['asin'])
                    if len(recommendations) >= top_n:
                        break
        else:
            recommendations = collab_recs[:top_n]
        
        return recommendations
    
    # ═══════════════════════════════════════════════════════════════════════
    # HELPER METHODS
    # ═══════════════════════════════════════════════════════════════════════
    
    def _fetch_product_details(self, product_ids):
        """Fetch full product details for given product IDs."""
        if not product_ids:
            return []
        
        try:
            with self.engine.connect() as conn:
                placeholders = ','.join([f"'{pid}'" for pid in product_ids])
                query = f"""
                    SELECT 
                        asin,
                        title,
                        img_url,
                        price,
                        stars,
                        reviews,
                        category_id
                    FROM amazon_products
                    WHERE asin IN ({placeholders})
                """
                df = pd.read_sql(text(query), conn)
                return df.to_dict('records')
        except Exception as e:
            logger.error(f"Fetch product details error: {e}")
            return []

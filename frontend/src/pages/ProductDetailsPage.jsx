import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Star, ShoppingCart, Heart } from 'lucide-react';
import ProductCard from '../components/ProductCard';
import Header from '../components/Header';
import MobileBottomNav from '../components/MobileBottomNav';
import CartModal from '../components/CartModal';

const ProductDetailsPage = () => {
  const { productId } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingRecs, setLoadingRecs] = useState(true);
  const [cartItems, setCartItems] = useState([]);
  const [isCartOpen, setIsCartOpen] = useState(false);

  useEffect(() => {
    fetchProductDetails();
    fetchRecommendations();
  }, [productId]);

  const fetchProductDetails = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://127.0.0.1:8005/products/${productId}`);
      if (!response.ok) throw new Error('Product not found');
      const data = await response.json();
      setProduct(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRecommendations = async () => {
    try {
      setLoadingRecs(true);
      const response = await fetch(`http://127.0.0.1:8005/recommendations/similar/${productId}?limit=8`);
      const data = await response.json();
      // Filter out current product from recommendations
      const filtered = (data.recommendations || []).filter(rec => rec.asin !== productId);
      setRecommendations(filtered);
    } catch (error) {
      console.error('Error:', error);
      setRecommendations([]);
    } finally {
      setLoadingRecs(false);
    }
  };

  const handleAddToCart = (prod) => {
    setCartItems(prev => {
      const existing = prev.find(item => item.asin === prod.asin);
      if (existing) {
        return prev.map(item =>
          item.asin === prod.asin ? { ...item, quantity: item.quantity + 1 } : item
        );
      }
      return [...prev, { ...prod, quantity: 1 }];
    });
    setIsCartOpen(true);
  };

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ width: '48px', height: '48px', border: '4px solid #f0f0f0', borderTop: '4px solid var(--primary)', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></div>
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  if (!product) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center' }}>
          <h2>Product Not Found</h2>
          <button onClick={() => navigate('/')} className="btn-primary">Go Back</button>
        </div>
      </div>
    );
  }

  const discount = product.original_price && product.price ? Math.round(((product.original_price - product.price) / product.original_price) * 100) : 0;

  return (
    <div style={{ minHeight: '100vh', background: '#F1F3F6', paddingBottom: '80px' }}>
      <Header cartCount={cartItems.length} onCartClick={() => setIsCartOpen(true)} />

      <div className="container" style={{ paddingTop: '24px' }}>
        <button onClick={() => navigate(-1)} style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'none', border: 'none', color: 'var(--primary)', fontSize: '14px', fontWeight: 600, cursor: 'pointer', marginBottom: '24px' }}>
          <ArrowLeft size={18} /> Back
        </button>

        <div style={{ background: '#fff', borderRadius: '8px', padding: '32px', marginBottom: '32px', display: 'grid', gridTemplateColumns: '400px 1fr', gap: '32px' }}>
          <div style={{ background: '#f8f8f8', borderRadius: '8px', padding: '32px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <img src={product.img_url || product.imgUrl || 'https://via.placeholder.com/400'} alt={product.title} style={{ maxWidth: '100%', maxHeight: '400px', objectFit: 'contain' }} onError={(e) => e.target.src = 'https://via.placeholder.com/400?text=No+Image'} />
          </div>

          <div>
            <h1 style={{ fontSize: '28px', fontWeight: 700, marginBottom: '16px' }}>{product.title}</h1>

            {product.stars > 0 && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
                <div style={{ background: 'var(--success)', color: 'white', padding: '4px 12px', borderRadius: '4px', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '14px', fontWeight: 600 }}>
                  {product.stars.toFixed(1)} <Star size={14} fill="white" />
                </div>
                <span style={{ fontSize: '14px', color: 'var(--text-gray)' }}>({product.reviews?.toLocaleString('en-IN') || 0} reviews)</span>
              </div>
            )}

            <div style={{ marginBottom: '24px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '8px' }}>
                <span style={{ fontSize: '36px', fontWeight: 700 }}>₹{product.price?.toLocaleString('en-IN')}</span>
                {product.original_price && product.original_price > product.price && (
                  <>
                    <span style={{ fontSize: '20px', color: 'var(--text-gray)', textDecoration: 'line-through' }}>₹{product.original_price.toLocaleString('en-IN')}</span>
                    <span style={{ fontSize: '18px', fontWeight: 700, color: 'var(--success)' }}>{discount}% off</span>
                  </>
                )}
              </div>
              <p style={{ fontSize: '14px', color: 'var(--success)', fontWeight: 600 }}>🚚 Free Delivery</p>
            </div>

            <div style={{ display: 'flex', gap: '16px', marginBottom: '32px' }}>
              <button onClick={() => handleAddToCart(product)} style={{ background: 'var(--primary)', color: 'white', border: 'none', padding: '14px 32px', borderRadius: '4px', fontSize: '16px', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <ShoppingCart size={20} /> Add to Cart
              </button>
              <button style={{ background: 'white', color: 'var(--primary)', border: '2px solid var(--primary)', padding: '14px 32px', borderRadius: '4px', fontSize: '16px', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Heart size={20} /> Wishlist
              </button>
            </div>

            <div style={{ borderTop: '1px solid var(--border)', paddingTop: '24px' }}>
              <h3 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '16px' }}>Product Details</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div style={{ display: 'flex' }}>
                  <span style={{ fontWeight: 600, width: '120px', color: 'var(--text-gray)' }}>ASIN:</span>
                  <span>{product.asin}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {!loadingRecs && recommendations.length > 0 && (
          <div style={{ background: '#fff', borderRadius: '8px', padding: '32px' }}>
            <h2 style={{ fontSize: '24px', fontWeight: 700, marginBottom: '24px' }}>You May Also Like</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '16px' }}>
              {recommendations.map(rec => (
                <ProductCard key={rec.asin} product={rec} onAddToCart={handleAddToCart} />
              ))}
            </div>
          </div>
        )}

        {!loadingRecs && recommendations.length === 0 && (
          <div style={{ background: '#fff', borderRadius: '8px', padding: '32px', textAlign: 'center' }}>
            <p style={{ color: 'var(--text-gray)', fontSize: '16px' }}>No similar products found.</p>
          </div>
        )}
      </div>

      <CartModal isOpen={isCartOpen} onClose={() => setIsCartOpen(false)} cartItems={cartItems} onRemoveItem={(asin) => setCartItems(prev => prev.filter(item => item.asin !== asin))} onUpdateQuantity={(asin, qty) => setCartItems(prev => prev.map(item => item.asin === asin ? { ...item, quantity: qty } : item))} />
      <MobileBottomNav activeTab="home" cartCount={cartItems.length} onCartClick={() => setIsCartOpen(true)} />
    </div>
  );
};

export default ProductDetailsPage;

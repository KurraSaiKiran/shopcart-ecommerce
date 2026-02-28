import React, { useState, useEffect } from 'react';
import ProductCard from './ProductCard';
import { Sparkles, Users, TrendingUp } from 'lucide-react';

const RecommendationsSection = ({ userId, productId, onAddToCart }) => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [type, setType] = useState('hybrid'); // collaborative, similar, hybrid

  useEffect(() => {
    fetchRecommendations();
  }, [userId, productId, type]);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      let url = '';
      
      if (type === 'collaborative' && userId) {
        url = `http://127.0.0.1:8005/recommendations/collaborative/${userId}?limit=8`;
      } else if (type === 'similar' && productId) {
        url = `http://127.0.0.1:8005/recommendations/similar/${productId}?limit=8`;
      } else if (type === 'hybrid' && userId) {
        url = `http://127.0.0.1:8005/recommendations/hybrid/${userId}${productId ? `?product_id=${productId}` : ''}`;
      }
      
      if (!url) {
        setRecommendations([]);
        setLoading(false);
        return;
      }

      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch recommendations');
      
      const data = await response.json();
      setRecommendations(data.recommendations || []);
    } catch (error) {
      console.error('Recommendations error:', error);
      setRecommendations([]);
    } finally {
      setLoading(false);
    }
  };

  if (!userId && !productId) return null;

  const getIcon = () => {
    switch (type) {
      case 'collaborative': return <Users size={20} />;
      case 'similar': return <TrendingUp size={20} />;
      default: return <Sparkles size={20} />;
    }
  };

  const getTitle = () => {
    switch (type) {
      case 'collaborative': return 'Users Like You Bought';
      case 'similar': return 'Similar Products';
      default: return 'Recommended For You';
    }
  };

  return (
    <div style={{
      background: '#fff',
      borderRadius: '8px',
      padding: '24px',
      marginTop: '32px'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '20px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '8px',
            background: 'rgba(40, 116, 240, 0.1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--primary)'
          }}>
            {getIcon()}
          </div>
          <div>
            <h2 style={{
              fontSize: '20px',
              fontWeight: 700,
              margin: 0,
              color: 'var(--text-dark)'
            }}>
              {getTitle()}
            </h2>
            <p style={{
              fontSize: '13px',
              color: 'var(--text-gray)',
              margin: 0
            }}>
              Personalized recommendations based on your preferences
            </p>
          </div>
        </div>

        {/* Type Selector */}
        <div style={{
          display: 'flex',
          gap: '8px',
          background: 'var(--bg-light)',
          padding: '4px',
          borderRadius: '6px'
        }}>
          {userId && (
            <>
              <button
                onClick={() => setType('hybrid')}
                style={{
                  padding: '6px 12px',
                  border: 'none',
                  borderRadius: '4px',
                  fontSize: '12px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  background: type === 'hybrid' ? 'var(--primary)' : 'transparent',
                  color: type === 'hybrid' ? 'white' : 'var(--text-gray)',
                  transition: 'all 0.2s'
                }}
              >
                Hybrid
              </button>
              <button
                onClick={() => setType('collaborative')}
                style={{
                  padding: '6px 12px',
                  border: 'none',
                  borderRadius: '4px',
                  fontSize: '12px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  background: type === 'collaborative' ? 'var(--primary)' : 'transparent',
                  color: type === 'collaborative' ? 'white' : 'var(--text-gray)',
                  transition: 'all 0.2s'
                }}
              >
                Similar Users
              </button>
            </>
          )}
          {productId && (
            <button
              onClick={() => setType('similar')}
              style={{
                padding: '6px 12px',
                border: 'none',
                borderRadius: '4px',
                fontSize: '12px',
                fontWeight: 600,
                cursor: 'pointer',
                background: type === 'similar' ? 'var(--primary)' : 'transparent',
                color: type === 'similar' ? 'white' : 'var(--text-gray)',
                transition: 'all 0.2s'
              }}
            >
              Similar Items
            </button>
          )}
        </div>
      </div>

      {/* Products */}
      {loading ? (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
          gap: '16px'
        }}>
          {[1, 2, 3, 4].map(i => (
            <div key={i} style={{
              height: '300px',
              background: 'var(--bg-light)',
              borderRadius: '8px',
              animation: 'pulse 1.5s infinite'
            }} />
          ))}
        </div>
      ) : recommendations.length === 0 ? (
        <div style={{
          textAlign: 'center',
          padding: '40px',
          color: 'var(--text-gray)'
        }}>
          <p>No recommendations available at the moment.</p>
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
          gap: '16px'
        }}>
          {recommendations.map(product => (
            <ProductCard
              key={product.asin}
              product={product}
              onAddToCart={onAddToCart}
            />
          ))}
        </div>
      )}

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  );
};

export default RecommendationsSection;

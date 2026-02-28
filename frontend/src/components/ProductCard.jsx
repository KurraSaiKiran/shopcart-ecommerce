import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Star, ShoppingCart } from 'lucide-react';

const ProductCard = ({ product, onAddToCart }) => {
  const navigate = useNavigate();
  const discount = product.price && product.original_price 
    ? Math.round(((product.original_price - product.price) / product.original_price) * 100)
    : 0;

  const rating = product.stars || 4.0;
  const reviews = product.reviews || 0;
  const price = product.price || 999;
  const originalPrice = product.original_price || price * 1.5;

  const handleCardClick = () => {
    navigate(`/product/${product.asin}`);
  };

  const handleAddToCart = (e) => {
    e.stopPropagation();
    onAddToCart?.(product);
  };

  return (
    <div className="product-card" onClick={handleCardClick}>
      <div className="product-image-wrapper">
        {discount > 0 && (
          <div className="discount-badge">{discount}% OFF</div>
        )}
        <img
          src={product.img_url || product.imgUrl || 'https://via.placeholder.com/300?text=No+Image'}
          alt={product.title}
          className="product-image"
          loading="lazy"
          onError={(e) => {
            e.target.src = 'https://via.placeholder.com/300?text=No+Image';
          }}
        />
      </div>

      <div className="product-info">
        <h3 className="product-title">{product.title}</h3>

        {rating > 0 && (
          <div className="product-rating">
            <span className="rating-badge">
              {rating.toFixed(1)} <Star size={10} fill="white" />
            </span>
            <span className="rating-count">({reviews.toLocaleString('en-IN')})</span>
          </div>
        )}

        <div className="product-price">
          <span className="current-price">₹{price.toLocaleString('en-IN')}</span>
          {originalPrice > price && (
            <>
              <span className="original-price">₹{originalPrice.toLocaleString('en-IN')}</span>
              <span className="discount-percent">{discount}% off</span>
            </>
          )}
        </div>

        <div className="free-delivery">Free Delivery</div>
      </div>

      <button 
        className="add-to-cart-btn"
        onClick={handleAddToCart}
      >
        <ShoppingCart size={16} style={{ display: 'inline', marginRight: '6px' }} />
        Add to Cart
      </button>
    </div>
  );
};

export default ProductCard;

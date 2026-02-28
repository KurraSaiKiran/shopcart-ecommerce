import React from 'react';
import { Home, Grid, Package, ShoppingCart, User } from 'lucide-react';

const MobileBottomNav = ({ activeTab = 'home', cartCount = 0, onCartClick }) => {
  return (
    <nav className="mobile-bottom-nav">
      <button className={`nav-item ${activeTab === 'home' ? 'active' : ''}`}>
        <Home size={20} />
        <span>Home</span>
      </button>
      
      <button className={`nav-item ${activeTab === 'categories' ? 'active' : ''}`}>
        <Grid size={20} />
        <span>Categories</span>
      </button>
      
      <button className={`nav-item ${activeTab === 'orders' ? 'active' : ''}`}>
        <Package size={20} />
        <span>Orders</span>
      </button>
      
      <button 
        className={`nav-item ${activeTab === 'cart' ? 'active' : ''}`} 
        style={{ position: 'relative' }}
        onClick={onCartClick}
      >
        <ShoppingCart size={20} />
        <span>Cart</span>
        {cartCount > 0 && <span className="cart-badge" style={{ top: 0, right: '20%' }}>{cartCount}</span>}
      </button>
      
      <button className={`nav-item ${activeTab === 'profile' ? 'active' : ''}`}>
        <User size={20} />
        <span>Profile</span>
      </button>
    </nav>
  );
};

export default MobileBottomNav;

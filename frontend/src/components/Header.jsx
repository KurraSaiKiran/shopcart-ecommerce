import React from 'react';
import { Search, ShoppingCart, User, Store } from 'lucide-react';

const Header = ({ cartCount = 0, onSearch, onCartClick }) => {
  const [searchValue, setSearchValue] = React.useState('');

  const handleSearchChange = (e) => {
    const value = e.target.value;
    setSearchValue(value);
    onSearch?.(value);
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    onSearch?.(searchValue);
  };

  return (
    <header className="header">
      <div className="container">
        <div className="header-main">
          <a href="/" className="logo">ShopKart</a>
          
          <form onSubmit={handleSearchSubmit} className="search-bar" style={{ flex: 1, maxWidth: '600px' }}>
            <Search className="search-icon" size={18} />
            <input
              type="text"
              className="search-input"
              placeholder="Search for products, brands and more"
              value={searchValue}
              onChange={handleSearchChange}
            />
          </form>

          <div className="header-actions hide-mobile">
            <button className="header-btn">
              <User size={18} />
              Login
            </button>
            
            <button 
              className="header-btn" 
              style={{ position: 'relative' }}
              onClick={onCartClick}
            >
              <ShoppingCart size={18} />
              Cart
              {cartCount > 0 && <span className="cart-badge">{cartCount}</span>}
            </button>
            
            <button className="header-btn">
              <Store size={18} />
              Become a Seller
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;

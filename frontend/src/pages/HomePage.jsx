import React, { useState } from 'react';
import Header from '../components/Header';
import CategoryNav from '../components/CategoryNav';
import StatsBar from '../components/StatsBar';
import FilterSidebar from '../components/FilterSidebar';
import ProductCard from '../components/ProductCard';
import MobileBottomNav from '../components/MobileBottomNav';
import CartModal from '../components/CartModal';
import { useProducts } from '../hooks/useProducts';
import { ChevronLeft, ChevronRight, PackageSearch } from 'lucide-react';

function HomePage() {
  const {
    products,
    categories,
    loading,
    error,
    selectedCategory,
    setSelectedCategory,
    page,
    setPage,
    setSearchQuery,
    priceRange,
    setPriceRange,
    minRating,
    setMinRating,
  } = useProducts();

  const [search, setSearch] = useState('');
  const [cartItems, setCartItems] = useState([]);
  const [isCartOpen, setIsCartOpen] = useState(false);

  const handleSearch = (value) => {
    setSearch(value);
    if (value.length > 2 || value.length === 0) {
      setSearchQuery(value);
      setPage(1);
    }
  };

  const handleAddToCart = (product) => {
    setCartItems(prev => {
      const existing = prev.find(item => item.asin === product.asin);
      if (existing) {
        return prev.map(item =>
          item.asin === product.asin ? { ...item, quantity: item.quantity + 1 } : item
        );
      }
      return [...prev, { ...product, quantity: 1 }];
    });
    setIsCartOpen(true);
  };

  const handleProductClick = (productId) => {
    navigate(`/product/${productId}`);
  };

  return (
    <div style={{ minHeight: '100vh', paddingBottom: '80px' }}>
      <Header cartCount={cartItems.length} onSearch={handleSearch} onCartClick={() => setIsCartOpen(true)} />
      <CategoryNav categories={categories} selectedCategory={selectedCategory} onSelectCategory={setSelectedCategory} />

      <div className="container">
        <StatsBar />

        {loading ? (
          <div style={{ textAlign: 'center', padding: '80px 20px' }}>
            <div style={{ width: '48px', height: '48px', border: '4px solid #f0f0f0', borderTop: '4px solid var(--primary)', borderRadius: '50%', animation: 'spin 1s linear infinite', margin: '0 auto 16px' }}></div>
            <p style={{ color: 'var(--text-gray)', fontSize: '14px' }}>Loading products...</p>
          </div>
        ) : error ? (
          <div style={{ background: '#fff', padding: '40px', borderRadius: '4px', textAlign: 'center', margin: '40px 0' }}>
            <p style={{ color: '#d32f2f', fontWeight: 600, marginBottom: '8px' }}>Unable to load products</p>
            <p style={{ color: 'var(--text-gray)', fontSize: '14px' }}>{error}</p>
          </div>
        ) : (
          <div className="layout-with-sidebar">
            <FilterSidebar categories={categories} selectedCategory={selectedCategory} onCategoryChange={setSelectedCategory} priceRange={priceRange} onPriceChange={setPriceRange} minRating={minRating} onRatingChange={setMinRating} />

            <div>
              {products.length === 0 ? (
                <div style={{ background: '#fff', padding: '80px 20px', borderRadius: '4px', textAlign: 'center' }}>
                  <PackageSearch size={64} style={{ color: '#e0e0e0', margin: '0 auto 16px' }} />
                  <p style={{ fontSize: '18px', fontWeight: 600, marginBottom: '8px' }}>No products found</p>
                  <p style={{ color: 'var(--text-gray)', fontSize: '14px', marginBottom: '16px' }}>Try adjusting your search or filters</p>
                  <button className="btn-primary" onClick={() => { setSearch(''); setSearchQuery(''); setSelectedCategory(null); setPriceRange({ min: null, max: null }); setMinRating(null); }}>Clear Filters</button>
                </div>
              ) : (
                <>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', padding: '12px 0' }}>
                    <div>
                      <p style={{ fontSize: '14px', color: 'var(--text-gray)', margin: 0 }}>Showing {products.length} products</p>
                      {search && <p style={{ fontSize: '13px', color: 'var(--primary)', margin: '4px 0 0 0', fontWeight: 600 }}>Search results for "{search}"</p>}
                      {(priceRange.min !== null || priceRange.max !== null) && <p style={{ fontSize: '13px', color: 'var(--success)', margin: '4px 0 0 0', fontWeight: 600 }}>Price: {priceRange.min !== null ? `₹${priceRange.min}` : '₹0'} - {priceRange.max !== null ? `₹${priceRange.max.toLocaleString('en-IN')}` : 'Above'}</p>}
                      {minRating !== null && <p style={{ fontSize: '13px', color: 'var(--warning)', margin: '4px 0 0 0', fontWeight: 600 }}>Rating: {minRating}★ & above</p>}
                    </div>
                    {(search || priceRange.min !== null || minRating !== null) && (
                      <button onClick={() => { setSearch(''); setSearchQuery(''); setPriceRange({ min: null, max: null }); setMinRating(null); }} style={{ background: 'none', border: '1px solid var(--border)', padding: '6px 16px', borderRadius: '4px', fontSize: '13px', fontWeight: 600, color: 'var(--text-gray)', cursor: 'pointer' }}>Clear All Filters</button>
                    )}
                  </div>

                  <div className="product-grid">
                    {products.map(product => (
                      <ProductCard key={product.asin} product={product} onAddToCart={handleAddToCart} />
                    ))}
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '24px', padding: '32px 0', background: '#fff', borderRadius: '4px', marginTop: '16px' }}>
                    <button disabled={page === 1} onClick={() => setPage(p => p - 1)} style={{ background: page === 1 ? '#f0f0f0' : 'var(--primary)', color: page === 1 ? '#ccc' : 'white', border: 'none', padding: '8px 16px', borderRadius: '2px', cursor: page === 1 ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '14px', fontWeight: 600 }}>
                      <ChevronLeft size={16} /> Previous
                    </button>
                    <span style={{ fontSize: '16px', fontWeight: 600 }}>Page {page}</span>
                    <button disabled={products.length < 20} onClick={() => setPage(p => p + 1)} style={{ background: products.length < 20 ? '#f0f0f0' : 'var(--primary)', color: products.length < 20 ? '#ccc' : 'white', border: 'none', padding: '8px 16px', borderRadius: '2px', cursor: products.length < 20 ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '14px', fontWeight: 600 }}>
                      Next <ChevronRight size={16} />
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        )}
      </div>

      <CartModal isOpen={isCartOpen} onClose={() => setIsCartOpen(false)} cartItems={cartItems} onRemoveItem={(asin) => setCartItems(prev => prev.filter(item => item.asin !== asin))} onUpdateQuantity={(asin, qty) => setCartItems(prev => prev.map(item => item.asin === asin ? { ...item, quantity: qty } : item))} />
      <MobileBottomNav activeTab="home" cartCount={cartItems.length} onCartClick={() => setIsCartOpen(true)} />

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

export default HomePage;

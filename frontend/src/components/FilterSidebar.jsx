import React from 'react';

const FilterSidebar = ({ categories, selectedCategory, onCategoryChange, priceRange, onPriceChange, minRating, onRatingChange }) => {
  return (
    <aside className="filter-sidebar hide-mobile">
      <div className="filter-section">
        <h3 className="filter-title">Categories</h3>
        <div className="filter-option">
          <input
            type="radio"
            id="cat-all"
            name="category"
            checked={!selectedCategory}
            onChange={() => onCategoryChange(null)}
          />
          <label htmlFor="cat-all">All Products</label>
        </div>
        {categories.slice(0, 10).map((cat) => (
          <div key={cat.id} className="filter-option">
            <input
              type="radio"
              id={`cat-${cat.id}`}
              name="category"
              checked={selectedCategory === cat.id}
              onChange={() => onCategoryChange(cat.id)}
            />
            <label htmlFor={`cat-${cat.id}`}>{cat.category_name}</label>
          </div>
        ))}
      </div>

      <div className="filter-section">
        <h3 className="filter-title">Price Range</h3>
        <div className="filter-option">
          <input 
            type="checkbox" 
            id="price1" 
            checked={priceRange.min === 0 && priceRange.max === 500}
            onChange={(e) => {
              if (e.target.checked) {
                onPriceChange({ min: 0, max: 500 });
              } else {
                onPriceChange({ min: null, max: null });
              }
            }}
          />
          <label htmlFor="price1">Under ₹500</label>
        </div>
        <div className="filter-option">
          <input 
            type="checkbox" 
            id="price2" 
            checked={priceRange.min === 500 && priceRange.max === 1000}
            onChange={(e) => {
              if (e.target.checked) {
                onPriceChange({ min: 500, max: 1000 });
              } else {
                onPriceChange({ min: null, max: null });
              }
            }}
          />
          <label htmlFor="price2">₹500 - ₹1,000</label>
        </div>
        <div className="filter-option">
          <input 
            type="checkbox" 
            id="price3" 
            checked={priceRange.min === 1000 && priceRange.max === 5000}
            onChange={(e) => {
              if (e.target.checked) {
                onPriceChange({ min: 1000, max: 5000 });
              } else {
                onPriceChange({ min: null, max: null });
              }
            }}
          />
          <label htmlFor="price3">₹1,000 - ₹5,000</label>
        </div>
        <div className="filter-option">
          <input 
            type="checkbox" 
            id="price4" 
            checked={priceRange.min === 5000 && priceRange.max === null}
            onChange={(e) => {
              if (e.target.checked) {
                onPriceChange({ min: 5000, max: null });
              } else {
                onPriceChange({ min: null, max: null });
              }
            }}
          />
          <label htmlFor="price4">Above ₹5,000</label>
        </div>
      </div>

      <div className="filter-section">
        <h3 className="filter-title">Customer Ratings</h3>
        <div className="filter-option">
          <input 
            type="checkbox" 
            id="rating4" 
            checked={minRating === 4}
            onChange={(e) => onRatingChange(e.target.checked ? 4 : null)}
          />
          <label htmlFor="rating4">4★ & above</label>
        </div>
        <div className="filter-option">
          <input 
            type="checkbox" 
            id="rating3" 
            checked={minRating === 3}
            onChange={(e) => onRatingChange(e.target.checked ? 3 : null)}
          />
          <label htmlFor="rating3">3★ & above</label>
        </div>
      </div>

      <div className="filter-section">
        <h3 className="filter-title">Delivery</h3>
        <div className="filter-option">
          <input type="checkbox" id="free-delivery" />
          <label htmlFor="free-delivery">Free Delivery</label>
        </div>
      </div>
    </aside>
  );
};

export default FilterSidebar;

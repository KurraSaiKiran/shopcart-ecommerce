import React from 'react';

const CategoryNav = ({ categories, selectedCategory, onSelectCategory }) => {
  return (
    <nav className="category-nav">
      <div className="container">
        <ul className="category-list">
          <li
            className={`category-item ${!selectedCategory ? 'active' : ''}`}
            onClick={() => onSelectCategory(null)}
          >
            All Products
          </li>
          {categories.map((cat) => (
            <li
              key={cat.id}
              className={`category-item ${selectedCategory === cat.id ? 'active' : ''}`}
              onClick={() => onSelectCategory(cat.id)}
            >
              {cat.category_name}
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
};

export default CategoryNav;

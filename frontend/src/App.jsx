import React, { useState } from 'react';
import Layout from './components/Layout';
import ProductCard from './components/ProductCard';
import ProductModal from './components/ProductModal';
import Toast from './components/Toast';
import { useProducts } from './hooks/useProducts';
import { Search, Plus, SlidersHorizontal, ChevronLeft, ChevronRight, PackageSearch } from 'lucide-react';

function App() {
  const {
    products,
    categories,
    loading,
    error,
    stats,
    selectedCategory,
    setSelectedCategory,
    page,
    setPage,
    notification,
    clearNotification,
    removeProduct,
    saveProduct
  } = useProducts();

  const [search, setSearch] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);

  const filteredProducts = products.filter(p =>
    p.title.toLowerCase().includes(search.toLowerCase()) ||
    p.asin.toLowerCase().includes(search.toLowerCase())
  );

  const handleEdit = (product) => {
    setEditingProduct(product);
    setModalOpen(true);
  };

  const handleAdd = () => {
    setEditingProduct(null);
    setModalOpen(true);
  };

  const handleModalSubmit = async (formData) => {
    const success = await saveProduct(formData, !!editingProduct);
    if (success) {
      setModalOpen(false);
    }
  };

  return (
    <Layout stats={stats}>
      {/* Search & Actions Bar */}
      <div className="flex flex-col md:flex-row gap-6 mb-12 items-center justify-between">
        <div className="flex flex-1 flex-col md:flex-row items-center gap-4 w-full">
          <div className="relative flex-1 w-full lg:max-w-xl">
            <Search className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
            <input
              type="text"
              placeholder="Search products by name or code..."
              className="input-field pl-14 h-16 text-sm font-medium"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="relative w-full md:w-64">
            <SlidersHorizontal className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-500" size={16} />
            <select
              className="input-field pl-14 pr-10 h-16 appearance-none cursor-pointer font-semibold text-slate-300 uppercase tracking-wider text-[11px]"
              value={selectedCategory || ''}
              onChange={(e) => setSelectedCategory(e.target.value || null)}
            >
              <option value="" className="bg-slate-900">All Categories</option>
              {categories.map(cat => (
                <option key={cat.id} value={cat.id} className="bg-slate-900">
                  {cat.category_name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <button onClick={handleAdd} className="btn-entry group">
          <Plus size={18} />
          <span>Add Product</span>
        </button>
      </div>

      {/* Grid State Handling */}
      {loading ? (
        <div className="flex flex-col items-center justify-center p-40 gap-6">
          <div className="w-12 h-12 border-2 border-slate-700 border-t-blue-500 rounded-full animate-spin"></div>
          <p className="stat-label text-slate-500 font-medium tracking-widest">Updating Catalog</p>
        </div>
      ) : error ? (
        <div className="glass-card p-12 text-center" style={{ borderColor: 'rgba(244, 63, 94, 0.2)' }}>
          <p className="text-white font-bold text-xl mb-2">Service Offline</p>
          <p className="text-slate-500 font-medium text-sm">{error}</p>
        </div>
      ) : filteredProducts.length === 0 ? (
        <div className="glass-card p-24 text-center flex flex-col items-center gap-6 animate-fade">
          <PackageSearch size={64} style={{ opacity: 0.2, color: '#60a5fa' }} />
          <div style={{ maxWidth: '320px' }}>
            <p className="stat-value text-2xl mb-2">No Results Found</p>
            <p className="stat-label" style={{ textTransform: 'none' }}>Modify filters or reset search to continue.</p>
          </div>
          <button
            onClick={() => { setSearch(''); setSelectedCategory(null); }}
            className="btn-entry" style={{ height: '3rem', fontSize: '10px' }}
          >
            Clear Filters
          </button>
        </div>
      ) : (
        <>
          <div className="product-grid">
            {filteredProducts.map(product => (
              <ProductCard
                key={product.asin}
                product={product}
                onEdit={handleEdit}
                onDelete={removeProduct}
              />
            ))}
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-center gap-10 pt-16 border-t border-white/5">
            <button
              disabled={page === 1}
              onClick={() => setPage(p => p - 1)}
              className="p-3 rounded-full hover:bg-white/5 disabled:opacity-0 transition-all"
            >
              <ChevronLeft size={20} className="text-slate-400" />
            </button>
            <div className="flex flex-col items-center">
              <span className="stat-label text-[10px] text-slate-600">Page</span>
              <span className="text-2xl font-bold text-white">{page}</span>
            </div>
            <button
              disabled={filteredProducts.length < 20}
              onClick={() => setPage(p => p + 1)}
              className="p-3 rounded-full hover:bg-white/5 disabled:opacity-0 transition-all"
            >
              <ChevronRight size={20} className="text-slate-400" />
            </button>
          </div>
        </>
      )}

      {/* Persistence Modal */}
      <ProductModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        product={editingProduct}
        onSubmit={handleModalSubmit}
        categories={categories}
      />
      {notification && (
        <Toast
          message={notification.message}
          type={notification.type}
          onClose={clearNotification}
        />
      )}
    </Layout>
  );
}

export default App;

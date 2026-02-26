import React from 'react';
import { X, Image as ImageIcon, Tag, Hash, DollarSign, ExternalLink } from 'lucide-react';

const ProductModal = ({ isOpen, onClose, product, onSubmit, categories }) => {
    const [formData, setFormData] = React.useState({
        asin: '',
        title: '',
        price: 0,
        stars: 0,
        reviews: 0,
        category_id: '',
        img_url: ''
    });

    const fileInputRef = React.useRef(null);

    React.useEffect(() => {
        if (product) {
            setFormData(product);
        } else {
            setFormData({ asin: '', title: '', price: 0, stars: 0, reviews: 0, category_id: '', img_url: '' });
        }
    }, [product, isOpen]);

    const handleFileChange = (e, field) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
                setFormData(prev => ({ ...prev, [field]: reader.result }));
            };
            reader.readAsDataURL(file);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-slate-950/95 backdrop-blur-3xl z-50 flex items-center justify-center p-4">
            <div className="glass-card w-full max-w-2xl bg-[#0a0c14] p-8 md:p-12 max-h-[95vh] overflow-y-auto relative animate-fade shadow-2xl" style={{ border: '1px solid rgba(37,99,235,0.2)' }}>
                <button
                    onClick={onClose}
                    className="absolute top-6 right-6 text-slate-500 hover:text-white p-2 hover:bg-slate-900 rounded-full transition-all z-10"
                >
                    <X size={24} />
                </button>

                <div className="mb-10">
                    <div className="inline-block px-3 py-1 mb-5 rounded-md bg-white/5 border border-white/10 text-slate-400 text-[9px] font-bold uppercase tracking-[0.2em]">
                        Inventory Control
                    </div>
                    <h2 className="text-3xl font-bold text-white mb-2 tracking-tight">
                        {product ? 'Edit Product Details' : 'Add New Product'}
                    </h2>
                    <p className="text-slate-500 text-sm">Update the catalog with verified inventory data.</p>
                </div>

                <form onSubmit={(e) => { e.preventDefault(); onSubmit(formData); }} className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
                    <div className="flex flex-col gap-2">
                        <label className="stat-label text-slate-400 ml-1">Product ID (ASIN)</label>
                        <div className="relative">
                            <Hash className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-600" size={18} />
                            <input
                                type="text"
                                disabled={!!product}
                                placeholder="B000..."
                                className="input-field pl-14 h-14 font-mono text-sm"
                                style={{ background: 'rgba(5,6,11,1)', border: '1px solid rgba(255,255,255,0.05)' }}
                                value={formData.asin}
                                onChange={(e) => setFormData({ ...formData, asin: e.target.value })}
                                required
                            />
                        </div>
                    </div>

                    <div className="flex flex-col gap-2">
                        <label className="stat-label text-slate-400 ml-1">Product Category</label>
                        <div className="relative">
                            <Tag className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-600" size={18} />
                            <select
                                className="input-field pl-14 pr-10 h-14 appearance-none cursor-pointer text-sm font-semibold"
                                style={{ background: 'rgba(5,6,11,1)', border: '1px solid rgba(255,255,255,0.05)' }}
                                value={formData.category_id}
                                onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
                                required
                                disabled={!categories || categories.length === 0}
                            >
                                <option value="" className="bg-slate-900">Select Category</option>
                                {categories && categories.map(cat => (
                                    <option key={cat.id} value={cat.id} className="bg-slate-900">{cat.category_name}</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    <div className="md:col-span-2 flex flex-col gap-2">
                        <label className="stat-label text-slate-400 ml-1">Product Title</label>
                        <input
                            type="text"
                            placeholder="Enter full product name"
                            className="input-field h-14 px-5 text-sm font-semibold"
                            style={{ background: 'rgba(5,6,11,1)', border: '1px solid rgba(255,255,255,0.05)' }}
                            value={formData.title}
                            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                            required
                        />
                    </div>

                    <div className="flex flex-col gap-2">
                        <label className="stat-label text-slate-400 ml-1">Price ($)</label>
                        <div className="relative">
                            <DollarSign className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-600" size={18} />
                            <input
                                type="number"
                                step="0.01"
                                placeholder="0.00"
                                className="input-field pl-14 h-14 text-sm font-mono"
                                style={{ background: 'rgba(5,6,11,1)', border: '1px solid rgba(255,255,255,0.05)' }}
                                value={formData.price === 0 ? '0' : (formData.price || '')}
                                onChange={(e) => setFormData({ ...formData, price: e.target.value === '' ? '' : parseFloat(e.target.value) })}
                                required
                            />
                        </div>
                    </div>

                    <div className="flex gap-4">
                        <div className="flex flex-col gap-2 flex-grow">
                            <label className="stat-label text-slate-400 ml-1">Market Rating</label>
                            <input
                                type="number"
                                step="0.1" max="5" min="0"
                                className="input-field h-14 text-center text-sm font-semibold"
                                style={{ background: 'rgba(5,6,11,1)', border: '1px solid rgba(255,255,255,0.05)' }}
                                value={formData.stars === 0 ? '0' : (formData.stars || '')}
                                onChange={(e) => setFormData({ ...formData, stars: e.target.value === '' ? '' : parseFloat(e.target.value) })}
                            />
                        </div>
                        <div className="flex flex-col gap-2 flex-grow">
                            <label className="stat-label text-slate-400 ml-1">Total Reviews</label>
                            <input
                                type="number"
                                min="0"
                                className="input-field h-14 text-center text-sm font-semibold"
                                style={{ background: 'rgba(5,6,11,1)', border: '1px solid rgba(255,255,255,0.05)' }}
                                value={formData.reviews === 0 ? '0' : (formData.reviews || '')}
                                onChange={(e) => setFormData({ ...formData, reviews: e.target.value === '' ? '' : parseInt(e.target.value) })}
                            />
                        </div>
                    </div>

                    <div className="flex flex-col gap-2 md:col-span-2">
                        <label className="stat-label text-slate-400 ml-1">Image Asset</label>
                        <div className="flex gap-2">
                            <div className="relative flex-1">
                                <ImageIcon className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-600" size={18} />
                                <input
                                    type="text"
                                    placeholder="Enter Image URL"
                                    className="input-field pl-14 h-14 text-xs font-mono"
                                    style={{ background: 'rgba(5,6,11,1)', border: '1px solid rgba(255,255,255,0.05)' }}
                                    value={formData.img_url || ''}
                                    onChange={(e) => setFormData({ ...formData, img_url: e.target.value })}
                                />
                            </div>
                            <button
                                type="button"
                                onClick={() => fileInputRef.current.click()}
                                className="p-3 bg-slate-800 border border-slate-700 rounded-lg hover:bg-slate-700 transition-all text-slate-300 shadow-lg"
                            >
                                <ExternalLink size={20} />
                            </button>
                            <input
                                type="file"
                                ref={fileInputRef}
                                className="hidden"
                                accept="image/*"
                                onChange={(e) => handleFileChange(e, 'img_url')}
                            />
                        </div>
                    </div>

                    <div className="md:col-span-2 pt-8">
                        <button type="submit" className="btn-entry w-full h-16 transition-all font-bold">
                            {product ? 'SAVE CHANGES' : 'CREATE PRODUCT'}
                        </button>
                        <p className="text-center text-slate-600 text-[10px] mt-4 font-semibold tracking-wider uppercase">
                            Secure Catalog Operation
                        </p>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default ProductModal;

import React from 'react';
import { Edit3, Trash2, Star, Layers, ExternalLink } from 'lucide-react';

const ProductCard = ({ product, onEdit, onDelete }) => {
    return (
        <div className="glass-card group relative flex flex-col h-full overflow-hidden animate-fade">
            {/* Product Media Section */}
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-900/10 flex items-center justify-center p-2">
                <img
                    src={product.img_url || 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&q=80&w=400'}
                    alt={product.title}
                    className="w-full h-full object-contain transition-transform duration-500 group-hover:scale-110"
                />

                {/* Hover Actions Float */}
                <div className="absolute top-4 right-4 flex flex-col gap-2 translate-x-12 opacity-0 group-hover:translate-x-0 group-hover:opacity-100 transition-all duration-300 z-20">
                    <button
                        onClick={() => onEdit(product)}
                        className="p-2.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-400 hover:text-white hover:bg-slate-800 transition-all shadow-xl"
                    >
                        <Edit3 size={16} />
                    </button>
                    <button
                        onClick={() => onDelete(product.asin)}
                        className="p-2.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-400 hover:text-rose-500 hover:bg-slate-800 transition-all shadow-xl"
                    >
                        <Trash2 size={16} />
                    </button>
                </div>

                {/* Price Tag Overlay */}
                <div className="absolute bottom-4 left-4 z-10">
                    <div className="bg-slate-900/90 px-3 py-1.5 rounded-md border border-white/10 shadow-lg">
                        <p className="text-white font-bold text-sm font-mono">${product.price}</p>
                    </div>
                </div>
            </div>

            {/* Product Info Section */}
            <div className="p-5 flex flex-col flex-1">
                <div className="flex items-center gap-2 mb-2">
                    <div className="flex text-amber-500 items-center">
                        <Star size={12} fill="currentColor" />
                        <span className="stat-label ml-1.5 text-slate-400 text-xs font-semibold">
                            {product.stars} <span className="text-slate-500 font-normal">({product.reviews})</span>
                        </span>
                    </div>
                </div>

                <h3 className="text-slate-100 font-semibold leading-relaxed line-clamp-2 mb-4 group-hover:text-blue-400 transition-all text-sm">
                    {product.title}
                </h3>

                <div className="mt-auto pt-4 flex items-center justify-between border-t border-white/5">
                    <div className="flex items-center gap-2 text-slate-400">
                        <Layers size={13} className="text-slate-500" />
                        <p className="stat-label truncate text-[11px] uppercase tracking-wider font-bold">
                            {product.category_name || 'Standard Distribution'}
                        </p>
                    </div>
                    <ExternalLink size={14} className="text-slate-600 hover:text-white cursor-pointer transition-all" />
                </div>
            </div>
        </div>
    );
};

export default ProductCard;

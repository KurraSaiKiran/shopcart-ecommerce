import { useState, useEffect, useCallback } from 'react';
import { ProductService } from '../services/api';

export const useProducts = () => {
    const [products, setProducts] = useState([]);
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedCategory, setSelectedCategory] = useState(null);
    const [page, setPage] = useState(1);
    const [searchQuery, setSearchQuery] = useState('');
    const [priceRange, setPriceRange] = useState({ min: null, max: null });
    const [minRating, setMinRating] = useState(null);

    const refreshProducts = useCallback(async () => {
        try {
            setLoading(true);
            
            let url;
            const hasFilters = searchQuery || selectedCategory || priceRange.min !== null || priceRange.max !== null || minRating !== null;
            
            if (hasFilters) {
                url = `http://127.0.0.1:8005/products/search?page=${page}&limit=20`;
                if (searchQuery) url += `&q=${encodeURIComponent(searchQuery)}`;
                if (selectedCategory) url += `&category_id=${selectedCategory}`;
                if (priceRange.min !== null) url += `&min_price=${priceRange.min}`;
                if (priceRange.max !== null) url += `&max_price=${priceRange.max}`;
                if (minRating !== null) url += `&min_rating=${minRating}`;
            } else {
                url = `http://127.0.0.1:8005/products?page=${page}&limit=20`;
            }
            
            const response = await fetch(url);
            if (!response.ok) throw new Error('Failed to fetch products');
            
            const data = await response.json();
            setProducts(data.products || []);
            setError(null);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, [page, selectedCategory, searchQuery, priceRange, minRating]);

    const loadInitialData = async () => {
        try {
            const cats = await ProductService.getCategories();
            setCategories(cats);
        } catch (err) {
            setError(err.message);
        }
    };

    useEffect(() => {
        loadInitialData();
    }, []);

    useEffect(() => {
        refreshProducts();
    }, [refreshProducts]);

    return {
        products,
        categories,
        loading,
        error,
        selectedCategory,
        setSelectedCategory,
        page,
        setPage,
        searchQuery,
        setSearchQuery,
        priceRange,
        setPriceRange,
        minRating,
        setMinRating,
        refreshProducts
    };
};

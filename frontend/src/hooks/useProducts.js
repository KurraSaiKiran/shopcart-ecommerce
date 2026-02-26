import { useState, useEffect, useCallback } from 'react';
import { ProductService } from '../services/api';

export const useProducts = () => {
    const [products, setProducts] = useState([]);
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [stats, setStats] = useState({});
    const [selectedCategory, setSelectedCategory] = useState(null);
    const [page, setPage] = useState(1);

    const refreshProducts = useCallback(async () => {
        try {
            setLoading(true);
            const data = await ProductService.getProducts(page, 20, selectedCategory);
            setProducts(data.products || []);
            setError(null);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, [page, selectedCategory]);

    const loadInitialData = async () => {
        try {
            const [cats, statData] = await Promise.all([
                ProductService.getCategories(),
                ProductService.getStats()
            ]);
            setCategories(cats);
            setStats(statData);
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

    const [notification, setNotification] = useState(null);

    const notify = (message, type = 'success') => {
        setNotification({ message, type });
    };

    const clearNotification = () => setNotification(null);

    const removeProduct = async (asin) => {
        if (!window.confirm('Are you sure you want to delete this product?')) return;
        try {
            await ProductService.deleteProduct(asin);
            refreshProducts();
            setStats(prev => ({ ...prev, total_products: prev.total_products - 1 }));
            notify(`Product ${asin} deleted successfully`, 'info');
        } catch (err) {
            notify(err.message, 'error');
        }
    };

    const saveProduct = async (formData, isEdit) => {
        try {
            if (isEdit) {
                await ProductService.updateProduct(formData.asin, formData);
                notify('Product updated successfully');
            } else {
                await ProductService.createProduct(formData);
                setStats(prev => ({ ...prev, total_products: prev.total_products + 1 }));
                notify('New product published successfully');
            }
            refreshProducts();
            return true;
        } catch (err) {
            notify(err.message, 'error');
            return false;
        }
    };

    return {
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
        refreshProducts,
        removeProduct,
        saveProduct
    };
};

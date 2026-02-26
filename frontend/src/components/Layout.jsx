import React from 'react';
import { Package, Users, BarChart3, Database } from 'lucide-react';

const Layout = ({ children, stats }) => {
    const statItems = [
        { label: 'Products', value: stats.total_products, icon: Package, color: 'text-indigo-400' },
        { label: 'Users', value: stats.total_users, icon: Users, color: 'text-emerald-400' },
        { label: 'Reviews', value: stats.total_ratings, icon: BarChart3, color: 'text-amber-400' },
        { label: 'Categories', value: stats.total_categories, icon: Database, color: 'text-purple-400' },
    ];

    return (
        <div className="flex min-h-screen bg-transparent relative">
            {/* Background Aesthetics */}
            <div className="bg-arc-container">
                <div className="bg-arc"></div>
            </div>

            <main className="flex-1 overflow-auto relative z-10">
                {/* Top Navbar */}
                <nav className="nav-bar">
                    <div className="container flex flex-col md:flex-row justify-between items-center gap-6">
                        <div className="flex flex-col items-center md:items-start">
                            <h1 className="text-3xl font-bold text-white tracking-tight">
                                Product Catalog
                            </h1>
                            <div className="flex items-center gap-2 mt-1">
                                <p className="stat-label text-slate-500 font-medium">
                                    Inventory Management System
                                </p>
                            </div>
                        </div>

                        <div className="flex items-center gap-6 md:gap-10">
                            {statItems.map((item, i) => (
                                <div key={i} className="flex flex-col items-center md:items-start">
                                    <div className="flex items-center gap-2 mb-1">
                                        <item.icon size={12} className="text-slate-500" />
                                        <p className="stat-label text-slate-500">
                                            {item.label}
                                        </p>
                                    </div>
                                    <p className="stat-value">
                                        {item.value?.toLocaleString() || '0'}
                                    </p>
                                </div>
                            ))}
                        </div>
                    </div>
                </nav>

                {/* Content Area */}
                <div className="container p-8 animate-fade">
                    {children}
                </div>
            </main>
        </div>
    );
};

export default Layout;

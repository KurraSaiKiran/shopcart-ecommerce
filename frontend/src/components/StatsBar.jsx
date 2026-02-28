import React, { useState, useEffect } from 'react';
import StatCard from './StatCard';
import { Package, Users, Star, Grid } from 'lucide-react';

const StatsBar = () => {
  const [stats, setStats] = useState({
    total_products: null,
    total_users: null,
    total_ratings: null,
    total_categories: null
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://127.0.0.1:8005/stats');
      if (!response.ok) throw new Error('Failed to fetch stats');
      const data = await response.json();
      setStats(data);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Stats fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (error) {
    return (
      <div style={{
        background: '#fff',
        border: '1px solid #ffcdd2',
        borderRadius: '8px',
        padding: '16px',
        marginBottom: '24px'
      }}>
        <p style={{ color: '#d32f2f', fontSize: '14px', margin: 0 }}>
          Failed to load statistics. Please check your connection.
        </p>
      </div>
    );
  }

  return (
    <div style={{
      display: 'flex',
      gap: '16px',
      marginBottom: '24px',
      flexWrap: 'wrap'
    }}>
      <StatCard
        label="Total Products"
        value={stats.total_products}
        icon={Package}
        loading={loading}
      />
      <StatCard
        label="Total Users"
        value={stats.total_users}
        icon={Users}
        loading={loading}
      />
      <StatCard
        label="Total Reviews"
        value={stats.total_ratings}
        icon={Star}
        loading={loading}
      />
      <StatCard
        label="Categories"
        value={stats.total_categories}
        icon={Grid}
        loading={loading}
      />
      
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
        @media (max-width: 768px) {
          .container > div:first-of-type {
            gap: 12px !important;
          }
          .container > div:first-of-type > div {
            min-width: calc(50% - 6px) !important;
          }
        }
      `}</style>
    </div>
  );
};

export default StatsBar;

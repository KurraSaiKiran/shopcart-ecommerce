import React, { useEffect } from 'react';
import { CheckCircle, AlertCircle, X, Info } from 'lucide-react';

const Toast = ({ message, type = 'success', onClose }) => {
    useEffect(() => {
        const timer = setTimeout(onClose, 5000);
        return () => clearTimeout(timer);
    }, [onClose]);

    const icons = {
        success: <CheckCircle className="text-emerald-400" size={20} />,
        error: <AlertCircle className="text-rose-400" size={20} />,
        info: <Info className="text-indigo-400" size={20} />
    };

    const borders = {
        success: 'border-emerald-500/20 bg-emerald-500/5',
        error: 'border-rose-500/20 bg-rose-500/5',
        info: 'border-indigo-500/20 bg-indigo-500/5'
    };

    return (
        <div
            className={`fixed bottom-8 right-8 z-50 flex items-center gap-4 p-4 pr-10 rounded-lg glass-card animate-fade`}
            style={{
                border: `1px solid rgba(255,255,255,0.05)`,
                background: 'rgba(15, 23, 42, 0.9)',
                backdropFilter: 'blur(20px)'
            }}
        >
            <div style={{ flexShrink: 0 }}>
                {icons[type]}
            </div>
            <div style={{ flexGrow: 1 }}>
                <p className="text-white text-sm font-semibold">{message}</p>
            </div>
            <button
                onClick={onClose}
                className="absolute top-3 right-3 text-slate-500 hover:text-white transition-all"
            >
                <X size={14} />
            </button>
        </div>
    );
};

export default Toast;

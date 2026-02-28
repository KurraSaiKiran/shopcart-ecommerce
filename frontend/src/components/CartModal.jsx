import React from 'react';
import { X, Trash2, ShoppingBag } from 'lucide-react';

const CartModal = ({ isOpen, onClose, cartItems, onRemoveItem, onUpdateQuantity }) => {
  if (!isOpen) return null;

  const total = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);

  return (
    <>
      <div 
        style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0,0,0,0.5)',
          zIndex: 999,
          animation: 'fadeIn 0.2s'
        }}
        onClick={onClose}
      />
      
      <div style={{
        position: 'fixed',
        top: 0,
        right: 0,
        bottom: 0,
        width: '100%',
        maxWidth: '450px',
        background: '#fff',
        zIndex: 1000,
        boxShadow: '-4px 0 24px rgba(0,0,0,0.15)',
        display: 'flex',
        flexDirection: 'column',
        animation: 'slideInRight 0.3s'
      }}>
        {/* Header */}
        <div style={{
          padding: '20px 24px',
          borderBottom: '1px solid var(--border)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <ShoppingBag size={24} color="var(--primary)" />
            <div>
              <h2 style={{ fontSize: '18px', fontWeight: 700, margin: 0 }}>
                My Cart
              </h2>
              <p style={{ fontSize: '13px', color: 'var(--text-gray)', margin: 0 }}>
                {cartItems.length} {cartItems.length === 1 ? 'item' : 'items'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: '8px',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <X size={24} color="var(--text-gray)" />
          </button>
        </div>

        {/* Cart Items */}
        <div style={{
          flex: 1,
          overflowY: 'auto',
          padding: '16px'
        }}>
          {cartItems.length === 0 ? (
            <div style={{
              textAlign: 'center',
              padding: '60px 20px',
              color: 'var(--text-gray)'
            }}>
              <ShoppingBag size={64} style={{ opacity: 0.3, margin: '0 auto 16px' }} />
              <p style={{ fontSize: '16px', fontWeight: 600, marginBottom: '8px' }}>
                Your cart is empty
              </p>
              <p style={{ fontSize: '14px' }}>
                Add products to get started!
              </p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {cartItems.map((item) => (
                <div key={item.asin} style={{
                  background: '#fff',
                  border: '1px solid var(--border)',
                  borderRadius: '8px',
                  padding: '12px',
                  display: 'flex',
                  gap: '12px'
                }}>
                  <img
                    src={item.img_url || item.imgUrl || 'https://via.placeholder.com/80?text=No+Image'}
                    alt={item.title}
                    style={{
                      width: '80px',
                      height: '80px',
                      objectFit: 'contain',
                      borderRadius: '4px',
                      background: '#f8f8f8'
                    }}
                    onError={(e) => {
                      e.target.src = 'https://via.placeholder.com/80?text=No+Image';
                    }}
                  />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <h3 style={{
                      fontSize: '14px',
                      fontWeight: 500,
                      margin: '0 0 8px 0',
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden'
                    }}>
                      {item.title}
                    </h3>
                    <p style={{
                      fontSize: '16px',
                      fontWeight: 700,
                      color: 'var(--text-dark)',
                      margin: '0 0 8px 0'
                    }}>
                      ₹{(item.price * item.quantity).toLocaleString('en-IN')}
                    </p>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px'
                    }}>
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        border: '1px solid var(--border)',
                        borderRadius: '4px'
                      }}>
                        <button
                          onClick={() => onUpdateQuantity(item.asin, Math.max(1, item.quantity - 1))}
                          style={{
                            background: 'none',
                            border: 'none',
                            padding: '4px 12px',
                            cursor: 'pointer',
                            fontSize: '16px',
                            fontWeight: 600
                          }}
                        >
                          −
                        </button>
                        <span style={{
                          padding: '4px 12px',
                          borderLeft: '1px solid var(--border)',
                          borderRight: '1px solid var(--border)',
                          fontSize: '14px',
                          fontWeight: 600
                        }}>
                          {item.quantity}
                        </span>
                        <button
                          onClick={() => onUpdateQuantity(item.asin, item.quantity + 1)}
                          style={{
                            background: 'none',
                            border: 'none',
                            padding: '4px 12px',
                            cursor: 'pointer',
                            fontSize: '16px',
                            fontWeight: 600
                          }}
                        >
                          +
                        </button>
                      </div>
                      <button
                        onClick={() => onRemoveItem(item.asin)}
                        style={{
                          background: 'none',
                          border: 'none',
                          cursor: 'pointer',
                          color: '#d32f2f',
                          padding: '4px',
                          display: 'flex',
                          alignItems: 'center'
                        }}
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        {cartItems.length > 0 && (
          <div style={{
            borderTop: '1px solid var(--border)',
            padding: '20px 24px',
            background: '#fff'
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '16px'
            }}>
              <span style={{ fontSize: '16px', fontWeight: 600 }}>Total:</span>
              <span style={{ fontSize: '24px', fontWeight: 700, color: 'var(--primary)' }}>
                ₹{total.toLocaleString('en-IN')}
              </span>
            </div>
            <button
              className="btn-primary"
              style={{
                width: '100%',
                padding: '14px',
                fontSize: '16px',
                fontWeight: 700
              }}
            >
              Proceed to Checkout
            </button>
          </div>
        )}
      </div>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes slideInRight {
          from { transform: translateX(100%); }
          to { transform: translateX(0); }
        }
      `}</style>
    </>
  );
};

export default CartModal;

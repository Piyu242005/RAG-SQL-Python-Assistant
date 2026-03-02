import React from 'react';
import { Toaster } from 'react-hot-toast';
import { useTheme } from '../context/ThemeContext';

const ToastProvider = () => {
    const { isDark } = useTheme();

    return (
        <Toaster
            position="top-right"
            toastOptions={{
                duration: 4000,
                style: {
                    background: isDark ? '#151A22' : '#FFFFFF',
                    color: isDark ? '#E5E7EB' : '#374151',
                    border: isDark ? '1px solid rgba(255,255,255,0.04)' : '1px solid rgba(0,0,0,0.05)',
                    borderRadius: '0.75rem',
                    padding: '12px 16px',
                    fontSize: '13px',
                    fontWeight: '500',
                    boxShadow: '0 10px 20px rgba(0,0,0,0.3), 0 6px 6px rgba(0,0,0,0.15)',
                },
                success: { iconTheme: { primary: '#34d399', secondary: isDark ? '#151A22' : '#fff' } },
                error: { iconTheme: { primary: '#fb7185', secondary: isDark ? '#151A22' : '#fff' } },
            }}
        />
    );
};

export default ToastProvider;

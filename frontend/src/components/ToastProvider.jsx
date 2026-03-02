import React from 'react';
import { Toaster } from 'react-hot-toast';
import { useTheme } from '../context/ThemeContext';

/**
 * Theme-aware toast notification provider.
 */
const ToastProvider = () => {
    const { isDark } = useTheme();

    return (
        <Toaster
            position="top-right"
            toastOptions={{
                duration: 4000,
                style: {
                    background: isDark ? '#1e293b' : '#ffffff',
                    color: isDark ? '#e2e8f0' : '#1e293b',
                    border: isDark
                        ? '1px solid rgba(148, 163, 184, 0.1)'
                        : '1px solid rgba(148, 163, 184, 0.2)',
                    borderRadius: '12px',
                    fontSize: '13px',
                    fontFamily: 'Inter, sans-serif',
                    boxShadow: isDark
                        ? '0 8px 32px rgba(0,0,0,0.4)'
                        : '0 8px 32px rgba(0,0,0,0.08)',
                    padding: '12px 16px',
                },
                success: {
                    iconTheme: {
                        primary: '#6366f1',
                        secondary: isDark ? '#e2e8f0' : '#ffffff',
                    },
                },
                error: {
                    iconTheme: {
                        primary: '#ef4444',
                        secondary: isDark ? '#e2e8f0' : '#ffffff',
                    },
                    style: {
                        border: isDark
                            ? '1px solid rgba(239, 68, 68, 0.2)'
                            : '1px solid rgba(239, 68, 68, 0.3)',
                    },
                },
            }}
        />
    );
};

export default ToastProvider;

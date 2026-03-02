import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const ThemeContext = createContext(undefined);

/**
 * Theme provider with localStorage persistence and smooth transitions.
 * Applies 'dark' class to <html> for Tailwind dark mode.
 */
export const ThemeProvider = ({ children }) => {
    const [theme, setThemeState] = useState(() => {
        if (typeof window !== 'undefined') {
            const stored = localStorage.getItem('aurora-theme');
            if (stored === 'light' || stored === 'dark') return stored;
            return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
        }
        return 'dark';
    });

    const isDark = theme === 'dark';

    // Apply theme class to <html>
    useEffect(() => {
        const root = document.documentElement;
        root.classList.add('theme-transition');

        if (isDark) {
            root.classList.add('dark');
        } else {
            root.classList.remove('dark');
        }

        localStorage.setItem('aurora-theme', theme);

        // Remove transition class after animation completes
        const timeout = setTimeout(() => {
            root.classList.remove('theme-transition');
        }, 350);

        return () => clearTimeout(timeout);
    }, [theme, isDark]);

    const toggleTheme = useCallback(() => {
        setThemeState((prev) => (prev === 'dark' ? 'light' : 'dark'));
    }, []);

    const setTheme = useCallback((t) => {
        if (t === 'light' || t === 'dark') setThemeState(t);
    }, []);

    return (
        <ThemeContext.Provider value={{ theme, isDark, toggleTheme, setTheme }}>
            {children}
        </ThemeContext.Provider>
    );
};

/**
 * Hook to access the current theme and toggle function.
 */
export const useTheme = () => {
    const ctx = useContext(ThemeContext);
    if (!ctx) throw new Error('useTheme must be used within a ThemeProvider');
    return ctx;
};

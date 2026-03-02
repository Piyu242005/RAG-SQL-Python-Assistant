import React from 'react';
import { motion } from 'framer-motion';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

/**
 * Accessible theme toggle with smooth Sun/Moon icon animation.
 */
const ThemeToggle = ({ className = '' }) => {
    const { isDark, toggleTheme } = useTheme();

    return (
        <button
            onClick={toggleTheme}
            className={`relative p-2 rounded-xl transition-colors
        dark:hover:bg-surface-700/50 hover:bg-surface-200
        dark:text-surface-400 text-surface-500
        hover:text-amber-500 dark:hover:text-amber-400
        ${className}`}
            aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
            role="switch"
            aria-checked={isDark}
        >
            <motion.div
                key={isDark ? 'moon' : 'sun'}
                initial={{ scale: 0, rotate: -90, opacity: 0 }}
                animate={{ scale: 1, rotate: 0, opacity: 1 }}
                exit={{ scale: 0, rotate: 90, opacity: 0 }}
                transition={{ duration: 0.25, ease: 'easeOut' }}
            >
                {isDark ? (
                    <Moon className="w-[18px] h-[18px]" />
                ) : (
                    <Sun className="w-[18px] h-[18px]" />
                )}
            </motion.div>
        </button>
    );
};

export default ThemeToggle;

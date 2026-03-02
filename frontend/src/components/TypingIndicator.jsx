import React from 'react';
import { motion } from 'framer-motion';
import { Bot } from 'lucide-react';

/**
 * Animated typing indicator — themed for light and dark mode.
 */
const TypingIndicator = () => {
    const dotVariants = {
        initial: { y: 0 },
        animate: (i) => ({
            y: [0, -6, 0],
            transition: {
                duration: 0.6,
                repeat: Infinity,
                repeatDelay: 0.2,
                delay: i * 0.15,
                ease: 'easeInOut',
            },
        }),
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.3 }}
            className="flex gap-3 mb-6"
        >
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-violet-600 flex items-center justify-center flex-shrink-0 shadow-lg shadow-primary-500/20">
                <Bot className="w-4 h-4 text-white" />
            </div>
            <div className="glass-card rounded-2xl rounded-tl-sm px-5 py-4">
                <div className="flex items-center gap-1.5">
                    {[0, 1, 2].map((i) => (
                        <motion.span
                            key={i}
                            custom={i}
                            variants={dotVariants}
                            initial="initial"
                            animate="animate"
                            className="w-2 h-2 rounded-full bg-primary-500 dark:bg-primary-400"
                        />
                    ))}
                </div>
            </div>
        </motion.div>
    );
};

export default TypingIndicator;

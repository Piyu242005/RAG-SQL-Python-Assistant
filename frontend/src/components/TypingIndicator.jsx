import React from 'react';
import { motion } from 'framer-motion';

const TypingIndicator = () => (
    <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        className="flex items-center gap-3 mb-5"
    >
        <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-primary-500 to-violet-600
      flex items-center justify-center shadow-glow-primary">
            <span className="text-white text-[10px] font-bold">AI</span>
        </div>
        <div className="bg-white dark:bg-[#151A22] border border-black/5 dark:border-white/[0.04] rounded-2xl rounded-bl-md px-5 py-3">
            <div className="flex items-center gap-1.5">
                {[0, 1, 2].map((i) => (
                    <motion.div
                        key={i}
                        className="w-1.5 h-1.5 rounded-full bg-primary-400"
                        animate={{ y: [0, -5, 0], opacity: [0.3, 1, 0.3] }}
                        transition={{ duration: 0.8, repeat: Infinity, delay: i * 0.15, ease: 'easeInOut' }}
                    />
                ))}
            </div>
        </div>
    </motion.div>
);

export default TypingIndicator;

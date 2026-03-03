import React from 'react';
import { motion } from 'framer-motion';
import { Bot } from 'lucide-react';

const TypingIndicator = () => (
    <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        transition={{ duration: 0.3, ease: [0.25, 0.1, 0.25, 1] }}
        className="flex items-start gap-4 mb-8 w-full"
    >
        {/* Avatar — matches AI message EXACTLY */}
        <div className="flex-shrink-0 w-9 h-9 mt-1 rounded-xl bg-gradient-to-br from-primary-500 to-violet-600
      flex items-center justify-center shadow-md shadow-primary-500/30 border border-white/10">
            <Bot className="w-5 h-5 text-white" />
        </div>

        {/* Typing bubble — matches AI message structure */}
        <div className="flex-1 min-w-0 max-w-3xl">
            <div className="relative overflow-hidden inline-flex items-center rounded-3xl rounded-tl-sm px-6 py-5 sm:px-7 sm:py-6
        bg-white dark:bg-[#151A22] border border-black/5 dark:border-white/[0.06]
        shadow-[0_4px_20px_-4px_rgba(0,0,0,0.05)] dark:shadow-[0_8px_30px_-4px_rgba(0,0,0,0.4)]
        transition-colors duration-300">

                {/* Decorative inner glow */}
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary-500/20 via-violet-500/20 to-transparent" />

                <div className="flex items-center gap-1.5 h-6">
                    {[0, 1, 2].map((i) => (
                        <motion.div
                            key={i}
                            className="w-2.5 h-2.5 rounded-full bg-primary-500 dark:bg-primary-400"
                            animate={{
                                y: [0, -6, 0],
                                opacity: [0.35, 1, 0.35],
                            }}
                            transition={{
                                duration: 0.8,
                                repeat: Infinity,
                                delay: i * 0.15,
                                ease: 'easeInOut',
                            }}
                        />
                    ))}
                </div>
            </div>
        </div>
    </motion.div>
);

export default TypingIndicator;

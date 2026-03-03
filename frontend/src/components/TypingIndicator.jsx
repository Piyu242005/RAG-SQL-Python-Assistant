import React from 'react';
import { motion } from 'framer-motion';
import { Bot } from 'lucide-react';

const TypingIndicator = () => (
    <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        transition={{ duration: 0.2 }}
        className="flex items-start gap-3 mb-5"
    >
        {/* Avatar — same size & style as AI messages */}
        <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-violet-600
      flex items-center justify-center shadow-glow-primary">
            <Bot className="w-4 h-4 text-white" />
        </div>

        {/* Typing bubble — matches AI message style */}
        <div className="max-w-xl">
            <div className="bg-[#151A22] border border-white/[0.04] rounded-2xl rounded-tl-md
        px-5 py-3.5 shadow-depth-sm">
                <div className="flex items-center gap-1.5">
                    {[0, 1, 2].map((i) => (
                        <motion.div
                            key={i}
                            className="w-2 h-2 rounded-full bg-primary-400"
                            animate={{
                                y: [0, -6, 0],
                                opacity: [0.35, 1, 0.35],
                            }}
                            transition={{
                                duration: 0.7,
                                repeat: Infinity,
                                delay: i * 0.12,
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

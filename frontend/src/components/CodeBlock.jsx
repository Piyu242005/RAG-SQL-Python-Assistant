import React, { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Copy, Check, Code2 } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { motion } from 'framer-motion';

const CodeBlock = ({ language, value }) => {
    const [copied, setCopied] = useState(false);
    const { isDark } = useTheme();

    const handleCopy = async () => {
        await navigator.clipboard.writeText(value);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="my-3 rounded-xl overflow-hidden bg-white dark:bg-[#0D0F13]
      border border-black/5 dark:border-white/[0.04] shadow-inner-sm">
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-2 border-b border-black/5 dark:border-white/[0.04]">
                <div className="flex items-center gap-2">
                    <Code2 className="w-3.5 h-3.5 text-primary-400" />
                    <span className="text-[10px] font-semibold uppercase tracking-widest text-dark-300">
                        {language || 'code'}
                    </span>
                </div>
                <motion.button
                    onClick={handleCopy}
                    whileTap={{ scale: 0.85 }}
                    className="flex items-center gap-1.5 px-2 py-1 rounded-md text-[10px] font-medium
            text-dark-300 hover:text-dark-50 hover:bg-white/[0.04]
            transition-all duration-200"
                >
                    {copied ? (
                        <><Check className="w-3 h-3 text-emerald-400" /><span className="text-emerald-400">Copied</span></>
                    ) : (
                        <><Copy className="w-3 h-3" />Copy</>
                    )}
                </motion.button>
            </div>

            <SyntaxHighlighter
                style={isDark ? oneDark : oneLight}
                language={language || 'text'}
                PreTag="div"
                customStyle={{
                    margin: 0,
                    padding: '1rem',
                    background: 'transparent',
                    fontSize: '0.8rem',
                    lineHeight: '1.6',
                }}
            >
                {value}
            </SyntaxHighlighter>
        </div>
    );
};

export default CodeBlock;

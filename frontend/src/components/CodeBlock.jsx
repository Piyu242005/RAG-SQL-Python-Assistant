import React, { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus, oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Copy, Check } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

/**
 * Code block with adaptive syntax highlighting, language badge, and copy button.
 */
const CodeBlock = ({ language, children }) => {
    const [copied, setCopied] = useState(false);
    const { isDark } = useTheme();
    const code = String(children).replace(/\n$/, '');

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(code);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch {
            const textarea = document.createElement('textarea');
            textarea.value = code;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    return (
        <div className="relative group my-3 rounded-xl overflow-hidden border border-surface-200 dark:border-surface-800/60">
            {/* Header bar */}
            <div className="flex items-center justify-between px-4 py-2
        bg-surface-100 dark:bg-surface-900/80
        border-b border-surface-200 dark:border-surface-800/50">
                <span className="text-[10px] font-semibold text-surface-400 dark:text-surface-500 uppercase tracking-wider font-mono">
                    {language || 'code'}
                </span>
                <button
                    onClick={handleCopy}
                    className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[10px] font-medium transition-all ${copied
                            ? 'bg-emerald-500/20 text-emerald-600 dark:text-emerald-400'
                            : 'text-surface-400 dark:text-surface-500 hover:text-surface-600 dark:hover:text-surface-300 hover:bg-surface-200/60 dark:hover:bg-surface-800/60'
                        }`}
                >
                    {copied ? (
                        <>
                            <Check className="w-3 h-3" />
                            Copied!
                        </>
                    ) : (
                        <>
                            <Copy className="w-3 h-3" />
                            Copy
                        </>
                    )}
                </button>
            </div>

            {/* Adaptive syntax highlighting */}
            <SyntaxHighlighter
                style={isDark ? vscDarkPlus : oneLight}
                language={language || 'text'}
                PreTag="div"
                customStyle={{
                    margin: 0,
                    borderRadius: 0,
                    background: isDark ? '#0c1222' : '#f8fafc',
                    fontSize: '0.82rem',
                    lineHeight: '1.6',
                    padding: '1rem 1.25rem',
                }}
            >
                {code}
            </SyntaxHighlighter>
        </div>
    );
};

export default CodeBlock;

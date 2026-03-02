import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Plus,
    MessageSquare,
    ChevronLeft,
    ChevronRight,
    Sparkles,
    Trash2,
    Database as DatabaseIcon,
    Code2,
    Layers,
    MessageCircle,
} from 'lucide-react';
import ThemeToggle from './ThemeToggle';

/**
 * Collapsible sidebar — icons, left accent, badge count, improved empty state.
 */
const Sidebar = ({
    isOpen,
    onToggle,
    conversations,
    activeConversationId,
    onNewChat,
    onSelectConversation,
    onDeleteConversation,
    docFilter,
    onDocFilterChange,
}) => {
    const filters = [
        { value: null, label: 'All Sources', icon: Layers, color: 'from-primary-500 to-violet-500', activeAccent: 'border-primary-500' },
        { value: 'mysql', label: 'MySQL', icon: DatabaseIcon, color: 'from-blue-500 to-cyan-500', activeAccent: 'border-blue-500' },
        { value: 'python', label: 'Python', icon: Code2, color: 'from-emerald-500 to-teal-500', activeAccent: 'border-emerald-500' },
    ];

    return (
        <>
            {/* Toggle button */}
            <button
                onClick={onToggle}
                className="fixed top-4 left-4 z-50 p-2 rounded-xl glass
          text-surface-500 dark:text-surface-400
          hover:text-surface-900 dark:hover:text-white
          hover:bg-surface-200/60 dark:hover:bg-surface-700/50"
                aria-label={isOpen ? 'Collapse sidebar' : 'Expand sidebar'}
            >
                {isOpen ? <ChevronLeft className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
            </button>

            <AnimatePresence>
                {isOpen && (
                    <motion.aside
                        initial={{ width: 0, opacity: 0 }}
                        animate={{ width: 280, opacity: 1 }}
                        exit={{ width: 0, opacity: 0 }}
                        transition={{ duration: 0.25, ease: [0.4, 0, 0.2, 1] }}
                        className="h-full flex-shrink-0 overflow-hidden"
                    >
                        <div className="w-[280px] h-full flex flex-col glass-light
              border-r border-surface-200/60 dark:border-surface-800/50">
                            {/* Header */}
                            <div className="pt-16 px-4 pb-4">
                                <div className="flex items-center justify-between mb-6">
                                    <div className="flex items-center gap-2.5">
                                        <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-primary-500 to-violet-600 flex items-center justify-center shadow-md shadow-primary-500/20">
                                            <Sparkles className="w-4 h-4 text-white" />
                                        </div>
                                        <span className="text-sm font-semibold text-surface-900 dark:text-white tracking-tight">
                                            Aurora RAG
                                        </span>
                                    </div>
                                    <ThemeToggle />
                                </div>

                                <button
                                    onClick={onNewChat}
                                    className="w-full flex items-center justify-center gap-2.5 px-4 py-2.5 rounded-xl bg-primary-600 hover:bg-primary-500 text-white text-sm font-medium transition-all hover:shadow-lg hover:shadow-primary-500/20 active:scale-[0.98]"
                                >
                                    <Plus className="w-4 h-4" />
                                    New Chat
                                </button>
                            </div>

                            {/* Document filters */}
                            <div className="px-4 pb-4">
                                <p className="text-[10px] font-semibold text-surface-400 dark:text-surface-500 uppercase tracking-widest mb-2 px-1">
                                    Source Filter
                                </p>
                                <div className="flex flex-col gap-0.5">
                                    {filters.map((f) => {
                                        const isActive = docFilter === f.value;
                                        return (
                                            <button
                                                key={f.label}
                                                onClick={() => onDocFilterChange(f.value)}
                                                className={`relative flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-xs font-medium transition-all duration-200
                          ${isActive
                                                        ? 'bg-surface-100 dark:bg-surface-700/60 text-surface-900 dark:text-white shadow-sm'
                                                        : 'text-surface-500 dark:text-surface-400 hover:text-surface-800 dark:hover:text-surface-200 hover:bg-surface-100/60 dark:hover:bg-surface-800/30'
                                                    }`}
                                            >
                                                {/* Left accent border */}
                                                {isActive && (
                                                    <motion.div
                                                        layoutId="filterAccent"
                                                        className={`absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-4 rounded-r-full ${f.activeAccent}`}
                                                        transition={{ type: 'spring', stiffness: 500, damping: 35 }}
                                                    />
                                                )}
                                                <f.icon className={`w-3.5 h-3.5 ${isActive ? '' : 'opacity-60'}`} />
                                                {f.label}
                                            </button>
                                        );
                                    })}
                                </div>
                            </div>

                            {/* Conversation history */}
                            <div className="flex-1 overflow-y-auto px-4 pb-4">
                                <div className="flex items-center justify-between mb-2 px-1">
                                    <p className="text-[10px] font-semibold text-surface-400 dark:text-surface-500 uppercase tracking-widest">
                                        History
                                    </p>
                                    {conversations.length > 0 && (
                                        <span className="text-[9px] font-bold text-surface-400 dark:text-surface-600 bg-surface-100 dark:bg-surface-800/60 px-1.5 py-0.5 rounded-full">
                                            {conversations.length}
                                        </span>
                                    )}
                                </div>

                                {conversations.length === 0 ? (
                                    /* Improved empty state */
                                    <div className="text-center py-8 px-2">
                                        <div className="w-12 h-12 mx-auto rounded-xl bg-surface-100 dark:bg-surface-800/40 flex items-center justify-center mb-3">
                                            <MessageCircle className="w-5 h-5 text-surface-300 dark:text-surface-600" />
                                        </div>
                                        <p className="text-xs font-medium text-surface-500 dark:text-surface-500 mb-1">No conversations yet</p>
                                        <p className="text-[10px] text-surface-400 dark:text-surface-600 leading-relaxed">
                                            Start your first SQL or Python query above
                                        </p>
                                    </div>
                                ) : (
                                    <div className="flex flex-col gap-0.5">
                                        {conversations.map((conv) => {
                                            const isActive = activeConversationId === conv.id;
                                            return (
                                                <div
                                                    key={conv.id}
                                                    className={`group flex items-center gap-2 px-3 py-2.5 rounded-lg cursor-pointer transition-all duration-200
                            ${isActive
                                                            ? 'bg-surface-100 dark:bg-surface-700/60 text-surface-900 dark:text-white shadow-sm'
                                                            : 'text-surface-500 dark:text-surface-400 hover:text-surface-800 dark:hover:text-surface-200 hover:bg-surface-100/60 dark:hover:bg-surface-800/30'
                                                        }`}
                                                    onClick={() => onSelectConversation(conv.id)}
                                                >
                                                    <MessageSquare className={`w-3.5 h-3.5 flex-shrink-0 ${isActive ? 'opacity-80' : 'opacity-40'}`} />
                                                    <span className="text-xs truncate flex-1">{conv.title}</span>
                                                    <button
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            onDeleteConversation(conv.id);
                                                        }}
                                                        className="opacity-0 group-hover:opacity-100 p-1 hover:text-red-500 dark:hover:text-red-400 transition-all"
                                                    >
                                                        <Trash2 className="w-3 h-3" />
                                                    </button>
                                                </div>
                                            );
                                        })}
                                    </div>
                                )}
                            </div>

                            {/* Footer */}
                            <div className="p-4 border-t border-surface-200/60 dark:border-surface-800/50">
                                <div className="flex items-center gap-2 text-surface-400 dark:text-surface-600">
                                    <Sparkles className="w-3 h-3" />
                                    <span className="text-[10px] font-medium">Aurora RAG v2.0</span>
                                </div>
                            </div>
                        </div>
                    </motion.aside>
                )}
            </AnimatePresence>
        </>
    );
};

export default Sidebar;

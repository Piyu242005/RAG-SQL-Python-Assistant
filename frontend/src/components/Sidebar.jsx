import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Plus, MessageSquare, ChevronLeft, ChevronRight, Sparkles,
    Trash2, Database as DatabaseIcon, Code2, Layers, MessageCircle,
} from 'lucide-react';
import ThemeToggle from './ThemeToggle';

const Sidebar = ({
    isOpen, onToggle, conversations, activeConversationId,
    onNewChat, onSelectConversation, onDeleteConversation,
    docFilter, onDocFilterChange,
}) => {
    const filters = [
        { value: null, label: 'All Sources', icon: Layers, accent: 'from-primary-400 to-primary-600' },
        { value: 'mysql', label: 'MySQL', icon: DatabaseIcon, accent: 'from-blue-400 to-cyan-500' },
        { value: 'python', label: 'Python', icon: Code2, accent: 'from-emerald-400 to-teal-500' },
    ];

    return (
        <>
            {/* Toggle */}
            <motion.button
                onClick={onToggle}
                whileTap={{ scale: 0.9 }}
                className="fixed top-4 left-4 z-50 w-9 h-9 rounded-xl flex items-center justify-center
          bg-white/80 dark:bg-[#151A22] border border-black/5 dark:border-white/[0.04]
          text-dark-300 hover:text-dark-50 shadow-depth-sm
          transition-all duration-200"
            >
                {isOpen ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            </motion.button>

            <AnimatePresence>
                {isOpen && (
                    <motion.aside
                        initial={{ width: 0, opacity: 0 }}
                        animate={{ width: 272, opacity: 1 }}
                        exit={{ width: 0, opacity: 0 }}
                        transition={{ duration: 0.25, ease: [0.4, 0, 0.2, 1] }}
                        className="h-full flex-shrink-0 overflow-hidden"
                    >
                        <div className="w-[272px] h-full flex flex-col
              bg-white dark:bg-[#0D0F13]
              border-r border-black/5 dark:border-white/[0.04]">

                            {/* Header */}
                            <div className="pt-14 px-4 pb-4">
                                <div className="flex items-center justify-between mb-5">
                                    <div className="flex items-center gap-2.5">
                                        <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-primary-500 to-violet-600
                      flex items-center justify-center shadow-glow-primary">
                                            <Sparkles className="w-3.5 h-3.5 text-white" />
                                        </div>
                                        <span className="text-[13px] font-bold text-dark-600 dark:text-dark-50 tracking-tight">
                                            Piyu RAG
                                        </span>
                                    </div>
                                    <ThemeToggle />
                                </div>

                                <motion.button
                                    onClick={onNewChat}
                                    whileTap={{ scale: 0.96 }}
                                    className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl
                    bg-gradient-to-r from-primary-500 to-primary-600 text-white text-sm font-semibold
                    shadow-lg shadow-primary-600/20 hover:shadow-primary-500/30 hover:brightness-110
                    transition-all duration-200"
                                >
                                    <Plus className="w-4 h-4" />
                                    New Chat
                                </motion.button>
                            </div>

                            {/* Filters */}
                            <div className="px-3 pb-3">
                                <p className="text-[10px] font-semibold text-dark-300 uppercase tracking-widest mb-2 px-2">
                                    Source Filter
                                </p>
                                <div className="flex flex-col gap-0.5">
                                    {filters.map((f) => {
                                        const isActive = docFilter === f.value;
                                        return (
                                            <motion.button
                                                key={f.label}
                                                onClick={() => onDocFilterChange(f.value)}
                                                whileTap={{ scale: 0.97 }}
                                                className={`relative flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-xs font-medium
                          transition-all duration-200
                          ${isActive
                                                        ? 'bg-primary-500/8 dark:bg-primary-500/[0.08] text-primary-600 dark:text-primary-400'
                                                        : 'text-dark-300 hover:text-dark-50 hover:bg-black/[0.02] dark:hover:bg-white/[0.03]'
                                                    }`}
                                            >
                                                {/* Glow accent line on active */}
                                                {isActive && (
                                                    <motion.div
                                                        layoutId="sidebarAccent"
                                                        className="absolute left-0 top-1/2 -translate-y-1/2 w-[2px] h-4 rounded-r-full bg-primary-500 shadow-glow-primary"
                                                        transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                                                    />
                                                )}
                                                <div className={`w-6 h-6 rounded-md flex items-center justify-center transition-all duration-200
                          ${isActive ? `bg-gradient-to-br ${f.accent}` : 'bg-dark-500/30 dark:bg-white/[0.06]'}`}>
                                                    <f.icon className={`w-3 h-3 ${isActive ? 'text-white' : 'text-dark-300'}`} />
                                                </div>
                                                {f.label}
                                            </motion.button>
                                        );
                                    })}
                                </div>
                            </div>

                            {/* History */}
                            <div className="flex-1 overflow-y-auto px-3 pb-3">
                                <div className="flex items-center justify-between mb-2 px-2">
                                    <p className="text-[10px] font-semibold text-dark-300 uppercase tracking-widest">History</p>
                                    {conversations.length > 0 && (
                                        <span className="text-[9px] font-bold text-dark-300 bg-white/5 px-1.5 py-0.5 rounded-md">
                                            {conversations.length}
                                        </span>
                                    )}
                                </div>

                                {conversations.length === 0 ? (
                                    <div className="text-center py-10 px-3">
                                        <div className="w-12 h-12 mx-auto rounded-xl bg-white/[0.03] dark:bg-white/[0.03] flex items-center justify-center mb-3">
                                            <MessageCircle className="w-5 h-5 text-dark-400" />
                                        </div>
                                        <p className="text-xs font-medium text-dark-300 mb-0.5">No conversations yet</p>
                                        <p className="text-[10px] text-dark-400 leading-relaxed">Start your first query above</p>
                                    </div>
                                ) : (
                                    <div className="flex flex-col gap-0.5">
                                        {conversations.map((conv) => {
                                            const isActive = activeConversationId === conv.id;
                                            return (
                                                <motion.div
                                                    key={conv.id}
                                                    whileTap={{ scale: 0.97 }}
                                                    className={`group flex items-center gap-2 px-2.5 py-2 rounded-lg cursor-pointer
                            transition-all duration-200
                            ${isActive
                                                            ? 'bg-white/[0.06] text-dark-50'
                                                            : 'text-dark-300 hover:text-dark-50 hover:bg-white/[0.03]'
                                                        }`}
                                                    onClick={() => onSelectConversation(conv.id)}
                                                >
                                                    {isActive && (
                                                        <div className="absolute left-0 w-[2px] h-4 rounded-r-full bg-primary-500 shadow-glow-primary" />
                                                    )}
                                                    <MessageSquare className={`w-3.5 h-3.5 flex-shrink-0 ${isActive ? 'text-primary-400' : 'opacity-30'}`} />
                                                    <span className="text-xs truncate flex-1">{conv.title}</span>
                                                    <button
                                                        onClick={(e) => { e.stopPropagation(); onDeleteConversation(conv.id); }}
                                                        className="opacity-0 group-hover:opacity-100 p-1 hover:text-rose-400 transition-all"
                                                    >
                                                        <Trash2 className="w-3 h-3" />
                                                    </button>
                                                </motion.div>
                                            );
                                        })}
                                    </div>
                                )}
                            </div>

                            {/* Footer */}
                            <div className="px-4 py-3 border-t border-black/5 dark:border-white/[0.04]">
                                <div className="flex items-center gap-2 text-dark-400">
                                    <Sparkles className="w-3 h-3" />
                                    <span className="text-[10px] font-medium">Piyu RAG v2.0</span>
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

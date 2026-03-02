import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FileText, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react';

/**
 * Expandable source citation card with themed hover effects.
 */
const SourceCard = ({ source }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const docStyles = {
    mysql: {
      gradient: 'from-blue-500 to-cyan-500',
      bg: 'bg-blue-500/10',
      text: 'text-blue-600 dark:text-blue-400',
      border: 'border-blue-500/20',
      label: 'MySQL',
    },
    python: {
      gradient: 'from-emerald-500 to-teal-500',
      bg: 'bg-emerald-500/10',
      text: 'text-emerald-600 dark:text-emerald-400',
      border: 'border-emerald-500/20',
      label: 'Python',
    },
    default: {
      gradient: 'from-surface-500 to-surface-600',
      bg: 'bg-surface-500/10',
      text: 'text-surface-600 dark:text-surface-400',
      border: 'border-surface-500/20',
      label: 'Unknown',
    },
  };

  const style = docStyles[source.doc_type] || docStyles.default;

  return (
    <motion.div
      layout
      className={`group glass-card rounded-xl overflow-hidden hover:border-opacity-20 cursor-pointer transition-all
        hover:shadow-lg hover:shadow-surface-900/5 dark:hover:shadow-black/10 ${style.border}`}
      onClick={() => setIsExpanded(!isExpanded)}
      whileHover={{ scale: 1.01 }}
      transition={{ duration: 0.15 }}
    >
      <div className={`h-0.5 bg-gradient-to-r ${style.gradient}`} />

      <div className="p-3.5">
        <div className="flex items-start gap-3">
          <div className={`p-1.5 rounded-lg ${style.bg} flex-shrink-0`}>
            <FileText className={`w-4 h-4 ${style.text}`} />
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-0.5">
              <span className="text-sm font-medium text-surface-700 dark:text-surface-200 truncate">
                {source.source}
              </span>
              <span className={`px-1.5 py-0.5 rounded-md text-[10px] font-semibold ${style.bg} ${style.text}`}>
                {style.label}
              </span>
            </div>
            <p className="text-[11px] text-surface-400 dark:text-surface-500 font-medium">
              Page {source.page}
            </p>
          </div>

          <div className="flex items-center gap-1.5">
            <div className={`p-1 rounded-md ${style.bg} opacity-0 group-hover:opacity-100 transition-opacity`}>
              <ExternalLink className={`w-3 h-3 ${style.text}`} />
            </div>
            {source.content_preview && (
              isExpanded
                ? <ChevronUp className="w-4 h-4 text-surface-400 dark:text-surface-500" />
                : <ChevronDown className="w-4 h-4 text-surface-400 dark:text-surface-500" />
            )}
          </div>
        </div>

        <AnimatePresence>
          {isExpanded && source.content_preview && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden"
            >
              <div className="mt-3 pt-3 border-t border-surface-200/50 dark:border-surface-800/50">
                <p className="text-xs text-surface-500 dark:text-surface-400 leading-relaxed">
                  {source.content_preview}
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

export default SourceCard;

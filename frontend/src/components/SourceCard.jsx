import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FileText, ChevronDown, ChevronUp, Hash } from 'lucide-react';

const SourceCard = ({ source, index }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const docType = source.doc_type || (source.source?.toLowerCase().includes('python') ? 'python' : 'mysql');
  const accent = docType === 'python' ? 'from-emerald-400 to-teal-500' : 'from-blue-400 to-cyan-500';

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08, duration: 0.25 }}
    >
      <div className="bg-white dark:bg-[#111318] rounded-lg overflow-hidden border border-black/5 dark:border-white/[0.04]">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full flex items-center gap-2.5 px-3 py-2 text-left hover:bg-black/[0.01] dark:hover:bg-white/[0.02] transition-all"
        >
          <div className={`w-6 h-6 rounded-md bg-gradient-to-br ${accent} flex items-center justify-center flex-shrink-0`}>
            <FileText className="w-3 h-3 text-white" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-[11px] font-medium text-dark-600 dark:text-dark-100 truncate">
              {source.source || 'Unknown Source'}
            </p>
            {source.page && (
              <div className="flex items-center gap-1 mt-0.5">
                <Hash className="w-2.5 h-2.5 text-dark-400" />
                <span className="text-[9px] text-dark-300 font-medium">Page {source.page}</span>
              </div>
            )}
          </div>
          <div className="text-dark-400">
            {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </div>
        </button>

        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden"
            >
              <div className="px-3 pb-3">
                <div className="bg-[#F3F4F6] dark:bg-[#0D0F13] rounded-md p-3 border border-black/3 dark:border-white/[0.03]">
                  <p className="text-[11px] text-dark-200 leading-relaxed line-clamp-4">
                    {source.content || 'No preview available'}
                  </p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

export default SourceCard;

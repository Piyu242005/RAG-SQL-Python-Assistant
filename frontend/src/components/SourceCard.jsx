import React from 'react';
import { FileText } from 'lucide-react';

/**
 * Component to display source citations from PDFs.
 */
const SourceCard = ({ source }) => {
  const getDocTypeColor = (docType) => {
    if (docType === 'mysql') return 'bg-blue-500/20 text-blue-300';
    if (docType === 'python') return 'bg-green-500/20 text-green-300';
    return 'bg-gray-500/20 text-gray-300';
  };

  const getDocTypeLabel = (docType) => {
    if (docType === 'mysql') return 'MySQL';
    if (docType === 'python') return 'Python';
    return 'Unknown';
  };

  return (
    <div className="flex items-start gap-3 p-3 bg-slate-700/50 rounded-lg border border-slate-600 hover:border-slate-500 transition-colors">
      <FileText className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />
      
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-sm font-medium text-slate-200 truncate">
            {source.source}
          </span>
          {source.doc_type && (
            <span className={`px-2 py-0.5 rounded text-xs font-medium ${getDocTypeColor(source.doc_type)}`}>
              {getDocTypeLabel(source.doc_type)}
            </span>
          )}
        </div>
        
        <p className="text-xs text-slate-400">
          Page {source.page}
        </p>
        
        {source.content_preview && (
          <p className="text-xs text-slate-500 mt-2 line-clamp-2">
            {source.content_preview}
          </p>
        )}
      </div>
    </div>
  );
};

export default SourceCard;

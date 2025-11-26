import React from 'react';
import { X, FileText } from 'lucide-react';
import { Button } from './ui/button';

interface SourceExcerptModalProps {
  isOpen: boolean;
  onClose: () => void;
  source: {
    document: string;
    page: number;
    excerpt: string;
    relevance: number;
  } | null;
}

export function SourceExcerptModal({ isOpen, onClose, source }: SourceExcerptModalProps) {
  if (!isOpen || !source) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative bg-white rounded-lg shadow-xl w-full max-w-2xl mx-4 max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-start justify-between p-6 border-b">
          <div className="flex items-start gap-3 flex-1">
            <div className="w-10 h-10 rounded-lg bg-indigo-100 flex items-center justify-center flex-shrink-0">
              <FileText className="w-5 h-5 text-indigo-600" />
            </div>
            <div className="flex-1 min-w-0">
              <h2 className="text-gray-900 truncate">
                Source Excerpt
              </h2>
              <p className="text-sm text-gray-500 mt-1">
                {source.document} • Page {source.page}
              </p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="flex-shrink-0 ml-4"
          >
            <X className="w-4 h-4" />
          </Button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
              {source.excerpt}
            </p>
          </div>
          
          {/* Relevance indicator */}
          <div className="mt-4 flex items-center gap-2">
            <span className="text-sm text-gray-600">Relevance:</span>
            <div className="flex-1 bg-gray-200 rounded-full h-2 max-w-xs">
              <div 
                className="bg-indigo-600 h-2 rounded-full transition-all"
                style={{ width: `${source.relevance * 100}%` }}
              />
            </div>
            <span className="text-sm text-gray-700">
              {Math.round(source.relevance * 100)}%
            </span>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t p-4">
          <Button onClick={onClose} className="w-full">
            Close
          </Button>
        </div>
      </div>
    </div>
  );
}

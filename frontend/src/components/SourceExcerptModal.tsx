import React, { useEffect, useState } from 'react';
import { X, FileText, Loader2 } from 'lucide-react';
import { Button } from './ui/button';
import { documentsAPI } from '../services/api';

interface SourceExcerptModalProps {
  isOpen: boolean;
  onClose: () => void;
  source: {
    document: string;
    page: number;
    excerpt: string;
    relevance: number;
  } | null;
  documentId: string | null;
}

export function SourceExcerptModal({ isOpen, onClose, source, documentId }: SourceExcerptModalProps) {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen || !source || !documentId) {
      setImageUrl(null);
      setError(null);
      return;
    }

    const fetchPageImage = async () => {
      setLoading(true);
      setError(null);
      try {
        const url = await documentsAPI.getPageImage(documentId, source.page);
        setImageUrl(url);
      } catch (err) {
        console.error('Failed to fetch page image:', err);
        setError('Failed to load page image');
      } finally {
        setLoading(false);
      }
    };

    fetchPageImage();

    // Cleanup: revoke object URL when component unmounts or source changes
    return () => {
      if (imageUrl) {
        URL.revokeObjectURL(imageUrl);
      }
    };
  }, [isOpen, source, documentId]);

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
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 text-indigo-600 animate-spin" />
              <span className="ml-3 text-gray-600">Loading page image...</span>
            </div>
          ) : error ? (
            <div className="bg-red-50 rounded-lg p-4 border border-red-200">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          ) : imageUrl ? (
            <div className="bg-gray-50 rounded-lg border border-gray-200 overflow-hidden">
              <img 
                src={imageUrl} 
                alt={`Page ${source.page}`}
                className="w-full h-auto"
              />
            </div>
          ) : null}
          
          {/* Relevance indicator */}
          {!loading && !error && (
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
          )}
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

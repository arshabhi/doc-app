import React, { useState } from 'react';
import { useDocuments } from '../context/DocumentContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { FileText, Trash2, Calendar, HardDrive, Loader2 } from 'lucide-react';
import { Badge } from './ui/badge';
import { toast } from 'sonner';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from './ui/alert-dialog';

interface DocumentListProps {
  onSelectDocument: (id: string) => void;
  selectedDocumentId?: string;
}

export function DocumentList({ onSelectDocument, selectedDocumentId }: DocumentListProps) {
  const { documents, deleteDocument, summarizeDocument } = useDocuments();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [documentToDelete, setDocumentToDelete] = useState<string | null>(null);
  const [summarizingId, setSummarizingId] = useState<string | null>(null);

  const handleDeleteClick = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setDocumentToDelete(id);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = () => {
    if (documentToDelete) {
      deleteDocument(documentToDelete);
      toast.success('Document deleted successfully');
      setDocumentToDelete(null);
      setDeleteDialogOpen(false);
    }
  };

  const handleSummarize = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setSummarizingId(id);
    try {
      await summarizeDocument(id);
      toast.success('Document summarized successfully');
    } catch (error) {
      toast.error('Failed to summarize document');
    } finally {
      setSummarizingId(null);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const formatDate = (date: Date) => {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  if (documents.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Your Documents</CardTitle>
          <CardDescription>No documents uploaded yet</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <FileText className="w-16 h-16 text-gray-300 mb-4" />
          <p className="text-gray-500">Upload your first document to get started</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>Your Documents</CardTitle>
          <CardDescription>{documents.length} document(s) uploaded</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {documents.map((doc) => (
            <div
              key={doc.id}
              className={`p-4 border rounded-lg hover:bg-gray-50 transition-colors cursor-pointer ${
                selectedDocumentId === doc.id ? 'border-indigo-600 bg-indigo-50' : ''
              }`}
              onClick={() => onSelectDocument(doc.id)}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  <FileText className="w-5 h-5 text-indigo-600 mt-1 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="truncate">{doc.name}</p>
                    <div className="flex flex-wrap items-center gap-2 mt-2 text-xs text-gray-500">
                      <span className="flex items-center gap-1">
                        <HardDrive className="w-3 h-3" />
                        {formatFileSize(doc.size)}
                      </span>
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {formatDate(doc.uploadDate)}
                      </span>
                      {doc.summary && <Badge variant="secondary">Summarized</Badge>}
                    </div>
                    {doc.summary && (
                      <p className="mt-2 text-xs text-gray-600 line-clamp-2">
                        {doc.summary}
                      </p>
                    )}
                  </div>
                </div>
                <div className="flex items-center space-x-2 ml-4">
                  {!doc.summary && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={(e) => handleSummarize(doc.id, e)}
                      disabled={summarizingId === doc.id}
                    >
                      {summarizingId === doc.id ? (
                        <>
                          <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                          Summarizing...
                        </>
                      ) : (
                        'Summarize'
                      )}
                    </Button>
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => handleDeleteClick(doc.id, e)}
                  >
                    <Trash2 className="w-4 h-4 text-red-500" />
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Document</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this document? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDeleteConfirm}>Delete</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}

import React, { useState, useMemo } from 'react';
import { useDocuments } from '../context/DocumentContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { FileText, Trash2, Calendar, HardDrive, Loader2, ZoomIn, ZoomOut, Download, Search, Filter, X } from 'lucide-react';
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
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from './ui/tooltip';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';
import { Separator } from './ui/separator';

interface DocumentListProps {
  onSelectDocument: (id: string) => void;
  selectedDocumentId?: string;
}

export function DocumentList({ 
  onSelectDocument, 
  selectedDocumentId
}: DocumentListProps) {
  const { documents, deleteDocument, summarizeDocument, getDocument } = useDocuments();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [documentToDelete, setDocumentToDelete] = useState<string | null>(null);
  const [summarizingId, setSummarizingId] = useState<string | null>(null);
  const [expandedDocumentId, setExpandedDocumentId] = useState<string | null>(null);
  
  // Search and filter states
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'summarized' | 'unsummarized'>('all');
  const [sortBy, setSortBy] = useState<'name' | 'date' | 'size'>('date');

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
      // Collapse if the deleted document was expanded
      if (expandedDocumentId === documentToDelete) {
        setExpandedDocumentId(null);
      }
    }
  };

  const handleSummarize = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const doc = getDocument(id);
    
    // If already has summary, just expand/collapse
    if (doc?.summary) {
      setExpandedDocumentId(expandedDocumentId === id ? null : id);
      return;
    }
    
    // Otherwise, fetch the summary first
    setSummarizingId(id);
    try {
      await summarizeDocument(id);
      toast.success('Document summarized successfully');
      setExpandedDocumentId(id);
    } catch (error) {
      toast.error('Failed to summarize document');
    } finally {
      setSummarizingId(null);
    }
  };

  const handleExportSummary = (doc: any) => {
    if (!doc.summary) return;
    
    const content = `Document Summary\n\nDocument: ${doc.name}\nDate: ${formatDate(doc.uploadDate)}\nSize: ${formatFileSize(doc.size)}\n\n${doc.summary}`;
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${doc.name.replace(/\.[^/.]+$/, '')}_summary.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('Summary exported successfully');
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

  // Filter and sort documents
  const filteredAndSortedDocuments = useMemo(() => {
    let filtered = documents;

    // Apply search filter
    if (searchQuery.trim()) {
      filtered = filtered.filter(doc => 
        doc.name.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Apply status filter
    if (filterStatus === 'summarized') {
      filtered = filtered.filter(doc => doc.summary);
    } else if (filterStatus === 'unsummarized') {
      filtered = filtered.filter(doc => !doc.summary);
    }

    // Apply sorting
    const sorted = [...filtered].sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'date':
          return new Date(b.uploadDate).getTime() - new Date(a.uploadDate).getTime();
        case 'size':
          return b.size - a.size;
        default:
          return 0;
      }
    });

    return sorted;
  }, [documents, searchQuery, filterStatus, sortBy]);

  const clearFilters = () => {
    setSearchQuery('');
    setFilterStatus('all');
    setSortBy('date');
  };

  const hasActiveFilters = searchQuery !== '' || filterStatus !== 'all' || sortBy !== 'date';

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
          <CardDescription>
            {documents.length} document(s) uploaded
          </CardDescription>
          
          {/* Search and Filter Controls */}
          <div className="space-y-3 mt-4">
            <div className="flex gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <Input
                  placeholder="Search documents..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9"
                />
              </div>
              {hasActiveFilters && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={clearFilters}
                  className="flex items-center gap-1"
                >
                  <X className="w-3 h-3" />
                  Clear
                </Button>
              )}
            </div>

            <div className="flex gap-2 flex-wrap">
              <Select value={filterStatus} onValueChange={(value: any) => setFilterStatus(value)}>
                <SelectTrigger className="w-[180px]">
                  <Filter className="w-3 h-3 mr-2" />
                  <SelectValue placeholder="Filter by status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Documents</SelectItem>
                  <SelectItem value="summarized">Summarized</SelectItem>
                  <SelectItem value="unsummarized">Not Summarized</SelectItem>
                </SelectContent>
              </Select>

              <Select value={sortBy} onValueChange={(value: any) => setSortBy(value)}>
                <SelectTrigger className="w-[160px]">
                  <SelectValue placeholder="Sort by" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="date">Date (Newest)</SelectItem>
                  <SelectItem value="name">Name (A-Z)</SelectItem>
                  <SelectItem value="size">Size (Largest)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {filteredAndSortedDocuments.length === 0 && (
              <div className="text-sm text-gray-500 text-center py-2">
                No documents match your search criteria
              </div>
            )}
          </div>
        </CardHeader>
        
        <CardContent className="space-y-3">
          {filteredAndSortedDocuments.map((doc) => (
            <div
              key={doc.id}
              className={`border rounded-lg transition-all ${
                selectedDocumentId === doc.id ? 'border-indigo-600 bg-indigo-50' : ''
              } ${expandedDocumentId === doc.id ? 'shadow-md' : ''}`}
            >
              <div
                className={`p-4 hover:bg-gray-50 transition-colors cursor-pointer ${
                  expandedDocumentId === doc.id ? 'bg-gray-50' : ''
                }`}
                onClick={() => onSelectDocument(doc.id)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3 flex-1 min-w-0">
                    <FileText className="w-5 h-5 text-indigo-600 mt-1 flex-shrink-0" />
                    <div className="flex-1 min-w-0 overflow-hidden">
                      <TooltipProvider>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <p className="truncate cursor-help">{doc.name}</p>
                          </TooltipTrigger>
                          <TooltipContent side="top" className="max-w-md">
                            <p className="break-all">{doc.name}</p>
                          </TooltipContent>
                        </Tooltip>
                      </TooltipProvider>
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
                    </div>
                  </div>
                  <div className="flex items-center space-x-2 ml-4">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={(e) => handleSummarize(doc.id, e)}
                      disabled={summarizingId === doc.id}
                      title={doc.summary ? (expandedDocumentId === doc.id ? 'Collapse summary' : 'View summary') : 'Generate summary'}
                    >
                      {summarizingId === doc.id ? (
                        <Loader2 className="w-3 h-3 animate-spin" />
                      ) : expandedDocumentId === doc.id ? (
                        <ZoomOut className="w-3 h-3" />
                      ) : (
                        <ZoomIn className="w-3 h-3" />
                      )}
                    </Button>
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

              {/* Expanded Summary View */}
              {expandedDocumentId === doc.id && doc.summary && (
                <div className="border-t bg-white">
                  <div className="p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <h4 className="font-medium text-sm text-gray-900">Document Summary</h4>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleExportSummary(doc);
                        }}
                        className="flex items-center gap-1"
                      >
                        <Download className="w-3 h-3" />
                        Export
                      </Button>
                    </div>
                    <Separator />
                    <div className="prose prose-sm max-w-none">
                      <p className="text-gray-700 whitespace-pre-wrap text-sm leading-relaxed">
                        {doc.summary}
                      </p>
                    </div>
                  </div>
                </div>
              )}
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
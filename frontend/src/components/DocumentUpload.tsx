import React, { useCallback, useState } from 'react';
import { useDocuments } from '../context/DocumentContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Upload, FileText, X } from 'lucide-react';
import { toast } from 'sonner';

export function DocumentUpload() {
  const { uploadDocument } = useDocuments();
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFiles(Array.from(e.target.files));
    }
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;

    setUploading(true);
    try {
      for (const file of selectedFiles) {
        await uploadDocument(file);
      }
      toast.success(`Successfully uploaded ${selectedFiles.length} document(s)`);
      setSelectedFiles([]);
    } catch (error) {
      toast.error('Failed to upload documents');
    } finally {
      setUploading(false);
    }
  };

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Upload Documents</CardTitle>
        <CardDescription>
          Upload documents to analyze, summarize, and chat with
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-indigo-500 transition-colors">
          <Upload className="w-12 h-12 mx-auto text-gray-400 mb-4" />
          <div className="space-y-2">
            <label htmlFor="file-upload" className="cursor-pointer">
              <span className="text-indigo-600 hover:text-indigo-700">Click to upload</span>
              <span className="text-gray-600"> or drag and drop</span>
            </label>
            <p className="text-sm text-gray-500">
              PDF, DOC, DOCX, TXT (Max 10MB)
            </p>
          </div>
          <input
            id="file-upload"
            type="file"
            className="hidden"
            multiple
            accept=".pdf,.doc,.docx,.txt"
            onChange={handleFileSelect}
          />
        </div>

        {selectedFiles.length > 0 && (
          <div className="space-y-2">
            <p className="text-sm">Selected Files:</p>
            {selectedFiles.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  <FileText className="w-5 h-5 text-indigo-600" />
                  <div>
                    <p className="text-sm">{file.name}</p>
                    <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => removeFile(index)}
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            ))}
            <Button
              onClick={handleUpload}
              disabled={uploading}
              className="w-full"
            >
              {uploading ? 'Uploading...' : `Upload ${selectedFiles.length} file(s)`}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

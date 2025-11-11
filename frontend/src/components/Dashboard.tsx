import React, { useState } from 'react';
import { DocumentUpload } from './DocumentUpload';
import { DocumentList } from './DocumentList';
import { DocumentChat } from './DocumentChat';
import { DocumentCompare } from './DocumentCompare';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Upload, MessageSquare, GitCompare } from 'lucide-react';

export function Dashboard() {
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(null);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1>Document Management</h1>
        <p className="text-gray-600 mt-2">
          Upload, analyze, and interact with your documents using AI-powered tools
        </p>
      </div>

      <Tabs defaultValue="upload" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="upload" className="flex items-center gap-2">
            <Upload className="w-4 h-4" />
            Upload
          </TabsTrigger>
          <TabsTrigger value="chat" className="flex items-center gap-2">
            <MessageSquare className="w-4 h-4" />
            Chat
          </TabsTrigger>
          <TabsTrigger value="compare" className="flex items-center gap-2">
            <GitCompare className="w-4 h-4" />
            Compare
          </TabsTrigger>
        </TabsList>

        <TabsContent value="upload" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <DocumentUpload />
            <DocumentList
              onSelectDocument={setSelectedDocumentId}
              selectedDocumentId={selectedDocumentId || undefined}
            />
          </div>
        </TabsContent>

        <TabsContent value="chat">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1">
              <DocumentList
                onSelectDocument={setSelectedDocumentId}
                selectedDocumentId={selectedDocumentId || undefined}
              />
            </div>
            <div className="lg:col-span-2">
              <DocumentChat documentId={selectedDocumentId} />
            </div>
          </div>
        </TabsContent>

        <TabsContent value="compare">
          <DocumentCompare />
        </TabsContent>
      </Tabs>
    </div>
  );
}

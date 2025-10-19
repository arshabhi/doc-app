import React, { createContext, useContext, useState } from 'react';

export interface Document {
  id: string;
  name: string;
  size: number;
  uploadDate: Date;
  content: string;
  summary?: string;
}

export interface ChatMessage {
  id: string;
  documentId: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface DocumentContextType {
  documents: Document[];
  uploadDocument: (file: File) => Promise<void>;
  deleteDocument: (id: string) => void;
  getDocument: (id: string) => Document | undefined;
  summarizeDocument: (id: string) => Promise<string>;
  chatMessages: ChatMessage[];
  sendMessage: (documentId: string, message: string) => Promise<void>;
  clearChat: () => void;
}

const DocumentContext = createContext<DocumentContextType | undefined>(undefined);

// Mock document processing
const mockSummarize = (content: string): string => {
  const words = content.split(' ').slice(0, 50).join(' ');
  return `Summary: This document discusses ${words}... [This is a mock summary. In a real application, this would use an AI model to generate a comprehensive summary.]`;
};

const mockChatResponse = (question: string, document: Document): string => {
  const responses = [
    `Based on the document "${document.name}", here's what I found: ${question.toLowerCase().includes('what') ? 'The document contains information about various topics.' : 'That\'s an interesting question about the document.'}`,
    `According to the document, the key points are related to your question about "${question}". [This is a mock response. A real implementation would use an AI model to analyze the document and provide accurate answers.]`,
    `The document "${document.name}" provides insights on this topic. Let me elaborate based on the content...`,
  ];
  return responses[Math.floor(Math.random() * responses.length)];
};

export function DocumentProvider({ children }: { children: React.ReactNode }) {
  const [documents, setDocuments] = useState<Document[]>([
    {
      id: '1',
      name: 'Sample Document 1.pdf',
      size: 245000,
      uploadDate: new Date('2025-10-15'),
      content: 'This is a sample document content. It contains information about various topics including technology, business strategies, and market analysis.',
      summary: 'A comprehensive document covering technology trends and business strategies.'
    },
    {
      id: '2',
      name: 'Research Paper.docx',
      size: 512000,
      uploadDate: new Date('2025-10-17'),
      content: 'Research paper on artificial intelligence and machine learning applications in modern business environments.',
      summary: 'Research focusing on AI/ML applications in business.'
    },
  ]);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);

  const uploadDocument = async (file: File): Promise<void> => {
    // Mock file upload - in real app, this would upload to storage
    const content = await file.text().catch(() => 'Mock document content for ' + file.name);
    
    const newDoc: Document = {
      id: Date.now().toString(),
      name: file.name,
      size: file.size,
      uploadDate: new Date(),
      content: content,
    };

    setDocuments(prev => [...prev, newDoc]);
  };

  const deleteDocument = (id: string) => {
    setDocuments(prev => prev.filter(doc => doc.id !== id));
    setChatMessages(prev => prev.filter(msg => msg.documentId !== id));
  };

  const getDocument = (id: string): Document | undefined => {
    return documents.find(doc => doc.id === id);
  };

  const summarizeDocument = async (id: string): Promise<string> => {
    const doc = getDocument(id);
    if (!doc) throw new Error('Document not found');

    // Mock delay for API call
    await new Promise(resolve => setTimeout(resolve, 1500));

    const summary = mockSummarize(doc.content);
    
    // Update document with summary
    setDocuments(prev => 
      prev.map(d => d.id === id ? { ...d, summary } : d)
    );

    return summary;
  };

  const sendMessage = async (documentId: string, message: string): Promise<void> => {
    const doc = getDocument(documentId);
    if (!doc) throw new Error('Document not found');

    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      documentId,
      role: 'user',
      content: message,
      timestamp: new Date(),
    };
    setChatMessages(prev => [...prev, userMessage]);

    // Mock delay for API call
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Add assistant response
    const assistantMessage: ChatMessage = {
      id: (Date.now() + 1).toString(),
      documentId,
      role: 'assistant',
      content: mockChatResponse(message, doc),
      timestamp: new Date(),
    };
    setChatMessages(prev => [...prev, assistantMessage]);
  };

  const clearChat = () => {
    setChatMessages([]);
  };

  return (
    <DocumentContext.Provider
      value={{
        documents,
        uploadDocument,
        deleteDocument,
        getDocument,
        summarizeDocument,
        chatMessages,
        sendMessage,
        clearChat,
      }}
    >
      {children}
    </DocumentContext.Provider>
  );
}

export function useDocuments() {
  const context = useContext(DocumentContext);
  if (context === undefined) {
    throw new Error('useDocuments must be used within a DocumentProvider');
  }
  return context;
}

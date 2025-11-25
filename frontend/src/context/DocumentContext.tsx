import React, { createContext, useContext, useState, useEffect } from 'react';
import { 
  documentsAPI, 
  chatAPI, 
  summarizeAPI,
  Document as APIDocument,
  ChatMessage as APIChatMessage,
  Summary
} from '../services/api';

export interface Document {
  id: string;
  name: string;
  size: number;
  uploadDate: Date;
  content?: string;
  summary?: string;
  status?: 'processing' | 'processed' | 'failed';
  url?: string;
  mimeType?: string;
  pageCount?: number;
  wordCount?: number;
}

export interface ChatMessage {
  id: string;
  documentId: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  confidence?: number;
  sources?: Array<{
    pageNumber: number;
    excerpt: string;
    relevance: number;
  }>;
}

interface DocumentContextType {
  documents: Document[];
  uploadDocument: (file: File) => Promise<void>;
  deleteDocument: (id: string) => Promise<void>;
  getDocument: (id: string) => Document | undefined;
  summarizeDocument: (id: string) => Promise<string>;
  chatMessages: ChatMessage[];
  sendMessage: (documentId: string, message: string) => Promise<void>;
  clearChat: (documentId: string) => Promise<void>;
  loading: boolean;
  refreshDocuments: () => Promise<void>;
  clearAllData: () => void;
}

const DocumentContext = createContext<DocumentContextType | undefined>(undefined);

// Helper functions to convert API types to local types
const convertAPIDocument = (apiDoc: APIDocument): Document => {
  if (!apiDoc || !apiDoc.id) {
    console.error('Invalid API document:', apiDoc);
    throw new Error('Cannot convert invalid document - missing required fields');
  }
  
  return {
    id: apiDoc.id,
    name: apiDoc.name || apiDoc.originalName || apiDoc.filename|| 'Untitled Document',
    size: apiDoc.size || 0,
    uploadDate: new Date(apiDoc.uploadedAt || Date.now()),
    content: apiDoc.extractedText,
    summary: apiDoc.summary,
    status: apiDoc.status || 'processing',
    url: apiDoc.url,
    mimeType: apiDoc.mimeType,
    pageCount: apiDoc.pageCount,
    wordCount: apiDoc.wordCount,
  };
};

const convertAPIChatMessage = (apiMsg: APIChatMessage): ChatMessage => ({
  id: apiMsg.id,
  documentId: apiMsg.documentId,
  role: apiMsg.type === 'user' ? 'user' : 'assistant',
  content: apiMsg.content,
  timestamp: new Date(apiMsg.timestamp),
  confidence: apiMsg.confidence,
  sources: apiMsg.sources,
});

export function DocumentProvider({ children }: { children: React.ReactNode }) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [currentConversationId, setCurrentConversationId] = useState<string | undefined>();

  // Load documents on mount
  useEffect(() => {
    refreshDocuments();
  }, []);

  const refreshDocuments = async (): Promise<void> => {
    try {
      setLoading(true);
      const response = await documentsAPI.getDocuments({ limit: 100 });
      // Ensure response.documents is an array
      if (response && Array.isArray(response.documents)) {
        setDocuments(response.documents.map(convertAPIDocument));
      } else {
        console.error('Invalid documents response:', response);
        setDocuments([]);
      }
    } catch (error) {
      console.error('Failed to fetch documents:', error);
      setDocuments([]);
    } finally {
      setLoading(false);
    }
  };

  const uploadDocument = async (file: File): Promise<void> => {
    try {
      setLoading(true);
      const response = await documentsAPI.uploadDocument(file);
      setDocuments(prev => [...prev, convertAPIDocument(response?.document)]);
    } catch (error) {
      console.error('Failed to upload document:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const deleteDocument = async (id: string): Promise<void> => {
    try {
      await documentsAPI.deleteDocument(id);
      setDocuments(prev => prev.filter(doc => doc.id !== id));
      setChatMessages(prev => prev.filter(msg => msg.documentId !== id));
    } catch (error) {
      console.error('Failed to delete document:', error);
      throw error;
    }
  };

  const getDocument = (id: string): Document | undefined => {
    return documents.find(doc => doc.id === id);
  };

  const summarizeDocument = async (id: string): Promise<string> => {
    try {
      const response = await summarizeAPI.summarizeDocument(id, {
        length: 'medium',
        style: 'executive',
      });

      const summary = response.summary.content;
      
      // Update document with summary
      setDocuments(prev => 
        prev.map(d => d.id === id ? { ...d, summary } : d)
      );

      return summary;
    } catch (error) {
      console.error('Failed to summarize document:', error);
      throw error;
    }
  };

  const sendMessage = async (documentId: string, message: string): Promise<void> => {
    try {
      // Add user message immediately
      const tempUserMessage: ChatMessage = {
        id: `temp-${Date.now()}`,
        documentId,
        role: 'user',
        content: message,
        timestamp: new Date(),
      };
      setChatMessages(prev => [...prev, tempUserMessage]);

      // Send query to API
      const response = await chatAPI.sendQuery(
        documentId,
        message,
        currentConversationId
      );

      // Update conversation ID if it's a new conversation
      if (response.response.conversationId && !currentConversationId) {
        setCurrentConversationId(response.response.conversationId);
      }

      // Replace temp message with real one and add assistant response
      setChatMessages(prev => {
        const withoutTemp = prev.filter(m => m.id !== tempUserMessage.id);
        
        // Create user message from query
        const userMsg: ChatMessage = {
          id: `user-${response.response.id}`,
          documentId,
          role: 'user',
          content: message,
          timestamp: new Date(),
        };

        // Create assistant message from response
        const assistantMsg: ChatMessage = {
          id: response.response.id,
          documentId: response.response.documentId,
          role: 'assistant',
          content: response.response.content,
          timestamp: new Date(response.response.timestamp),
          confidence: response.response.confidence,
          sources: response.response.sources,
        };

        return [...withoutTemp, userMsg, assistantMsg];
      });
    } catch (error) {
      console.error('Failed to send message:', error);
      // Remove temp message on error
      setChatMessages(prev => prev.filter(m => !m.id.startsWith('temp-')));
      throw error;
    }
  };

  const clearChat = async (documentId: string): Promise<void> => {
    try {
      await chatAPI.clearChatHistory(documentId, currentConversationId);
      setChatMessages(prev => prev.filter(msg => msg.documentId !== documentId));
      setCurrentConversationId(undefined);
    } catch (error) {
      console.error('Failed to clear chat:', error);
      throw error;
    }
  };

  const clearAllData = () => {
    setDocuments([]);
    setChatMessages([]);
    setCurrentConversationId(undefined);
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
        loading,
        refreshDocuments,
        clearAllData,
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

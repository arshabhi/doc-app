// API Service Layer for Backend Communication
// Base URL: In development, uses Vite proxy to avoid CORS issues
// In production, this should be configured via environment variables

import { config } from '../config/environment';

// Use /api in development (Vite proxy) or the configured API base URL
const API_BASE_URL = typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_BASE_URL 
  ? import.meta.env.VITE_API_BASE_URL 
  : '/api';

// Token Management
class TokenManager {
  private static ACCESS_TOKEN_KEY = 'access_token';
  private static REFRESH_TOKEN_KEY = 'refresh_token';

  static getAccessToken(): string | null {
    return localStorage.getItem(this.ACCESS_TOKEN_KEY);
  }

  static getRefreshToken(): string | null {
    return localStorage.getItem(this.REFRESH_TOKEN_KEY);
  }

  static setTokens(accessToken: string, refreshToken: string): void {
    localStorage.setItem(this.ACCESS_TOKEN_KEY, accessToken);
    localStorage.setItem(this.REFRESH_TOKEN_KEY, refreshToken);
  }

  static clearTokens(): void {
    localStorage.removeItem(this.ACCESS_TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_TOKEN_KEY);
  }
}

// API Error Class
export class APIError extends Error {
  constructor(
    public code: string,
    message: string,
    public status?: number
  ) {
    super(message);
    this.name = 'APIError';
  }
}

// Base API Client
class APIClient {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = TokenManager.getAccessToken();
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
      });

      // Handle 401 - Try to refresh token
      if (response.status === 401 && token) {
        const refreshed = await this.refreshAccessToken();
        if (refreshed) {
          // Retry the original request
          const retryHeaders = { ...headers };
          retryHeaders['Authorization'] = `Bearer ${TokenManager.getAccessToken()}`;
          const retryResponse = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers: retryHeaders,
          });
          return this.handleResponse<T>(retryResponse);
        }
      }

      return this.handleResponse<T>(response);
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      
      // Better error diagnostics
      console.error('Network Error Details:', {
        endpoint: `${API_BASE_URL}${endpoint}`,
        error: error instanceof Error ? error.message : 'Unknown error',
        originalError: error
      });
      
      throw new APIError(
        'NETWORK_ERROR', 
        `Failed to connect to the server. Please ensure the backend is running on port 8000. Error: ${error instanceof Error ? error.message : 'Unknown error'}`
      );
    }
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    const contentType = response.headers.get('content-type');
    
    // Handle file downloads
    if (contentType && !contentType.includes('application/json')) {
      return response as any;
    }

    let data;
    try {
      data = await response.json();
    } catch (e) {
      throw new APIError(
        'PARSE_ERROR',
        'Failed to parse server response',
        response.status
      );
    }

    if (!response.ok) {
      const error = data.error || data;
      throw new APIError(
        error.code || 'UNKNOWN_ERROR',
        error.message || error.detail || 'An error occurred',
        response.status
      );
    }

    console.log('Raw API response:', data);
    
    // Handle both wrapped ({success: true, data: {...}}) and direct responses
    const result = (data.data !== undefined ? data.data : data) as T;
    console.log('Unwrapped result:', result);
    return result;
  }

  private async refreshAccessToken(): Promise<boolean> {
    const refreshToken = TokenManager.getRefreshToken();
    if (!refreshToken) return false;

    try {
      const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refreshToken }),
      });

      const data = await response.json();
      if (data.success && data.data.accessToken) {
        const currentRefreshToken = TokenManager.getRefreshToken()!;
        TokenManager.setTokens(data.data.accessToken, currentRefreshToken);
        return true;
      }
    } catch (error) {
      console.error('Failed to refresh token:', error);
    }

    TokenManager.clearTokens();
    return false;
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }

  async uploadFile<T>(endpoint: string, formData: FormData): Promise<T> {
    const token = TokenManager.getAccessToken();
    const headers: HeadersInit = {};
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers,
        body: formData,
      });

      const result = await this.handleResponse<T>(response);
      console.log('Upload file response after handling:', result);
      return result;
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      
      console.error('File Upload Error:', error);
      throw new APIError(
        'NETWORK_ERROR', 
        `Failed to upload file. Error: ${error instanceof Error ? error.message : 'Unknown error'}`
      );
    }
  }
}

const client = new APIClient();

// Type Definitions
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user';
  avatar?: string;
  createdAt: string;
  updatedAt?: string;
  lastLogin?: string;
  preferences?: {
    theme?: string;
    language?: string;
    notifications?: boolean;
  };
  stats?: {
    totalDocuments: number;
    totalChats: number;
    storageUsed: number;
  };
}

export interface AuthResponse {
  user: User;
  tokens: {
    accessToken: string;
    refreshToken: string;
    expiresIn: number;
  };
}

export interface Document {
  id: string;
  name: string;
  originalName: string;
  filename?: string;
  size: number;
  mimeType: string;
  url: string;
  thumbnailUrl?: string;
  userId: string;
  status: 'processing' | 'processed' | 'failed';
  pageCount?: number;
  wordCount?: number;
  uploadedAt: string;
  processedAt?: string;
  tags?: string[];
  metadata?: Record<string, any>;
  extractedText?: string;
  summary?: string;
}

export interface ChatMessage {
  id: string;
  conversationId: string;
  documentId: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: string;
  confidence?: number;
  sources?: Array<{
    pageNumber: number;
    excerpt: string;
    relevance: number;
  }>;
}

export interface Comparison {
  id: string;
  documentId1: string;
  documentId2: string;
  document1Name: string;
  document2Name: string;
  comparisonType: string;
  status: 'processing' | 'completed' | 'failed';
  createdAt: string;
  completedAt?: string;
  summary?: {
    totalChanges: number;
    additions: number;
    deletions: number;
    modifications: number;
    similarityScore: number;
    changesPercentage: number;
  };
  changes?: any[];
  diffUrl?: string;
  sideBySideUrl?: string;
}

export interface Summary {
  id: string;
  documentId: string;
  documentName: string;
  style: string;
  length: string;
  content: string;
  keyPoints?: string[];
  wordCount: number;
  readingTime: string;
  confidence: number;
  createdAt: string;
}

export interface Analytics {
  period: string;
  startDate: string;
  endDate: string;
  users: {
    total: number;
    active: number;
    new: number;
    growth: number;
  };
  documents: {
    total: number;
    uploaded: number;
    totalStorage: number;
  };
  chats: {
    total: number;
    thisMonth: number;
  };
  comparisons: {
    total: number;
    thisMonth: number;
  };
  summaries: {
    total: number;
    thisMonth: number;
  };
}

// Authentication API
export const authAPI = {
  async login(email: string, password: string): Promise<AuthResponse> {
    const response = await client.post<AuthResponse>('/auth/login', {
      email,
      password,
    });
    
    // Validate response structure
    if (!response || !response.tokens || !response.tokens.accessToken) {
      console.error('Invalid auth response structure:', response);
      throw new APIError('INVALID_RESPONSE', 'Invalid authentication response from server');
    }
    
    TokenManager.setTokens(
      response.tokens.accessToken,
      response.tokens.refreshToken
    );
    return response;
  },

  async register(
    email: string,
    password: string,
    name: string,
    confirmPassword: string
  ): Promise<AuthResponse> {
    const response = await client.post<AuthResponse>('/auth/register', {
      email,
      password,
      name,
      confirmPassword,
    });
    
    // Validate response structure
    if (!response || !response.tokens || !response.tokens.accessToken) {
      console.error('Invalid auth response structure:', response);
      throw new APIError('INVALID_RESPONSE', 'Invalid authentication response from server');
    }
    
    TokenManager.setTokens(
      response.tokens.accessToken,
      response.tokens.refreshToken
    );
    return response;
  },

  async logout(): Promise<void> {
    const refreshToken = TokenManager.getRefreshToken();
    try {
      await client.post('/auth/logout', { refreshToken });
    } finally {
      TokenManager.clearTokens();
    }
  },

  async getCurrentUser(): Promise<{ user: User }> {
    return client.get('/auth/me');
  },

  getAccessToken(): string | null {
    return TokenManager.getAccessToken();
  },

  isAuthenticated(): boolean {
    return !!TokenManager.getAccessToken();
  },
};

// Documents API
export const documentsAPI = {
  async getDocuments(params?: {
    page?: number;
    limit?: number;
    search?: string;
  }): Promise<{
    data: Document[]; documents: Document[]; pagination: any 
}> {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.search) queryParams.append('search', params.search);

    const query = queryParams.toString();
    return client.get(`/documents/list${query ? `?${query}` : ''}`);
  },

  async getDocument(id: string): Promise<{ document: Document }> {
    return client.get(`/documents/${id}`);
  },

  async uploadDocument(
    file: File,
    tags?: string[],
    metadata?: Record<string, any>
  ): Promise<{ document: Document }> {
    const formData = new FormData();
    formData.append('file', file);
    if (tags) {
      formData.append('tags', JSON.stringify(tags));
    }
    if (metadata) {
      formData.append('metadata', JSON.stringify(metadata));
    }

    return client.uploadFile('/documents/upload', formData);
  },

  async updateDocument(
    id: string,
    data: {
      name?: string;
      tags?: string[];
      metadata?: Record<string, any>;
    }
  ): Promise<{ document: Document }> {
    return client.put(`/documents/${id}`, data);
  },

  async deleteDocument(id: string): Promise<{ message: string; documentId: string }> {
    return client.delete(`/documents/${id}`);
  },

  async downloadDocument(id: string): Promise<{ success: boolean; downloadUrl: string; filename: string }> {
    const token = TokenManager.getAccessToken();
    const response = await fetch(`${API_BASE_URL}/documents/${id}/download`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    
    if (!response.ok) {
      throw new APIError('DOWNLOAD_FAILED', 'Failed to download document');
    }
    
    const data = await response.json();
    return data;
  },
};

// Chat API
export const chatAPI = {
  async sendQuery(
    document_id: string,
    message: string,
    conversationId?: string
  ): Promise<{ response: ChatMessage }> {
    return client.post('/chat/query', {
      document_id,
      message,
      conversationId,
    });
  },

  async getChatHistory(
    documentId: string,
    params?: {
      conversationId?: string;
      limit?: number;
    }
  ): Promise<{ history: ChatMessage[]; metadata: any }> {
    const queryParams = new URLSearchParams();
    if (params?.conversationId) queryParams.append('conversationId', params.conversationId);
    if (params?.limit) queryParams.append('limit', params.limit.toString());

    const query = queryParams.toString();
    return client.get(`/chat/history/${documentId}${query ? `?${query}` : ''}`);
  },

  async clearChatHistory(
    documentId: string,
    conversationId?: string
  ): Promise<{ message: string; deletedMessages: number }> {
    const queryParams = new URLSearchParams();
    if (conversationId) queryParams.append('conversationId', conversationId);

    const query = queryParams.toString();
    return client.delete(`/chat/history/${documentId}${query ? `?${query}` : ''}`);
  },

  async getConversations(params?: {
    page?: number;
    limit?: number;
  }): Promise<{ conversations: any[]; pagination: any }> {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());

    const query = queryParams.toString();
    return client.get(`/chat/conversations${query ? `?${query}` : ''}`);
  },
};

// Compare API
export const compareAPI = {
  async compareDocuments(
    documentId1: string,
    documentId2: string,
    options?: {
      comparisonType?: 'full' | 'structure' | 'content' | 'metadata';
      ignoreFormatting?: boolean;
      caseSensitive?: boolean;
      highlightChanges?: boolean;
    }
  ): Promise<{ comparison: Comparison }> {
    return client.post('/compare', {
      documentId1,
      documentId2,
      comparisonType: options?.comparisonType || 'full',
      options,
    });
  },

  async getComparison(id: string): Promise<{ comparison: Comparison }> {
    return client.get(`/compare/${id}`);
  },

  async getComparisonHistory(params?: {
    page?: number;
    limit?: number;
    documentId?: string;
  }): Promise<{ comparisons: Comparison[]; pagination: any }> {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.documentId) queryParams.append('documentId', params.documentId);

    const query = queryParams.toString();
    return client.get(`/compare/history${query ? `?${query}` : ''}`);
  },

  async deleteComparison(id: string): Promise<{ message: string }> {
    return client.delete(`/compare/${id}`);
  },
};

// Summarize API
export const summarizeAPI = {
  async summarizeDocument(
    documentId: string,
    options?: {
      length?: 'short' | 'medium' | 'long';
      style?: 'executive' | 'technical' | 'simple' | 'bullet-points';
      focusAreas?: string[];
      language?: string;
    }
  ): Promise<{ summary: Summary }> {
    return client.post('/summarize', {
      documentId,
      options: options || { length: 'medium', style: 'executive' },
    });
  },

  async getDocumentSummaries(
    documentId: string,
    params?: {
      summaryId?: string;
      style?: string;
    }
  ): Promise<{ summaries: Summary[] }> {
    const queryParams = new URLSearchParams();
    if (params?.summaryId) queryParams.append('summaryId', params.summaryId);
    if (params?.style) queryParams.append('style', params.style);

    const query = queryParams.toString();
    return client.get(`/summarize/${documentId}${query ? `?${query}` : ''}`);
  },

  async getSummary(summaryId: string): Promise<{ summary: Summary }> {
    return client.get(`/summarize/summary/${summaryId}`);
  },

  async deleteSummary(summaryId: string): Promise<{ message: string }> {
    return client.delete(`/summarize/${summaryId}`);
  },
};

// Admin API
export const adminAPI = {
  async getUsers(params?: {
    page?: number;
    limit?: number;
    search?: string;
    role?: 'user' | 'admin';
    status?: 'active' | 'inactive';
  }): Promise<{ users: User[]; pagination: any; summary: any }> {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.search) queryParams.append('search', params.search);
    if (params?.role) queryParams.append('role', params.role);
    if (params?.status) queryParams.append('status', params.status);

    const query = queryParams.toString();
    return client.get(`/admin/users${query ? `?${query}` : ''}`);
  },

  async getUser(id: string): Promise<{ user: User }> {
    return client.get(`/admin/users/${id}`);
  },

  async updateUser(
    id: string,
    data: {
      name?: string;
      email?: string;
      role?: 'admin' | 'user';
      status?: 'active' | 'inactive';
      storageLimit?: number;
    }
  ): Promise<{ user: User }> {
    return client.put(`/admin/users/${id}`, data);
  },

  async deleteUser(id: string): Promise<{ message: string; deletedResources: any }> {
    return client.delete(`/admin/users/${id}`);
  },

  async getAnalytics(params?: {
    period?: 'today' | 'week' | 'month' | 'year' | 'all';
    startDate?: string;
    endDate?: string;
  }): Promise<{ analytics: Analytics }> {
    const queryParams = new URLSearchParams();
    if (params?.period) queryParams.append('period', params.period);
    if (params?.startDate) queryParams.append('startDate', params.startDate);
    if (params?.endDate) queryParams.append('endDate', params.endDate);

    const query = queryParams.toString();
    return client.get(`/admin/analytics${query ? `?${query}` : ''}`);
  },

  async getAllDocuments(params?: {
    page?: number;
    limit?: number;
    userId?: string;
    status?: string;
    search?: string;
  }): Promise<{ documents: Document[]; pagination: any; summary: any }> {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.userId) queryParams.append('userId', params.userId);
    if (params?.status) queryParams.append('status', params.status);
    if (params?.search) queryParams.append('search', params.search);

    const query = queryParams.toString();
    return client.get(`/admin/documents${query ? `?${query}` : ''}`);
  },

  async getActivity(params?: {
    limit?: number;
    type?: string;
  }): Promise<{ activities: any[]; pagination: any }> {
    const queryParams = new URLSearchParams();
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.type) queryParams.append('type', params.type);

    const query = queryParams.toString();
    return client.get(`/admin/activity${query ? `?${query}` : ''}`);
  },

  async sendBroadcast(data: {
    title: string;
    message: string;
    recipients: 'all' | 'active' | 'inactive' | string[];
    type: 'info' | 'warning' | 'alert';
    expiresAt?: string;
  }): Promise<{ broadcastId: string; recipientCount: number }> {
    return client.post('/admin/broadcast', data);
  },
};

export { TokenManager };

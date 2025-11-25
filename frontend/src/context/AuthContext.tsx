import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authAPI, User as APIUser } from '../services/api';

interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user';
  avatar?: string;
  stats?: {
    totalDocuments: number;
    totalChats: number;
    storageUsed: number;
  };
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<boolean>;
  register: (email: string, password: string, name: string, confirmPassword: string) => Promise<boolean>;
  logout: () => void;
  isAdmin: boolean;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is authenticated on mount
    const initAuth = async () => {
      try {
        if (authAPI.isAuthenticated()) {
          const response = await authAPI.getCurrentUser();
          setUser(response.user as User);
        }
      } catch (error) {
        console.error('Failed to fetch current user:', error);
        // Clear invalid tokens
        await authAPI.logout();
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      const response = await authAPI.login(email, password);
      if (response && response.user) {
        setUser(response.user as User);
        return true;
      } else {
        console.error('Invalid login response:', response);
        return false;
      }
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    }
  };

  const register = async (
    email: string,
    password: string,
    name: string,
    confirmPassword: string
  ): Promise<boolean> => {
    try {
      const response = await authAPI.register(email, password, name, confirmPassword);
      if (response && response.user) {
        setUser(response.user as User);
        return true;
      } else {
        console.error('Invalid registration response:', response);
        throw new Error('Invalid response from registration');
      }
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  };

  const logout = useCallback(async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      // Force a full page reload to clear all state
      window.location.href = '/';
    }
  }, []);

  const isAdmin = user?.role === 'admin';

  return (
    <AuthContext.Provider value={{ user, login, register, logout, isAdmin, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

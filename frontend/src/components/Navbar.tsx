import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Button } from './ui/button';
import { FileText, LogOut, User, Shield } from 'lucide-react';
import { Badge } from './ui/badge';

interface NavbarProps {
  currentView: 'documents' | 'admin';
  onViewChange: (view: 'documents' | 'admin') => void;
}

export function Navbar({ currentView, onViewChange }: NavbarProps) {
  const { user, logout, isAdmin } = useAuth();

  return (
    <nav className="border-b bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center space-x-8">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-indigo-600 rounded flex items-center justify-center">
                <FileText className="w-5 h-5 text-white" />
              </div>
              <span>DocuManager</span>
            </div>

            <div className="flex space-x-4">
              <Button
                variant={currentView === 'documents' ? 'default' : 'ghost'}
                onClick={() => onViewChange('documents')}
              >
                Documents
              </Button>
              {isAdmin && (
                <Button
                  variant={currentView === 'admin' ? 'default' : 'ghost'}
                  onClick={() => onViewChange('admin')}
                >
                  <Shield className="w-4 h-4 mr-2" />
                  Admin Dashboard
                </Button>
              )}
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <User className="w-4 h-4 text-gray-500" />
              <span className="text-sm">{user?.name}</span>
              {isAdmin && <Badge variant="secondary">Admin</Badge>}
            </div>
            <Button variant="outline" size="sm" onClick={logout}>
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
}

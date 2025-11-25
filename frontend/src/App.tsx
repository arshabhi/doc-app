import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { DocumentProvider, useDocuments } from './context/DocumentContext';
import { Login } from './components/Login';
import { Register } from './components/Register';
import { Navbar } from './components/Navbar';
import { Dashboard } from './components/Dashboard';
import { AdminDashboard } from './components/AdminDashboard';
import { Toaster } from './components/ui/sonner';
import { Loader2 } from 'lucide-react';

function AppContent() {
  const { user, isAdmin, loading } = useAuth();
  const { refreshDocuments, clearAllData } = useDocuments();
  const [currentView, setCurrentView] = useState<'documents' | 'admin'>('documents');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  const [previousUserId, setPreviousUserId] = useState<string | null>(null);

  useEffect(() => {
    const wasLoggedIn = isLoggedIn;
    const nowLoggedIn = !!user;
    setIsLoggedIn(nowLoggedIn);

    // If user changed (different user ID), refresh documents
    if (nowLoggedIn && user && user.id !== previousUserId) {
      setPreviousUserId(user.id);
      clearAllData();
      refreshDocuments();
    } else if (!nowLoggedIn && wasLoggedIn) {
      // User logged out, clear data
      clearAllData();
      setPreviousUserId(null);
    }
  }, [user, isLoggedIn, previousUserId, refreshDocuments, clearAllData]);

  const handleLoginSuccess = async () => {
    setIsLoggedIn(true);
    setShowRegister(false);
    // Documents will be refreshed by the useEffect watching user changes
  };

  const handleRegisterSuccess = async () => {
    setIsLoggedIn(true);
    setShowRegister(false);
    // Documents will be refreshed by the useEffect watching user changes
  };

  const handleRegisterClick = () => {
    setShowRegister(true);
  };

  const handleBackToLogin = () => {
    setShowRegister(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  if (!isLoggedIn) {
    if (showRegister) {
      return (
        <Register
          onRegisterSuccess={handleRegisterSuccess}
          onBackToLogin={handleBackToLogin}
        />
      );
    }
    return (
      <Login
        onLoginSuccess={handleLoginSuccess}
        onRegisterClick={handleRegisterClick}
      />
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar currentView={currentView} onViewChange={setCurrentView} />
      {currentView === 'documents' ? <Dashboard /> : <AdminDashboard />}
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <DocumentProvider>
        <AppContent />
        <Toaster />
      </DocumentProvider>
    </AuthProvider>
  );
}

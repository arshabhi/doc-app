import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { DocumentProvider } from './context/DocumentContext';
import { Login } from './components/Login';
import { Navbar } from './components/Navbar';
import { Dashboard } from './components/Dashboard';
import { AdminDashboard } from './components/AdminDashboard';
import { Toaster } from './components/ui/sonner';

function AppContent() {
  const { user, isAdmin } = useAuth();
  const [currentView, setCurrentView] = useState<'documents' | 'admin'>('documents');
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    setIsLoggedIn(!!user);
  }, [user]);

  const handleLoginSuccess = () => {
    setIsLoggedIn(true);
  };

  if (!isLoggedIn) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
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

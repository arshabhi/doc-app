import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/globals.css';
import { logBackendDiagnostics } from './services/healthCheck';

// Run backend health check in development
if (import.meta.env.DEV) {
  logBackendDiagnostics();
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

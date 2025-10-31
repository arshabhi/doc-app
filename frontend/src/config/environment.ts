/**
 * Environment Configuration
 * 
 * This file centralizes all environment-specific configuration.
 * It reads from environment variables and provides defaults.
 */

interface EnvironmentConfig {
  // API Configuration
  apiBaseUrl: string;
  
  // Application Configuration
  appName: string;
  appVersion: string;
  
  // Feature Flags
  enableDebugMode: boolean;
  enableAnalytics: boolean;
  
  // File Upload Limits
  maxFileSize: number; // in bytes
  allowedFileTypes: string[];
  
  // Session Configuration
  tokenRefreshInterval: number; // in milliseconds
}

const getEnvironmentConfig = (): EnvironmentConfig => {
  return {
    // API Base URL - can be overridden with VITE_API_BASE_URL environment variable
    apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
    
    // Application Info
    appName: import.meta.env.VITE_APP_NAME || 'Document Management System',
    appVersion: import.meta.env.VITE_APP_VERSION || '1.0.0',
    
    // Feature Flags
    enableDebugMode: import.meta.env.VITE_ENABLE_DEBUG === 'true' || import.meta.env.DEV,
    enableAnalytics: import.meta.env.VITE_ENABLE_ANALYTICS === 'true',
    
    // File Upload Configuration
    maxFileSize: Number(import.meta.env.VITE_MAX_FILE_SIZE) || 10 * 1024 * 1024, // 10MB default
    allowedFileTypes: import.meta.env.VITE_ALLOWED_FILE_TYPES?.split(',') || [
      '.pdf',
      '.doc',
      '.docx',
      '.txt',
      '.xlsx',
      '.xls',
    ],
    
    // Session Configuration
    tokenRefreshInterval: Number(import.meta.env.VITE_TOKEN_REFRESH_INTERVAL) || 5 * 60 * 1000, // 5 minutes
  };
};

export const config = getEnvironmentConfig();

// Validate required configuration
export const validateConfig = (): boolean => {
  const errors: string[] = [];
  
  if (!config.apiBaseUrl) {
    errors.push('API_BASE_URL is not configured');
  }
  
  if (errors.length > 0) {
    console.error('Configuration Errors:', errors);
    return false;
  }
  
  return true;
};

// Debug helper
export const logConfig = (): void => {
  if (config.enableDebugMode) {
    console.group('🔧 Environment Configuration');
    console.log('API Base URL:', config.apiBaseUrl);
    console.log('App Name:', config.appName);
    console.log('App Version:', config.appVersion);
    console.log('Debug Mode:', config.enableDebugMode);
    console.log('Max File Size:', config.maxFileSize, 'bytes');
    console.log('Allowed File Types:', config.allowedFileTypes);
    console.groupEnd();
  }
};

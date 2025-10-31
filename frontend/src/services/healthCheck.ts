/**
 * Backend Health Check Utility
 * 
 * This utility helps diagnose connection issues with the backend API
 */

const BACKEND_URL = 'http://localhost:8000';

export interface HealthCheckResult {
  healthy: boolean;
  message: string;
  details?: {
    apiReachable: boolean;
    responseTime?: number;
    error?: string;
  };
}

/**
 * Check if the backend API is reachable and healthy
 */
export const checkBackendHealth = async (): Promise<HealthCheckResult> => {
  const startTime = Date.now();
  
  try {
    // Try to reach the backend health endpoint
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
    
    const response = await fetch(`${BACKEND_URL}/health`, {
      method: 'GET',
      signal: controller.signal,
    });
    
    clearTimeout(timeoutId);
    const responseTime = Date.now() - startTime;
    
    if (response.ok) {
      return {
        healthy: true,
        message: 'Backend is healthy',
        details: {
          apiReachable: true,
          responseTime,
        },
      };
    } else {
      return {
        healthy: false,
        message: `Backend returned status ${response.status}`,
        details: {
          apiReachable: true,
          responseTime,
          error: `HTTP ${response.status}`,
        },
      };
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    
    return {
      healthy: false,
      message: 'Cannot connect to backend',
      details: {
        apiReachable: false,
        error: errorMessage,
      },
    };
  }
};

/**
 * Log backend connection diagnostics to console
 */
export const logBackendDiagnostics = async (): Promise<void> => {
  console.group('🔍 Backend Connection Diagnostics');
  console.log('Backend URL:', BACKEND_URL);
  console.log('Checking health...');
  
  const result = await checkBackendHealth();
  
  if (result.healthy) {
    console.log('✅ Backend is healthy');
    console.log(`Response time: ${result.details?.responseTime}ms`);
  } else {
    console.error('❌ Backend is not healthy');
    console.error('Message:', result.message);
    if (result.details?.error) {
      console.error('Error:', result.details.error);
    }
    console.log('\n📋 Troubleshooting steps:');
    console.log('1. Ensure the backend server is running: python main.py');
    console.log('2. Check if port 8000 is accessible: curl http://localhost:8000/health');
    console.log('3. Verify PostgreSQL is running on port 5432');
    console.log('4. Check backend logs for any errors');
  }
  
  console.groupEnd();
};

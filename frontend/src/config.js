// Dynamic configuration for different environments
export const getBackendURL = () => {
  // Defensive check for environment variables
  let envBackendURL = '';
  
  try {
    if (typeof process !== 'undefined' && process.env && process.env.REACT_APP_BACKEND_URL) {
      envBackendURL = process.env.REACT_APP_BACKEND_URL;
    } else if (typeof import !== 'undefined' && import.meta && import.meta.env && import.meta.env.REACT_APP_BACKEND_URL) {
      envBackendURL = import.meta.env.REACT_APP_BACKEND_URL;
    }
  } catch (error) {
    console.warn('Environment variable access error:', error);
  }
  
  if (envBackendURL && envBackendURL.trim() !== '') {
    return envBackendURL;
  }
  
  // For all environments, use empty string to rely on proxy configuration
  return '';
};

// Don't call the function at module level - let components call it when needed
export const API_BASE_URL = '';
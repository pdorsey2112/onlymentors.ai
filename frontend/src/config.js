// Dynamic configuration for different environments
export const getBackendURL = () => {
  // Defensive check for environment variables
  const processEnv = (typeof process !== 'undefined' && process.env) ? process.env.REACT_APP_BACKEND_URL : undefined;
  const importMetaEnv = (typeof import !== 'undefined' && import.meta && import.meta.env) ? import.meta.env.REACT_APP_BACKEND_URL : undefined;
  
  const envBackendURL = processEnv || importMetaEnv;
  
  if (envBackendURL && envBackendURL.trim() !== '') {
    return envBackendURL;
  }
  
  // For all environments, use empty string to rely on proxy configuration
  return '';
};

// Don't call the function at module level - let components call it when needed
export const API_BASE_URL = '';
// Dynamic configuration for different environments
export const getBackendURL = () => {
  // Check if REACT_APP_BACKEND_URL is explicitly set
  const envBackendURL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
  
  if (envBackendURL && envBackendURL.trim() !== '') {
    return envBackendURL;
  }
  
  // For all environments, use empty string to rely on proxy configuration
  return '';
};

export const API_BASE_URL = getBackendURL();
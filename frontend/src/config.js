// Dynamic configuration for different environments
export const getBackendURL = () => {
  // Check if REACT_APP_BACKEND_URL is explicitly set
  const envBackendURL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
  
  if (envBackendURL && envBackendURL.trim() !== '') {
    return envBackendURL;
  }
  
  // Determine backend URL based on current host
  const currentHost = window.location.host;
  
  if (currentHost.includes('localhost') || currentHost.includes('127.0.0.1')) {
    // Local development - use proxy (empty string means same origin with proxy)
    return '';
  } else {
    // Preview/production environment - use same origin (Kubernetes ingress handles /api routing)
    return '';
  }
};

export const API_BASE_URL = getBackendURL();
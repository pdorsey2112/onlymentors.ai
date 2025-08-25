// Dynamic configuration for different environments
export const getBackendURL = () => {
  // Return the configured backend URL from environment variable
  return process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
};

export const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
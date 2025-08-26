// OnlyMentors.ai Admin Console Configuration
// Updated: January 26, 2025 - Fresh deployment for testing
export const getBackendURL = () => {
  // Return the configured backend URL from environment variable
  return process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
};

export const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
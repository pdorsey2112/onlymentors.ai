import React, { useState, useEffect } from 'react';
import { GoogleLogin, GoogleOAuthProvider } from '@react-oauth/google';

const GoogleOAuthButton = ({ onSuccess, onError, disabled = false, text = "Sign in with Google" }) => {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [configError, setConfigError] = useState(null);

  useEffect(() => {
    // Fetch Google OAuth config from backend
    const fetchConfig = async () => {
      try {
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/auth/google/config`);
        if (response.ok) {
          const configData = await response.json();
          setConfig(configData);
        } else {
          const error = await response.json();
          setConfigError(error.detail || 'Google OAuth not configured');
        }
      } catch (error) {
        console.error('Failed to fetch Google OAuth config:', error);
        setConfigError('Failed to load Google OAuth configuration');
      } finally {
        setLoading(false);
      }
    };

    fetchConfig();
  }, []);

  const handleSuccess = async (credentialResponse) => {
    try {
      setLoading(true);

      console.log('Google OAuth Response:', credentialResponse);

      // Prepare the request body based on what Google provides
      const requestBody = {
        provider: 'google'
      };

      // Handle different Google OAuth response types
      if (credentialResponse.credential) {
        // ID token flow (most common with new Google OAuth)
        requestBody.id_token = credentialResponse.credential;
      } else if (credentialResponse.code) {
        // Authorization code flow
        requestBody.code = credentialResponse.code;
      } else {
        throw new Error('No valid credential or code received from Google');
      }

      console.log('Sending to backend:', requestBody);

      // Send the credential to our backend
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/auth/google`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      if (response.ok) {
        const authData = await response.json();
        console.log('Backend response:', authData);
        onSuccess(authData);
      } else {
        const error = await response.json();
        console.error('Backend error:', error);
        onError(error.detail || 'Google authentication failed');
      }
    } catch (error) {
      console.error('Google OAuth error:', error);
      onError('Google authentication failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleError = (error) => {
    console.error('Google OAuth error:', error);
    onError('Google authentication failed');
  };

  if (loading && !config) {
    return (
      <div className="flex items-center justify-center p-3 border border-gray-300 rounded-lg bg-gray-50">
        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 mr-2"></div>
        <span className="text-gray-600">Loading Google Sign-In...</span>
      </div>
    );
  }

  if (configError) {
    return (
      <div className="p-3 border border-red-300 rounded-lg bg-red-50">
        <span className="text-red-600 text-sm">{configError}</span>
      </div>
    );
  }

  if (!config) {
    return null;
  }

  return (
    <GoogleOAuthProvider clientId={config.client_id}>
      <div className="w-full">
        <GoogleLogin
          onSuccess={handleSuccess}
          onError={handleError}
          disabled={disabled || loading}
          text={text}
          theme="outline"
          size="large"
          shape="rectangular"
          width="100%"
          logo_alignment="left"
          useOneTap={false}
          auto_select={false}
        />
        {loading && (
          <div className="absolute inset-0 bg-white bg-opacity-70 flex items-center justify-center rounded-lg">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
          </div>
        )}
      </div>
    </GoogleOAuthProvider>
  );
};

export default GoogleOAuthButton;
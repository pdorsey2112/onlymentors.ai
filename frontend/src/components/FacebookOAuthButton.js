import React, { useState, useEffect } from 'react';

const FacebookOAuthButton = ({ onSuccess, onError, disabled = false, text = "Continue with Facebook" }) => {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [configError, setConfigError] = useState(null);
  const [fbLoaded, setFbLoaded] = useState(false);

  useEffect(() => {
    // Load Facebook SDK
    const loadFacebookSDK = () => {
      return new Promise((resolve, reject) => {
        // Check if FB is already loaded
        if (window.FB) {
          setFbLoaded(true);
          resolve(window.FB);
          return;
        }

        // Load Facebook SDK script
        const script = document.createElement('script');
        script.src = 'https://connect.facebook.net/en_US/sdk.js';
        script.async = true;
        script.defer = true;
        script.crossOrigin = 'anonymous';
        
        script.onload = () => {
          // Set up fbAsyncInit function
          window.fbAsyncInit = () => {
            try {
              if (config && config.app_id) {
                window.FB.init({
                  appId: config.app_id,
                  cookie: true,
                  xfbml: true,
                  version: 'v18.0'
                });
                setFbLoaded(true);
                resolve(window.FB);
              }
            } catch (err) {
              console.error('Facebook SDK init error:', err);
              reject(err);
            }
          };
          
          // If fbAsyncInit was already called, call it again
          if (window.FB && config && config.app_id) {
            try {
              window.FB.init({
                appId: config.app_id,
                cookie: true,
                xfbml: true,
                version: 'v18.0'
              });
              setFbLoaded(true);
              resolve(window.FB);
            } catch (err) {
              console.error('Facebook SDK direct init error:', err);
              reject(err);
            }
          }
        };

        script.onerror = () => {
          console.error('Failed to load Facebook SDK script');
          reject(new Error('Failed to load Facebook SDK'));
        };

        document.head.appendChild(script);
      });
    };

    // Fetch Facebook OAuth config from backend
    const fetchConfig = async () => {
      try {
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/auth/facebook/config`);
        if (response.ok) {
          const configData = await response.json();
          console.log('Facebook OAuth config loaded:', configData);
          setConfig(configData);
          
          // Load Facebook SDK after getting config
          try {
            await loadFacebookSDK();
            console.log('Facebook SDK loaded successfully');
          } catch (sdkError) {
            console.error('Facebook SDK loading failed:', sdkError);
            setConfigError('Failed to load Facebook SDK');
          }
        } else {
          const error = await response.json();
          console.error('Facebook config error:', error);
          setConfigError(error.detail || 'Facebook OAuth not configured');
        }
      } catch (error) {
        console.error('Failed to fetch Facebook OAuth config:', error);
        setConfigError('Failed to load Facebook OAuth configuration');
      } finally {
        setLoading(false);
      }
    };

    fetchConfig();
  }, []); // Remove config dependency to avoid infinite loop

  const handleFacebookLogin = () => {
    if (!window.FB || !fbLoaded || !config) {
      onError('Facebook SDK not loaded');
      return;
    }

    setLoading(true);

    window.FB.login(async (response) => {
      try {
        if (response.status === 'connected') {
          console.log('Facebook login successful:', response);
          
          // Send the access token to our backend
          const authResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/auth/facebook`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              provider: 'facebook',
              access_token: response.authResponse.accessToken
            })
          });

          if (authResponse.ok) {
            const authData = await authResponse.json();
            console.log('Backend auth response:', authData);
            onSuccess(authData);
          } else {
            const error = await authResponse.json();
            console.error('Backend auth error:', error);
            onError(error.detail || 'Facebook authentication failed');
          }
        } else if (response.status === 'not_authorized') {
          onError('Facebook login was cancelled or failed');
        } else {
          onError('Facebook login failed');
        }
      } catch (error) {
        console.error('Facebook OAuth error:', error);
        onError('Facebook authentication failed: ' + error.message);
      } finally {
        setLoading(false);
      }
    }, {
      scope: 'email,public_profile',
      return_scopes: true
    });
  };

  if (loading && !config) {
    return (
      <div className="flex items-center justify-center p-3 border border-gray-300 rounded-lg bg-gray-50">
        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 mr-2"></div>
        <span className="text-gray-600">Loading Facebook Sign-In...</span>
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
    return (
      <div className="p-3 border border-yellow-300 rounded-lg bg-yellow-50">
        <span className="text-yellow-600 text-sm">Facebook login temporarily unavailable</span>
      </div>
    );
  }

  return (
    <div className="w-full">
      <button
        onClick={handleFacebookLogin}
        disabled={disabled || loading}
        className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {loading ? (
          <div className="flex items-center">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
            <span>Signing in...</span>
          </div>
        ) : (
          <div className="flex items-center">
            {/* Facebook Icon */}
            <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24" fill="#1877F2">
              <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
            </svg>
            <span>{text}</span>
          </div>
        )}
      </button>
    </div>
  );
};

export default FacebookOAuthButton;
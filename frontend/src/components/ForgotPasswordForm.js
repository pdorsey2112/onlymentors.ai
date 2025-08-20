import React, { useState } from 'react';
import { getBackendURL } from '../config';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Alert, AlertDescription } from './ui/alert';
import { ArrowLeft, Mail, Shield, Clock } from 'lucide-react';

const ForgotPasswordForm = ({ userType, onBack, onSuccess }) => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!email.trim()) {
      setError('Please enter your email address');
      return;
    }

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError('Please enter a valid email address');
      return;
    }

    try {
      setLoading(true);
      setError('');

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/auth/forgot-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email.trim(),
          user_type: userType
        })
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess(true);
        if (onSuccess) {
          onSuccess(data);
        }
      } else {
        if (response.status === 429) {
          setError('Too many reset attempts. Please wait 1 hour before trying again.');
        } else {
          setError(data.detail || 'Failed to send password reset email');
        }
      }
    } catch (err) {
      setError('Network error. Please check your connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <Card className="w-full max-w-md mx-auto">
        <CardHeader className="text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Mail className="w-8 h-8 text-green-600" />
          </div>
          <CardTitle className="text-xl font-bold text-gray-900">Check Your Email</CardTitle>
          <CardDescription>
            Password reset instructions have been sent
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <Shield className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-sm text-green-800 font-medium">Email sent successfully!</p>
                <p className="text-sm text-green-700 mt-1">
                  If an account with <strong>{email}</strong> exists, you'll receive a password reset link shortly.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <Clock className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-sm text-blue-800 font-medium">Important:</p>
                <ul className="text-sm text-blue-700 mt-1 space-y-1">
                  <li>• Check your spam/junk folder if you don't see the email</li>
                  <li>• The reset link expires in <strong>1 hour</strong></li>
                  <li>• Only use the most recent email if you receive multiple</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="flex flex-col space-y-3">
            <Button
              onClick={onBack}
              variant="outline"
              className="w-full"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Sign In
            </Button>
            
            <Button
              onClick={() => {
                setSuccess(false);
                setEmail('');
              }}
              variant="ghost"
              className="w-full text-sm text-gray-600 hover:text-gray-800"
            >
              Send to different email
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader className="text-center">
        <CardTitle className="text-xl font-bold text-gray-900">Forgot Password</CardTitle>
        <CardDescription>
          Enter your email to receive a password reset link
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <Alert className="border-red-200 bg-red-50">
              <AlertDescription className="text-red-800">{error}</AlertDescription>
            </Alert>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email Address
            </label>
            <Input
              type="email"
              placeholder={`Enter your ${userType === 'mentor' ? 'mentor' : ''} email address`}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full"
              disabled={loading}
              autoComplete="email"
              autoFocus
            />
            <p className="text-xs text-gray-500 mt-1">
              {userType === 'mentor' 
                ? 'Use the email address associated with your mentor account' 
                : 'Use the email address you signed up with'
              }
            </p>
          </div>

          <div className="flex flex-col space-y-3">
            <Button 
              type="submit" 
              className="w-full bg-purple-600 hover:bg-purple-700"
              disabled={loading}
            >
              {loading ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Sending...
                </div>
              ) : (
                <>
                  <Mail className="w-4 h-4 mr-2" />
                  Send Reset Link
                </>
              )}
            </Button>

            <Button
              type="button"
              onClick={onBack}
              variant="outline"
              className="w-full"
              disabled={loading}
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Sign In
            </Button>
          </div>
        </form>

        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Security Notice</h4>
          <p className="text-xs text-gray-600">
            For your security, we'll only send reset instructions to email addresses 
            associated with existing accounts. If you don't receive an email, 
            please check that you entered the correct email address.
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

export default ForgotPasswordForm;
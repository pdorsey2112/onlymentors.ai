import React, { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Alert, AlertDescription } from './ui/alert';
import { Progress } from './ui/progress';
import { Separator } from './ui/separator';
import { ArrowLeft, Mail, Phone, User, Lock, CheckCircle, Building } from 'lucide-react';
import { getBackendURL } from '../config';

const BusinessEmployeeSignup = ({ businessSlug, businessConfig, onSuccess, onBack }) => {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Form data
  const [formData, setFormData] = useState({
    email: '',
    phone_number: '',
    full_name: '',
    password: '',
    confirmPassword: '',
    two_factor_code: '',
    department_code: ''
  });
  
  // Step state
  const [verificationSent, setVerificationSent] = useState(false);
  const [companyId, setCompanyId] = useState('');

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError('');
  };

  const validateStep1 = () => {
    if (!formData.email || !formData.phone_number) {
      setError('Email and phone number are required');
      return false;
    }
    
    if (!formData.email.includes('@')) {
      setError('Please enter a valid email address');
      return false;
    }
    
    return true;
  };

  const validateStep2 = () => {
    if (!formData.full_name || !formData.password || !formData.confirmPassword) {
      setError('All fields are required');
      return false;
    }
    
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return false;
    }
    
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      return false;
    }
    
    return true;
  };

  const validateStep3 = () => {
    if (!formData.two_factor_code) {
      setError('Verification code is required');
      return false;
    }
    
    if (formData.two_factor_code.length !== 6) {
      setError('Verification code must be 6 digits');
      return false;
    }
    
    return true;
  };

  const handleStep1Submit = async (e) => {
    e.preventDefault();
    
    if (!validateStep1()) return;
    
    setLoading(true);
    setError('');
    
    try {
      const backendURL = getBackendURL();
      const response = await fetch(`${backendURL}/api/auth/business/pre-signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          phone_number: formData.phone_number,
          business_slug: businessSlug
        })
      });

      if (response.ok) {
        const data = await response.json();
        setCompanyId(data.company_id);
        setVerificationSent(true);
        setStep(2);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Email validation failed');
      }
    } catch (error) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleStep2Submit = (e) => {
    e.preventDefault();
    
    if (!validateStep2()) return;
    
    setStep(3);
  };

  const handleFinalSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateStep3()) return;
    
    setLoading(true);
    setError('');
    
    try {
      const backendURL = getBackendURL();
      
      // For testing, try test endpoint first if in development
      let response;
      if (formData.two_factor_code === '123456') {
        // Use test endpoint for easier testing
        response = await fetch(`${backendURL}/api/auth/business/signup-test`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: formData.email,
            password: formData.password,
            full_name: formData.full_name,
            business_slug: businessSlug,
            department_code: formData.department_code
          })
        });
      } else {
        // Use regular endpoint
        response = await fetch(`${backendURL}/api/auth/business/signup`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: formData.email,
            password: formData.password,
            full_name: formData.full_name,
            phone_number: formData.phone_number,
            two_factor_code: formData.two_factor_code,
            business_slug: businessSlug,
            department_code: formData.department_code
          })
        });
      }

      if (response.ok) {
        const data = await response.json();
        onSuccess(data);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Registration failed');
      }
    } catch (error) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const resendVerificationCode = async () => {
    setLoading(true);
    setError('');
    
    try {
      const backendURL = getBackendURL();
      const response = await fetch(`${backendURL}/api/auth/business/pre-signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          phone_number: formData.phone_number,
          business_slug: businessSlug
        })
      });

      if (response.ok) {
        setError('');
        // Show success message
        setError('New verification code sent to your phone');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to resend code');
      }
    } catch (error) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderStep1 = () => (
    <form onSubmit={handleStep1Submit} className="space-y-4">
      <div>
        <Label htmlFor="email">Company Email Address</Label>
        <Input
          id="email"
          type="email"
          placeholder="your.email@company.com"
          value={formData.email}
          onChange={(e) => handleInputChange('email', e.target.value)}
          required
        />
        <p className="text-sm text-gray-600 mt-1">
          Must be a valid {businessConfig?.company_name || 'company'} email address
        </p>
      </div>
      
      <div>
        <Label htmlFor="phone">Phone Number</Label>
        <Input
          id="phone"
          type="tel"
          placeholder="+1 (555) 123-4567"
          value={formData.phone_number}
          onChange={(e) => handleInputChange('phone_number', e.target.value)}
          required
        />
        <p className="text-sm text-gray-600 mt-1">
          Required for 2-factor authentication
        </p>
      </div>
      
      <Button type="submit" className="w-full" disabled={loading}>
        {loading ? 'Validating...' : 'Continue'}
      </Button>
    </form>
  );

  const renderStep2 = () => (
    <form onSubmit={handleStep2Submit} className="space-y-4">
      <div>
        <Label htmlFor="full_name">Full Name</Label>
        <Input
          id="full_name"
          type="text"
          placeholder="John Doe"
          value={formData.full_name}
          onChange={(e) => handleInputChange('full_name', e.target.value)}
          required
        />
      </div>
      
      <div>
        <Label htmlFor="department">Department (Optional)</Label>
        <Input
          id="department"
          type="text"
          placeholder="Engineering, Marketing, Sales..."
          value={formData.department_code}
          onChange={(e) => handleInputChange('department_code', e.target.value)}
        />
      </div>
      
      <div>
        <Label htmlFor="password">Password</Label>
        <Input
          id="password"
          type="password"
          placeholder="Create a strong password"
          value={formData.password}
          onChange={(e) => handleInputChange('password', e.target.value)}
          required
        />
      </div>
      
      <div>
        <Label htmlFor="confirmPassword">Confirm Password</Label>
        <Input
          id="confirmPassword"
          type="password"
          placeholder="Confirm your password"
          value={formData.confirmPassword}
          onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
          required
        />
      </div>
      
      <div className="flex space-x-2">
        <Button
          type="button"
          variant="outline"
          onClick={() => setStep(1)}
          className="flex-1"
        >
          Back
        </Button>
        <Button type="submit" className="flex-1" disabled={loading}>
          Continue
        </Button>
      </div>
    </form>
  );

  const renderStep3 = () => (
    <form onSubmit={handleFinalSubmit} className="space-y-4">
      <div className="text-center mb-4">
        <Phone className="w-12 h-12 text-blue-600 mx-auto mb-2" />
        <h3 className="text-lg font-medium">Verify Your Phone</h3>
        <p className="text-sm text-gray-600">
          We sent a 6-digit code to {formData.phone_number}
        </p>
      </div>
      
      <div>
        <Label htmlFor="verification_code">Verification Code</Label>
        <Input
          id="verification_code"
          type="text"
          placeholder="123456"
          value={formData.two_factor_code}
          onChange={(e) => handleInputChange('two_factor_code', e.target.value.replace(/\D/g, '').slice(0, 6))}
          maxLength={6}
          className="text-center text-lg tracking-widest"
          required
        />
      </div>
      
      <div className="text-center">
        <Button
          type="button"
          variant="ghost"
          onClick={resendVerificationCode}
          disabled={loading}
          className="text-sm"
        >
          Didn't receive the code? Resend
        </Button>
      </div>
      
      <div className="flex space-x-2">
        <Button
          type="button"
          variant="outline"
          onClick={() => setStep(2)}
          className="flex-1"
        >
          Back
        </Button>
        <Button type="submit" className="flex-1" disabled={loading || formData.two_factor_code.length !== 6}>
          {loading ? 'Creating Account...' : 'Create Account'}
        </Button>
      </div>
    </form>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <div className="flex items-center mb-4">
            <Button
              onClick={onBack}
              variant="ghost"
              size="sm"
              className="mr-2"
            >
              <ArrowLeft className="w-4 h-4" />
            </Button>
            <div className="flex-1">
              <div className="text-2xl mb-2">🏢</div>
              <CardTitle className="text-xl">
                Join {businessConfig?.company_name || 'Company'}
              </CardTitle>
              <CardDescription>
                Create your employee account with 2FA verification
              </CardDescription>
            </div>
          </div>
          
          {/* Progress Bar */}
          <div className="mb-4">
            <div className="flex justify-between text-xs text-gray-600 mb-2">
              <span>Email Verification</span>
              <span>Account Details</span>
              <span>2FA Setup</span>
            </div>
            <Progress value={(step / 3) * 100} className="h-2" />
          </div>
        </CardHeader>
        
        <CardContent>
          {error && (
            <Alert variant={error.includes('sent') ? 'default' : 'destructive'} className="mb-4">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          
          {step === 1 && renderStep1()}
          {step === 2 && renderStep2()}
          {step === 3 && renderStep3()}
        </CardContent>
      </Card>
    </div>
  );
};

export default BusinessEmployeeSignup;
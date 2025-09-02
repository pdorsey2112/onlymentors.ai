import React, { useState } from 'react';
import { getBackendURL } from '../config';

const UserSignup = ({ onSuccess, onSwitchToLogin }) => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    // Basic Information
    email: '',
    password: '',
    confirm_password: '',
    full_name: '',
    phone_number: '',
    
    // Communication Preferences
    communication_preferences: {
      email: true,
      text: false,
      both: false
    },
    
    // Subscription Choice
    subscription_plan: 'free', // 'free' or 'premium'
    
    // Mentor Option
    become_mentor: false,
    
    // Payment Information (for premium)
    payment_info: {
      card_number: '',
      expiry_month: '',
      expiry_year: '',
      cvv: '',
      cardholder_name: '',
      billing_address: {
        street: '',
        city: '',
        state: '',
        zip_code: '',
        country: 'US'
      }
    }
  });

  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    if (name.startsWith('payment_info.')) {
      const field = name.split('.')[1];
      if (field === 'billing_address') {
        const addressField = name.split('.')[2];
        setFormData(prev => ({
          ...prev,
          payment_info: {
            ...prev.payment_info,
            billing_address: {
              ...prev.payment_info.billing_address,
              [addressField]: value
            }
          }
        }));
      } else {
        setFormData(prev => ({
          ...prev,
          payment_info: {
            ...prev.payment_info,
            [field]: value
          }
        }));
      }
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleCommunicationChange = (preference) => {
    setFormData(prev => ({
      ...prev,
      communication_preferences: {
        email: preference === 'email' || preference === 'both',
        text: preference === 'text' || preference === 'both',
        both: preference === 'both'
      }
    }));
  };

  const validateStep1 = () => {
    const newErrors = {};
    
    if (!formData.email || !/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }
    
    if (!formData.password || formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters long';
    }
    
    if (formData.password !== formData.confirm_password) {
      newErrors.confirm_password = 'Passwords do not match';
    }
    
    if (!formData.full_name || formData.full_name.trim().length < 2) {
      newErrors.full_name = 'Please enter your full name';
    }
    
    if (!formData.phone_number || !/^\+?[\d\s\-\(\)]{10,}$/.test(formData.phone_number)) {
      newErrors.phone_number = 'Please enter a valid phone number';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateStep2 = () => {
    if (formData.subscription_plan === 'free') return true;
    
    const newErrors = {};
    const { payment_info } = formData;
    
    if (!payment_info.card_number || payment_info.card_number.replace(/\s/g, '').length < 13) {
      newErrors.card_number = 'Please enter a valid card number';
    }
    
    if (!payment_info.expiry_month || !payment_info.expiry_year) {
      newErrors.expiry = 'Please enter expiry date';
    }
    
    if (!payment_info.cvv || payment_info.cvv.length < 3) {
      newErrors.cvv = 'Please enter CVV';
    }
    
    if (!payment_info.cardholder_name) {
      newErrors.cardholder_name = 'Please enter cardholder name';
    }
    
    if (!payment_info.billing_address.street || !payment_info.billing_address.city || 
        !payment_info.billing_address.state || !payment_info.billing_address.zip_code) {
      newErrors.billing_address = 'Please complete billing address';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (step === 1 && validateStep1()) {
      setStep(2);
    } else if (step === 2 && validateStep2()) {
      setStep(3);
    } else if (step === 3) {
      handleSubmit();
    }
  };

  const handleBack = () => {
    setStep(prev => Math.max(1, prev - 1));
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    setErrors({});

    try {
      const backendURL = getBackendURL();
      
      const formDataToSend = new FormData();
      formDataToSend.append('email', formData.email);
      formDataToSend.append('password', formData.password);
      formDataToSend.append('full_name', formData.full_name);
      formDataToSend.append('phone_number', formData.phone_number);
      formDataToSend.append('communication_preferences', JSON.stringify(formData.communication_preferences));
      formDataToSend.append('subscription_plan', formData.subscription_plan);
      formDataToSend.append('become_mentor', formData.become_mentor);
      
      if (formData.subscription_plan === 'premium' && formData.payment_info) {
        formDataToSend.append('payment_info', JSON.stringify(formData.payment_info));
      }

      const response = await fetch(`${backendURL}/api/auth/register`, {
        method: 'POST',
        body: formDataToSend
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('auth_token', data.token);
        localStorage.setItem('user_data', JSON.stringify(data.user));
        onSuccess(data.user);
      } else {
        const errorData = await response.json();
        setErrors({ submit: errorData.detail || 'Registration failed. Please try again.' });
      }
    } catch (error) {
      console.error('Registration error:', error);
      setErrors({ submit: 'Network error. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };

  const formatCardNumber = (value) => {
    const v = value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
    const matches = v.match(/\d{4,16}/g);
    const match = matches && matches[0] || '';
    const parts = [];
    for (let i = 0, len = match.length; i < len; i += 4) {
      parts.push(match.substring(i, i + 4));
    }
    if (parts.length) {
      return parts.join(' ');
    } else {
      return v;
    }
  };

  const handleCardNumberChange = (e) => {
    const formatted = formatCardNumber(e.target.value);
    handleInputChange({ target: { name: 'payment_info.card_number', value: formatted } });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Join OnlyMentors.ai</h1>
          <p className="text-gray-600">Create your account to start learning from AI and human mentors</p>
          
          {/* Progress Indicator */}
          <div className="flex items-center justify-center mt-6 space-x-2">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
              step >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
            }`}>1</div>
            <div className={`w-8 h-1 ${step >= 2 ? 'bg-blue-600' : 'bg-gray-200'}`}></div>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
              step >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
            }`}>2</div>
            <div className={`w-8 h-1 ${step >= 3 ? 'bg-blue-600' : 'bg-gray-200'}`}></div>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
              step >= 3 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
            }`}>3</div>
          </div>
        </div>

        {errors.submit && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-600 text-sm">{errors.submit}</p>
          </div>
        )}

        {/* Step 1: Basic Information */}
        {step === 1 && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Personal Information</h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
              <input
                type="text"
                name="full_name"
                value={formData.full_name}
                onChange={handleInputChange}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  errors.full_name ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Enter your full name"
              />
              {errors.full_name && <p className="mt-1 text-sm text-red-600">{errors.full_name}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  errors.email ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Enter your email"
              />
              {errors.email && <p className="mt-1 text-sm text-red-600">{errors.email}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Phone Number</label>
              <input
                type="tel"
                name="phone_number"
                value={formData.phone_number}
                onChange={handleInputChange}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  errors.phone_number ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Enter your phone number"
              />
              {errors.phone_number && <p className="mt-1 text-sm text-red-600">{errors.phone_number}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  errors.password ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Create a password (8+ characters)"
              />
              {errors.password && <p className="mt-1 text-sm text-red-600">{errors.password}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Confirm Password</label>
              <input
                type="password"
                name="confirm_password"
                value={formData.confirm_password}
                onChange={handleInputChange}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  errors.confirm_password ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Confirm your password"
              />
              {errors.confirm_password && <p className="mt-1 text-sm text-red-600">{errors.confirm_password}</p>}
            </div>

            <div className="mt-6">
              <label className="block text-sm font-medium text-gray-700 mb-3">How would you like to receive notifications?</label>
              <div className="space-y-2">
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="communication"
                    value="email"
                    checked={formData.communication_preferences.email && !formData.communication_preferences.text}
                    onChange={(e) => handleCommunicationChange(e.target.value)}
                    className="text-blue-600"
                  />
                  <span className="ml-2 text-sm text-gray-700">Email only</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="communication"
                    value="text"
                    checked={formData.communication_preferences.text && !formData.communication_preferences.email}
                    onChange={(e) => handleCommunicationChange(e.target.value)}
                    className="text-blue-600"
                  />
                  <span className="ml-2 text-sm text-gray-700">Text/SMS only</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="communication"
                    value="both"
                    checked={formData.communication_preferences.both}
                    onChange={(e) => handleCommunicationChange(e.target.value)}
                    className="text-blue-600"
                  />
                  <span className="ml-2 text-sm text-gray-700">Both email and text</span>
                </label>
              </div>
            </div>
          </div>
        )}

        {/* Step 2: Subscription Plan */}
        {step === 2 && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900">Choose Your Plan</h3>
            
            <div className="space-y-4">
              <div 
                className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
                  formData.subscription_plan === 'free' ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                }`}
                onClick={() => setFormData(prev => ({ ...prev, subscription_plan: 'free' }))}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-semibold text-gray-900">Free Plan</h4>
                    <p className="text-sm text-gray-600">Access to 5 mentors, 10 questions/month</p>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-gray-900">$0</div>
                    <div className="text-sm text-gray-600">per month</div>
                  </div>
                </div>
              </div>

              <div 
                className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
                  formData.subscription_plan === 'premium' ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                }`}
                onClick={() => setFormData(prev => ({ ...prev, subscription_plan: 'premium' }))}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-semibold text-gray-900">Premium Plan</h4>
                    <p className="text-sm text-gray-600">Unlimited mentors and questions</p>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-gray-900">$29</div>
                    <div className="text-sm text-gray-600">per month</div>
                  </div>
                </div>
              </div>
            </div>

            {formData.subscription_plan === 'premium' && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-sm text-yellow-800">
                  💳 You'll be able to add your payment information on the next step
                </p>
              </div>
            )}
          </div>
        )}

        {/* Step 3: Payment Information (if premium) */}
        {step === 3 && formData.subscription_plan === 'premium' && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Payment Information</h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Cardholder Name</label>
              <input
                type="text"
                name="payment_info.cardholder_name"
                value={formData.payment_info.cardholder_name}
                onChange={handleInputChange}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  errors.cardholder_name ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Name on card"
              />
              {errors.cardholder_name && <p className="mt-1 text-sm text-red-600">{errors.cardholder_name}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Card Number</label>
              <input
                type="text"
                name="payment_info.card_number"
                value={formData.payment_info.card_number}
                onChange={handleCardNumberChange}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  errors.card_number ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="1234 5678 9012 3456"
                maxLength="19"
              />
              {errors.card_number && <p className="mt-1 text-sm text-red-600">{errors.card_number}</p>}
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Month</label>
                <select
                  name="payment_info.expiry_month"
                  value={formData.payment_info.expiry_month}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">MM</option>
                  {Array.from({ length: 12 }, (_, i) => (
                    <option key={i + 1} value={String(i + 1).padStart(2, '0')}>
                      {String(i + 1).padStart(2, '0')}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Year</label>
                <select
                  name="payment_info.expiry_year"
                  value={formData.payment_info.expiry_year}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">YYYY</option>
                  {Array.from({ length: 10 }, (_, i) => (
                    <option key={i} value={new Date().getFullYear() + i}>
                      {new Date().getFullYear() + i}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">CVV</label>
                <input
                  type="text"
                  name="payment_info.cvv"
                  value={formData.payment_info.cvv}
                  onChange={handleInputChange}
                  className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    errors.cvv ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="123"
                  maxLength="4"
                />
              </div>
            </div>
            {(errors.expiry || errors.cvv) && (
              <p className="text-sm text-red-600">{errors.expiry || errors.cvv}</p>
            )}

            <div className="space-y-3">
              <h4 className="font-medium text-gray-900">Billing Address</h4>
              
              <input
                type="text"
                name="payment_info.billing_address.street"
                value={formData.payment_info.billing_address.street}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Street address"
              />

              <div className="grid grid-cols-2 gap-4">
                <input
                  type="text"
                  name="payment_info.billing_address.city"
                  value={formData.payment_info.billing_address.city}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="City"
                />
                <input
                  type="text"
                  name="payment_info.billing_address.state"
                  value={formData.payment_info.billing_address.state}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="State"
                />
              </div>

              <input
                type="text"
                name="payment_info.billing_address.zip_code"
                value={formData.payment_info.billing_address.zip_code}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="ZIP code"
              />
              
              {errors.billing_address && <p className="text-sm text-red-600">{errors.billing_address}</p>}
            </div>
          </div>
        )}

        {/* Step 3: Review (if free plan) */}
        {step === 3 && formData.subscription_plan === 'free' && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Review Your Information</h3>
            
            <div className="bg-gray-50 rounded-lg p-4 space-y-3">
              <div><strong>Name:</strong> {formData.full_name}</div>
              <div><strong>Email:</strong> {formData.email}</div>
              <div><strong>Phone:</strong> {formData.phone_number}</div>
              <div><strong>Plan:</strong> Free Plan</div>
              <div><strong>Notifications:</strong> 
                {formData.communication_preferences.both ? ' Email & Text' : 
                 formData.communication_preferences.email ? ' Email only' : 
                 formData.communication_preferences.text ? ' Text only' : ' None'}
              </div>
            </div>
          </div>
        )}

        {/* Navigation Buttons */}
        <div className="flex justify-between mt-8">
          <button
            type="button"
            onClick={step === 1 ? onSwitchToLogin : handleBack}
            className="px-6 py-2 text-gray-600 hover:text-gray-800 font-medium"
          >
            {step === 1 ? 'Already have an account?' : 'Back'}
          </button>
          
          <button
            type="button"
            onClick={handleNext}
            disabled={isLoading}
            className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Creating Account...' : 
             step === 3 ? 'Create Account' : 'Next'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default UserSignup;
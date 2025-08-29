import React, { useState, useEffect } from 'react';
import { getBackendURL } from '../config';

const PremiumContentPurchase = ({ content, onSuccess, onCancel, user }) => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('card');
  const [cardDetails, setCardDetails] = useState({
    number: '',
    expiry: '',
    cvc: '',
    name: ''
  });

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  const formatCardNumber = (value) => {
    // Remove all non-digits
    const v = value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
    // Add spaces every 4 digits
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

  const formatExpiry = (value) => {
    const v = value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
    if (v.length >= 2) {
      return v.substring(0, 2) + '/' + v.substring(2, 4);
    }
    return v;
  };

  const handleCardInputChange = (e) => {
    const { name, value } = e.target;
    let formattedValue = value;

    if (name === 'number') {
      formattedValue = formatCardNumber(value);
    } else if (name === 'expiry') {
      formattedValue = formatExpiry(value);
    } else if (name === 'cvc') {
      formattedValue = value.replace(/[^0-9]/g, '').substring(0, 4);
    }

    setCardDetails(prev => ({
      ...prev,
      [name]: formattedValue
    }));
  };

  const validateCardDetails = () => {
    const errors = [];
    
    if (!cardDetails.number || cardDetails.number.replace(/\s/g, '').length < 13) {
      errors.push('Valid card number is required');
    }
    
    if (!cardDetails.expiry || !cardDetails.expiry.match(/^\d{2}\/\d{2}$/)) {
      errors.push('Valid expiry date (MM/YY) is required');
    }
    
    if (!cardDetails.cvc || cardDetails.cvc.length < 3) {
      errors.push('Valid CVC is required');
    }
    
    if (!cardDetails.name.trim()) {
      errors.push('Cardholder name is required');
    }
    
    return errors;
  };

  const handlePurchase = async () => {
    setError('');
    
    const validationErrors = validateCardDetails();
    if (validationErrors.length > 0) {
      setError(validationErrors.join('. '));
      return;
    }
    
    setIsProcessing(true);
    
    try {
      // In a real implementation, you would integrate with Stripe Elements or similar
      // For this demo, we'll simulate the purchase process
      
      const backendURL = getBackendURL();
      const token = localStorage.getItem('auth_token');
      
      // Create a mock payment method ID (in production, this would come from Stripe)
      const mockPaymentMethodId = 'pm_card_' + Math.random().toString(36).substring(7);
      
      const purchaseData = {
        content_id: content.content_id,
        payment_method_id: mockPaymentMethodId
      };
      
      const response = await fetch(`${backendURL}/api/content/purchase`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(purchaseData)
      });
      
      if (response.ok) {
        const result = await response.json();
        onSuccess && onSuccess(result);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Purchase failed. Please try again.');
      }
    } catch (err) {
      setError('Network error. Please check your connection and try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const getContentTypeIcon = (type) => {
    const icons = {
      'document': '📄',
      'video': '🎥',
      'audio': '🎵',
      'image': '🖼️',
      'interactive': '⚡'
    };
    return icons[type] || '📁';
  };

  if (!content) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-6 rounded-t-2xl">
          <h2 className="text-xl font-bold">Complete Purchase</h2>
          <p className="text-purple-100 text-sm mt-1">Secure payment powered by Stripe</p>
        </div>

        <div className="p-6">
          {/* Content Summary */}
          <div className="bg-gray-50 rounded-lg p-4 mb-6">
            <div className="flex items-start gap-3">
              <div className="text-3xl">{getContentTypeIcon(content.content_type)}</div>
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900">{content.title}</h3>
                <p className="text-gray-600 text-sm mt-1 line-clamp-2">{content.description}</p>
                <div className="mt-2 flex items-center justify-between">
                  <span className="text-sm text-gray-500">
                    {content.content_type.charAt(0).toUpperCase() + content.content_type.slice(1)}
                  </span>
                  <span className="text-xl font-bold text-purple-600">
                    {formatPrice(content.price)}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* User Info */}
          <div className="mb-6">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Purchasing as:</h4>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <p className="text-blue-900 font-medium">{user?.full_name || 'User'}</p>
              <p className="text-blue-700 text-sm">{user?.email || 'No email'}</p>
            </div>
          </div>

          {/* Payment Method */}
          <div className="mb-6">
            <h4 className="text-sm font-medium text-gray-700 mb-3">Payment Method</h4>
            
            <div className="space-y-4">
              {/* Card Number */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Card Number
                </label>
                <input
                  type="text"
                  name="number"
                  value={cardDetails.number}
                  onChange={handleCardInputChange}
                  placeholder="1234 5678 9012 3456"
                  maxLength="19"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>

              {/* Expiry and CVC */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Expiry Date
                  </label>
                  <input
                    type="text"
                    name="expiry"
                    value={cardDetails.expiry}
                    onChange={handleCardInputChange}
                    placeholder="MM/YY"
                    maxLength="5"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    CVC
                  </label>
                  <input
                    type="text"
                    name="cvc"
                    value={cardDetails.cvc}
                    onChange={handleCardInputChange}
                    placeholder="123"
                    maxLength="4"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Cardholder Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Cardholder Name
                </label>
                <input
                  type="text"
                  name="name"
                  value={cardDetails.name}
                  onChange={handleCardInputChange}
                  placeholder="John Doe"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Total */}
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 mb-6">
            <div className="flex justify-between items-center">
              <span className="text-gray-700 font-medium">Total Amount:</span>
              <span className="text-2xl font-bold text-purple-600">{formatPrice(content.price)}</span>
            </div>
            <p className="text-purple-700 text-sm mt-1">
              ✓ Instant access • ✓ Lifetime ownership • ✓ Up to 10 downloads
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
              {error}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3">
            <button
              onClick={onCancel}
              disabled={isProcessing}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handlePurchase}
              disabled={isProcessing}
              className="flex-1 px-4 py-3 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 disabled:opacity-50 flex items-center justify-center"
            >
              {isProcessing ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Processing...
                </>
              ) : (
                <>
                  🔒 Pay {formatPrice(content.price)}
                </>
              )}
            </button>
          </div>

          {/* Security Notice */}
          <div className="mt-4 text-center">
            <p className="text-xs text-gray-500">
              🔐 Your payment information is encrypted and secure
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PremiumContentPurchase;
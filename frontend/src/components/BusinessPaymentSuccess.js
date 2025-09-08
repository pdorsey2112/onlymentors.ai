import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Alert, AlertDescription } from './ui/alert';
import { Badge } from './ui/badge';
import { CheckCircle, Building, Mail, Phone, CreditCard, Calendar, Users, ArrowRight } from 'lucide-react';
import { getBackendURL } from '../config';

const BusinessPaymentSuccess = ({ sessionId, onContinue }) => {
  const [loading, setLoading] = useState(true);
  const [paymentData, setPaymentData] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (sessionId) {
      verifyPayment();
    }
  }, [sessionId]);

  const verifyPayment = async () => {
    try {
      setLoading(true);
      const backendURL = getBackendURL();
      const response = await fetch(`${backendURL}/api/business/payment-status/${sessionId}`);
      
      if (response.ok) {
        const data = await response.json();
        setPaymentData(data);
      } else {
        setError('Failed to verify payment status');
      }
    } catch (error) {
      setError('Error verifying payment');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Verifying your payment...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 to-orange-50 flex items-center justify-center p-4">
        <Card className="max-w-md w-full">
          <CardHeader className="text-center">
            <div className="text-4xl mb-4">⚠️</div>
            <CardTitle className="text-xl text-red-600">Payment Verification Failed</CardTitle>
          </CardHeader>
          <CardContent className="text-center">
            <Alert variant="destructive" className="mb-4">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
            <Button onClick={() => window.location.href = '/'} variant="outline">
              Return to Homepage
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const planDetails = {
    starter: { 
      name: 'Starter Plan', 
      employees: 'Up to 25 employees',
      color: 'blue'
    },
    professional: { 
      name: 'Professional Plan', 
      employees: '26-100 employees',
      color: 'purple'
    }
  };

  const plan = planDetails[paymentData?.plan_id] || { name: 'Business Plan', employees: 'Enterprise', color: 'blue' };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Success Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-green-100 rounded-full mb-6">
            <CheckCircle className="w-12 h-12 text-green-600" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            🎉 Welcome to OnlyMentors.ai for Business!
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Your payment was successful and your business account is now active. 
            Let's get your organization set up with AI-powered mentorship.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Payment Confirmation */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <CreditCard className="w-5 h-5 mr-2 text-green-600" />
                Payment Confirmed
              </CardTitle>
              <CardDescription>
                Transaction completed successfully
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-green-50 p-4 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-green-900">Status</span>
                  <Badge className="bg-green-600 text-white">Paid</Badge>
                </div>
                <div className="text-sm text-green-800">
                  Session ID: {sessionId}
                </div>
              </div>
              
              {paymentData && (
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="font-medium">Plan</span>
                    <span>{plan.name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Amount</span>
                    <span>${paymentData.amount}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Company</span>
                    <span>{paymentData.company_name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Employee Limit</span>
                    <span>{plan.employees}</span>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Next Steps */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Building className="w-5 h-5 mr-2 text-blue-600" />
                Next Steps
              </CardTitle>
              <CardDescription>
                Complete your business setup
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                    <span className="text-xs font-bold text-blue-600">1</span>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">Check Your Email</h4>
                    <p className="text-sm text-gray-600">We've sent setup instructions to your email address</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3">
                  <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                    <span className="text-xs font-bold text-blue-600">2</span>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">Access Admin Console</h4>
                    <p className="text-sm text-gray-600">Configure departments, invite employees, and manage mentors</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3">
                  <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                    <span className="text-xs font-bold text-blue-600">3</span>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">Start Onboarding</h4>
                    <p className="text-sm text-gray-600">Begin inviting your team and assigning mentors</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Feature Highlights */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>Your Business Plan Includes</CardTitle>
            <CardDescription>
              Everything you need to transform your organization with AI mentorship
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="text-center p-4">
                <div className="w-12 h-12 bg-blue-100 rounded-lg mx-auto mb-3 flex items-center justify-center">
                  <Users className="w-6 h-6 text-blue-600" />
                </div>
                <h4 className="font-medium text-gray-900 mb-1">Department Management</h4>
                <p className="text-sm text-gray-600">Organize employees and track usage by department</p>
              </div>
              
              <div className="text-center p-4">
                <div className="w-12 h-12 bg-purple-100 rounded-lg mx-auto mb-3 flex items-center justify-center">
                  <Building className="w-6 h-6 text-purple-600" />
                </div>
                <h4 className="font-medium text-gray-900 mb-1">Multi-Tenant Platform</h4>
                <p className="text-sm text-gray-600">Dedicated workspace with complete data isolation</p>
              </div>
              
              <div className="text-center p-4">
                <div className="w-12 h-12 bg-green-100 rounded-lg mx-auto mb-3 flex items-center justify-center">
                  <Calendar className="w-6 h-6 text-green-600" />
                </div>
                <h4 className="font-medium text-gray-900 mb-1">Usage Analytics</h4>
                <p className="text-sm text-gray-600">Real-time insights on employee engagement</p>
              </div>
              
              <div className="text-center p-4">
                <div className="w-12 h-12 bg-orange-100 rounded-lg mx-auto mb-3 flex items-center justify-center">
                  <Mail className="w-6 h-6 text-orange-600" />
                </div>
                <h4 className="font-medium text-gray-900 mb-1">Priority Support</h4>
                <p className="text-sm text-gray-600">Dedicated support team for your organization</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="text-center mt-12 space-y-4">
          <div className="space-x-4">
            <Button 
              onClick={() => window.location.href = '/app?business-console=true'}
              size="lg"
              className="px-8"
            >
              Access Admin Console
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
            <Button 
              onClick={onContinue}
              variant="outline"
              size="lg"
            >
              Explore Platform
            </Button>
          </div>
          
          <div className="text-sm text-gray-600">
            <p>Need help? Contact our support team at <a href="mailto:business@onlymentors.ai" className="text-blue-600 hover:underline">business@onlymentors.ai</a></p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BusinessPaymentSuccess;
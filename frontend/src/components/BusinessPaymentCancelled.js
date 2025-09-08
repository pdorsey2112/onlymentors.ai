import React from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { XCircle, ArrowLeft, CreditCard, HelpCircle, Mail } from 'lucide-react';

const BusinessPaymentCancelled = ({ onRetry, onBack }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-red-50 py-12">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-orange-100 rounded-full mb-6">
            <XCircle className="w-12 h-12 text-orange-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Payment Cancelled
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Your payment was cancelled and no charges were made to your account. 
            You can try again or contact us if you need assistance.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Retry Payment */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <CreditCard className="w-5 h-5 mr-2 text-blue-600" />
                Try Again
              </CardTitle>
              <CardDescription>
                Complete your business subscription setup
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="flex items-center text-sm text-gray-600">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
                  Your business information is saved
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
                  Secure payment with Stripe
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
                  14-day free trial included
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
                  Cancel anytime, no commitment
                </div>
              </div>
              
              <div className="pt-4">
                <Button 
                  onClick={onRetry}
                  className="w-full"
                  size="lg"
                >
                  <CreditCard className="w-4 h-4 mr-2" />
                  Complete Payment
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Help & Support */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <HelpCircle className="w-5 h-5 mr-2 text-green-600" />
                Need Help?
              </CardTitle>
              <CardDescription>
                We're here to assist with your setup
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Common Issues</h4>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• Payment method declined</li>
                    <li>• Browser security settings</li>
                    <li>• Network connectivity issues</li>
                    <li>• Questions about pricing</li>
                  </ul>
                </div>
                
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Get Support</h4>
                  <div className="space-y-2">
                    <a 
                      href="mailto:business@onlymentors.ai"
                      className="flex items-center text-sm text-blue-600 hover:text-blue-800"
                    >
                      <Mail className="w-4 h-4 mr-2" />
                      business@onlymentors.ai
                    </a>
                    <p className="text-sm text-gray-600">
                      Response time: Within 2 hours
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Pricing Reminder */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>OnlyMentors.ai for Business</CardTitle>
            <CardDescription>
              Transform your organization with AI-powered mentorship
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="text-center p-6 bg-blue-50 rounded-lg">
                <h3 className="text-lg font-bold text-gray-900 mb-2">Starter Plan</h3>
                <div className="text-3xl font-bold text-blue-600 mb-1">$99</div>
                <div className="text-gray-600 text-sm mb-4">per month</div>
                <div className="text-sm text-gray-600">Up to 25 employees</div>
              </div>
              
              <div className="text-center p-6 bg-purple-50 rounded-lg">
                <h3 className="text-lg font-bold text-gray-900 mb-2">Professional Plan</h3>
                <div className="text-3xl font-bold text-purple-600 mb-1">$150</div>
                <div className="text-gray-600 text-sm mb-4">per month</div>
                <div className="text-sm text-gray-600">26-100 employees</div>
              </div>
            </div>
            
            <div className="text-center mt-6">
              <p className="text-sm text-gray-600">
                ✓ 14-day free trial • ✓ No setup fees • ✓ Cancel anytime • ✓ Enterprise support
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="text-center mt-12">
          <div className="space-x-4">
            <Button 
              onClick={onRetry}
              size="lg"
              className="px-8"
            >
              Try Payment Again
            </Button>
            <Button 
              onClick={onBack}
              variant="outline"
              size="lg"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Homepage
            </Button>
          </div>
          
          <div className="mt-6">
            <p className="text-sm text-gray-600">
              Still have questions? <a href="mailto:business@onlymentors.ai" className="text-blue-600 hover:underline">Contact our business team</a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BusinessPaymentCancelled;
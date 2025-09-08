import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Alert, AlertDescription } from './ui/alert';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { CheckCircle, CreditCard, Building, ArrowLeft, Loader } from 'lucide-react';
import { getBackendURL } from '../config';

const BusinessSignupFlow = ({ onComplete, onBack }) => {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [signupData, setSignupData] = useState(null);
  
  // Payment state
  const [paymentLoading, setPaymentLoading] = useState(false);
  const [paymentComplete, setPaymentComplete] = useState(false);

  useEffect(() => {
    // Load signup data from localStorage (from landing page modal)
    const savedData = localStorage.getItem('businessSignupData');
    console.log('BusinessSignupFlow: Checking localStorage for businessSignupData:', savedData);
    
    if (savedData) {
      try {
        const parsedData = JSON.parse(savedData);
        console.log('BusinessSignupFlow: Successfully parsed data:', parsedData);
        setSignupData(parsedData);
        // Don't remove localStorage data immediately - keep it for debugging
        // localStorage.removeItem('businessSignupData');
      } catch (error) {
        console.error('BusinessSignupFlow: Error parsing localStorage data:', error);
        setSignupData(null); // This will show loading state
      }
    } else {
      console.log('BusinessSignupFlow: No businessSignupData found in localStorage');
      // Don't create default data - let the user know there's an issue
      setSignupData(null);
    }
  }, []);

  const planDetails = {
    starter: {
      name: 'Starter Plan',
      price: 99.00,
      priceDisplay: '$99',
      period: 'month',
      employees: 'Up to 25 employees',
      features: [
        'AI Mentorship Platform',
        'Department Management', 
        'Usage Analytics',
        '14-Day Free Trial',
        'Email Support'
      ]
    },
    professional: {
      name: 'Professional Plan',
      price: 150.00,
      priceDisplay: '$150',
      period: 'month',
      employees: '26-100 employees',
      features: [
        'Everything in Starter',
        'Advanced Analytics',
        'Priority Support',
        'Custom Integrations',
        '14-Day Free Trial'
      ]
    }
  };

  const handlePayment = async () => {
    if (!signupData) return;
    
    setPaymentLoading(true);
    setError('');
    
    try {
      const plan = planDetails[signupData.plan];
      const backendURL = getBackendURL();
      
      // Create business checkout session
      const response = await fetch(`${backendURL}/api/business/create-checkout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          plan_id: signupData.plan,
          company_name: signupData.company_name,
          contact_name: signupData.contact_name,
          contact_email: signupData.contact_email,
          contact_phone: signupData.contact_phone,
          company_size: signupData.company_size,
          skip_trial: signupData.skip_trial,
          amount: plan.price,
          currency: 'usd',
          origin_url: window.location.origin + '/app'
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        // Redirect to Stripe checkout
        window.location.href = data.url;
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to create checkout session');
      }
    } catch (error) {
      setError('Network error. Please try again.');
    } finally {
      setPaymentLoading(false);
    }
  };

  const handleCompanyRegistration = async () => {
    if (!signupData) return;
    
    setLoading(true);
    setError('');
    
    try {
      const backendURL = getBackendURL();
      
      // Register company first
      const response = await fetch(`${backendURL}/api/business/company/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          company_name: signupData.company_name,
          company_email: signupData.contact_email,
          contact_name: signupData.contact_name,
          contact_email: signupData.contact_email,
          contact_phone: signupData.contact_phone,
          company_size: signupData.company_size,
          plan_type: signupData.plan,
          allowed_email_domains: [], // Will be configured later
          departments: []
        })
      });

      if (response.ok) {
        const data = await response.json();
        setSignupData(prev => ({ ...prev, company_id: data.company_id }));
        setStep(2); // Move to payment step
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to register company');
      }
    } catch (error) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!signupData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading signup information...</p>
        </div>
      </div>
    );
  }

  const plan = planDetails[signupData.plan];

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            {onBack && (
              <Button
                onClick={onBack}
                variant="ghost"
                size="sm"
                className="mr-4"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
            )}
            <h1 className="text-3xl font-bold text-gray-900">Complete Your Business Setup</h1>
          </div>
          
          {/* Progress Steps */}
          <div className="flex justify-center space-x-8 mb-8">
            <div className={`flex items-center ${step >= 1 ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-2 ${
                step >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-600'
              }`}>
                {step > 1 ? <CheckCircle className="w-5 h-5" /> : '1'}
              </div>
              <span className="text-sm font-medium">Company Details</span>
            </div>
            <div className={`flex items-center ${step >= 2 ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-2 ${
                step >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-600'
              }`}>
                {step > 2 ? <CheckCircle className="w-5 h-5" /> : '2'}
              </div>
              <span className="text-sm font-medium">Payment Setup</span>
            </div>
            <div className={`flex items-center ${step >= 3 ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-2 ${
                step >= 3 ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-600'
              }`}>
                {step > 3 ? <CheckCircle className="w-5 h-5" /> : '3'}
              </div>
              <span className="text-sm font-medium">Account Setup</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Plan Summary */}
          <div className="lg:col-span-1">
            <Card className="sticky top-8">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Building className="w-5 h-5 mr-2" />
                  Your Plan
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <Badge variant="secondary" className="mb-2">{plan.name}</Badge>
                  <div className="text-2xl font-bold text-blue-600">{plan.priceDisplay}</div>
                  <div className="text-sm text-gray-600">per {plan.period}</div>
                  <div className="text-sm text-gray-600 mt-1">{plan.employees}</div>
                  {!signupData.skip_trial && (
                    <div className="text-sm text-green-600 font-medium mt-2">
                      ✓ 14-Day Free Trial
                    </div>
                  )}
                </div>
                
                <div className="space-y-2">
                  <h4 className="font-medium text-gray-900">Included Features:</h4>
                  {plan.features.map((feature, index) => (
                    <div key={index} className="flex items-center text-sm text-gray-600">
                      <CheckCircle className="w-4 h-4 text-green-500 mr-2 flex-shrink-0" />
                      {feature}
                    </div>
                  ))}
                </div>
                
                <Separator />
                
                <div className="space-y-2 text-sm">
                  <div><span className="font-medium">Company:</span> {signupData.company_name}</div>
                  <div><span className="font-medium">Contact:</span> {signupData.contact_name}</div>
                  <div><span className="font-medium">Email:</span> {signupData.contact_email}</div>
                  <div><span className="font-medium">Size:</span> {signupData.company_size}</div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-2">
            {step === 1 && (
              <Card>
                <CardHeader>
                  <CardTitle>Confirm Company Details</CardTitle>
                  <CardDescription>
                    Please review your company information before proceeding to payment setup.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {error && (
                    <Alert variant="destructive" className="mb-6">
                      <AlertDescription>{error}</AlertDescription>
                    </Alert>
                  )}
                  
                  <div className="space-y-4">
                    <div>
                      <Label>Company Name</Label>
                      <Input value={signupData.company_name} disabled />
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label>Contact Name</Label>
                        <Input value={signupData.contact_name} disabled />
                      </div>
                      <div>
                        <Label>Contact Email</Label>
                        <Input value={signupData.contact_email} disabled />
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label>Phone Number</Label>
                        <Input value={signupData.contact_phone} disabled />
                      </div>
                      <div>
                        <Label>Company Size</Label>
                        <Input value={signupData.company_size} disabled />
                      </div>
                    </div>
                    
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <h4 className="font-medium text-blue-900 mb-2">What happens next?</h4>
                      <ul className="text-sm text-blue-800 space-y-1">
                        <li>• We'll register your company in our system</li>
                        <li>• Set up your payment method with Stripe</li>
                        <li>• Create your business admin account</li>
                        <li>• Provide access to your branded portal</li>
                      </ul>
                    </div>
                    
                    <div className="flex justify-end">
                      <Button
                        onClick={handleCompanyRegistration}
                        disabled={loading}
                        className="px-8"
                      >
                        {loading ? (
                          <>
                            <Loader className="w-4 h-4 mr-2 animate-spin" />
                            Registering Company...
                          </>
                        ) : (
                          'Continue to Payment'
                        )}
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {step === 2 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <CreditCard className="w-5 h-5 mr-2" />
                    Payment Setup
                  </CardTitle>
                  <CardDescription>
                    Secure payment processing powered by Stripe. 
                    {!signupData.skip_trial && " Your card won't be charged during the 14-day free trial."}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {error && (
                    <Alert variant="destructive" className="mb-6">
                      <AlertDescription>{error}</AlertDescription>
                    </Alert>
                  )}
                  
                  <div className="space-y-6">
                    <div className="bg-green-50 p-4 rounded-lg">
                      <h4 className="font-medium text-green-900 mb-2">✅ Company Registration Complete</h4>
                      <p className="text-sm text-green-800">
                        Your company has been successfully registered. Now let's set up your payment method.
                      </p>
                    </div>
                    
                    <div className="border rounded-lg p-6">
                      <h4 className="font-medium text-gray-900 mb-4">Payment Summary</h4>
                      <div className="space-y-3">
                        <div className="flex justify-between">
                          <span>{plan.name}</span>
                          <span>{plan.priceDisplay}/{plan.period}</span>
                        </div>
                        {!signupData.skip_trial && (
                          <div className="flex justify-between text-green-600">
                            <span>14-Day Free Trial</span>
                            <span>$0.00</span>
                          </div>
                        )}
                        <Separator />
                        <div className="flex justify-between font-bold">
                          <span>
                            {signupData.skip_trial ? 'First Payment' : 'Due Today'}
                          </span>
                          <span>
                            {signupData.skip_trial ? plan.priceDisplay : '$0.00'}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <h4 className="font-medium text-blue-900 mb-2">Secure Payment</h4>
                      <ul className="text-sm text-blue-800 space-y-1">
                        <li>• SSL encrypted and PCI compliant</li>
                        <li>• Powered by Stripe (trusted by millions)</li>
                        <li>• No setup fees or hidden charges</li>
                        <li>• Cancel anytime with no penalty</li>
                      </ul>
                    </div>
                    
                    <div className="flex justify-end">
                      <Button
                        onClick={handlePayment}
                        disabled={paymentLoading}
                        size="lg"
                        className="px-8"
                      >
                        {paymentLoading ? (
                          <>
                            <Loader className="w-4 h-4 mr-2 animate-spin" />
                            Creating Payment Session...
                          </>
                        ) : (
                          <>
                            <CreditCard className="w-4 h-4 mr-2" />
                            Continue to Secure Payment
                          </>
                        )}
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BusinessSignupFlow;
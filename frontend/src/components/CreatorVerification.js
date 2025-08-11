import React, { useState, useEffect } from 'react';

const CreatorVerification = ({ creatorId, onVerificationComplete }) => {
  const [verificationStatus, setVerificationStatus] = useState(null);
  const [currentStep, setCurrentStep] = useState('banking');
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});
  
  // Banking information state
  const [bankingData, setBankingData] = useState({
    bank_account_number: '',
    routing_number: '',
    tax_id: '',
    account_holder_name: '',
    bank_name: ''
  });

  // ID upload state
  const [idFile, setIdFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  useEffect(() => {
    fetchVerificationStatus();
  }, [creatorId]);

  const fetchVerificationStatus = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/creators/${creatorId}/verification-status`);
      if (response.ok) {
        const status = await response.json();
        setVerificationStatus(status);
        
        // Determine current step based on status
        if (!status.verification.bank_submitted) {
          setCurrentStep('banking');
        } else if (!status.verification.id_submitted) {
          setCurrentStep('id-upload');
        } else if (status.is_fully_verified) {
          setCurrentStep('complete');
          onVerificationComplete && onVerificationComplete();
        } else {
          setCurrentStep('review');
        }
      }
    } catch (error) {
      console.error('Failed to fetch verification status:', error);
    }
  };

  const handleBankingSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setErrors({});

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/creators/${creatorId}/banking`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(bankingData),
      });

      if (response.ok) {
        const result = await response.json();
        await fetchVerificationStatus(); // Refresh status
        if (result.verified) {
          setCurrentStep('id-upload');
        }
      } else {
        const errorData = await response.json();
        setErrors({ submit: errorData.detail || 'Failed to submit banking information' });
      }
    } catch (error) {
      setErrors({ submit: 'Network error. Please try again.' });
    }
    setIsLoading(false);
  };

  const handleIdUpload = async (e) => {
    e.preventDefault();
    if (!idFile) {
      setErrors({ file: 'Please select an ID document to upload' });
      return;
    }

    setIsLoading(true);
    setErrors({});
    
    const formData = new FormData();
    formData.append('id_document', idFile);

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/creators/${creatorId}/id-verification`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        await fetchVerificationStatus(); // Refresh status
        setCurrentStep('review');
      } else {
        const errorData = await response.json();
        setErrors({ file: errorData.detail || 'Failed to upload ID document' });
      }
    } catch (error) {
      setErrors({ file: 'Network error. Please try again.' });
    }
    setIsLoading(false);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setBankingData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf'];
      if (!allowedTypes.includes(file.type)) {
        setErrors({ file: 'Please upload a JPG, PNG, or PDF file' });
        return;
      }
      
      // Validate file size (10MB max)
      if (file.size > 10 * 1024 * 1024) {
        setErrors({ file: 'File size must be less than 10MB' });
        return;
      }
      
      setIdFile(file);
      setErrors({ file: '' });
    }
  };

  const StepIndicator = ({ steps, currentStep }) => (
    <div className="flex items-center justify-center mb-8">
      {steps.map((step, index) => (
        <div key={step.id} className="flex items-center">
          <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium ${
            step.id === currentStep 
              ? 'bg-purple-600 text-white' 
              : step.completed
                ? 'bg-green-500 text-white'
                : 'bg-gray-200 text-gray-600'
          }`}>
            {step.completed ? '✓' : index + 1}
          </div>
          {index < steps.length - 1 && (
            <div className={`w-16 h-1 mx-2 ${
              step.completed ? 'bg-green-500' : 'bg-gray-200'
            }`}></div>
          )}
        </div>
      ))}
    </div>
  );

  const renderBankingForm = () => (
    <div className="max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Banking Information</h2>
        <p className="text-gray-600">Provide your banking details to receive payments</p>
      </div>

      <form onSubmit={handleBankingSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Bank Account Number
            </label>
            <input
              type="text"
              name="bank_account_number"
              value={bankingData.bank_account_number}
              onChange={handleInputChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="123456789"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Routing Number
            </label>
            <input
              type="text"
              name="routing_number"
              value={bankingData.routing_number}
              onChange={handleInputChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="987654321"
              maxLength="9"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tax ID (SSN or EIN)
            </label>
            <input
              type="text"
              name="tax_id"
              value={bankingData.tax_id}
              onChange={handleInputChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="12-3456789 or 123-45-6789"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Account Holder Name
            </label>
            <input
              type="text"
              name="account_holder_name"
              value={bankingData.account_holder_name}
              onChange={handleInputChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="John Doe"
              required
            />
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Bank Name
            </label>
            <input
              type="text"
              name="bank_name"
              value={bankingData.bank_name}
              onChange={handleInputChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="Chase Bank, Wells Fargo, etc."
              required
            />
          </div>
        </div>

        {errors.submit && (
          <div className="text-red-600 text-sm bg-red-50 border border-red-200 rounded-lg p-3">
            {errors.submit}
          </div>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-purple-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-purple-700 transition-colors disabled:opacity-50"
        >
          {isLoading ? 'Submitting...' : 'Submit Banking Information'}
        </button>
      </form>
    </div>
  );

  const renderIdUpload = () => (
    <div className="max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Identity Verification</h2>
        <p className="text-gray-600">Upload a government-issued ID to verify your identity</p>
      </div>

      <form onSubmit={handleIdUpload} className="space-y-6">
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
          <div className="mb-4">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>
          
          <div className="mb-4">
            <label htmlFor="id-upload" className="cursor-pointer">
              <span className="text-purple-600 font-medium hover:text-purple-500">
                Click to upload your ID
              </span>
              <input
                id="id-upload"
                type="file"
                className="hidden"
                onChange={handleFileChange}
                accept=".jpg,.jpeg,.png,.pdf"
              />
            </label>
            <p className="text-gray-500 text-sm mt-2">
              JPG, PNG, or PDF up to 10MB
            </p>
          </div>

          {idFile && (
            <div className="mt-4 p-3 bg-green-50 rounded-lg">
              <p className="text-green-700 font-medium">✓ {idFile.name}</p>
              <p className="text-green-600 text-sm">{(idFile.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
          )}
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-medium text-blue-900 mb-2">Accepted Documents:</h4>
          <ul className="text-blue-800 text-sm space-y-1">
            <li>• Driver's License</li>
            <li>• Passport</li>
            <li>• State ID Card</li>
            <li>• Military ID</li>
          </ul>
        </div>

        {errors.file && (
          <div className="text-red-600 text-sm bg-red-50 border border-red-200 rounded-lg p-3">
            {errors.file}
          </div>
        )}

        <button
          type="submit"
          disabled={isLoading || !idFile}
          className="w-full bg-purple-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-purple-700 transition-colors disabled:opacity-50"
        >
          {isLoading ? 'Uploading...' : 'Upload ID Document'}
        </button>
      </form>
    </div>
  );

  const renderReview = () => (
    <div className="max-w-2xl mx-auto text-center">
      <div className="mb-8">
        <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Under Review</h2>
        <p className="text-gray-600">
          Thank you for submitting your verification documents. 
          Our team is reviewing your information and will notify you once approved.
        </p>
      </div>

      <div className="bg-gray-50 rounded-lg p-6">
        <h3 className="font-semibold text-gray-900 mb-4">Submitted Documents</h3>
        <div className="space-y-2 text-left">
          <div className="flex items-center justify-between">
            <span className="text-gray-700">Banking Information</span>
            <span className="text-green-600">✓ Submitted</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-700">ID Document</span>
            <span className="text-green-600">✓ Submitted</span>
          </div>
        </div>
      </div>

      <p className="text-sm text-gray-500 mt-6">
        Verification typically takes 1-2 business days. You'll receive an email when approved.
      </p>
    </div>
  );

  const renderComplete = () => (
    <div className="max-w-2xl mx-auto text-center">
      <div className="mb-8">
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Verification Complete!</h2>
        <p className="text-gray-600 mb-6">
          Your creator account has been verified and approved. 
          You can now start uploading content and earning from subscribers.
        </p>

        <button
          onClick={() => onVerificationComplete && onVerificationComplete()}
          className="bg-purple-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-purple-700 transition-colors"
        >
          Go to Dashboard
        </button>
      </div>
    </div>
  );

  if (!verificationStatus) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading verification status...</p>
        </div>
      </div>
    );
  }

  const steps = [
    { id: 'banking', name: 'Banking', completed: verificationStatus.verification.bank_verified },
    { id: 'id-upload', name: 'ID Upload', completed: verificationStatus.verification.id_verified },
    { id: 'review', name: 'Review', completed: verificationStatus.is_fully_verified },
    { id: 'complete', name: 'Complete', completed: verificationStatus.is_fully_verified }
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Mentor Verification</h1>
          <p className="text-gray-600 mt-2">Complete your verification to start earning</p>
        </div>

        <StepIndicator steps={steps} currentStep={currentStep} />

        <div className="bg-white rounded-2xl shadow-xl p-8">
          {currentStep === 'banking' && renderBankingForm()}
          {currentStep === 'id-upload' && renderIdUpload()}
          {currentStep === 'review' && renderReview()}
          {currentStep === 'complete' && renderComplete()}
        </div>
      </div>
    </div>
  );
};

export default CreatorVerification;
import React, { useState } from 'react';
import { getBackendURL } from '../config';

const BusinessInquiry = ({ onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    company_name: '',
    contact_name: '',
    contact_email: '',
    phone_number: '',
    company_size: '',
    industry: '',
    use_case: '',
    specific_requirements: '',
    budget_range: '',
    timeline: ''
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState({});

  const companySizeOptions = [
    { value: '1-10', label: '1-10 employees' },
    { value: '11-50', label: '11-50 employees' },
    { value: '51-200', label: '51-200 employees' },
    { value: '201-1000', label: '201-1000 employees' },
    { value: '1000+', label: '1000+ employees' }
  ];

  const budgetRanges = [
    { value: 'under-5k', label: 'Under $5,000/month' },
    { value: '5k-15k', label: '$5,000 - $15,000/month' },
    { value: '15k-50k', label: '$15,000 - $50,000/month' },
    { value: '50k+', label: '$50,000+/month' },
    { value: 'custom', label: 'Custom pricing needed' }
  ];

  const timelineOptions = [
    { value: 'immediate', label: 'Immediate (within 30 days)' },
    { value: '1-3months', label: '1-3 months' },
    { value: '3-6months', label: '3-6 months' },
    { value: '6months+', label: '6+ months' },
    { value: 'exploring', label: 'Just exploring options' }
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.company_name.trim()) newErrors.company_name = 'Company name is required';
    if (!formData.contact_name.trim()) newErrors.contact_name = 'Contact name is required';
    if (!formData.contact_email.trim()) newErrors.contact_email = 'Email is required';
    if (!formData.contact_email.includes('@')) newErrors.contact_email = 'Valid email is required';
    if (!formData.company_size) newErrors.company_size = 'Company size is required';
    if (!formData.use_case.trim()) newErrors.use_case = 'Use case description is required';

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setIsSubmitting(true);
    
    try {
      const backendURL = getBackendURL();
      const response = await fetch(`${backendURL}/api/business/inquiry`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          submitted_at: new Date().toISOString()
        })
      });

      if (response.ok) {
        onSuccess && onSuccess();
        setCurrentView('business_success');
      } else {
        const errorData = await response.json();
        setErrors({ submit: errorData.detail || 'Failed to submit inquiry' });
      }
    } catch (error) {
      setErrors({ submit: 'Network error. Please try again.' });
    }

    setIsSubmitting(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 py-8">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <button
              onClick={onClose}
              className="float-right text-gray-500 hover:text-gray-700 text-2xl"
            >
              ×
            </button>
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              🏢 OnlyMentors.ai for Business
            </h1>
            <p className="text-xl text-gray-600">
              Transform your organization with AI-powered mentoring and knowledge sharing
            </p>
          </div>

          {/* Benefits */}
          <div className="grid md:grid-cols-3 gap-6 mb-12">
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="text-3xl mb-3">🎯</div>
              <h3 className="font-semibold text-gray-900 mb-2">Custom Mentor Selection</h3>
              <p className="text-gray-600 text-sm">Choose from 400+ AI mentors plus add your internal experts</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="text-3xl mb-3">📊</div>
              <h3 className="font-semibold text-gray-900 mb-2">Department Tracking</h3>
              <p className="text-gray-600 text-sm">Track usage and costs by department or project code</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="text-3xl mb-3">🛡️</div>
              <h3 className="font-semibold text-gray-900 mb-2">Enterprise Security</h3>
              <p className="text-gray-600 text-sm">SSO integration, audit logs, and compliance features</p>
            </div>
          </div>

          {/* Form */}
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Get Started - Tell Us About Your Business</h2>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Company Information */}
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Company Name *
                  </label>
                  <input
                    type="text"
                    name="company_name"
                    value={formData.company_name}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Acme Corporation"
                  />
                  {errors.company_name && <p className="text-red-500 text-sm mt-1">{errors.company_name}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Industry
                  </label>
                  <input
                    type="text"
                    name="industry"
                    value={formData.industry}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Technology, Healthcare, Finance, etc."
                  />
                </div>
              </div>

              {/* Contact Information */}
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Contact Name *
                  </label>
                  <input
                    type="text"
                    name="contact_name"
                    value={formData.contact_name}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="John Smith"
                  />
                  {errors.contact_name && <p className="text-red-500 text-sm mt-1">{errors.contact_name}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Business Email *
                  </label>
                  <input
                    type="email"
                    name="contact_email"
                    value={formData.contact_email}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="john@company.com"
                  />
                  {errors.contact_email && <p className="text-red-500 text-sm mt-1">{errors.contact_email}</p>}
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Phone Number
                  </label>
                  <input
                    type="tel"
                    name="phone_number"
                    value={formData.phone_number}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="+1 (555) 123-4567"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Company Size *
                  </label>
                  <select
                    name="company_size"
                    value={formData.company_size}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select company size</option>
                    {companySizeOptions.map(option => (
                      <option key={option.value} value={option.value}>{option.label}</option>
                    ))}
                  </select>
                  {errors.company_size && <p className="text-red-500 text-sm mt-1">{errors.company_size}</p>}
                </div>
              </div>

              {/* Use Case */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  How would you use OnlyMentors.ai in your business? *
                </label>
                <textarea
                  name="use_case"
                  value={formData.use_case}
                  onChange={handleInputChange}
                  rows={4}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Employee development, Leadership training, Technical mentoring, Innovation consulting..."
                />
                {errors.use_case && <p className="text-red-500 text-sm mt-1">{errors.use_case}</p>}
              </div>

              {/* Specific Requirements */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Specific Requirements or Integrations
                </label>
                <textarea
                  name="specific_requirements"
                  value={formData.specific_requirements}
                  onChange={handleInputChange}
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., SSO integration, Slack/Teams integration, Custom mentor training, Compliance requirements..."
                />
              </div>

              {/* Budget and Timeline */}
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Budget Range
                  </label>
                  <select
                    name="budget_range"
                    value={formData.budget_range}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select budget range</option>
                    {budgetRanges.map(option => (
                      <option key={option.value} value={option.value}>{option.label}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Timeline
                  </label>
                  <select
                    name="timeline"
                    value={formData.timeline}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select timeline</option>
                    {timelineOptions.map(option => (
                      <option key={option.value} value={option.value}>{option.label}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Submit */}
              {errors.submit && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                  {errors.submit}
                </div>
              )}

              <div className="flex gap-4">
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all disabled:opacity-50"
                >
                  {isSubmitting ? 'Submitting...' : 'Submit Business Inquiry'}
                </button>
                <button
                  type="button"
                  onClick={onClose}
                  className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BusinessInquiry;
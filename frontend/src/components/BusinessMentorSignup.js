import React, { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Alert, AlertDescription } from './ui/alert';
import { Separator } from './ui/separator';
import { ArrowLeft, Crown, User, Mail, Building, Award } from 'lucide-react';
import { getBackendURL } from '../config';

const BusinessMentorSignup = ({ businessSlug, businessConfig, onSuccess, onBack }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Form data
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
    department_code: '',
    expertise_areas: '',
    bio: '',
    years_experience: '',
    mentoring_topics: ''
  });

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError('');
  };

  const validateForm = () => {
    if (!formData.email || !formData.password || !formData.full_name) {
      setError('Email, password, and full name are required');
      return false;
    }
    
    if (!formData.email.includes('@')) {
      setError('Please enter a valid email address');
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setLoading(true);
    setError('');
    
    try {
      const backendURL = getBackendURL();
      
      // First, create business employee account
      const signupResponse = await fetch(`${backendURL}/api/auth/business/signup-test`, {
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

      if (signupResponse.ok) {
        const signupData = await signupResponse.json();
        
        // Then, upgrade to mentor
        const mentorResponse = await fetch(`${backendURL}/api/users/become-mentor`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${signupData.token}`
          }
        });

        if (mentorResponse.ok) {
          // Update user data to include mentor status
          const userData = {
            ...signupData,
            user: {
              ...signupData.user,
              is_mentor: true
            }
          };
          
          onSuccess(userData);
        } else {
          const mentorError = await mentorResponse.json();
          setError(mentorError.detail || 'Failed to create mentor profile');
        }
      } else {
        const errorData = await signupResponse.json();
        setError(errorData.detail || 'Registration failed');
      }
    } catch (error) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-100 flex items-center justify-center px-4">
      <Card className="w-full max-w-2xl">
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
              <div className="flex items-center mb-2">
                <Crown className="w-6 h-6 text-purple-600 mr-2" />
                <CardTitle className="text-xl">
                  Become a Business Mentor
                </CardTitle>
              </div>
              <CardDescription>
                Join {businessConfig?.company_name || 'the company'} mentor program and help guide your colleagues
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        
        <CardContent>
          {error && (
            <Alert variant="destructive" className="mb-6">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Account Information */}
            <div className="space-y-4">
              <div className="flex items-center space-x-2 mb-4">
                <User className="w-5 h-5 text-blue-600" />
                <h3 className="text-lg font-medium">Account Information</h3>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="full_name">Full Name *</Label>
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
                  <Label htmlFor="email">Company Email *</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="john.doe@company.com"
                    value={formData.email}
                    onChange={(e) => handleInputChange('email', e.target.value)}
                    required
                  />
                  <p className="text-sm text-gray-600 mt-1">
                    Must be a valid {businessConfig?.company_name || 'company'} email address
                  </p>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="password">Password *</Label>
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
                  <Label htmlFor="confirmPassword">Confirm Password *</Label>
                  <Input
                    id="confirmPassword"
                    type="password"
                    placeholder="Confirm your password"
                    value={formData.confirmPassword}
                    onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                    required
                  />
                </div>
              </div>
              
              <div>
                <Label htmlFor="department">Department</Label>
                <Input
                  id="department"
                  type="text"
                  placeholder="Engineering, Marketing, Sales..."
                  value={formData.department_code}
                  onChange={(e) => handleInputChange('department_code', e.target.value)}
                />
              </div>
            </div>

            <Separator />

            {/* Mentor Information */}
            <div className="space-y-4">
              <div className="flex items-center space-x-2 mb-4">
                <Award className="w-5 h-5 text-purple-600" />
                <h3 className="text-lg font-medium">Mentor Profile</h3>
              </div>
              
              <div>
                <Label htmlFor="years_experience">Years of Experience</Label>
                <Input
                  id="years_experience"
                  type="number"
                  placeholder="5"
                  value={formData.years_experience}
                  onChange={(e) => handleInputChange('years_experience', e.target.value)}
                />
              </div>
              
              <div>
                <Label htmlFor="expertise_areas">Areas of Expertise</Label>
                <Input
                  id="expertise_areas"
                  type="text"
                  placeholder="e.g., Software Development, Project Management, Leadership"
                  value={formData.expertise_areas}
                  onChange={(e) => handleInputChange('expertise_areas', e.target.value)}
                />
                <p className="text-sm text-gray-600 mt-1">
                  Separate multiple areas with commas
                </p>
              </div>
              
              <div>
                <Label htmlFor="mentoring_topics">Topics You Can Help With</Label>
                <Textarea
                  id="mentoring_topics"
                  placeholder="e.g., Career development, Technical skills, Problem-solving, Team leadership..."
                  value={formData.mentoring_topics}
                  onChange={(e) => handleInputChange('mentoring_topics', e.target.value)}
                  rows={3}
                />
              </div>
              
              <div>
                <Label htmlFor="bio">Bio</Label>
                <Textarea
                  id="bio"
                  placeholder="Tell your colleagues about your background, experience, and how you can help them grow..."
                  value={formData.bio}
                  onChange={(e) => handleInputChange('bio', e.target.value)}
                  rows={4}
                />
              </div>
            </div>

            <Separator />

            {/* Mentor Program Information */}
            <div className="bg-blue-50 p-4 rounded-lg">
              <h4 className="font-medium text-blue-900 mb-2">About the Business Mentor Program</h4>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• Help your colleagues grow and develop their skills</li>
                <li>• No revenue sharing - this is about supporting your team</li>
                <li>• Flexible commitment - mentor when your schedule allows</li>
                <li>• Build your leadership skills and company reputation</li>
                <li>• Access to mentor training and resources</li>
              </ul>
            </div>

            {/* Submit Button */}
            <div className="flex space-x-4">
              <Button
                type="button"
                variant="outline"
                onClick={onBack}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button 
                type="submit" 
                className="flex-1" 
                disabled={loading}
              >
                {loading ? 'Creating Account...' : 'Apply to Become Mentor'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default BusinessMentorSignup;
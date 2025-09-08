import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { Separator } from './ui/separator';
import { Search, Filter, MessageSquare, Brain, Users, Building, Phone, Mail, CheckCircle, User, LogOut } from 'lucide-react';
import BusinessEmployeeSignup from './BusinessEmployeeSignup';
import UserProfile from './UserProfile';
import { getBackendURL } from '../config';

const BusinessEmployeeApp = ({ businessSlug }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [showSignup, setShowSignup] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  
  // Mentor marketplace state
  const [mentors, setMentors] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [loadingMentors, setLoadingMentors] = useState(false);
  const [businessConfig, setBusinessConfig] = useState(null);
  
  // Question state
  const [selectedMentor, setSelectedMentor] = useState(null);
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState('');
  const [showQuestionForm, setShowQuestionForm] = useState(false);
  const [submittingQuestion, setSubmittingQuestion] = useState(false);

  useEffect(() => {
    checkAuthentication();
    loadBusinessConfig();
  }, [businessSlug]);

  useEffect(() => {
    if (isAuthenticated && user) {
      loadMentors();
      loadCategories();
    }
  }, [isAuthenticated, user, selectedCategory, searchTerm]);

  const checkAuthentication = async () => {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        setIsLoading(false);
        return;
      }

      const backendURL = getBackendURL();
      const response = await fetch(`${backendURL}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const userData = await response.json();
        
        // Verify user is a business employee for this company
        if (userData.user.user_type === 'business_employee') {
          setUser(userData.user);
          setIsAuthenticated(true);
        } else {
          // Not a business employee
          localStorage.removeItem('token');
        }
      } else {
        localStorage.removeItem('token');
      }
    } catch (error) {
      console.error('Authentication check failed:', error);
      localStorage.removeItem('token');
    } finally {
      setIsLoading(false);
    }
  };

  const loadBusinessConfig = async () => {
    try {
      const backendURL = getBackendURL();
      const response = await fetch(`${backendURL}/api/business/public/${businessSlug}`);
      
      if (response.ok) {
        const config = await response.json();
        setBusinessConfig(config);
      }
    } catch (error) {
      console.error('Failed to load business config:', error);
    }
  };

  const loadMentors = async () => {
    if (!isAuthenticated || !user) return;
    
    try {
      setLoadingMentors(true);
      const backendURL = getBackendURL();
      const token = localStorage.getItem('token');
      
      let url = `${backendURL}/api/business/employee/mentors?q=${encodeURIComponent(searchTerm)}`;
      if (selectedCategory) {
        url += `&category_id=${selectedCategory}`;
      }
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setMentors(data.results || []);
      } else {
        console.error('Failed to load mentors:', response.statusText);
        setMentors([]);
      }
    } catch (error) {
      console.error('Error loading mentors:', error);
      setMentors([]);
    } finally {
      setLoadingMentors(false);
    }
  };

  const loadCategories = async () => {
    if (!businessConfig) return;
    
    try {
      const backendURL = getBackendURL();
      const response = await fetch(`${backendURL}/api/business/public/${businessSlug}/categories`);
      
      if (response.ok) {
        const data = await response.json();
        setCategories(data || []);
      }
    } catch (error) {
      console.error('Failed to load categories:', error);
    }
  };

  const handleLogin = async (loginData) => {
    try {
      const backendURL = getBackendURL();
      const response = await fetch(`${backendURL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(loginData)
      });

      if (response.ok) {
        const data = await response.json();
        
        // Verify user is a business employee
        if (data.user.user_type === 'business_employee') {
          localStorage.setItem('token', data.token);
          setUser(data.user);
          setIsAuthenticated(true);
        } else {
          throw new Error('Access denied. Business employee account required.');
        }
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }
    } catch (error) {
      throw error;
    }
  };

  const handleSignupSuccess = (userData) => {
    localStorage.setItem('token', userData.token);
    setUser(userData.user);
    setIsAuthenticated(true);
    setShowSignup(false);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setIsAuthenticated(false);
    setShowProfile(false);
  };

  const handleQuestionSubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedMentor || !question.trim()) return;
    
    setSubmittingQuestion(true);
    
    try {
      const backendURL = getBackendURL();
      const token = localStorage.getItem('token');
      
      const response = await fetch(`${backendURL}/api/mentor/${selectedMentor.mentor_id}/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ question: question.trim() })
      });

      if (response.ok) {
        const data = await response.json();
        setResponse(data.response);
      } else {
        throw new Error('Failed to get mentor response');
      }
    } catch (error) {
      console.error('Error submitting question:', error);
      setResponse('Sorry, there was an error processing your question. Please try again.');
    } finally {
      setSubmittingQuestion(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (showSignup) {
    return (
      <BusinessEmployeeSignup
        businessSlug={businessSlug}
        businessConfig={businessConfig}
        onSuccess={handleSignupSuccess}
        onBack={() => setShowSignup(false)}
      />
    );
  }

  if (showProfile && isAuthenticated) {
    return (
      <UserProfile
        user={user}
        onBack={() => setShowProfile(false)}
        onLogout={handleLogout}
      />
    );
  }

  if (!isAuthenticated) {
    return (
      <BusinessEmployeeLogin
        businessSlug={businessSlug}
        businessConfig={businessConfig}
        onLogin={handleLogin}
        onShowSignup={() => setShowSignup(true)}
      />
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <div className="text-xl font-bold text-blue-600">
                🏢 {businessConfig?.company_name || 'Business Portal'}
              </div>
              <div className="hidden md:block">
                <Badge variant="outline">Employee Portal</Badge>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                👋 Welcome, {user.full_name}
              </span>
              <Button
                onClick={() => setShowProfile(true)}
                variant="outline"
                size="sm"
              >
                <User className="w-4 h-4 mr-2" />
                Profile
              </Button>
              <Button
                onClick={handleLogout}
                variant="outline"
                size="sm"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Welcome to Your Company Mentorship Portal
          </h1>
          <p className="text-gray-600">
            Connect with expert mentors assigned to your organization for personalized guidance and professional development.
          </p>
        </div>

        {/* Search and Filters */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Search className="w-5 h-5 mr-2" />
              Find Mentors
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <Input
                  placeholder="Search mentors by name or expertise..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full"
                />
              </div>
              
              {categories.length > 0 && (
                <div>
                  <Label className="text-sm font-medium mb-2 block">Category</Label>
                  <div className="flex flex-wrap gap-2">
                    <Button
                      onClick={() => setSelectedCategory(null)}
                      variant={selectedCategory === null ? "default" : "outline"}
                      size="sm"
                    >
                      All Categories
                    </Button>
                    {categories.map(category => (
                      <Button
                        key={category.category_id}
                        onClick={() => setSelectedCategory(category.category_id)}
                        variant={selectedCategory === category.category_id ? "default" : "outline"}
                        size="sm"
                      >
                        {category.icon} {category.name}
                      </Button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Mentors Grid */}
        {loadingMentors ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading mentors...</p>
          </div>
        ) : mentors.length === 0 ? (
          <Card>
            <CardContent className="text-center py-12">
              <Brain className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Mentors Found</h3>
              <p className="text-gray-600">
                {searchTerm || selectedCategory 
                  ? "Try adjusting your search or filters"
                  : "No mentors have been assigned to your company yet"
                }
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {mentors.map(mentor => (
              <Card key={`${mentor.type}_${mentor.mentor_id}`} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-center space-x-3">
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-xl ${
                      mentor.type === 'ai' ? 'bg-blue-500' : 'bg-green-500'
                    }`}>
                      {mentor.type === 'ai' ? '🤖' : '👨‍🏫'}
                    </div>
                    <div className="flex-1">
                      <CardTitle className="text-lg">{mentor.name}</CardTitle>
                      <CardDescription>
                        {mentor.type === 'ai' ? 'AI Mentor' : `Company Mentor • ${mentor.department || 'Internal'}`}
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600 mb-4 line-clamp-3">
                    {mentor.description || 'Expert guidance in various areas'}
                  </p>
                  
                  {mentor.expertise && (
                    <div className="mb-4">
                      <Badge variant="secondary" className="text-xs">
                        {mentor.expertise}
                      </Badge>
                    </div>
                  )}
                  
                  <Button
                    onClick={() => {
                      setSelectedMentor(mentor);
                      setShowQuestionForm(true);
                      setQuestion('');
                      setResponse('');
                    }}
                    className="w-full"
                  >
                    <MessageSquare className="w-4 h-4 mr-2" />
                    Ask Question
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Question Modal */}
        {showQuestionForm && selectedMentor && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-bold mr-3 ${
                    selectedMentor.type === 'ai' ? 'bg-blue-500' : 'bg-green-500'
                  }`}>
                    {selectedMentor.type === 'ai' ? '🤖' : '👨‍🏫'}
                  </div>
                  Ask {selectedMentor.name}
                </CardTitle>
                <CardDescription>
                  {selectedMentor.description}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleQuestionSubmit} className="space-y-4">
                  <div>
                    <Label htmlFor="question">Your Question</Label>
                    <Textarea
                      id="question"
                      placeholder={`What would you like to ask ${selectedMentor.name}?`}
                      value={question}
                      onChange={(e) => setQuestion(e.target.value)}
                      rows={4}
                      required
                    />
                  </div>
                  
                  {response && (
                    <div>
                      <Label>Response</Label>
                      <div className="bg-gray-50 p-4 rounded-lg mt-2">
                        <p className="text-gray-800 whitespace-pre-wrap">{response}</p>
                      </div>
                    </div>
                  )}
                  
                  <div className="flex justify-end space-x-2">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => {
                        setShowQuestionForm(false);
                        setSelectedMentor(null);
                        setQuestion('');
                        setResponse('');
                      }}
                    >
                      Cancel
                    </Button>
                    <Button
                      type="submit"
                      disabled={submittingQuestion || !question.trim()}
                    >
                      {submittingQuestion ? 'Asking...' : 'Ask Question'}
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

// Business Employee Login Component
const BusinessEmployeeLogin = ({ businessSlug, businessConfig, onLogin, onShowSignup }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      await onLogin({ email, password });
    } catch (error) {
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="text-3xl mb-4">🏢</div>
          <CardTitle className="text-2xl">
            {businessConfig?.company_name || 'Business'} Portal
          </CardTitle>
          <CardDescription>
            Sign in to access your company's mentorship platform
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            
            <div>
              <Label htmlFor="email">Company Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="your.email@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            
            <div>
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? 'Signing In...' : 'Sign In'}
            </Button>
          </form>
          
          <Separator className="my-4" />
          
          <Button 
            variant="outline" 
            className="w-full"
            onClick={onShowSignup}
          >
            New Employee? Create Account
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};

export default BusinessEmployeeApp;
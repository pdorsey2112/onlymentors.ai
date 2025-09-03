import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Button } from './components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Input } from './components/ui/input';
import CreatorSignup from './components/CreatorSignup';
import CreatorLogin from './components/CreatorLogin';
import CreatorDashboard from './components/CreatorDashboard';
import CreatorVerification from './components/CreatorVerification';
import AdminLogin from './components/AdminLogin';
import AdminDashboardSimple from './components/AdminDashboardSimple';
import GoogleOAuthButton from './components/GoogleOAuthButton';
import FacebookOAuthButton from './components/FacebookOAuthButton';
import ForgotPasswordForm from './components/ForgotPasswordForm';
import ResetPasswordForm from './components/ResetPasswordForm';
import LandingRedirect from './components/LandingRedirect';
import UserSignup from './components/UserSignup';
import UserProfile from './components/UserProfile';
import DatabaseManagement from './components/DatabaseManagement';
import { Label } from './components/ui/label';
import { Textarea } from './components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Badge } from './components/ui/badge';
import { Separator } from './components/ui/separator';
import { Progress } from './components/ui/progress';
import { Alert, AlertDescription } from './components/ui/alert';
import { Checkbox } from './components/ui/checkbox';
import { Brain, Users, Heart, Atom, Crown, MessageSquare, Sparkles, Star, Lock, Zap, Search, Filter, CheckCircle, User } from 'lucide-react';
import { getBackendURL } from './config';

import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/admin" element={<AdminApp />} />
        <Route path="/admin/*" element={<AdminApp />} />
        <Route path="/creator" element={<CreatorApp />} />
        <Route path="/creator/*" element={<CreatorApp />} />
        <Route path="/forgot-password" element={<ForgotPasswordApp />} />
        <Route path="/reset-password" element={<ResetPasswordApp />} />
        <Route path="/landing" element={<LandingRedirect />} />
        <Route path="/" element={<MainApp />} />
      </Routes>
    </Router>
  );
}

function AdminApp() {
  const [admin, setAdmin] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if admin is already logged in
    const token = localStorage.getItem('admin_token');
    const adminData = localStorage.getItem('admin_data');
    
    if (token && adminData) {
      try {
        const parsedAdmin = JSON.parse(adminData);
        setAdmin(parsedAdmin);
      } catch (e) {
        // Clear invalid data
        localStorage.removeItem('admin_token');
        localStorage.removeItem('admin_data');
      }
    }
    setIsLoading(false);
  }, []);

  const handleAdminLoginSuccess = (adminData) => {
    setAdmin(adminData.admin);
    localStorage.setItem('admin_token', adminData.token);
    localStorage.setItem('admin_data', JSON.stringify(adminData.admin));
  };

  const handleAdminLoginError = (error) => {
    console.error('Admin login error:', error);
  };

  const handleAdminLogout = () => {
    setAdmin(null);
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_data');
    window.location.href = '/'; // Redirect to main page
  };

  // Show loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-blue-900 flex items-center justify-center">
        <div className="text-white text-center">
          <h2 className="text-2xl font-bold mb-4">Loading...</h2>
        </div>
      </div>
    );
  }

  // Show admin dashboard if authenticated
  if (admin) {
    return <AdminDashboardSimple admin={admin} onLogout={handleAdminLogout} />;
  }

  // Show admin login if not authenticated
  return (
    <AdminLogin 
      onLogin={handleAdminLoginSuccess}
      onError={handleAdminLoginError}
    />
  );
}

function CreatorApp() {
  const [creator, setCreator] = useState(null);
  const [isCreator, setIsCreator] = useState(false);
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [creatorAuthMode, setCreatorAuthMode] = useState('login');

  useEffect(() => {
    // Check if creator is already logged in
    const token = localStorage.getItem('creatorToken');
    const creatorData = localStorage.getItem('creator_data');
    
    if (token && creatorData) {
      try {
        const parsedCreator = JSON.parse(creatorData);
        setCreator(parsedCreator);
        setIsCreator(true);
      } catch (e) {
        // Clear invalid data
        localStorage.removeItem('creatorToken');
        localStorage.removeItem('creator_data');
      }
    }
  }, []);

  const handleCreatorLoginSuccess = (creatorData) => {
    setCreator(creatorData);
    setIsCreator(true);
  };

  const handleCreatorSignupSuccess = (creatorData) => {
    setCreator(creatorData);
    setIsCreator(true);
  };

  if (isCreator && creator) {
    return <CreatorDashboard />;
  }

  // Show forgot password form
  if (showForgotPassword) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <ForgotPasswordForm
          userType="mentor"
          onBack={() => {
            setShowForgotPassword(false);
          }}
          onSuccess={(data) => {
            console.log('Password reset email sent:', data);
            // Show success message or redirect
            setShowForgotPassword(false);
          }}
        />
      </div>
    );
  }

  // Show creator login/signup options
  if (creatorAuthMode === 'login') {
    return (
      <CreatorLogin 
        onSuccess={handleCreatorLoginSuccess}
        onSwitchToSignup={() => setCreatorAuthMode('signup')}
        onForgotPassword={() => {
          setShowForgotPassword(true);
        }}
      />
    );
  } else {
    return (
      <CreatorSignup 
        onSuccess={handleCreatorSignupSuccess}
      />
    );
  }
}

function ForgotPasswordApp() {
  return <ForgotPasswordForm />;
}

function ResetPasswordApp() {
  return <ResetPasswordForm />;
}

function MainApp() {
  // User states
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  
  // Auth states
  const [showCreatorAuth, setShowCreatorAuth] = useState(false);
  const [showAdminAuth, setShowAdminAuth] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [admin, setAdmin] = useState(null);
  
  // Main app states
  const [currentView, setCurrentView] = useState('categories');
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedMentors, setSelectedMentors] = useState([]);
  const [question, setQuestion] = useState('');
  const [responses, setResponses] = useState([]);
  const [authMode, setAuthMode] = useState('login');
  
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [forgotPasswordUserType, setForgotPasswordUserType] = useState('user');
  const [authForm, setAuthForm] = useState({ email: '', password: '', full_name: '' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [questionHistory, setQuestionHistory] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  // Removed selectAll state - now limiting to 5 mentors max
  
  // Mentor type filter state
 // 'all', 'ai', 'human'

  // Category icons mapping
  const categoryIcons = {
    business: Users,
    sports: Crown,
    health: Heart,
    science: Atom,
    relationships: Heart  // Added icon for relationships category
  };

  // Initialize app and check authentication
  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Check for regular user token
        const token = localStorage.getItem('auth_token');
        const userData = localStorage.getItem('user');
        
        if (token && userData) {
          try {
            setUser(JSON.parse(userData));
          } catch (e) {
            console.error('Invalid user data in localStorage:', e);
            localStorage.removeItem('auth_token');
            localStorage.removeItem('user');
          }
        }
        
        await fetchCategories();
      } catch (error) {
        console.error('Auth check failed:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    checkAuth();
  }, []);

  // Google OAuth handlers
  const handleGoogleAuthSuccess = (authData) => {
    try {
      localStorage.setItem('auth_token', authData.access_token);
      
      const userData = {
        user_id: authData.user_id,
        email: authData.email,
        full_name: authData.full_name,
        profile_image_url: authData.profile_image_url,
        questions_asked: 0,
        is_subscribed: false
      };
      
      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
      setSuccess(
        authData.is_new_user 
          ? `Welcome to OnlyMentors.ai, ${authData.full_name}!` 
          : `Welcome back, ${authData.full_name}!`
      );
      setCurrentView('categories');
      setError('');
    } catch (error) {
      console.error('Google auth success handler error:', error);
      setError('Authentication successful but failed to complete login');
    }
  };

  const handleGoogleAuthError = (error) => {
    console.error('Google OAuth error:', error);
    setError(typeof error === 'string' ? error : 'Google authentication failed');
  };

  // Facebook OAuth handlers
  const handleFacebookAuthSuccess = (authData) => {
    try {
      localStorage.setItem('auth_token', authData.access_token);
      
      const userData = {
        user_id: authData.user_id,
        email: authData.email,
        full_name: authData.full_name,
        profile_image_url: authData.profile_image_url,
        questions_asked: 0,
        is_subscribed: false
      };
      
      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
      setSuccess(
        authData.is_new_user 
          ? `Welcome to OnlyMentors.ai, ${authData.full_name}!` 
          : `Welcome back, ${authData.full_name}!`
      );
      setCurrentView('categories');
      setError('');
    } catch (error) {
      console.error('Facebook auth success handler error:', error);
      setError('Authentication successful but failed to complete login');
    }
  };

  const handleFacebookAuthError = (error) => {
    console.error('Facebook OAuth error:', error);
    setError(typeof error === 'string' ? error : 'Facebook authentication failed');
  };

  // API functions
  const fetchCategories = async () => {
    try {
      const backendURL = getBackendURL();
      const response = await fetch(`${backendURL}/api/categories`);
      const data = await response.json();
      setCategories(data.categories);
    } catch (error) {
      console.error('Failed to fetch categories:', error);
    }
  };

  const fetchUserData = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const backendURL = getBackendURL();
      const response = await fetch(`${backendURL}/api/auth/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
      }
    } catch (error) {
      console.error('Failed to fetch user data:', error);
    }
  };

  const fetchQuestionHistory = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const backendURL = getBackendURL();
      const response = await fetch(`${backendURL}/api/questions/history`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setQuestionHistory(data.questions);
      }
    } catch (error) {
      console.error('Failed to fetch question history:', error);
    }
  };

  const handleAuth = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const endpoint = authMode === 'login' ? '/api/auth/login' : '/api/auth/signup';
      const backendURL = getBackendURL();
      const response = await fetch(`${backendURL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(authForm)
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('auth_token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        setUser(data.user);
        setSuccess(authMode === 'login' ? 'Welcome back!' : 'Account created successfully!');
        setCurrentView('categories');
        setAuthForm({ email: '', password: '', full_name: '' });
      } else {
        setError(data.detail || 'Authentication failed');
      }
    } catch (error) {
      setError('Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    setUser(null);
    setCurrentView('categories');
    setSelectedCategory(null);
    setSelectedMentors([]);
    setResponses([]);
    setQuestionHistory([]);
  };

  // Creator auth is now handled in CreatorApp component

  // Admin auth handlers
  const handleAdminLoginSuccess = (adminData) => {
    setIsAdmin(true);
    setAdmin(adminData);
    setShowAdminAuth(false);
  };

  const handleAdminLoginError = (error) => {
    setError(error);
  };

  const handleAdminLogout = () => {
    setIsAdmin(false);
    setAdmin(null);
    localStorage.removeItem('adminToken');
    localStorage.removeItem('adminData');
  };

  const handleMentorSelect = (mentor) => {
    setSelectedMentors(prev => {
      const isSelected = prev.some(m => m.id === mentor.id);
      if (isSelected) {
        // Deselect mentor
        return prev.filter(m => m.id !== mentor.id);
      } else {
        // Check if we're at the 5-mentor limit
        if (prev.length >= 5) {
          setError('You can select a maximum of 5 mentors per question for optimal response time and quality.');
          return prev; // Don't add mentor if at limit
        }
        // Add mentor
        setError(''); // Clear any previous error
        return [...prev, mentor];
      }
    });
  };



  // Removed handleSelectAll function - now limiting to 5 mentors max

  const askQuestion = async () => {
    if (!question.trim() || selectedMentors.length === 0) return;

    setIsLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('auth_token');
      const backendURL = getBackendURL();
      const response = await fetch(`${backendURL}/api/questions/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          category: selectedCategory.id,
          mentor_ids: selectedMentors.map(m => m.id),
          question: question
        })
      });

      const data = await response.json();

      if (response.ok) {
        setResponses(data.responses);
        setQuestion('');
        setCurrentView('responses');
        // Update user data to reflect new question count
        if (user) {
          setUser({
            ...user,
            questions_asked: user.questions_asked + 1
          });
        }
      } else {
        if (response.status === 402) {
          setError(data.detail);
          setCurrentView('subscription');
        } else {
          setError(data.detail || 'Failed to get response');
        }
      }
    } catch (error) {
      setError('Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const initiateSubscription = async (packageId = 'monthly') => {
    try {
      setIsLoading(true);
      const token = localStorage.getItem('auth_token');
      const origin = window.location.origin;

      const backendURL = getBackendURL();
      const response = await fetch(`${backendURL}/api/payments/checkout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          package_id: packageId,
          origin_url: origin
        })
      });

      const data = await response.json();

      if (response.ok) {
        window.location.href = data.url;
      } else {
        setError('Failed to initiate payment');
      }
    } catch (error) {
      setError('Payment error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Check for payment success on page load
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');
    
    if (sessionId && user) {
      checkPaymentStatus(sessionId);
    }
  }, [user]);

  const checkPaymentStatus = async (sessionId, attempts = 0) => {
    const maxAttempts = 5;
    
    if (attempts >= maxAttempts) {
      setError('Payment verification timed out. Please contact support.');
      return;
    }

    try {
      const token = localStorage.getItem('auth_token');
      const backendURL = getBackendURL();
      const response = await fetch(`${backendURL}/api/payments/status/${sessionId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      const data = await response.json();

      if (data.payment_status === 'paid') {
        setSuccess('Payment successful! You now have unlimited access to all mentors.');
        await fetchUserData(); // Refresh user data
        window.history.replaceState({}, document.title, "/");
        return;
      } else if (data.status === 'expired') {
        setError('Payment session expired. Please try again.');
        return;
      }

      // Continue polling
      setTimeout(() => checkPaymentStatus(sessionId, attempts + 1), 2000);
    } catch (error) {
      setError('Error verifying payment. Please contact support.');
    }
  };

  // State for filtered mentors
  const [filteredMentors, setFilteredMentors] = useState([]);
  const [isLoadingMentors, setIsLoadingMentors] = useState(false);

  // Fetch mentors based on search term, category, and mentor type filter
  // Simple function to load mentors - Amazon-style approach
  // Load all mentors when category or search changes
  useEffect(() => {
    if (!selectedCategory) return;
    
    setIsLoadingMentors(true);
    const params = new URLSearchParams();
    if (searchTerm) params.append('q', searchTerm);
    if (selectedCategory.id) params.append('category', selectedCategory.id);
    
    fetch(`${getBackendURL()}/api/search/mentors?${params}`)
      .then(response => response.json())
      .then(data => {
        setFilteredMentors(data.results || []);
        setIsLoadingMentors(false);
      })
      .catch(() => {
        setFilteredMentors([]);
        setIsLoadingMentors(false);
      });
  }, [selectedCategory, searchTerm]);

  // Removed selectAll useEffect - now limiting to 5 mentors max

  // Render functions
  const renderAuth = () => {
    // Show forgot password form
    if (showForgotPassword) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
          <ForgotPasswordForm
            userType={forgotPasswordUserType}
            onBack={() => {
              setShowForgotPassword(false);
              setForgotPasswordUserType('user');
            }}
            onSuccess={(data) => {
              console.log('Password reset email sent:', data);
              // Could show success message or redirect
            }}
          />
        </div>
      );
    }

    return (
    <div className="min-h-screen bg-white">
      {/* Header with Become a Mentor button for non-logged-in users */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-purple-600">OnlyMentors.ai</h1>
              <p className="ml-4 text-gray-600 hidden sm:block">Ask questions to 400+ greatest minds</p>
            </div>
            
            <div className="flex items-center space-x-4">
              <Button 
                onClick={() => setShowCreatorAuth(true)} 
                variant="outline"
                className="text-purple-600 border-purple-600 hover:bg-purple-50"
              >
                Become a Mentor
              </Button>
              <Button 
                onClick={() => window.location.href = '/admin'} 
                variant="outline"
                className="text-red-600 border-red-600 hover:bg-red-50"
              >
                Admin Console
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main auth content */}
      <div className="flex items-center justify-center p-4 py-12">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <Brain className="h-12 w-12 mx-auto text-purple-600 mb-4" />
            <h1 className="text-3xl font-bold text-gray-900 mb-2">OnlyMentors.ai</h1>
            <p className="text-gray-600">Ask questions to 400+ greatest minds</p>
          </div>

          <Card className="bg-white border-gray-200 shadow-lg">
            <CardHeader>
              <Tabs value={authMode} onValueChange={setAuthMode}>
                <TabsList className="grid w-full grid-cols-2 bg-gray-100">
                  <TabsTrigger value="login" className="data-[state=active]:bg-white">Login</TabsTrigger>
                  <TabsTrigger value="signup" className="data-[state=active]:bg-white">Sign Up</TabsTrigger>
                </TabsList>
              </Tabs>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleAuth} className="space-y-4">
                {authMode === 'signup' && (
                  <div>
                    <Label htmlFor="name" className="text-gray-700">Full Name</Label>
                    <Input
                      id="name"
                      type="text"
                      value={authForm.full_name}
                      onChange={(e) => setAuthForm({...authForm, full_name: e.target.value})}
                      className="border-gray-300 focus:border-purple-500 focus:ring-purple-500"
                      required
                    />
                  </div>
                )}
                
                <div>
                  <Label htmlFor="email" className="text-gray-700">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={authForm.email}
                    onChange={(e) => setAuthForm({...authForm, email: e.target.value})}
                    className="border-gray-300 focus:border-purple-500 focus:ring-purple-500"
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="password" className="text-gray-700">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    value={authForm.password}
                    onChange={(e) => setAuthForm({...authForm, password: e.target.value})}
                    className="border-gray-300 focus:border-purple-500 focus:ring-purple-500"
                    required
                  />
                </div>

                {error && (
                  <Alert className="border-red-200 bg-red-50">
                    <AlertDescription className="text-red-700">{error}</AlertDescription>
                  </Alert>
                )}

                {success && (
                  <Alert className="border-green-200 bg-green-50">
                    <AlertDescription className="text-green-700">{success}</AlertDescription>
                  </Alert>
                )}

                <Button 
                  type="submit" 
                  className="w-full bg-purple-600 hover:bg-purple-700" 
                  disabled={isLoading}
                >
                  {isLoading ? 'Processing...' : (authMode === 'login' ? 'Sign In' : 'Create Account')}
                </Button>
              </form>
              
              {/* Divider */}
              <div className="flex items-center my-6">
                <div className="flex-grow border-t border-gray-300"></div>
                <span className="px-4 text-sm text-gray-500 bg-white">or</span>
                <div className="flex-grow border-t border-gray-300"></div>
              </div>
              
              {/* OAuth Buttons */}
              <div className="space-y-3">
                <GoogleOAuthButton
                  onSuccess={handleGoogleAuthSuccess}
                  onError={handleGoogleAuthError}
                  disabled={isLoading}
                  text={authMode === 'login' ? "signin_with" : "signup_with"}
                />
                <FacebookOAuthButton
                  onSuccess={handleFacebookAuthSuccess}
                  onError={handleFacebookAuthError}
                  disabled={isLoading}
                  text={authMode === 'login' ? "Continue with Facebook" : "Sign up with Facebook"}
                />
              </div>

              {/* Forgot Password Link */}
              {authMode === 'login' && (
                <div className="text-center">
                  <button
                    type="button"
                    onClick={() => {
                      setForgotPasswordUserType('user');
                      setShowForgotPassword(true);
                    }}
                    className="text-sm text-purple-600 hover:text-purple-700 underline"
                    disabled={isLoading}
                  >
                    Forgot your password?
                  </button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
    );
  };

  const renderCategories = () => (
    <div className="min-h-screen bg-white">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Brain className="h-10 w-10 text-purple-600" />
            <h1 className="text-4xl font-bold text-gray-900">OnlyMentors.ai</h1>
          </div>
          <p className="text-xl text-gray-600 mb-6">Ask questions to history's greatest minds</p>
          
          {user && (
            <div className="bg-purple-50 p-4 rounded-lg mb-8 flex justify-between items-center">
              <div className="text-sm text-gray-700">
                Welcome back, <span className="text-purple-600 font-semibold">{user.full_name}</span>
              </div>
              <div className="flex items-center gap-2">
                {user.is_subscribed ? (
                  <Badge className="bg-green-100 text-green-800 border-green-200">
                    <Crown className="h-3 w-3 mr-1" />
                    Unlimited Access
                  </Badge>
                ) : (
                  <Badge className="bg-purple-100 text-purple-800 border-purple-200">
                    {10 - user.questions_asked} free questions left
                  </Badge>
                )}
                {/* Profile and Logout buttons */}
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => setCurrentView('profile')} 
                  className="border-purple-300 text-purple-600 hover:bg-purple-50"
                >
                  <User className="h-4 w-4 mr-1" />
                  Profile
                </Button>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={handleLogout} 
                  className="border-gray-300 text-gray-600 hover:bg-gray-50"
                >
                  Logout
                </Button>
              </div>
            </div>
          )}

          {user && !user.is_subscribed && (
            <Progress value={(user?.questions_asked || 0) * 10} className="w-64 mx-auto mb-4" />
          )}
        </div>

        {/* Categories Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {categories.map((category) => {
            const IconComponent = categoryIcons[category.id];
            return (
              <Card
                key={category.id}
                className="bg-white border-gray-200 hover:border-purple-300 hover:shadow-lg transition-all duration-300 cursor-pointer group"
                onClick={() => {
                  setSelectedCategory(category);
                  setSelectedMentors([]);
                  setSearchTerm('');
                  setCurrentView('mentors');
                }}
              >
                <CardHeader className="text-center">
                  <div className="mx-auto mb-4 p-3 bg-purple-100 rounded-full w-fit group-hover:bg-purple-200 transition-colors">
                    <IconComponent className="h-8 w-8 text-purple-600" />
                  </div>
                  <CardTitle className="text-gray-900">{category.name}</CardTitle>
                  <CardDescription className="text-gray-600 text-sm">
                    {category.description}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center">
                    <Badge variant="secondary" className="bg-purple-100 text-purple-800">
                      {category.count} mentors
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* History Button */}
        {user && user.questions_asked > 0 && (
          <div className="text-center mt-12">
            <Button
              variant="outline"
              onClick={() => {
                fetchQuestionHistory();
                setCurrentView('history');
              }}
              className="border-purple-300 text-purple-600 hover:bg-purple-50"
            >
              <MessageSquare className="h-4 w-4 mr-2" />
              View Question History ({user.questions_asked})
            </Button>
          </div>
        )}
      </div>
    </div>
  );

  const renderMentors = () => (
    <div className="min-h-screen bg-white">
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center gap-4 mb-8 flex-wrap">
          <Button
            variant="outline"
            onClick={() => setCurrentView('categories')}
            className="border-gray-300 text-gray-600 hover:bg-gray-50"
          >
            ← Back to Categories
          </Button>
          <div className="flex items-center gap-3">
            {React.createElement(categoryIcons[selectedCategory.id], {
              className: "h-8 w-8 text-purple-600"
            })}
            <h1 className="text-3xl font-bold text-gray-900">{selectedCategory.name} Mentors</h1>
          </div>
        </div>

        {/* Search and Controls */}
        <div className="mb-8 space-y-4">
          <div className="flex gap-4 items-center flex-wrap">
            <div className="relative flex-1 min-w-64">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                type="text"
                placeholder="Search mentors by name or expertise..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 border-gray-300 focus:border-purple-500 focus:ring-purple-500"
              />
            </div>
            

            
            <div className="text-sm text-gray-600">
              Select up to <span className="font-semibold">5 mentors</span> for your question ({selectedMentors.length}/5 selected)
            </div>
          </div>

          {selectedMentors.length > 0 && user && (
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <div className="flex items-center justify-between flex-wrap gap-4">
                <div className="text-gray-900">
                  <span className="font-semibold">{selectedMentors.length} mentors selected</span>
                  <p className="text-sm text-gray-600">They will all answer your next question</p>
                </div>
                <Button
                  onClick={() => setCurrentView('question')}
                  className="bg-purple-600 hover:bg-purple-700"
                >
                  <Zap className="h-4 w-4 mr-2" />
                  Ask Question
                </Button>
              </div>
            </div>
          )}
        </div>

        {/* OnlyFans-style White Mentors Grid */}
        {isLoadingMentors ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
            <span className="ml-3 text-gray-600">Loading mentors...</span>
          </div>
        ) : filteredMentors.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">
              {mentorTypeFilter === 'ai' ? '🤖' : 
               mentorTypeFilter === 'human' ? '👥' : 
               '🔍'}
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              {mentorTypeFilter === 'ai' ? 'No AI Mentors Found' :
               mentorTypeFilter === 'human' ? 'No Human Mentors Available Yet' :
               'No Mentors Found'}
            </h3>
            <p className="text-gray-600 mb-4 max-w-md mx-auto">
              {mentorTypeFilter === 'ai' ? 
                searchTerm ? `No AI mentors match "${searchTerm}". Try different keywords or browse all categories.` :
                'No AI mentors found in this category. Try browsing other categories.' :
               mentorTypeFilter === 'human' ? 
                'Human mentors will appear here once professional creators join and get verified. Meanwhile, explore our AI mentors for instant guidance!' :
                searchTerm ? `No mentors match "${searchTerm}". Try different keywords or clear your search.` :
                'No mentors found. Try browsing different categories or clearing your search.'
              }
            </p>
            {mentorTypeFilter === 'human' ? (
              <div className="space-y-3">
                <button
                  onClick={() => setMentorTypeFilter('ai')}
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  🤖 Explore AI Mentors Instead
                </button>
                <div className="text-sm text-gray-500">
                  <p>Want to become a human mentor? 
                    <button className="text-purple-600 hover:text-purple-700 underline ml-1">
                      Join as a Creator
                    </button>
                  </p>
                </div>
              </div>
            ) : (
              <button
                onClick={() => {
                  setSearchTerm('');
                  setMentorTypeFilter('all');
                }}
                className="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 transition-colors"
              >
                Clear Filters & Show All Mentors
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          {filteredMentors.map((mentor) => {
            const isSelected = selectedMentors.some(m => m.id === mentor.id);
            const isAtLimit = selectedMentors.length >= 5 && !isSelected;
            return (
              <Card
                key={mentor.id}
                className={`bg-white border-gray-200 transition-all duration-300 relative ${
                  isSelected 
                    ? 'ring-2 ring-purple-500 border-purple-500 bg-purple-50' 
                    : isAtLimit 
                      ? 'opacity-50 cursor-not-allowed' 
                      : 'hover:border-purple-300 hover:shadow-md cursor-pointer'
                } group`}
                onClick={() => user && handleMentorSelect(mentor)}
              >
                {/* Selection Checkbox */}
                {user && (
                  <div className="absolute top-2 right-2 z-10">
                    <div className="bg-white rounded-full p-1 shadow-sm border border-gray-200">
                      {isSelected ? (
                        <CheckCircle className="h-5 w-5 text-purple-600" />
                      ) : (
                        <div className="h-5 w-5 border-2 border-gray-300 rounded-full" />
                      )}
                    </div>
                  </div>
                )}

                {/* Mentor Image */}
                <div className="relative">
                  <div className="w-full h-48 rounded-t-lg bg-gray-200 flex items-center justify-center">
                    {mentor.image_url ? (
                      <img 
                        src={mentor.image_url} 
                        alt={mentor.name}
                        className="object-cover w-full h-full rounded-t-lg"
                      />
                    ) : (
                      <div className="bg-gray-100 text-gray-600 text-xl font-bold w-full h-full rounded-t-lg flex items-center justify-center">
                        <User className="h-12 w-12" />
                      </div>
                    )}
                  </div>
                  
                  {/* Hover overlay */}
                  <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-all duration-300 rounded-t-lg flex items-center justify-center">
                    <div className="opacity-0 group-hover:opacity-100 transition-all duration-300">
                      {isSelected ? (
                        <div className="text-white text-center">
                          <Star className="h-6 w-6 mx-auto mb-1 text-purple-400" />
                          <p className="text-sm">Selected</p>
                        </div>
                      ) : (
                        <div className="text-white text-center">
                          <MessageSquare className="h-6 w-6 mx-auto mb-1" />
                          <p className="text-sm">Select to Ask</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Mentor Info */}
                <CardContent className="p-3 space-y-2">
                  <h3 className="text-gray-900 font-semibold text-sm leading-tight">{mentor.name}</h3>
                  <p className="text-purple-600 text-xs">{mentor.title}</p>
                  <p className="text-gray-600 text-xs leading-tight line-clamp-2">{mentor.bio}</p>
                  
                  {/* Expertise Tags */}
                  <div className="flex flex-wrap gap-1 mb-2">
                    {mentor.expertise.split(', ').slice(0, 2).map((skill, index) => (
                      <Badge key={index} variant="secondary" className="bg-purple-100 text-purple-700 text-xs px-1 py-0">
                        {skill}
                      </Badge>
                    ))}
                  </div>

                  {/* Mentor Type Badge */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-1">
                      {mentor.mentor_type === 'ai' ? (
                        <Badge className="bg-blue-100 text-blue-700 text-xs px-2 py-0.5">
                          🤖 AI Mentor
                        </Badge>
                      ) : (
                        <div className="flex items-center space-x-1">
                          <Badge className="bg-green-100 text-green-700 text-xs px-2 py-0.5">
                            👥 Human
                          </Badge>
                          {mentor.tier && mentor.tier !== 'New Mentor' && (
                            <Badge 
                              className="text-xs px-2 py-0.5"
                              style={{ 
                                backgroundColor: `${mentor.tier_badge_color}15`, 
                                color: mentor.tier_badge_color,
                                border: `1px solid ${mentor.tier_badge_color}`
                              }}
                            >
                              {mentor.tier_level === 'ultimate' && '👑'}
                              {mentor.tier_level === 'platinum' && '💎'}
                              {mentor.tier_level === 'gold' && '🥇'}
                              {mentor.tier_level === 'silver' && '🥈'}
                              {mentor.tier?.replace(' Mentor', '')}
                            </Badge>
                          )}
                        </div>
                      )}
                    </div>
                    {mentor.mentor_type === 'human' && mentor.subscriber_count > 0 && (
                      <span className="text-xs text-gray-500">
                        {mentor.subscriber_count >= 1000 
                          ? `${Math.floor(mentor.subscriber_count / 1000)}K` 
                          : mentor.subscriber_count} subs
                      </span>
                    )}
                  </div>

                </CardContent>

                {!user && (
                  <div className="absolute inset-0 bg-white/90 flex items-center justify-center rounded-lg">
                    <div className="text-center">
                      <Lock className="h-6 w-6 mx-auto mb-2 text-gray-600" />
                      <p className="text-gray-600 text-sm">Login to Ask</p>
                    </div>
                  </div>
                )}
              </Card>
            );
          })}
        </div>
        )}
      </div>
    </div>
  );

  const renderQuestion = () => (
    <div className="min-h-screen bg-white">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-4 mb-8">
            <Button
              variant="outline"
              onClick={() => setCurrentView('mentors')}
              className="border-gray-300 text-gray-600 hover:bg-gray-50"
            >
              ← Back to Mentors
            </Button>
            <h1 className="text-2xl font-bold text-gray-900">
              Ask {selectedMentors.length} {selectedMentors.length === 1 ? 'Mentor' : 'Mentors'}
            </h1>
          </div>

          {/* Selected Mentors Display */}
          <div className="mb-8">
            <h3 className="text-gray-900 text-lg mb-4">Selected Mentors ({selectedMentors.length})</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
              {selectedMentors.map((mentor) => (
                <div key={mentor.id} className="text-center">
                  <div className="h-16 w-16 mx-auto mb-2 rounded-full bg-gray-200 flex items-center justify-center">
                    {mentor.image_url ? (
                      <img src={mentor.image_url} alt={mentor.name} className="h-16 w-16 rounded-full object-cover" />
                    ) : (
                      <div className="bg-purple-100 text-purple-600 font-bold h-16 w-16 rounded-full flex items-center justify-center">
                        <User className="h-8 w-8" />
                      </div>
                    )}
                  </div>
                  <p className="text-gray-900 text-sm font-medium leading-tight">{mentor.name}</p>
                  <p className="text-purple-600 text-xs">{mentor.title}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Question Form */}
          <Card className="bg-white border-gray-200 shadow-lg mb-8">
            <CardHeader>
              <CardTitle className="text-gray-900 flex items-center gap-2">
                <MessageSquare className="h-5 w-5" />
                Ask Your Question
              </CardTitle>
              <CardDescription className="text-gray-600">
                Get personalized wisdom from {selectedMentors.length} legendary {selectedMentors.length === 1 ? 'mind' : 'minds'}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label className="text-gray-700 mb-2 block">Your Question</Label>
                <Textarea
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="What would you like to ask these mentors?"
                  className="border-gray-300 focus:border-purple-500 focus:ring-purple-500 min-h-[100px]"
                  maxLength={500}
                />
                <div className="text-right text-sm text-gray-500 mt-1">
                  {question.length}/500
                </div>
              </div>

              {error && (
                <Alert className="border-red-200 bg-red-50">
                  <AlertDescription className="text-red-700">{error}</AlertDescription>
                </Alert>
              )}

              <Button
                onClick={askQuestion}
                disabled={!question.trim() || isLoading || selectedMentors.length === 0 || (!user?.is_subscribed && user?.questions_asked >= 10)}
                className="w-full bg-purple-600 hover:bg-purple-700"
              >
                {isLoading ? (
                  <>
                    <Sparkles className="h-4 w-4 mr-2 animate-spin" />
                    Getting wisdom from {selectedMentors.length} {selectedMentors.length === 1 ? 'mentor' : 'mentors'}...
                  </>
                ) : (
                  <>
                    <Zap className="h-4 w-4 mr-2" />
                    Ask {selectedMentors.length} {selectedMentors.length === 1 ? 'Mentor' : 'Mentors'}
                    {!user?.is_subscribed && ` (${Math.max(0, 10 - (user?.questions_asked || 0))} remaining)`}
                  </>
                )}
              </Button>

              {!user?.is_subscribed && user?.questions_asked >= 10 && (
                <div className="text-center p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <Lock className="h-8 w-8 mx-auto text-yellow-600 mb-2" />
                  <p className="text-yellow-700 mb-3">You've used all your free questions!</p>
                  <Button onClick={() => setCurrentView('subscription')} className="bg-purple-600 hover:bg-purple-700">
                    Upgrade for Unlimited Access
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );

  const renderResponses = () => (
    <div className="min-h-screen bg-white">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-4 mb-8">
            <Button
              variant="outline"
              onClick={() => setCurrentView('mentors')}
              className="border-gray-300 text-gray-600 hover:bg-gray-50"
            >
              ← Back to Mentors
            </Button>
            <h1 className="text-2xl font-bold text-gray-900">Mentor Responses</h1>
          </div>

          {/* Responses */}
          <div className="space-y-6">
            {responses.map((response, index) => (
              <Card key={index} className="bg-white border-gray-200 shadow-lg">
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <div className="h-12 w-12 rounded-full bg-gray-200 flex items-center justify-center">
                      {response.mentor.image_url ? (
                        <img src={response.mentor.image_url} alt={response.mentor.name} className="h-12 w-12 rounded-full object-cover" />
                      ) : (
                        <div className="bg-purple-100 text-purple-600 font-bold h-12 w-12 rounded-full flex items-center justify-center">
                          <User className="h-6 w-6" />
                        </div>
                      )}
                    </div>
                    <div>
                      <CardTitle className="text-gray-900">{response.mentor.name}</CardTitle>
                      <CardDescription className="text-purple-600">
                        {response.mentor.title}
                      </CardDescription>
                    </div>
                    <Star className="h-5 w-5 text-yellow-500 ml-auto" />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="prose prose-gray max-w-none">
                    <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">{response.response}</p>
                  </div>
                </CardContent>
              </Card>
            ))}

            {/* Action Buttons */}
            <div className="flex gap-4 justify-center pt-6">
              <Button
                variant="outline"
                onClick={() => {
                  setSelectedMentors([]);
                  setCurrentView('mentors');
                }}
                className="border-gray-300 text-gray-600 hover:bg-gray-50"
              >
                Ask Different Mentors
              </Button>
              <Button
                onClick={() => {
                  setQuestion('');
                  setCurrentView('question');
                }}
                className="bg-purple-600 hover:bg-purple-700"
              >
                Ask Another Question
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderSubscription = () => (
    <div className="min-h-screen bg-white flex items-center justify-center p-4">
      <div className="max-w-4xl w-full">
        <Card className="bg-white border-gray-200 shadow-lg">
          <CardHeader className="text-center">
            <Crown className="h-16 w-16 mx-auto text-yellow-500 mb-4" />
            <CardTitle className="text-3xl text-gray-900 mb-2">Unlock All Mentors</CardTitle>
            <CardDescription className="text-gray-600 text-lg">
              Get unlimited access to history's greatest minds
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
              {/* Monthly Plan */}
              <div className="bg-purple-50 rounded-lg p-6 border border-purple-200">
                <div className="text-center">
                  <h3 className="text-xl font-bold text-gray-900 mb-2">Monthly</h3>
                  <div className="text-4xl font-bold text-gray-900 mb-1">$29.99</div>
                  <div className="text-purple-600 text-sm mb-6">per month</div>
                  <div className="space-y-3 text-left mb-6">
                    <div className="flex items-center gap-2 text-gray-700">
                      <Star className="h-4 w-4 text-yellow-500" />
                      Unlimited questions to all mentors
                    </div>
                    <div className="flex items-center gap-2 text-gray-700">
                      <Star className="h-4 w-4 text-yellow-500" />
                      All 4 categories (Business, Sports, Health, Science)
                    </div>
                    <div className="flex items-center gap-2 text-gray-700">
                      <Star className="h-4 w-4 text-yellow-500" />
                      Multiple mentor responses per question
                    </div>
                    <div className="flex items-center gap-2 text-gray-700">
                      <Star className="h-4 w-4 text-yellow-500" />
                      Complete question history
                    </div>
                  </div>
                  <Button 
                    onClick={() => initiateSubscription('monthly')}
                    disabled={isLoading}
                    className="w-full bg-purple-600 hover:bg-purple-700"
                  >
                    {isLoading ? 'Processing...' : 'Start Monthly Plan'}
                  </Button>
                </div>
              </div>

              {/* Yearly Plan */}
              <div className="bg-green-50 rounded-lg p-6 border border-green-200 relative">
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <Badge className="bg-green-600 text-white">Save $60</Badge>
                </div>
                <div className="text-center">
                  <h3 className="text-xl font-bold text-gray-900 mb-2">Yearly</h3>
                  <div className="text-4xl font-bold text-gray-900 mb-1">$299.99</div>
                  <div className="text-green-600 text-sm mb-6">per year ($24.99/month)</div>
                  <div className="space-y-3 text-left mb-6">
                    <div className="flex items-center gap-2 text-gray-700">
                      <Star className="h-4 w-4 text-yellow-500" />
                      Everything in Monthly plan
                    </div>
                    <div className="flex items-center gap-2 text-gray-700">
                      <Star className="h-4 w-4 text-yellow-500" />
                      Save 2 months ($60 savings)
                    </div>
                    <div className="flex items-center gap-2 text-gray-700">
                      <Star className="h-4 w-4 text-yellow-500" />
                      Priority support
                    </div>
                    <div className="flex items-center gap-2 text-gray-700">
                      <Star className="h-4 w-4 text-yellow-500" />
                      Early access to new mentors
                    </div>
                  </div>
                  <Button 
                    onClick={() => initiateSubscription('yearly')}
                    disabled={isLoading}
                    className="w-full bg-green-600 hover:bg-green-700"
                  >
                    {isLoading ? 'Processing...' : 'Start Yearly Plan'}
                  </Button>
                </div>
              </div>
            </div>

            {error && (
              <Alert className="border-red-200 bg-red-50 mb-6">
                <AlertDescription className="text-red-700">{error}</AlertDescription>
              </Alert>
            )}

            <div className="text-center">
              <Button
                variant="outline"
                onClick={() => setCurrentView('categories')}
                className="border-gray-300 text-gray-600 hover:bg-gray-50"
              >
                Back to Categories
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );

  const renderHistory = () => (
    <div className="min-h-screen bg-white">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-4 mb-8">
            <Button
              variant="outline"
              onClick={() => setCurrentView('categories')}
              className="border-gray-300 text-gray-600 hover:bg-gray-50"
            >
              ← Back to Categories
            </Button>
            <h1 className="text-3xl font-bold text-gray-900">Question History</h1>
          </div>

          <div className="space-y-6">
            {questionHistory.map((item, index) => (
              <Card key={item.question_id} className="bg-white border-gray-200 shadow-lg">
                <CardHeader>
                  <div className="flex items-center gap-3 mb-2">
                    <MessageSquare className="h-5 w-5 text-purple-600" />
                    <div className="text-purple-600 text-sm">{new Date(item.created_at).toLocaleDateString()}</div>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-3">
                    <p className="text-gray-700 italic text-sm">"{item.question}"</p>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {item.responses && item.responses.map((response, idx) => (
                    <div key={idx} className="border-l-2 border-purple-300 pl-4">
                      <div className="flex items-center gap-2 mb-2">
                        <div className="h-6 w-6 rounded-full bg-gray-200 flex items-center justify-center">
                          {response.mentor?.image_url ? (
                            <img src={response.mentor?.image_url} alt={response.mentor?.name} className="h-6 w-6 rounded-full object-cover" />
                          ) : (
                            <div className="bg-purple-100 text-purple-600 text-xs h-6 w-6 rounded-full flex items-center justify-center">
                              <User className="h-3 w-3" />
                            </div>
                          )}
                        </div>
                        <div className="text-gray-900 font-medium text-sm">{response.mentor?.name}</div>
                      </div>
                      <p className="text-gray-800 text-sm leading-relaxed">{response.response}</p>
                    </div>
                  ))}
                </CardContent>
              </Card>
            ))}
            
            {questionHistory.length === 0 && (
              <Card className="bg-white border-gray-200 shadow-lg">
                <CardContent className="text-center py-12">
                  <MessageSquare className="h-16 w-16 mx-auto text-gray-400 mb-4" />
                  <p className="text-gray-600">No questions asked yet. Start your journey!</p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );

  // Render loading screen
  if (isLoading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading OnlyMentors.ai...</p>
        </div>
      </div>
    );
  }

  // Handle success from comprehensive UserSignup component
  const handleUserSignupSuccess = (userData) => {
    setUser(userData);
    setSuccess('Account created successfully with complete profile!');
    setCurrentView('categories');
  };

  // Render comprehensive user signup
  if (authMode === 'signup' && !user) {
    return (
      <UserSignup 
        onSuccess={handleUserSignupSuccess}
        onSwitchToLogin={() => setAuthMode('login')}
      />
    );
  }

  // Render creator authentication (redirects to /creator)
  if (showCreatorAuth) {
    window.location.href = '/creator';
    return null;
  }

  // Render admin authentication
  if (showAdminAuth) {
    return (
      <AdminLogin 
        onLogin={handleAdminLoginSuccess}
        onError={handleAdminLoginError}
      />
    );
  }

  // Render admin dashboard
  if (isAdmin && admin) {
    return <AdminDashboardSimple admin={admin} onLogout={handleAdminLogout} />;
  }

  // Creator dashboard is handled in CreatorApp component, not MainApp

  // FORCE RELOAD TRIGGER - RANDOM COMMENT CHANGE 12345
  const renderHeader = () => (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-purple-600">OnlyMentors.ai</h1>
            <p className="ml-4 text-gray-600 hidden sm:block">Ask questions to 400+ greatest minds</p>
          </div>
          
          <div className="flex items-center space-x-4">
            {user ? (
              <>
                <span className="text-gray-700">Welcome, {user.full_name}</span>
                <span className="bg-purple-100 text-purple-700 px-3 py-1 rounded-full text-sm">
                  {user.is_subscribed ? 'Unlimited' : `${Math.max(0, 10 - user.questions_asked)} questions left`}
                </span>
                <Button 
                  onClick={() => setCurrentView('profile')} 
                  variant="outline"
                  className="text-purple-600 hover:text-purple-700"
                >
                  <User className="h-4 w-4 mr-1" />
                  Profile
                </Button>
                <Button 
                  onClick={handleLogout} 
                  variant="outline"
                  className="text-gray-600 hover:text-gray-800"
                >
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Button 
                  onClick={() => setShowCreatorAuth(true)} 
                  variant="outline"
                  className="text-purple-600 border-purple-600 hover:bg-purple-50"
                >
                  Become a Mentor
                </Button>
                <Button 
                  onClick={() => window.location.href = '/admin'} 
                  variant="outline"
                  className="text-red-600 border-red-600 hover:bg-red-50"
                >
                  Admin Console
                </Button>
                <Button 
                  onClick={() => setAuthMode('login')} 
                  variant="outline"
                  className="text-gray-600 hover:text-gray-800"
                >
                  Login
                </Button>
                <Button 
                  onClick={() => setAuthMode('signup')} 
                  className="bg-purple-600 hover:bg-purple-700 text-white"
                >
                  Sign Up
                </Button>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );

  // Main render logic
  if (!user) {
    return renderAuth();
  }

  return (
    <div className="min-h-screen bg-white">
      {renderHeader()}
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded mb-6">
            {success}
          </div>
        )}

        {(() => {
          switch (currentView) {
            case 'categories':
              return renderCategories();
            case 'mentors':
              return renderMentors();
            case 'question':
              return renderQuestion();
            case 'responses':
              return renderResponses();
            case 'subscription':
              return renderSubscription();
            case 'history':
              return renderHistory();
            case 'profile':
              return (
                <UserProfile 
                  user={user}
                  onProfileUpdate={(updatedProfile) => {
                    const updatedUser = { ...user, ...updatedProfile };
                    setUser(updatedUser);
                    localStorage.setItem('user', JSON.stringify(updatedUser));
                  }}
                  onLogout={handleLogout}
                />
              );
            default:
              return renderCategories();
          }
        })()}
      </main>

    </div>
  );
}

export default App; 
// TRIGGER

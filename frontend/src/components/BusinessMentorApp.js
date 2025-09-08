import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { Separator } from './ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Building, Users, MessageSquare, TrendingUp, Calendar, User, LogOut, Crown, Star } from 'lucide-react';
import BusinessMentorSignup from './BusinessMentorSignup';
import { getBackendURL } from '../config';

const BusinessMentorApp = ({ businessSlug }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [showSignup, setShowSignup] = useState(false);
  const [businessConfig, setBusinessConfig] = useState(null);
  
  // Dashboard state
  const [stats, setStats] = useState({
    total_questions: 0,
    questions_this_month: 0,
    active_employees: 0,
    average_rating: 5.0
  });
  const [recentQuestions, setRecentQuestions] = useState([]);
  const [activeTab, setActiveTab] = useState('dashboard');

  useEffect(() => {
    checkAuthentication();
    loadBusinessConfig();
  }, [businessSlug]);

  useEffect(() => {
    if (isAuthenticated && user) {
      loadDashboardData();
    }
  }, [isAuthenticated, user]);

  const checkAuthentication = async () => {
    try {
      const token = localStorage.getItem('mentorToken') || localStorage.getItem('token');
      
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
        
        // Check if user is a business mentor (business employee who is also a mentor)
        if (userData.user.user_type === 'business_employee' && userData.user.is_mentor) {
          setUser(userData.user);
          setIsAuthenticated(true);
        } else {
          // Clear invalid token
          localStorage.removeItem('mentorToken');
          localStorage.removeItem('token');
        }
      } else {
        localStorage.removeItem('mentorToken');
        localStorage.removeItem('token');
      }
    } catch (error) {
      console.error('Authentication check failed:', error);
      localStorage.removeItem('mentorToken');
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

  const loadDashboardData = async () => {
    try {
      const backendURL = getBackendURL();
      const token = localStorage.getItem('mentorToken') || localStorage.getItem('token');
      
      // Load mentor stats (placeholder for now)
      setStats({
        total_questions: 42,
        questions_this_month: 12,
        active_employees: 25,
        average_rating: 4.8
      });
      
      // Load recent questions (placeholder)
      setRecentQuestions([
        {
          id: '1',
          question: 'What strategies do you recommend for improving team productivity?',
          employee: 'Sarah Johnson',
          department: 'Engineering',
          timestamp: '2 hours ago',
          status: 'answered'
        },
        {
          id: '2',
          question: 'How do you handle difficult conversations with stakeholders?',
          employee: 'Mike Chen',
          department: 'Product',
          timestamp: '1 day ago',
          status: 'pending'
        },
        {
          id: '3',
          question: 'What are the key principles of effective leadership?',
          employee: 'Lisa Davis',
          department: 'Marketing',
          timestamp: '2 days ago',
          status: 'answered'
        }
      ]);
      
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
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
        
        // Verify user is a business mentor
        if (data.user.user_type === 'business_employee' && data.user.is_mentor) {
          localStorage.setItem('mentorToken', data.token);
          setUser(data.user);
          setIsAuthenticated(true);
        } else {
          throw new Error('Access denied. Business mentor account required.');
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
    localStorage.setItem('mentorToken', userData.token);
    setUser(userData.user);
    setIsAuthenticated(true);
    setShowSignup(false);
  };

  const handleLogout = () => {
    localStorage.removeItem('mentorToken');
    localStorage.removeItem('token');
    setUser(null);
    setIsAuthenticated(false);
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
      <BusinessMentorSignup
        businessSlug={businessSlug}
        businessConfig={businessConfig}
        onSuccess={handleSignupSuccess}
        onBack={() => setShowSignup(false)}
      />
    );
  }

  if (!isAuthenticated) {
    return (
      <BusinessMentorLogin
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
                <Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-200">
                  <Crown className="w-3 h-3 mr-1" />
                  Mentor Portal
                </Badge>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                👨‍🏫 {user.full_name}
              </span>
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
            Welcome to Your Business Mentor Dashboard
          </h1>
          <p className="text-gray-600">
            Help guide your colleagues and share your expertise within {businessConfig?.company_name || 'your organization'}.
          </p>
        </div>

        {/* Dashboard Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
            <TabsTrigger value="questions">Questions</TabsTrigger>
            <TabsTrigger value="profile">Profile</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>

          {/* Dashboard Tab */}
          <TabsContent value="dashboard" className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Questions</CardTitle>
                  <MessageSquare className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.total_questions}</div>
                  <p className="text-xs text-muted-foreground">All time</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">This Month</CardTitle>
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.questions_this_month}</div>
                  <p className="text-xs text-muted-foreground">Questions answered</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Active Employees</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.active_employees}</div>
                  <p className="text-xs text-muted-foreground">Seeking guidance</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Rating</CardTitle>
                  <Star className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.average_rating}</div>
                  <p className="text-xs text-muted-foreground">Average rating</p>
                </CardContent>
              </Card>
            </div>

            {/* Recent Questions */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Questions</CardTitle>
                <CardDescription>
                  Questions from your colleagues that need your attention
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recentQuestions.map(question => (
                    <div key={question.id} className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg">
                      <div className="flex-1">
                        <p className="font-medium text-gray-900 mb-1">
                          {question.question}
                        </p>
                        <div className="flex items-center space-x-4 text-sm text-gray-600">
                          <span>👤 {question.employee}</span>
                          <span>🏢 {question.department}</span>
                          <span>⏰ {question.timestamp}</span>
                        </div>
                      </div>
                      <Badge
                        variant={question.status === 'answered' ? 'default' : 'outline'}
                        className={question.status === 'answered' ? 'bg-green-100 text-green-800' : ''}
                      >
                        {question.status === 'answered' ? 'Answered' : 'Pending'}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Questions Tab */}
          <TabsContent value="questions">
            <Card>
              <CardHeader>
                <CardTitle>All Questions</CardTitle>
                <CardDescription>
                  Manage questions from your colleagues
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Question management interface will be implemented here.
                  This would include filtering, searching, and responding to questions.
                </p>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Profile Tab */}
          <TabsContent value="profile">
            <Card>
              <CardHeader>
                <CardTitle>Mentor Profile</CardTitle>
                <CardDescription>
                  Manage your mentor profile and expertise areas
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="full_name">Full Name</Label>
                  <Input id="full_name" value={user.full_name} disabled />
                </div>
                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" value={user.email} disabled />
                </div>
                <div>
                  <Label htmlFor="department">Department</Label>
                  <Input id="department" value={user.department_code || 'Not specified'} disabled />
                </div>
                <div>
                  <Label htmlFor="bio">Bio</Label>
                  <Textarea 
                    id="bio" 
                    placeholder="Share your background and expertise to help colleagues understand how you can help them..."
                    rows={4}
                  />
                </div>
                <Button>Update Profile</Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="settings">
            <Card>
              <CardHeader>
                <CardTitle>Mentor Settings</CardTitle>
                <CardDescription>
                  Configure your mentoring preferences
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Availability</Label>
                  <div className="space-y-2">
                    <label className="flex items-center space-x-2">
                      <input type="checkbox" defaultChecked />
                      <span className="text-sm">Available for new questions</span>
                    </label>
                    <label className="flex items-center space-x-2">
                      <input type="checkbox" defaultChecked />
                      <span className="text-sm">Email notifications for new questions</span>
                    </label>
                    <label className="flex items-center space-x-2">
                      <input type="checkbox" />
                      <span className="text-sm">Weekly summary reports</span>
                    </label>
                  </div>
                </div>
                
                <Separator />
                
                <div className="space-y-2">
                  <Label>Response Time</Label>
                  <select className="w-full p-2 border rounded">
                    <option>Within 24 hours</option>
                    <option>Within 48 hours</option>
                    <option>Within 1 week</option>
                  </select>
                </div>
                
                <Button>Save Settings</Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

// Business Mentor Login Component
const BusinessMentorLogin = ({ businessSlug, businessConfig, onLogin, onShowSignup }) => {
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
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-100 flex items-center justify-center px-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="text-3xl mb-4">👨‍🏫</div>
          <CardTitle className="text-2xl">
            {businessConfig?.company_name || 'Business'} Mentor Portal
          </CardTitle>
          <CardDescription>
            Sign in to your mentor dashboard to help guide your colleagues
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
            Want to become a mentor? Apply now
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};

export default BusinessMentorApp;
import React, { useState, useEffect } from 'react';
import { Button } from './components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Input } from './components/ui/input';
import { Label } from './components/ui/label';
import { Textarea } from './components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Badge } from './components/ui/badge';
import { Separator } from './components/ui/separator';
import { Avatar, AvatarFallback, AvatarImage } from './components/ui/avatar';
import { Progress } from './components/ui/progress';
import { Alert, AlertDescription } from './components/ui/alert';
import { Checkbox } from './components/ui/checkbox';
import { Brain, Users, Heart, Atom, Crown, MessageSquare, Sparkles, Star, Lock, Zap, Search, Filter } from 'lucide-react';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  // State management
  const [user, setUser] = useState(null);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedMentors, setSelectedMentors] = useState([]); // Multiple mentors
  const [question, setQuestion] = useState('');
  const [responses, setResponses] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [authMode, setAuthMode] = useState('login');
  const [authForm, setAuthForm] = useState({ email: '', password: '', full_name: '' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [questionHistory, setQuestionHistory] = useState([]);
  const [currentView, setCurrentView] = useState('categories');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectAll, setSelectAll] = useState(false);

  // Category icons mapping
  const categoryIcons = {
    business: Users,
    sports: Crown,
    health: Heart,
    science: Atom
  };

  // Load user data on app start
  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      fetchUserData();
      fetchCategories();
    } else {
      fetchCategories();
    }
  }, []);

  // API functions
  const fetchCategories = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/categories`);
      const data = await response.json();
      setCategories(data.categories);
    } catch (error) {
      console.error('Failed to fetch categories:', error);
    }
  };

  const fetchUserData = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${BACKEND_URL}/api/auth/me`, {
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
      const response = await fetch(`${BACKEND_URL}/api/questions/history`, {
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
      const response = await fetch(`${BACKEND_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(authForm)
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('auth_token', data.token);
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

  const handleMentorSelect = (mentor) => {
    setSelectedMentors(prev => {
      const isSelected = prev.some(m => m.id === mentor.id);
      if (isSelected) {
        return prev.filter(m => m.id !== mentor.id);
      } else {
        return [...prev, mentor];
      }
    });
  };

  const handleSelectAll = () => {
    if (selectAll) {
      setSelectedMentors([]);
    } else {
      const filteredMentors = selectedCategory.mentors.filter(mentor =>
        mentor.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        mentor.expertise.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setSelectedMentors(filteredMentors);
    }
    setSelectAll(!selectAll);
  };

  const askQuestion = async () => {
    if (!question.trim() || selectedMentors.length === 0) return;

    setIsLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${BACKEND_URL}/api/questions/ask`, {
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

      const response = await fetch(`${BACKEND_URL}/api/payments/checkout`, {
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
      const response = await fetch(`${BACKEND_URL}/api/payments/status/${sessionId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      const data = await response.json();

      if (data.payment_status === 'paid') {
        setSuccess('Payment successful! You now have unlimited access to all 400 mentors.');
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

  // Filter mentors based on search
  const filteredMentors = selectedCategory ? 
    selectedCategory.mentors.filter(mentor =>
      mentor.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      mentor.expertise.toLowerCase().includes(searchTerm.toLowerCase())
    ) : [];

  // Update selectAll state when filtered mentors change
  useEffect(() => {
    if (filteredMentors.length > 0) {
      setSelectAll(filteredMentors.every(mentor => 
        selectedMentors.some(selected => selected.id === mentor.id)
      ));
    }
  }, [selectedMentors, filteredMentors]);

  // Render functions
  const renderAuth = () => (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Brain className="h-12 w-12 mx-auto text-purple-400 mb-4" />
          <h1 className="text-3xl font-bold text-white mb-2">OnlyMentors.ai</h1>
          <p className="text-gray-300">Ask questions to 400+ greatest minds</p>
        </div>

        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardHeader>
            <Tabs value={authMode} onValueChange={setAuthMode}>
              <TabsList className="grid w-full grid-cols-2 bg-black/20">
                <TabsTrigger value="login">Login</TabsTrigger>
                <TabsTrigger value="signup">Sign Up</TabsTrigger>
              </TabsList>
            </Tabs>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleAuth} className="space-y-4">
              {authMode === 'signup' && (
                <div>
                  <Label htmlFor="name" className="text-white">Full Name</Label>
                  <Input
                    id="name"
                    type="text"
                    value={authForm.full_name}
                    onChange={(e) => setAuthForm({...authForm, full_name: e.target.value})}
                    className="bg-black/20 border-white/20 text-white"
                    required
                  />
                </div>
              )}
              
              <div>
                <Label htmlFor="email" className="text-white">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={authForm.email}
                  onChange={(e) => setAuthForm({...authForm, email: e.target.value})}
                  className="bg-black/20 border-white/20 text-white"
                  required
                />
              </div>

              <div>
                <Label htmlFor="password" className="text-white">Password</Label>
                <Input
                  id="password"
                  type="password"
                  value={authForm.password}
                  onChange={(e) => setAuthForm({...authForm, password: e.target.value})}
                  className="bg-black/20 border-white/20 text-white"
                  required
                />
              </div>

              {error && (
                <Alert className="bg-red-500/20 border-red-500/50">
                  <AlertDescription className="text-red-200">{error}</AlertDescription>
                </Alert>
              )}

              {success && (
                <Alert className="bg-green-500/20 border-green-500/50">
                  <AlertDescription className="text-green-200">{success}</AlertDescription>
                </Alert>
              )}

              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? 'Processing...' : (authMode === 'login' ? 'Sign In' : 'Create Account')}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );

  const renderCategories = () => (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Brain className="h-10 w-10 text-purple-400" />
            <h1 className="text-4xl font-bold text-white">OnlyMentors.ai</h1>
          </div>
          <p className="text-xl text-gray-300 mb-6">Ask questions to 400+ history's greatest minds</p>
          
          {user && (
            <div className="flex items-center justify-center gap-6 mb-6">
              <div className="text-sm text-gray-300">
                Welcome back, <span className="text-purple-400 font-semibold">{user.full_name}</span>
              </div>
              <div className="flex items-center gap-2">
                {user.is_subscribed ? (
                  <Badge className="bg-green-500/20 text-green-400 border-green-500/50">
                    <Crown className="h-3 w-3 mr-1" />
                    Unlimited Access to 400 Mentors
                  </Badge>
                ) : (
                  <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/50">
                    {10 - user.questions_asked} free questions left
                  </Badge>
                )}
              </div>
              <Button variant="outline" size="sm" onClick={handleLogout} className="border-gray-600 text-gray-300">
                Logout
              </Button>
            </div>
          )}

          {!user.is_subscribed && (
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
                className="bg-white/10 backdrop-blur-md border-white/20 hover:bg-white/20 transition-all duration-300 cursor-pointer group"
                onClick={() => {
                  setSelectedCategory(category);
                  setSelectedMentors([]);
                  setSearchTerm('');
                  setCurrentView('mentors');
                }}
              >
                <CardHeader className="text-center">
                  <div className="mx-auto mb-4 p-3 bg-purple-500/20 rounded-full w-fit group-hover:bg-purple-500/30 transition-colors">
                    <IconComponent className="h-8 w-8 text-purple-400" />
                  </div>
                  <CardTitle className="text-white">{category.name}</CardTitle>
                  <CardDescription className="text-gray-300 text-sm">
                    {category.description}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center">
                    <Badge variant="secondary" className="bg-purple-500/20 text-purple-400">
                      {category.count || category.mentors.length} mentors
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
              className="border-purple-500/50 text-purple-400 hover:bg-purple-500/20"
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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center gap-4 mb-8">
          <Button
            variant="outline"
            onClick={() => setCurrentView('categories')}
            className="border-gray-600 text-gray-300"
          >
            ← Back to Categories
          </Button>
          <div className="flex items-center gap-3">
            {React.createElement(categoryIcons[selectedCategory.id], {
              className: "h-8 w-8 text-purple-400"
            })}
            <h1 className="text-3xl font-bold text-white">{selectedCategory.name} Mentors</h1>
          </div>
        </div>

        {/* Search and Controls */}
        <div className="mb-8 space-y-4">
          <div className="flex gap-4 items-center">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                type="text"
                placeholder="Search mentors by name or expertise..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 bg-black/20 border-white/20 text-white"
              />
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="selectAll"
                checked={selectAll}
                onCheckedChange={handleSelectAll}
                className="border-white/20"
              />
              <Label htmlFor="selectAll" className="text-white text-sm">
                Select All ({filteredMentors.length})
              </Label>
            </div>
          </div>

          {selectedMentors.length > 0 && (
            <div className="bg-purple-500/20 border border-purple-500/50 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div className="text-white">
                  <span className="font-semibold">{selectedMentors.length} mentors selected</span>
                  <p className="text-sm text-gray-300">They will all answer your next question</p>
                </div>
                <Button
                  onClick={() => setCurrentView('question')}
                  className="bg-gradient-to-r from-purple-500 to-pink-500"
                  disabled={!user}
                >
                  <Zap className="h-4 w-4 mr-2" />
                  Ask Question
                </Button>
              </div>
            </div>
          )}
        </div>

        {/* OnlyFans-style Mentors Grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          {filteredMentors.map((mentor) => {
            const isSelected = selectedMentors.some(m => m.id === mentor.id);
            return (
              <Card
                key={mentor.id}
                className={`bg-white/10 backdrop-blur-md border-white/20 hover:bg-white/20 transition-all duration-300 cursor-pointer group relative ${
                  isSelected ? 'ring-2 ring-purple-400 bg-purple-500/20' : ''
                }`}
                onClick={() => user && handleMentorSelect(mentor)}
              >
                {/* Selection Checkbox */}
                {user && (
                  <div className="absolute top-2 right-2 z-10">
                    <Checkbox
                      checked={isSelected}
                      onCheckedChange={() => handleMentorSelect(mentor)}
                      className="border-white/50 bg-black/50"
                      onClick={(e) => e.stopPropagation()}
                    />
                  </div>
                )}

                {/* Mentor Image */}
                <div className="relative">
                  <Avatar className="w-full h-48 rounded-t-lg rounded-none">
                    <AvatarImage 
                      src={mentor.image_url} 
                      alt={mentor.name}
                      className="object-cover w-full h-full"
                    />
                    <AvatarFallback className="bg-purple-500/20 text-purple-400 text-xl font-bold w-full h-full rounded-t-lg rounded-none">
                      {mentor.name.split(' ').map(n => n[0]).join('')}
                    </AvatarFallback>
                  </Avatar>
                  
                  {/* Hover overlay */}
                  <div className="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-all duration-300 rounded-t-lg flex items-center justify-center">
                    <div className="opacity-0 group-hover:opacity-100 transition-all duration-300">
                      {isSelected ? (
                        <div className="text-white text-center">
                          <Star className="h-6 w-6 mx-auto mb-1" />
                          <p className="text-sm">Selected</p>
                        </div>
                      ) : (
                        <div className="text-white text-center">
                          <MessageSquare className="h-6 w-6 mx-auto mb-1" />
                          <p className="text-sm">Ask Question</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Mentor Info */}
                <CardContent className="p-3 space-y-2">
                  <h3 className="text-white font-semibold text-sm leading-tight">{mentor.name}</h3>
                  <p className="text-purple-400 text-xs">{mentor.title}</p>
                  <p className="text-gray-300 text-xs leading-tight line-clamp-2">{mentor.bio}</p>
                  
                  {/* Expertise Tags */}
                  <div className="flex flex-wrap gap-1">
                    {mentor.expertise.split(', ').slice(0, 2).map((skill, index) => (
                      <Badge key={index} variant="secondary" className="bg-purple-500/20 text-purple-400 text-xs px-1 py-0">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </CardContent>

                {!user && (
                  <div className="absolute inset-0 bg-black/50 flex items-center justify-center rounded-lg">
                    <div className="text-center">
                      <Lock className="h-6 w-6 mx-auto mb-2 text-white" />
                      <p className="text-white text-sm">Login to Ask</p>
                    </div>
                  </div>
                )}
              </Card>
            );
          })}
        </div>

        {filteredMentors.length === 0 && searchTerm && (
          <div className="text-center py-12">
            <Search className="h-16 w-16 mx-auto text-gray-600 mb-4" />
            <p className="text-gray-400">No mentors found matching "{searchTerm}"</p>
          </div>
        )}
      </div>
    </div>
  );

  const renderQuestion = () => (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-4 mb-8">
            <Button
              variant="outline"
              onClick={() => setCurrentView('mentors')}
              className="border-gray-600 text-gray-300"
            >
              ← Back to Mentors
            </Button>
            <h1 className="text-2xl font-bold text-white">
              Ask {selectedMentors.length} {selectedMentors.length === 1 ? 'Mentor' : 'Mentors'}
            </h1>
          </div>

          {/* Selected Mentors Display */}
          <div className="mb-8">
            <h3 className="text-white text-lg mb-4">Selected Mentors ({selectedMentors.length})</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {selectedMentors.map((mentor) => (
                <div key={mentor.id} className="text-center">
                  <Avatar className="h-16 w-16 mx-auto mb-2">
                    <AvatarImage src={mentor.image_url} alt={mentor.name} />
                    <AvatarFallback className="bg-purple-500/20 text-purple-400 font-bold">
                      {mentor.name.split(' ').map(n => n[0]).join('')}
                    </AvatarFallback>
                  </Avatar>
                  <p className="text-white text-sm font-medium">{mentor.name}</p>
                  <p className="text-purple-400 text-xs">{mentor.title}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Question Form */}
          <Card className="bg-white/10 backdrop-blur-md border-white/20 mb-8">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <MessageSquare className="h-5 w-5" />
                Ask Your Question
              </CardTitle>
              <CardDescription className="text-gray-300">
                Get personalized wisdom from {selectedMentors.length} legendary {selectedMentors.length === 1 ? 'mind' : 'minds'}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label className="text-white mb-2 block">Your Question</Label>
                <Textarea
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="What would you like to ask these mentors?"
                  className="bg-black/20 border-white/20 text-white min-h-[100px]"
                  maxLength={500}
                />
                <div className="text-right text-sm text-gray-400 mt-1">
                  {question.length}/500
                </div>
              </div>

              {error && (
                <Alert className="bg-red-500/20 border-red-500/50">
                  <AlertDescription className="text-red-200">{error}</AlertDescription>
                </Alert>
              )}

              <Button
                onClick={askQuestion}
                disabled={!question.trim() || isLoading || selectedMentors.length === 0 || (!user?.is_subscribed && user?.questions_asked >= 10)}
                className="w-full"
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
                <div className="text-center p-4 bg-yellow-500/20 border border-yellow-500/50 rounded-lg">
                  <Lock className="h-8 w-8 mx-auto text-yellow-400 mb-2" />
                  <p className="text-yellow-200 mb-3">You've used all your free questions!</p>
                  <Button onClick={() => setCurrentView('subscription')} className="bg-gradient-to-r from-purple-500 to-pink-500">
                    Upgrade for Unlimited Access
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Responses */}
          {responses.length > 0 && (
            <div className="space-y-6">
              {responses.map((response, index) => (
                <Card key={index} className="bg-white/10 backdrop-blur-md border-white/20">
                  <CardHeader>
                    <div className="flex items-center gap-3">
                      <Avatar className="h-12 w-12">
                        <AvatarImage src={response.mentor.image_url} alt={response.mentor.name} />
                        <AvatarFallback className="bg-purple-500/20 text-purple-400 font-bold">
                          {response.mentor.name.split(' ').map(n => n[0]).join('')}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <CardTitle className="text-white">{response.mentor.name}</CardTitle>
                        <CardDescription className="text-purple-400">
                          {response.mentor.title}
                        </CardDescription>
                      </div>
                      <Star className="h-5 w-5 text-yellow-400 ml-auto" />
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="prose prose-gray max-w-none">
                      <p className="text-gray-200 leading-relaxed whitespace-pre-wrap">{response.response}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const renderSubscription = () => (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
      <div className="max-w-4xl w-full">
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardHeader className="text-center">
            <Crown className="h-16 w-16 mx-auto text-yellow-400 mb-4" />
            <CardTitle className="text-3xl text-white mb-2">Unlock All 400 Mentors</CardTitle>
            <CardDescription className="text-gray-300 text-lg">
              Get unlimited access to history's greatest minds
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
              {/* Monthly Plan */}
              <div className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-lg p-6 border border-purple-500/50">
                <div className="text-center">
                  <h3 className="text-xl font-bold text-white mb-2">Monthly</h3>
                  <div className="text-4xl font-bold text-white mb-1">$29.99</div>
                  <div className="text-purple-400 text-sm mb-6">per month</div>
                  <div className="space-y-3 text-left mb-6">
                    <div className="flex items-center gap-2 text-gray-300">
                      <Star className="h-4 w-4 text-yellow-400" />
                      Unlimited questions to all 400 mentors
                    </div>
                    <div className="flex items-center gap-2 text-gray-300">
                      <Star className="h-4 w-4 text-yellow-400" />
                      Business, Sports, Health & Science categories
                    </div>
                    <div className="flex items-center gap-2 text-gray-300">
                      <Star className="h-4 w-4 text-yellow-400" />
                      Multiple mentor responses per question
                    </div>
                    <div className="flex items-center gap-2 text-gray-300">
                      <Star className="h-4 w-4 text-yellow-400" />
                      Complete question history
                    </div>
                  </div>
                  <Button 
                    onClick={() => initiateSubscription('monthly')}
                    disabled={isLoading}
                    className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
                  >
                    {isLoading ? 'Processing...' : 'Start Monthly Plan'}
                  </Button>
                </div>
              </div>

              {/* Yearly Plan */}
              <div className="bg-gradient-to-r from-green-500/20 to-blue-500/20 rounded-lg p-6 border border-green-500/50 relative">
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <Badge className="bg-green-500 text-white">Save $59.89</Badge>
                </div>
                <div className="text-center">
                  <h3 className="text-xl font-bold text-white mb-2">Yearly</h3>
                  <div className="text-4xl font-bold text-white mb-1">$299.99</div>
                  <div className="text-green-400 text-sm mb-6">per year ($24.99/month)</div>
                  <div className="space-y-3 text-left mb-6">
                    <div className="flex items-center gap-2 text-gray-300">
                      <Star className="h-4 w-4 text-yellow-400" />
                      Everything in Monthly plan
                    </div>
                    <div className="flex items-center gap-2 text-gray-300">
                      <Star className="h-4 w-4 text-yellow-400" />
                      Save 2 months ($59.89 savings)
                    </div>
                    <div className="flex items-center gap-2 text-gray-300">
                      <Star className="h-4 w-4 text-yellow-400" />
                      Priority support
                    </div>
                    <div className="flex items-center gap-2 text-gray-300">
                      <Star className="h-4 w-4 text-yellow-400" />
                      Early access to new mentors
                    </div>
                  </div>
                  <Button 
                    onClick={() => initiateSubscription('yearly')}
                    disabled={isLoading}
                    className="w-full bg-gradient-to-r from-green-500 to-blue-500 hover:from-green-600 hover:to-blue-600"
                  >
                    {isLoading ? 'Processing...' : 'Start Yearly Plan'}
                  </Button>
                </div>
              </div>
            </div>

            {error && (
              <Alert className="bg-red-500/20 border-red-500/50 mb-6">
                <AlertDescription className="text-red-200">{error}</AlertDescription>
              </Alert>
            )}

            <div className="text-center">
              <Button
                variant="outline"
                onClick={() => setCurrentView('categories')}
                className="border-gray-600 text-gray-300"
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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-4 mb-8">
            <Button
              variant="outline"
              onClick={() => setCurrentView('categories')}
              className="border-gray-600 text-gray-300"
            >
              ← Back to Categories
            </Button>
            <h1 className="text-3xl font-bold text-white">Question History</h1>
          </div>

          <div className="space-y-6">
            {questionHistory.map((item, index) => (
              <Card key={item.question_id} className="bg-white/10 backdrop-blur-md border-white/20">
                <CardHeader>
                  <div className="flex items-center gap-3 mb-2">
                    <MessageSquare className="h-5 w-5 text-purple-400" />
                    <div className="text-purple-400 text-sm">{new Date(item.created_at).toLocaleDateString()}</div>
                  </div>
                  <div className="bg-black/20 rounded-lg p-3">
                    <p className="text-gray-300 italic text-sm">"{item.question}"</p>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {item.responses && item.responses.map((response, idx) => (
                    <div key={idx} className="border-l-2 border-purple-500/50 pl-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Avatar className="h-6 w-6">
                          <AvatarImage src={response.mentor?.image_url} alt={response.mentor?.name} />
                          <AvatarFallback className="bg-purple-500/20 text-purple-400 text-xs">
                            {response.mentor?.name?.split(' ').map(n => n[0]).join('') || 'GM'}
                          </AvatarFallback>
                        </Avatar>
                        <div className="text-white font-medium text-sm">{response.mentor?.name}</div>
                      </div>
                      <p className="text-gray-200 text-sm leading-relaxed">{response.response}</p>
                    </div>
                  ))}
                </CardContent>
              </Card>
            ))}
            
            {questionHistory.length === 0 && (
              <Card className="bg-white/10 backdrop-blur-md border-white/20">
                <CardContent className="text-center py-12">
                  <MessageSquare className="h-16 w-16 mx-auto text-gray-600 mb-4" />
                  <p className="text-gray-400">No questions asked yet. Start your journey!</p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );

  // Main render logic
  if (!user) {
    return renderAuth();
  }

  switch (currentView) {
    case 'categories':
      return renderCategories();
    case 'mentors':
      return renderMentors();
    case 'question':
      return renderQuestion();
    case 'subscription':
      return renderSubscription();
    case 'history':
      return renderHistory();
    default:
      return renderCategories();
  }
}

export default App;
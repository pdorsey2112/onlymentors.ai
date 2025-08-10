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
import { Brain, Users, Heart, Atom, Crown, MessageSquare, Sparkles, Star, Lock, Zap } from 'lucide-react';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  // State management
  const [user, setUser] = useState(null);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedMentor, setSelectedMentor] = useState(null);
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [authMode, setAuthMode] = useState('login');
  const [authForm, setAuthForm] = useState({ email: '', password: '', full_name: '' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [questionHistory, setQuestionHistory] = useState([]);
  const [currentView, setCurrentView] = useState('categories');

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
    setSelectedMentor(null);
    setResponse(null);
    setQuestionHistory([]);
  };

  const askQuestion = async () => {
    if (!question.trim() || !selectedMentor) return;

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
          great_mind_id: selectedMentor.id,
          question: question
        })
      });

      const data = await response.json();

      if (response.ok) {
        setResponse(data);
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

  const initiateSubscription = async () => {
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
          package_id: 'monthly',
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
        setSuccess('Payment successful! You now have unlimited access.');
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

  // Render functions
  const renderAuth = () => (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Brain className="h-12 w-12 mx-auto text-purple-400 mb-4" />
          <h1 className="text-3xl font-bold text-white mb-2">AI Mentorship</h1>
          <p className="text-gray-300">Learn from history's greatest minds</p>
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
            <h1 className="text-4xl font-bold text-white">AI Mentorship</h1>
          </div>
          <p className="text-xl text-gray-300 mb-6">Ask questions to history's greatest minds</p>
          
          {user && (
            <div className="flex items-center justify-center gap-6 mb-6">
              <div className="text-sm text-gray-300">
                Welcome back, <span className="text-purple-400 font-semibold">{user.full_name}</span>
              </div>
              <div className="flex items-center gap-2">
                {user.is_subscribed ? (
                  <Badge className="bg-green-500/20 text-green-400 border-green-500/50">
                    <Crown className="h-3 w-3 mr-1" />
                    Unlimited Access
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
                      {category.great_minds.length} mentors
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

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {selectedCategory.great_minds.map((mentor) => (
            <Card
              key={mentor.id}
              className="bg-white/10 backdrop-blur-md border-white/20 hover:bg-white/20 transition-all duration-300 cursor-pointer group"
              onClick={() => {
                setSelectedMentor(mentor);
                setCurrentView('question');
              }}
            >
              <CardHeader>
                <div className="flex items-center gap-4">
                  <Avatar className="h-16 w-16">
                    <AvatarFallback className="bg-purple-500/20 text-purple-400 text-lg font-bold">
                      {mentor.name.split(' ').map(n => n[0]).join('')}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <CardTitle className="text-white text-lg">{mentor.name}</CardTitle>
                    <CardDescription className="text-purple-400 font-medium">
                      {mentor.title}
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-gray-300 text-sm mb-4">{mentor.bio}</p>
                <div className="flex flex-wrap gap-1">
                  {mentor.expertise.split(', ').map((skill, index) => (
                    <Badge key={index} variant="secondary" className="bg-purple-500/20 text-purple-400 text-xs">
                      {skill}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
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
            <div className="flex items-center gap-3">
              <Avatar className="h-10 w-10">
                <AvatarFallback className="bg-purple-500/20 text-purple-400 font-bold">
                  {selectedMentor.name.split(' ').map(n => n[0]).join('')}
                </AvatarFallback>
              </Avatar>
              <div>
                <h1 className="text-2xl font-bold text-white">{selectedMentor.name}</h1>
                <p className="text-purple-400">{selectedMentor.title}</p>
              </div>
            </div>
          </div>

          {/* Question Form */}
          <Card className="bg-white/10 backdrop-blur-md border-white/20 mb-8">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <MessageSquare className="h-5 w-5" />
                Ask {selectedMentor.name.split(' ')[0]} a Question
              </CardTitle>
              <CardDescription className="text-gray-300">
                Get personalized wisdom and insights from this legendary mind
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label className="text-white mb-2 block">Your Question</Label>
                <Textarea
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder={`What would you like to ask ${selectedMentor.name}?`}
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
                disabled={!question.trim() || isLoading || (!user?.is_subscribed && user?.questions_asked >= 10)}
                className="w-full"
              >
                {isLoading ? (
                  <>
                    <Sparkles className="h-4 w-4 mr-2 animate-spin" />
                    Getting wisdom from {selectedMentor.name}...
                  </>
                ) : (
                  <>
                    <Zap className="h-4 w-4 mr-2" />
                    Ask Question {!user?.is_subscribed && `(${Math.max(0, 10 - (user?.questions_asked || 0))} remaining)`}
                  </>
                )}
              </Button>

              {!user?.is_subscribed && user?.questions_asked >= 10 && (
                <div className="text-center p-4 bg-yellow-500/20 border border-yellow-500/50 rounded-lg">
                  <Lock className="h-8 w-8 mx-auto text-yellow-400 mb-2" />
                  <p className="text-yellow-200 mb-3">You've used all your free questions!</p>
                  <Button onClick={() => setCurrentView('subscription')} className="bg-gradient-to-r from-purple-500 to-pink-500">
                    Upgrade to Pro
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Response */}
          {response && (
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <Avatar className="h-10 w-10">
                    <AvatarFallback className="bg-purple-500/20 text-purple-400 font-bold">
                      {response.great_mind.name.split(' ').map(n => n[0]).join('')}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <CardTitle className="text-white">{response.great_mind.name}</CardTitle>
                    <CardDescription className="text-purple-400">
                      {response.great_mind.title}
                    </CardDescription>
                  </div>
                  <Star className="h-5 w-5 text-yellow-400 ml-auto" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="bg-black/20 rounded-lg p-4 mb-4">
                  <p className="text-gray-300 italic text-sm mb-2">"{response.question}"</p>
                </div>
                <div className="prose prose-gray max-w-none">
                  <p className="text-gray-200 leading-relaxed whitespace-pre-wrap">{response.response}</p>
                </div>
                
                {response.questions_remaining !== null && (
                  <div className="mt-4 p-3 bg-purple-500/20 border border-purple-500/50 rounded-lg">
                    <p className="text-purple-200 text-sm">
                      {response.questions_remaining > 0 
                        ? `${response.questions_remaining} free questions remaining`
                        : 'This was your last free question! Upgrade to continue.'
                      }
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );

  const renderSubscription = () => (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardHeader className="text-center">
            <Crown className="h-16 w-16 mx-auto text-yellow-400 mb-4" />
            <CardTitle className="text-2xl text-white mb-2">Upgrade to Pro</CardTitle>
            <CardDescription className="text-gray-300">
              Unlock unlimited access to all great minds
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-lg p-6 border border-purple-500/50">
              <div className="text-center">
                <div className="text-3xl font-bold text-white mb-1">$29.99</div>
                <div className="text-purple-400 text-sm mb-4">per month</div>
                <div className="space-y-2 text-left">
                  <div className="flex items-center gap-2 text-gray-300">
                    <Star className="h-4 w-4 text-yellow-400" />
                    Unlimited questions to all mentors
                  </div>
                  <div className="flex items-center gap-2 text-gray-300">
                    <Star className="h-4 w-4 text-yellow-400" />
                    Access to all categories
                  </div>
                  <div className="flex items-center gap-2 text-gray-300">
                    <Star className="h-4 w-4 text-yellow-400" />
                    Priority AI responses
                  </div>
                  <div className="flex items-center gap-2 text-gray-300">
                    <Star className="h-4 w-4 text-yellow-400" />
                    Question history & favorites
                  </div>
                </div>
              </div>
            </div>

            {error && (
              <Alert className="bg-red-500/20 border-red-500/50">
                <AlertDescription className="text-red-200">{error}</AlertDescription>
              </Alert>
            )}

            <Button 
              onClick={initiateSubscription}
              disabled={isLoading}
              className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
            >
              {isLoading ? 'Processing...' : 'Subscribe Now'}
            </Button>

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
                  <div className="flex items-center gap-3">
                    <Avatar className="h-8 w-8">
                      <AvatarFallback className="bg-purple-500/20 text-purple-400 text-sm">
                        {item.great_mind?.name.split(' ').map(n => n[0]).join('') || 'GM'}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <div className="text-white font-medium">{item.great_mind?.name}</div>
                      <div className="text-purple-400 text-sm">{new Date(item.created_at).toLocaleDateString()}</div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="bg-black/20 rounded-lg p-3 mb-4">
                    <p className="text-gray-300 italic text-sm">"{item.question}"</p>
                  </div>
                  <p className="text-gray-200 text-sm leading-relaxed">{item.response}</p>
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
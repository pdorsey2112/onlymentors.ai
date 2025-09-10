import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { 
  Building, 
  Users, 
  TrendingUp, 
  MessageSquare, 
  Shield, 
  Award,
  ArrowRight,
  CheckCircle,
  User,
  Crown,
  Brain,
  Target
} from 'lucide-react';
import { getBackendURL } from '../config';

const BusinessPortalLanding = () => {
  const { companySlug } = useParams();
  const navigate = useNavigate();
  const [businessConfig, setBusinessConfig] = useState(null);
  const [mentors, setMentors] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadBusinessPortalData();
  }, [companySlug]);

  const loadBusinessPortalData = async () => {
    try {
      setLoading(true);
      const backendURL = getBackendURL();
      
      // Load business configuration
      const response = await fetch(`${backendURL}/api/business/portal/${companySlug}`);
      
      if (response.ok) {
        const data = await response.json();
        setBusinessConfig(data.business);
        setMentors(data.mentors || []);
        setCategories(data.categories || []);
      } else {
        setError('Business portal not found');
      }
    } catch (error) {
      console.error('Error loading business portal:', error);
      setError('Failed to load business portal');
    } finally {
      setLoading(false);
    }
  };

  const handleEmployeeSignup = () => {
    navigate(`/app/${companySlug}`);
  };

  const handleMentorPortal = () => {
    navigate(`/creator/${companySlug}`);
  };

  const handleAdminConsole = () => {
    navigate('/app?business-console=true');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading business portal...</p>
        </div>
      </div>
    );
  }

  if (error || !businessConfig) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="max-w-md w-full">
          <CardHeader className="text-center">
            <div className="text-4xl mb-4">🏢</div>
            <CardTitle className="text-xl text-red-600">Portal Not Found</CardTitle>
          </CardHeader>
          <CardContent className="text-center">
            <p className="text-gray-600 mb-4">
              {error || 'This business portal could not be found.'}
            </p>
            <Button onClick={() => window.location.href = '/'}>
              Return to Homepage
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Get customization settings with defaults
  const customization = businessConfig.customization || {};
  const primaryColor = customization.primary_color || '#2563eb';
  const secondaryColor = customization.secondary_color || '#64748b';
  const layout = customization.layout || 'default';

  return (
    <div className="min-h-screen bg-gray-50" style={{ '--primary-color': primaryColor, '--secondary-color': secondaryColor }}>
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                {businessConfig.logo_url ? (
                  <img 
                    src={businessConfig.logo_url} 
                    alt={`${businessConfig.company_name} logo`}
                    className="h-8 w-auto"
                  />
                ) : (
                  <div className="w-8 h-8 rounded bg-blue-600 flex items-center justify-center">
                    <Building className="w-5 h-5 text-white" />
                  </div>
                )}
                <div>
                  <h1 className="text-xl font-bold text-gray-900">{businessConfig.company_name}</h1>
                  <p className="text-xs text-gray-600">Mentorship Portal</p>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="outline" onClick={handleAdminConsole}>
                Admin Console
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section - Corporate Focus */}
      <section className="relative bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 text-white py-20">
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-4xl mx-auto">
            <div className="mb-6">
              <Badge className="bg-blue-600/20 text-blue-300 border-blue-400/30 mb-4">
                {businessConfig.company_name} Employee Portal
              </Badge>
            </div>
            <h1 className="text-4xl md:text-6xl font-bold mb-6 leading-tight">
              Accelerate Your
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400"> Professional Growth</span>
            </h1>
            <p className="text-xl md:text-2xl text-gray-300 mb-8 leading-relaxed">
              Access personalized mentorship from industry experts and AI-powered guidance 
              designed specifically for {businessConfig.company_name} employees.
            </p>
            
            {/* Primary CTA - Employee Signup */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
              <Button 
                onClick={handleEmployeeSignup}
                size="lg"
                className="px-8 py-4 text-lg bg-blue-600 hover:bg-blue-700 transform hover:scale-105 transition-all duration-200"
              >
                <User className="mr-2 h-5 w-5" />
                Join as Employee
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
              <Button 
                onClick={handleMentorPortal}
                variant="outline"
                size="lg"
                className="px-8 py-4 text-lg border-white/30 text-white hover:bg-white/10"
              >
                <Crown className="mr-2 h-5 w-5" />
                Become a Mentor
              </Button>
            </div>

            {/* Company Stats */}
            <div className="flex flex-wrap justify-center gap-8 text-sm">
              <div className="flex items-center space-x-2">
                <Users className="h-4 w-4 text-blue-400" />
                <span className="text-gray-300">{businessConfig.employee_count || '0'} Employees</span>
              </div>
              <div className="flex items-center space-x-2">
                <MessageSquare className="h-4 w-4 text-blue-400" />
                <span className="text-gray-300">{businessConfig.total_questions || '0'} Questions Answered</span>
              </div>
              <div className="flex items-center space-x-2">
                <TrendingUp className="h-4 w-4 text-blue-400" />
                <span className="text-gray-300">{categories.length} Expert Categories</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works - Corporate Process */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Your Path to Professional Excellence
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our streamlined process connects {businessConfig.company_name} employees with 
              expert mentorship in just four simple steps.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <User className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">1. Sign Up</h3>
              <p className="text-gray-600">
                Register with your company email and get instant access to our mentorship platform.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Target className="h-8 w-8 text-purple-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">2. Get Matched</h3>
              <p className="text-gray-600">
                Access mentors specifically assigned to {businessConfig.company_name} based on your needs.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <MessageSquare className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">3. Ask Questions</h3>
              <p className="text-gray-600">
                Get personalized guidance from both AI mentors and experienced colleagues.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="h-8 w-8 text-orange-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">4. Advance</h3>
              <p className="text-gray-600">
                Apply insights to your role and accelerate your professional development.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Mentor Showcase */}
      {mentors.length > 0 && (
        <section className="py-20 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                Meet Your Expert Mentors
              </h2>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                Access carefully curated mentors specifically assigned to guide {businessConfig.company_name} employees.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {mentors.slice(0, 6).map(mentor => (
                <Card key={mentor.mentor_id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-center space-x-3">
                      <div className={`w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-xl ${
                        mentor.type === 'ai' ? 'bg-blue-500' : 'bg-green-500'
                      }`}>
                        {mentor.type === 'ai' ? <Brain className="w-6 h-6" /> : <User className="w-6 h-6" />}
                      </div>
                      <div className="flex-1">
                        <CardTitle className="text-lg">{mentor.name}</CardTitle>
                        <CardDescription>
                          {mentor.type === 'ai' ? 'AI Expert' : 'Company Mentor'}
                        </CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-600 mb-4 line-clamp-3">
                      {mentor.description || 'Expert guidance in various professional areas'}
                    </p>
                    
                    {mentor.expertise && (
                      <Badge variant="secondary" className="text-xs">
                        {mentor.expertise}
                      </Badge>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>

            <div className="text-center mt-12">
              <Button onClick={handleEmployeeSignup} size="lg" className="px-8">
                Access All Mentors
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </div>
          </div>
        </section>
      )}

      {/* Categories Overview */}
      {categories.length > 0 && (
        <section className="py-20 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                Expertise Areas
              </h2>
              <p className="text-xl text-gray-600">
                Get guidance across all key areas of professional development
              </p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              {categories.map(category => (
                <div key={category.category_id} className="text-center p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
                  <div className="text-3xl mb-2">{category.icon}</div>
                  <h3 className="font-semibold text-gray-900">{category.name}</h3>
                  <p className="text-sm text-gray-600 mt-1">{category.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Ready to Accelerate Your Career?
          </h2>
          <p className="text-xl mb-8 text-blue-100 max-w-2xl mx-auto">
            Join your colleagues at {businessConfig.company_name} and start your mentorship journey today.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button 
              onClick={handleEmployeeSignup}
              size="lg"
              className="px-8 py-4 bg-white text-blue-600 hover:bg-gray-100"
            >
              <User className="mr-2 h-5 w-5" />
              Get Started as Employee
            </Button>
            <Button 
              onClick={handleMentorPortal}
              variant="outline"
              size="lg"
              className="px-8 py-4 border-white/30 text-white hover:bg-white/10"
            >
              <Crown className="mr-2 h-5 w-5" />
              Apply as Mentor
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                {businessConfig.logo_url ? (
                  <img 
                    src={businessConfig.logo_url} 
                    alt={`${businessConfig.company_name} logo`}
                    className="h-8 w-auto"
                  />
                ) : (
                  <div className="w-8 h-8 rounded bg-blue-600 flex items-center justify-center">
                    <Building className="w-5 h-5 text-white" />
                  </div>
                )}
                <span className="text-lg font-bold">{businessConfig.company_name}</span>
              </div>
              <p className="text-gray-400">
                Empowering professional growth through expert mentorship.
              </p>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-4">Quick Access</h3>
              <div className="space-y-2">
                <button 
                  onClick={handleEmployeeSignup}
                  className="block text-gray-400 hover:text-white transition-colors"
                >
                  Employee Portal
                </button>
                <button 
                  onClick={handleMentorPortal}
                  className="block text-gray-400 hover:text-white transition-colors"
                >
                  Mentor Portal
                </button>
                <button 
                  onClick={handleAdminConsole}
                  className="block text-gray-400 hover:text-white transition-colors"
                >
                  Admin Console
                </button>
              </div>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-4">Platform</h3>
              <p className="text-gray-400 text-sm">
                Powered by OnlyMentors.ai
              </p>
              <p className="text-gray-500 text-xs mt-2">
                Professional mentorship platform for enterprise teams
              </p>
            </div>
          </div>
          
          <Separator className="my-8 bg-gray-800" />
          
          <div className="text-center text-gray-400 text-sm">
            <p>&copy; 2024 {businessConfig.company_name}. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default BusinessPortalLanding;
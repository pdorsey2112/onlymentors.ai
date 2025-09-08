import React, { useState, useEffect } from 'react';
import { getBackendURL } from '../config';

const BusinessLandingPage = ({ businessSlug }) => {
  const [businessConfig, setBusinessConfig] = useState(null);
  const [categories, setCategories] = useState([]);
  const [mentorsByCategory, setMentorsByCategory] = useState({});
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState(null);

  useEffect(() => {
    loadBusinessData();
  }, [businessSlug]);

  const loadBusinessData = async () => {
    try {
      setLoading(true);
      const backendURL = getBackendURL();
      
      // Load business configuration by slug
      const businessResponse = await fetch(`${backendURL}/api/business/public/${businessSlug}`);
      if (businessResponse.ok) {
        const business = await businessResponse.json();
        setBusinessConfig(business);
        
        // Load categories for this business
        const categoriesResponse = await fetch(`${backendURL}/api/business/public/${businessSlug}/categories`);
        if (categoriesResponse.ok) {
          const categoriesData = await categoriesResponse.json();
          setCategories(categoriesData);
          
          // Load mentors by category
          const mentorsData = {};
          for (const category of categoriesData) {
            const mentorsResponse = await fetch(`${backendURL}/api/business/public/${businessSlug}/categories/${category.category_id}/mentors`);
            if (mentorsResponse.ok) {
              const mentors = await mentorsResponse.json();
              mentorsData[category.category_id] = mentors;
            }
          }
          setMentorsByCategory(mentorsData);
        }
      }
    } catch (error) {
      console.error('Error loading business data:', error);
    } finally {
      setLoading(false);
    }
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

  if (!businessConfig) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">🏢</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Business Not Found</h1>
          <p className="text-gray-600">The requested business portal could not be found.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <div className="text-2xl font-bold text-blue-600">
                🏢 {businessConfig.company_name}
              </div>
              <div className="hidden md:block">
                <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                  Mentorship Portal
                </span>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <a href={`/app/${businessSlug}`} className="text-gray-600 hover:text-blue-600 font-medium">
                Employee Sign In
              </a>
              <a href={`/creator/${businessSlug}`} className="text-gray-600 hover:text-blue-600 font-medium">
                Mentor Portal
              </a>
              <a href={`/app/${businessSlug}?signup=true`} className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors">
                Join Program
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-50 to-indigo-100 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-6">
            Welcome to {businessConfig.company_name} 
            <span className="block text-blue-600">Mentorship Platform</span>
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
            Connect with expert mentors across different departments and expertise areas. 
            Get personalized guidance to accelerate your professional growth within our organization.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a href={`/app/${businessSlug}?signup=true`} className="inline-flex items-center justify-center px-8 py-4 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 transform hover:scale-105 transition-all duration-200 shadow-lg">
              👤 Join as Employee
              <svg className="ml-2 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7l5 5m0 0l-5 5m5-5H6"></path>
              </svg>
            </a>
            <a href={`/creator/${businessSlug}?signup=true`} className="inline-flex items-center justify-center px-8 py-4 border-2 border-blue-600 text-blue-600 rounded-xl font-semibold hover:bg-blue-600 hover:text-white transition-all duration-200">
              👨‍🏫 Become a Mentor
            </a>
          </div>
        </div>
      </section>

      {/* Categories Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Browse Mentors by Expertise</h2>
            <p className="text-lg text-gray-600">Find the right mentor for your specific needs and career goals</p>
          </div>

          {/* Category Navigation */}
          <div className="flex flex-wrap justify-center gap-4 mb-12">
            <button
              onClick={() => setSelectedCategory(null)}
              className={`px-6 py-3 rounded-full font-medium transition-colors ${
                selectedCategory === null
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              All Categories
            </button>
            {categories.map(category => (
              <button
                key={category.category_id}
                onClick={() => setSelectedCategory(category.category_id)}
                className={`px-6 py-3 rounded-full font-medium transition-colors ${
                  selectedCategory === category.category_id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {category.icon} {category.name}
              </button>
            ))}
          </div>

          {/* Mentors Display */}
          {selectedCategory ? (
            // Show mentors for selected category
            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-8 text-center">
                {categories.find(c => c.category_id === selectedCategory)?.icon}{' '}
                {categories.find(c => c.category_id === selectedCategory)?.name} Mentors
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {(mentorsByCategory[selectedCategory] || []).map(mentor => (
                  <div key={`${mentor.type}_${mentor.mentor_id}`} className="bg-white p-6 rounded-xl shadow-lg border hover:shadow-xl transition-shadow">
                    <div className="flex items-center space-x-4 mb-4">
                      <div className={`w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-xl ${
                        mentor.type === 'ai' ? 'bg-blue-500' : 'bg-green-500'
                      }`}>
                        {mentor.type === 'ai' ? '🤖' : '👨‍🏫'}
                      </div>
                      <div>
                        <h4 className="text-lg font-bold text-gray-900">{mentor.name}</h4>
                        <p className="text-sm text-gray-600">
                          {mentor.type === 'ai' ? 'AI Mentor' : `Human Mentor • ${mentor.department || 'Internal'}`}
                        </p>
                      </div>
                    </div>
                    {mentor.description && (
                      <p className="text-gray-600 mb-4">{mentor.description}</p>
                    )}
                    {mentor.expertise && mentor.expertise.length > 0 && (
                      <div className="mb-4">
                        <div className="flex flex-wrap gap-2">
                          {mentor.expertise.map((skill, index) => (
                            <span key={index} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-blue-700 transition-colors">
                      Connect with {mentor.name.split(' ')[0]}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            // Show all categories with mentor previews
            <div className="space-y-16">
              {categories.map(category => (
                <div key={category.category_id}>
                  <div className="flex items-center justify-between mb-8">
                    <div className="flex items-center space-x-4">
                      <div className="text-3xl">{category.icon}</div>
                      <div>
                        <h3 className="text-2xl font-bold text-gray-900">{category.name}</h3>
                        <p className="text-gray-600">{category.description}</p>
                      </div>
                    </div>
                    <button
                      onClick={() => setSelectedCategory(category.category_id)}
                      className="text-blue-600 hover:text-blue-700 font-medium"
                    >
                      View All →
                    </button>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {(mentorsByCategory[category.category_id] || []).slice(0, 3).map(mentor => (
                      <div key={`${mentor.type}_${mentor.mentor_id}`} className="bg-gray-50 p-4 rounded-lg border">
                        <div className="flex items-center space-x-3 mb-3">
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-bold ${
                            mentor.type === 'ai' ? 'bg-blue-500' : 'bg-green-500'
                          }`}>
                            {mentor.type === 'ai' ? '🤖' : '👨‍🏫'}
                          </div>
                          <div>
                            <h4 className="font-medium text-gray-900">{mentor.name}</h4>
                            <p className="text-sm text-gray-600">{mentor.type === 'ai' ? 'AI Mentor' : 'Human Mentor'}</p>
                          </div>
                        </div>
                        <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                          Connect →
                        </button>
                      </div>
                    ))}
                  </div>
                  
                  {(mentorsByCategory[category.category_id] || []).length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      <div className="text-2xl mb-2">🔍</div>
                      <p>No mentors assigned to this category yet</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="text-lg font-bold mb-4">🏢 {businessConfig.company_name}</h3>
              <p className="text-gray-400">
                Empowering our team through personalized mentorship and professional development.
              </p>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">Quick Links</h4>
              <ul className="space-y-2">
                <li><a href={`/app/${businessSlug}?signup=true`} className="text-gray-400 hover:text-white">Join as Employee</a></li>
                <li><a href={`/creator/${businessSlug}?signup=true`} className="text-gray-400 hover:text-white">Become a Mentor</a></li>
                <li><a href={`/app/${businessSlug}`} className="text-gray-400 hover:text-white">Sign In</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">Support</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-gray-400 hover:text-white">Help Center</a></li>
                <li><a href="#" className="text-gray-400 hover:text-white">Contact IT</a></li>
                <li><a href="#" className="text-gray-400 hover:text-white">Privacy Policy</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center">
            <p className="text-gray-400">
              © 2024 {businessConfig.company_name}. Powered by OnlyMentors.ai
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default BusinessLandingPage;
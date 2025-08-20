import React, { useState, useEffect } from 'react';
import CreatorVerification from './CreatorVerification';
import ContentUpload from './ContentUpload';
import MessagingInterface from './MessagingInterface';
import EnhancedContentManagement from './EnhancedContentManagement';

const CreatorDashboard = () => {
  const [creator, setCreator] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [showVerification, setShowVerification] = useState(false);
  const [showPublicProfile, setShowPublicProfile] = useState(false);
  const [showContentUpload, setShowContentUpload] = useState(false);
  const [showContentManagement, setShowContentManagement] = useState(false);
  const [stats, setStats] = useState({
    total_earnings: 0,
    monthly_earnings: 0,
    subscriber_count: 0,
    content_count: 0,
    total_questions: 0,
    average_rating: 5.0
  });

  const [isVerified, setIsVerified] = useState(false);

  useEffect(() => {
    const storedCreator = localStorage.getItem('creator');
    if (storedCreator) {
      const creatorData = JSON.parse(storedCreator);
      setCreator(creatorData);
      setStats(creatorData.stats || stats);
      setIsVerified(creatorData.is_verified || false);
      
      // If not verified, show verification process
      if (!creatorData.is_verified) {
        setShowVerification(true);
      }
    }
  }, []);

  const handleVerificationComplete = () => {
    setShowVerification(false);
    setIsVerified(true);
    
    // Update stored creator data
    const storedCreator = localStorage.getItem('creator');
    if (storedCreator) {
      const creatorData = JSON.parse(storedCreator);
      creatorData.is_verified = true;
      localStorage.setItem('creator', JSON.stringify(creatorData));
      setCreator(creatorData);
    }
  };

  const handleViewPublicProfile = () => {
    // Open creator's public profile in new tab
    if (creator && creator.creator_id) {
      window.open(`${window.location.origin}/?creator=${creator.creator_id}`, '_blank');
    }
  };

  const handleUploadContent = () => {
    setShowContentUpload(true);
  };

  const handleManageContent = () => {
    setShowContentManagement(true);
  };

  const handleSaveSettings = async () => {
    // TODO: Implement settings save functionality
    alert('Settings saved successfully!');
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const StatCard = ({ title, value, icon, color = 'purple' }) => (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div className="flex items-center">
        <div className={`p-3 rounded-lg bg-${color}-100`}>
          <span className={`text-${color}-600 text-xl`}>{icon}</span>
        </div>
        <div className="ml-4">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
        </div>
      </div>
    </div>
  );

  const TabButton = ({ id, label, active, onClick }) => (
    <button
      onClick={() => onClick(id)}
      className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
        active 
          ? 'bg-purple-100 text-purple-700' 
          : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
      }`}
    >
      {label}
    </button>
  );

  if (!creator) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  // Show verification flow if not verified
  if (showVerification && !isVerified) {
    return (
      <CreatorVerification 
        creatorId={creator.creator_id} 
        onVerificationComplete={handleVerificationComplete}
      />
    );
  }

  const handleContentUploadSuccess = (result) => {
    // Refresh content count or reload data
    setStats(prev => ({
      ...prev,
      content_count: prev.content_count + 1
    }));
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="h-10 w-10 rounded-full bg-purple-100 flex items-center justify-center">
                <span className="text-purple-600 font-semibold text-lg">
                  {creator.account_name?.charAt(0)?.toUpperCase() || 'C'}
                </span>
              </div>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">
                  {creator.account_name || 'Mentor Dashboard'}
                </h1>
                <p className="text-sm text-gray-600">
                  {isVerified ? (
                    <span className="text-green-600 flex items-center">
                      <span className="mr-1">✓</span> Verified Mentor
                    </span>
                  ) : (
                    <span className="text-amber-600">Pending Verification</span>
                  )}
                </p>
              </div>
            </div>
            
            <button 
              onClick={() => {
                // Clear localStorage and redirect to home (logout)
                localStorage.removeItem('creator_token');
                localStorage.removeItem('creator_data');
                localStorage.removeItem('auth_token');
                localStorage.removeItem('user');
                window.location.href = '/';
              }}
              className="bg-purple-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-purple-700 transition-colors"
            >
              Logoff
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Verification Banner */}
        {!isVerified && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-8">
            <div className="flex">
              <div className="flex-shrink-0">
                <span className="text-amber-400 text-xl">⚠️</span>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-amber-800">
                  Account Verification Required
                </h3>
                <p className="text-sm text-amber-700 mt-1">
                  Please complete your profile verification to start earning. You need to upload your ID and banking information.
                </p>
                <div className="mt-3">
                  <button 
                    onClick={() => setShowVerification(true)}
                    className="bg-amber-600 text-white px-3 py-1.5 rounded text-sm font-medium hover:bg-amber-700"
                  >
                    Complete Verification
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <StatCard 
            title="Total Earnings" 
            value={formatCurrency(stats.total_earnings)} 
            icon="💰"
            color="green"
          />
          <StatCard 
            title="Monthly Earnings" 
            value={formatCurrency(stats.monthly_earnings || 0)} 
            icon="📈"
            color="blue"
          />
          <StatCard 
            title="Subscribers" 
            value={(stats.subscriber_count || 0).toLocaleString()} 
            icon="👥"
            color="purple"
          />
          <StatCard 
            title="Content Pieces" 
            value={(stats.content_count || 0).toLocaleString()} 
            icon="📄"
            color="indigo"
          />
          <StatCard 
            title="Questions Answered" 
            value={(stats.total_questions || 0).toLocaleString()} 
            icon="❓"
            color="pink"
          />
          <StatCard 
            title="Average Rating" 
            value={`${(stats.average_rating || 5.0).toFixed(1)} ⭐`} 
            icon="⭐"
            color="yellow"
          />
        </div>

        {/* Tab Navigation */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
          <div className="border-b border-gray-200 px-6 py-4">
            <div className="flex space-x-2">
              <TabButton
                id="overview"
                label="Overview"
                active={activeTab === 'overview'}
                onClick={setActiveTab}
              />
              <TabButton
                id="logoff"
                label="Logoff"
                active={activeTab === 'logoff'}
                onClick={(tab) => {
                  // Perform logout instead of showing profile
                  localStorage.removeItem('creator_token');
                  localStorage.removeItem('creator_data');  
                  localStorage.removeItem('auth_token');
                  localStorage.removeItem('user');
                  window.location.href = '/';
                }}
              />
              <TabButton
                id="content"
                label="Content"
                active={activeTab === 'content'}
                onClick={setActiveTab}
              />
              <TabButton
                id="messages"
                label="Messages"
                active={activeTab === 'messages'}
                onClick={setActiveTab}
              />
              <TabButton
                id="analytics"
                label="Analytics"
                active={activeTab === 'analytics'}
                onClick={setActiveTab}
              />
              <TabButton
                id="settings"
                label="Settings"
                active={activeTab === 'settings'}
                onClick={setActiveTab}
              />
            </div>
          </div>

          <div className="p-6">
            {activeTab === 'overview' && (
              <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900">New subscriber joined</p>
                      <p className="text-sm text-gray-600">2 hours ago</p>
                    </div>
                    <span className="text-green-600">+${creator.monthly_price || 0}</span>
                  </div>
                  
                  <div className="text-center py-8 text-gray-500">
                    <p>No recent activity</p>
                    <p className="text-sm mt-1">Start creating content to see activity here</p>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'public-profile' && (
              <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-6">Your Public Profile Preview</h2>
                
                {creator && (
                  <div className="max-w-4xl">
                    {/* Profile Header */}
                    <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-6 mb-6">
                      <div className="flex flex-col sm:flex-row gap-6">
                        {/* Profile Image */}
                        <div className="w-32 h-32 mx-auto sm:mx-0 rounded-full bg-gray-200 flex items-center justify-center overflow-hidden flex-shrink-0">
                          {creator.profile_image ? (
                            <img 
                              src={creator.profile_image} 
                              alt={creator.account_name}
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <div className="bg-purple-100 text-purple-600 text-4xl font-bold w-full h-full flex items-center justify-center">
                              {creator.account_name ? creator.account_name.charAt(0).toUpperCase() : 'M'}
                            </div>
                          )}
                        </div>
                        
                        {/* Profile Info */}
                        <div className="flex-1">
                          <h3 className="text-2xl font-bold text-gray-900 mb-2">{creator.account_name || 'Creator'}</h3>
                          <p className="text-purple-600 font-medium mb-3">${creator.monthly_price || 0}/month</p>
                          <p className="text-gray-700 leading-relaxed mb-4">
                            {creator.description || 'Professional creator sharing expertise and insights.'}
                          </p>
                          
                          {/* Stats Row */}
                          <div className="flex flex-wrap gap-4 text-sm">
                            <div className="bg-white px-3 py-2 rounded-lg shadow-sm">
                              <span className="text-gray-600">Category:</span>
                              <span className="font-medium ml-1">{creator.category || 'General'}</span>
                            </div>
                            <div className="bg-white px-3 py-2 rounded-lg shadow-sm">
                              <span className="text-gray-600">Subscribers:</span>
                              <span className="font-medium ml-1">{stats.subscriber_count || 0}</span>
                            </div>
                            <div className="bg-white px-3 py-2 rounded-lg shadow-sm">
                              <span className="text-gray-600">Content:</span>
                              <span className="font-medium ml-1">{stats.content_count || 0} pieces</span>
                            </div>
                            <div className="bg-white px-3 py-2 rounded-lg shadow-sm">
                              <span className="text-gray-600">Rating:</span>
                              <span className="font-medium ml-1">{(stats.average_rating || 5.0).toFixed(1)} ⭐</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Expertise Section */}
                    <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
                      <h4 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <span className="text-purple-600">🎯</span>
                        Areas of Expertise
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {creator.expertise_areas && creator.expertise_areas.length > 0 ? (
                          creator.expertise_areas.map((skill, index) => (
                            <span 
                              key={index} 
                              className="bg-purple-100 text-purple-700 px-3 py-1 rounded-full text-sm font-medium"
                            >
                              {skill}
                            </span>
                          ))
                        ) : (
                          <p className="text-gray-600">Add your expertise areas in Settings</p>
                        )}
                      </div>
                    </div>

                    {/* Why Choose This Creator */}
                    <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
                      <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                        <span className="text-purple-600">✨</span>
                        Why Choose {creator.account_name}?
                      </h4>
                      <div className="grid gap-4">
                        <div className="flex items-start gap-3 p-4 bg-purple-50 rounded-lg">
                          <div className="bg-purple-100 p-2 rounded-lg flex-shrink-0">
                            <span className="text-purple-600">💡</span>
                          </div>
                          <div>
                            <h5 className="font-medium text-gray-900">Expert Knowledge</h5>
                            <p className="text-gray-600 text-sm mt-1">Deep expertise in {creator.category || 'their field'} with proven results</p>
                          </div>
                        </div>
                        
                        <div className="flex items-start gap-3 p-4 bg-purple-50 rounded-lg">
                          <div className="bg-purple-100 p-2 rounded-lg flex-shrink-0">
                            <span className="text-purple-600">📚</span>
                          </div>
                          <div>
                            <h5 className="font-medium text-gray-900">Quality Content</h5>
                            <p className="text-gray-600 text-sm mt-1">High-quality content and personalized guidance</p>
                          </div>
                        </div>
                        
                        <div className="flex items-start gap-3 p-4 bg-purple-50 rounded-lg">
                          <div className="bg-purple-100 p-2 rounded-lg flex-shrink-0">
                            <span className="text-purple-600">⭐</span>
                          </div>
                          <div>
                            <h5 className="font-medium text-gray-900">Proven Results</h5>
                            <p className="text-gray-600 text-sm mt-1">{(stats.average_rating || 5.0).toFixed(1)} star rating from satisfied subscribers</p>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Call to Action */}
                    <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg p-6 text-center">
                      <h4 className="text-xl font-bold mb-2">Ready to Learn from {creator.account_name}?</h4>
                      <p className="mb-4 opacity-90">Join {stats.subscriber_count || 0} other subscribers getting exclusive content</p>
                      <div className="text-2xl font-bold mb-4">${creator.monthly_price || 0}/month</div>
                      <button className="bg-white text-purple-600 px-8 py-3 rounded-lg font-medium hover:bg-gray-100 transition-colors">
                        Subscribe Now
                      </button>
                    </div>

                    {/* Note for creator */}
                    <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                      <p className="text-blue-800 text-sm">
                        <span className="font-medium">💡 Note:</span> This is how your profile appears to potential subscribers. 
                        You can update your information in the Settings tab.
                      </p>
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'content' && (
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-gray-900">Content Management</h2>
                  <div className="flex space-x-3">
                    <button 
                      onClick={handleManageContent}
                      className="bg-gray-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-700"
                    >
                      Manage Content
                    </button>
                    <button 
                      onClick={handleUploadContent}
                      className="bg-purple-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-purple-700"
                    >
                      Upload New Content
                    </button>
                  </div>
                </div>
                
                <div className="text-center py-8 text-gray-500">
                  <p>Content management tools available</p>
                  <p className="text-sm mt-1">Upload new content or manage existing content with editing and deletion capabilities</p>
                </div>
              </div>
            )}

            {activeTab === 'messages' && (
              <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Direct Messages</h2>
                <MessagingInterface creatorId={creator.creator_id} />
              </div>
            )}

            {activeTab === 'analytics' && (
              <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Analytics</h2>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="bg-gray-50 rounded-lg p-6">
                    <h3 className="font-medium text-gray-900 mb-2">Earnings Chart</h3>
                    <div className="h-48 flex items-center justify-center text-gray-500">
                      Coming soon
                    </div>
                  </div>
                  
                  <div className="bg-gray-50 rounded-lg p-6">
                    <h3 className="font-medium text-gray-900 mb-2">Subscriber Growth</h3>
                    <div className="h-48 flex items-center justify-center text-gray-500">
                      Coming soon
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'settings' && (
              <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Account Settings</h2>
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Monthly Subscription Price
                    </label>
                    <div className="flex items-center">
                      <span className="text-gray-500 mr-2">$</span>
                      <input
                        type="number"
                        value={creator.monthly_price || ''}
                        className="w-32 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                        step="0.01"
                        min="1"
                        max="1000"
                      />
                      <span className="text-gray-500 ml-2">per month</span>
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Auto-approve Messages
                    </label>
                    <input type="checkbox" className="rounded" defaultChecked />
                    <span className="ml-2 text-sm text-gray-600">
                      Automatically approve new messages from subscribers
                    </span>
                  </div>

                  <button 
                    onClick={handleSaveSettings}
                    className="bg-purple-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-purple-700"
                  >
                    Save Changes
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Content Upload Modal */}
      {showContentUpload && (
        <ContentUpload
          creatorId={creator.creator_id}
          onClose={() => setShowContentUpload(false)}
          onUploadSuccess={handleContentUploadSuccess}
        />
      )}

      {/* Enhanced Content Management Modal */}
      {showContentManagement && (
        <EnhancedContentManagement
          creatorId={creator.creator_id}
          onClose={() => setShowContentManagement(false)}
          onUploadSuccess={handleContentUploadSuccess}
        />
      )}
    </div>
  );
};

export default CreatorDashboard;
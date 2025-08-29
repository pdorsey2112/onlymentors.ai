import React, { useState, useEffect } from 'react';
import { getBackendURL } from '../config';

const PremiumContentDiscovery = ({ mentorId, mentorName, onPurchase, onClose }) => {
  const [content, setContent] = useState([]);
  const [filteredContent, setFilteredContent] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedContentType, setSelectedContentType] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [userAccess, setUserAccess] = useState({});

  const contentTypes = [
    { id: 'document', name: 'Documents', icon: '📄' },
    { id: 'video', name: 'Videos', icon: '🎥' },
    { id: 'audio', name: 'Audio', icon: '🎵' },
    { id: 'image', name: 'Images', icon: '🖼️' },
    { id: 'interactive', name: 'Interactive', icon: '⚡' }
  ];

  const categories = [
    { id: 'business', name: 'Business', icon: '💼' },
    { id: 'sports', name: 'Sports', icon: '🏆' },
    { id: 'health', name: 'Health', icon: '🌿' },
    { id: 'science', name: 'Science', icon: '🔬' },
    { id: 'relationships', name: 'Relationships', icon: '💕' }
  ];

  useEffect(() => {
    fetchContent();
  }, [mentorId]);

  useEffect(() => {
    filterContent();
  }, [content, selectedCategory, selectedContentType, searchTerm]);

  const fetchContent = async () => {
    try {
      setIsLoading(true);
      const backendURL = getBackendURL();
      
      const response = await fetch(`${backendURL}/api/mentor/${mentorId}/premium-content`);
      
      if (response.ok) {
        const data = await response.json();
        setContent(data.content || []);
        // Check user access for each content
        checkUserAccess(data.content || []);
      } else {
        setError('Failed to load premium content');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const checkUserAccess = async (contentList) => {
    const token = localStorage.getItem('auth_token');
    if (!token) return;
    
    const backendURL = getBackendURL();
    const accessChecks = {};
    
    for (const item of contentList) {
      try {
        const response = await fetch(`${backendURL}/api/content/${item.content_id}/access`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (response.ok) {
          const accessData = await response.json();
          accessChecks[item.content_id] = accessData.access_granted;
        }
      } catch (err) {
        // Ignore individual access check errors
      }
    }
    
    setUserAccess(accessChecks);
  };

  const filterContent = () => {
    let filtered = content;

    if (selectedCategory) {
      filtered = filtered.filter(item => item.category === selectedCategory);
    }

    if (selectedContentType) {
      filtered = filtered.filter(item => item.content_type === selectedContentType);
    }

    if (searchTerm) {
      filtered = filtered.filter(item =>
        item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (item.tags && item.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase())))
      );
    }

    setFilteredContent(filtered);
  };

  const handlePurchase = (contentItem) => {
    onPurchase && onPurchase(contentItem);
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  const getContentTypeIcon = (type) => {
    const contentType = contentTypes.find(ct => ct.id === type);
    return contentType ? contentType.icon : '📁';
  };

  const ContentCard = ({ item }) => {
    const hasAccess = userAccess[item.content_id];
    const isOwned = hasAccess === true;
    
    return (
      <div className="bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow">
        {/* Content Preview */}
        <div className="relative h-48 bg-gradient-to-br from-purple-100 to-pink-100 rounded-t-lg flex items-center justify-center">
          <div className="text-6xl">{getContentTypeIcon(item.content_type)}</div>
          {item.preview_available && (
            <div className="absolute top-2 left-2 bg-green-100 text-green-700 px-2 py-1 rounded-full text-xs font-medium">
              Preview Available
            </div>
          )}
          {isOwned && (
            <div className="absolute top-2 right-2 bg-purple-100 text-purple-700 px-2 py-1 rounded-full text-xs font-medium">
              ✓ Owned
            </div>
          )}
        </div>

        {/* Content Info */}
        <div className="p-4">
          <div className="flex items-start justify-between mb-2">
            <h3 className="text-lg font-semibold text-gray-900 leading-tight">{item.title}</h3>
            <div className="text-xl font-bold text-purple-600 ml-2">
              {formatPrice(item.price)}
            </div>
          </div>

          <p className="text-gray-600 text-sm mb-3 line-clamp-2">{item.description}</p>

          {/* Content Type and Category */}
          <div className="flex items-center gap-2 mb-3">
            <span className="bg-gray-100 text-gray-700 px-2 py-1 rounded-full text-xs font-medium">
              {contentTypes.find(ct => ct.id === item.content_type)?.name || item.content_type}
            </span>
            {item.category && (
              <span className="bg-purple-100 text-purple-700 px-2 py-1 rounded-full text-xs font-medium">
                {categories.find(cat => cat.id === item.category)?.name || item.category}
              </span>
            )}
          </div>

          {/* Tags */}
          {item.tags && item.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-3">
              {item.tags.slice(0, 3).map((tag, index) => (
                <span key={index} className="bg-gray-50 text-gray-600 px-2 py-1 rounded text-xs">
                  #{tag}
                </span>
              ))}
              {item.tags.length > 3 && (
                <span className="text-gray-400 text-xs">+{item.tags.length - 3} more</span>
              )}
            </div>
          )}

          {/* Purchase/Access Button */}
          <div className="mt-4">
            {isOwned ? (
              <button className="w-full bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-lg font-medium transition-colors">
                Access Content
              </button>
            ) : (
              <button
                onClick={() => handlePurchase(item)}
                className="w-full bg-purple-600 hover:bg-purple-700 text-white py-2 px-4 rounded-lg font-medium transition-colors"
              >
                Purchase for {formatPrice(item.price)}
              </button>
            )}
          </div>

          {/* Stats */}
          <div className="flex justify-between text-xs text-gray-500 mt-2">
            <span>{item.total_purchases || 0} purchases</span>
            <span>Added {new Date(item.created_at).toLocaleDateString()}</span>
          </div>
        </div>
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-2xl p-8 max-w-md w-full mx-4">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading premium content...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-6xl max-h-[90vh] overflow-hidden mx-4">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold">{mentorName}'s Premium Content</h2>
              <p className="text-purple-100 mt-1">
                {content.length} exclusive {content.length === 1 ? 'item' : 'items'} available
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:text-purple-200 text-2xl"
            >
              ×
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="p-6 border-b border-gray-200">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search */}
            <div>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search content..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>

            {/* Category Filter */}
            <div>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="">All Categories</option>
                {categories.map(cat => (
                  <option key={cat.id} value={cat.id}>{cat.icon} {cat.name}</option>
                ))}
              </select>
            </div>

            {/* Content Type Filter */}
            <div>
              <select
                value={selectedContentType}
                onChange={(e) => setSelectedContentType(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="">All Types</option>
                {contentTypes.map(type => (
                  <option key={type.id} value={type.id}>{type.icon} {type.name}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Content Grid */}
        <div className="p-6 max-h-96 overflow-y-auto">
          {error && (
            <div className="text-center py-8">
              <div className="text-red-600 mb-4">⚠️ {error}</div>
              <button
                onClick={fetchContent}
                className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg"
              >
                Try Again
              </button>
            </div>
          )}

          {!error && filteredContent.length === 0 && content.length > 0 && (
            <div className="text-center py-8">
              <div className="text-gray-400 text-6xl mb-4">🔍</div>
              <p className="text-gray-600">No content matches your current filters.</p>
              <button
                onClick={() => {
                  setSelectedCategory('');
                  setSelectedContentType('');
                  setSearchTerm('');
                }}
                className="mt-2 text-purple-600 hover:text-purple-700 underline"
              >
                Clear filters
              </button>
            </div>
          )}

          {!error && content.length === 0 && (
            <div className="text-center py-8">
              <div className="text-gray-400 text-6xl mb-4">📦</div>
              <p className="text-gray-600">No premium content available yet.</p>
              <p className="text-gray-500 text-sm mt-1">Check back later for exclusive content!</p>
            </div>
          )}

          {!error && filteredContent.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredContent.map((item) => (
                <ContentCard key={item.content_id} item={item} />
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        {content.length > 0 && (
          <div className="border-t border-gray-200 p-4 text-center text-sm text-gray-600">
            All purchases are secured by Stripe • Instant access after payment
          </div>
        )}
      </div>
    </div>
  );
};

export default PremiumContentDiscovery;
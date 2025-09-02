import React, { useState, useEffect } from 'react';
import { getBackendURL } from '../config';
import MentorTierBadge from './MentorTierBadge';

const MentorTierInfo = ({ onClose }) => {
  const [tiers, setTiers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTierInfo();
  }, []);

  const fetchTierInfo = async () => {
    try {
      const backendURL = getBackendURL();
      const response = await fetch(`${backendURL}/api/mentor-tiers/info`);
      
      if (response.ok) {
        const data = await response.json();
        setTiers(data.tiers || []);
      }
    } catch (error) {
      console.error('Error fetching tier info:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatSubscriberCount = (count) => {
    if (count >= 100000) return `${(count / 1000).toFixed(0)}K+`;
    if (count >= 1000) return `${(count / 1000).toFixed(0)}K+`;
    return `${count}+`;
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-2xl p-8 max-w-md w-full mx-4">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading tier information...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden mx-4">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold">Mentor Tier System</h2>
              <p className="text-purple-100 mt-1">Build your reputation and unlock exclusive benefits</p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:text-purple-200 text-2xl"
            >
              ×
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 max-h-96 overflow-y-auto">
          <div className="space-y-6">
            {tiers.map((tier, index) => (
              <div 
                key={tier.level} 
                className="bg-white border-2 border-gray-200 rounded-xl p-6 hover:border-gray-300 transition-colors"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      <MentorTierBadge 
                        tier={tier.tier}
                        level={tier.level}
                        badgeColor={tier.badge_color}
                        description={tier.description}
                        size="large"
                      />
                    </div>
                    <p className="text-gray-600 mb-2">{tier.description}</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {formatSubscriberCount(tier.min_subscribers)} subscribers required
                    </p>
                  </div>
                </div>

                {/* Benefits */}
                <div>
                  <h4 className="font-semibold text-gray-900 mb-3">Benefits & Perks:</h4>
                  <ul className="space-y-2">
                    {tier.benefits.map((benefit, benefitIndex) => (
                      <li key={benefitIndex} className="flex items-start">
                        <span className="text-green-500 mr-2 mt-0.5">✓</span>
                        <span className="text-gray-700 text-sm">{benefit}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Progress indicator for current tier */}
                {index < tiers.length - 1 && (
                  <div className="mt-4 pt-4 border-t border-gray-100">
                    <div className="flex items-center justify-between text-sm text-gray-500">
                      <span>Next tier: {tiers[index + 1]?.tier}</span>
                      <span>{formatSubscriberCount(tiers[index + 1]?.min_subscribers)} subscribers</span>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* How to Gain Subscribers */}
          <div className="mt-8 bg-blue-50 border border-blue-200 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-blue-900 mb-4">How to Gain Subscribers & Advance Tiers</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-medium text-blue-800 mb-2">Quality Content</h4>
                <ul className="text-sm text-blue-700 space-y-1">
                  <li>• Create valuable premium content</li>
                  <li>• Offer free previews to attract users</li>
                  <li>• Regular content updates</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-blue-800 mb-2">Engagement</h4>
                <ul className="text-sm text-blue-700 space-y-1">
                  <li>• Respond promptly to messages</li>
                  <li>• Provide personalized guidance</li>
                  <li>• Build lasting relationships</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-blue-800 mb-2">Marketing</h4>
                <ul className="text-sm text-blue-700 space-y-1">
                  <li>• Share your OnlyMentors profile</li>
                  <li>• Cross-promote on social media</li>
                  <li>• Network with other mentors</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-blue-800 mb-2">Specialization</h4>
                <ul className="text-sm text-blue-700 space-y-1">
                  <li>• Focus on your expertise areas</li>
                  <li>• Build authority in your niche</li>
                  <li>• Showcase your credentials</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 p-4 bg-gray-50 flex justify-center">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            Got It!
          </button>
        </div>
      </div>
    </div>
  );
};

export default MentorTierInfo;
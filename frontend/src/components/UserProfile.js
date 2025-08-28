import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { User, Lock, Phone, Mail, Save, Eye, EyeOff } from 'lucide-react';
import { getBackendURL } from '../config';

const UserProfile = ({ user, onProfileUpdate, onLogout }) => {
  // Get backend URL dynamically
  const BACKEND_URL = getBackendURL();
  
  // Profile state
  const [profileData, setProfileData] = useState({
    full_name: '',
    email: '',
    phone_number: '',
    communication_preferences: {
      email: true,
      sms: false,
      notifications: true
    }
  });
  
  // Password change state
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [activeTab, setActiveTab] = useState('personal');
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false
  });

  // Load user profile on mount
  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('auth_token');
      
      const response = await fetch(`${BACKEND_URL}/api/user/profile`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const profile = await response.json();
        setProfileData({
          full_name: profile.full_name || '',
          email: profile.email || '',
          phone_number: profile.phone_number || '',
          communication_preferences: profile.communication_preferences || {
            email: true,
            sms: false,
            notifications: true
          }
        });
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to load profile');
      }
    } catch (error) {
      console.error('Profile fetch error:', error);
      setError('Failed to connect to server');
    } finally {
      setLoading(false);
    }
  };

  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const token = localStorage.getItem('auth_token');
      
      const response = await fetch(`${BACKEND_URL}/api/user/profile`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(profileData)
      });

      if (response.ok) {
        const result = await response.json();
        setSuccess(result.message);
        
        // Update parent component with new profile data
        if (onProfileUpdate) {
          onProfileUpdate(result.profile);
        }
        
        // Auto-clear success message
        setTimeout(() => setSuccess(''), 3000);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to update profile');
      }
    } catch (error) {
      console.error('Profile update error:', error);
      setError('Failed to connect to server');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    // Validate password confirmation
    if (passwordData.new_password !== passwordData.confirm_password) {
      setError('New passwords do not match');
      setLoading(false);
      return;
    }

    try {
      const token = localStorage.getItem('auth_token');
      
      const response = await fetch(`${BACKEND_URL}/api/user/password`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          current_password: passwordData.current_password,
          new_password: passwordData.new_password
        })
      });

      if (response.ok) {
        const result = await response.json();
        setSuccess(result.message);
        
        // Clear password form
        setPasswordData({
          current_password: '',
          new_password: '',
          confirm_password: ''
        });
        
        // Auto-clear success message and suggest re-login
        setTimeout(() => {
          setSuccess('');
          if (window.confirm('Password changed successfully. You will be logged out for security. Click OK to continue.')) {
            onLogout();
          }
        }, 3000);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to change password');
      }
    } catch (error) {
      console.error('Password change error:', error);
      setError('Failed to connect to server');
    } finally {
      setLoading(false);
    }
  };

  const togglePasswordVisibility = (field) => {
    setShowPasswords(prev => ({
      ...prev,
      [field]: !prev[field]
    }));
  };

  if (loading && !profileData.email) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-purple-50 to-pink-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">My Profile</h1>
          <p className="text-gray-600">Manage your account settings and preferences</p>
        </div>

        {/* Profile Card */}
        <Card className="bg-white shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5" />
              Account Settings
            </CardTitle>
            <CardDescription>
              Update your personal information and security settings
            </CardDescription>
          </CardHeader>
          
          <CardContent>
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="personal" className="flex items-center gap-2">
                  <User className="h-4 w-4" />
                  Personal Info
                </TabsTrigger>
                <TabsTrigger value="password" className="flex items-center gap-2">
                  <Lock className="h-4 w-4" />
                  Password
                </TabsTrigger>
              </TabsList>

              {/* Success/Error Messages */}
              {(error || success) && (
                <div className="mt-4">
                  {error && (
                    <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                      <p className="text-red-600 text-sm">{error}</p>
                    </div>
                  )}
                  {success && (
                    <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                      <p className="text-green-600 text-sm">{success}</p>
                    </div>
                  )}
                </div>
              )}

              {/* Personal Info Tab */}
              <TabsContent value="personal" className="space-y-6 mt-6">
                <form onSubmit={handleProfileUpdate} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Full Name */}
                    <div className="space-y-2">
                      <Label htmlFor="full_name">Full Name</Label>
                      <Input
                        id="full_name"
                        type="text"
                        value={profileData.full_name}
                        onChange={(e) => setProfileData(prev => ({
                          ...prev,
                          full_name: e.target.value
                        }))}
                        placeholder="Enter your full name"
                        className="border-gray-300"
                      />
                    </div>

                    {/* Phone Number */}
                    <div className="space-y-2">
                      <Label htmlFor="phone_number">Phone Number</Label>
                      <div className="relative">
                        <Phone className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                        <Input
                          id="phone_number"
                          type="tel"
                          value={profileData.phone_number}
                          onChange={(e) => setProfileData(prev => ({
                            ...prev,
                            phone_number: e.target.value
                          }))}
                          placeholder="+1 (555) 123-4567"
                          className="pl-10 border-gray-300"
                        />
                      </div>
                      <p className="text-xs text-gray-500">
                        Include country code for international numbers
                      </p>
                    </div>
                  </div>

                  {/* Email */}
                  <div className="space-y-2">
                    <Label htmlFor="email">Email Address</Label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <Input
                        id="email"
                        type="email"
                        value={profileData.email}
                        onChange={(e) => setProfileData(prev => ({
                          ...prev,
                          email: e.target.value
                        }))}
                        placeholder="your.email@example.com"
                        className="pl-10 border-gray-300"
                      />
                    </div>
                  </div>

                  <Button type="submit" disabled={loading} className="flex items-center gap-2">
                    <Save className="h-4 w-4" />
                    {loading ? 'Saving...' : 'Save Changes'}
                  </Button>
                </form>
              </TabsContent>

              {/* Password Tab */}
              <TabsContent value="password" className="space-y-6 mt-6">
                <form onSubmit={handlePasswordChange} className="space-y-4">
                  {/* Current Password */}
                  <div className="space-y-2">
                    <Label htmlFor="current_password">Current Password</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <Input
                        id="current_password"
                        type={showPasswords.current ? "text" : "password"}
                        value={passwordData.current_password}
                        onChange={(e) => setPasswordData(prev => ({
                          ...prev,
                          current_password: e.target.value
                        }))}
                        placeholder="Enter current password"
                        className="pl-10 pr-10 border-gray-300"
                      />
                      <button
                        type="button"
                        onClick={() => togglePasswordVisibility('current')}
                        className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                      >
                        {showPasswords.current ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </button>
                    </div>
                  </div>

                  {/* New Password */}
                  <div className="space-y-2">
                    <Label htmlFor="new_password">New Password</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <Input
                        id="new_password"
                        type={showPasswords.new ? "text" : "password"}
                        value={passwordData.new_password}
                        onChange={(e) => setPasswordData(prev => ({
                          ...prev,
                          new_password: e.target.value
                        }))}
                        placeholder="Enter new password"
                        className="pl-10 pr-10 border-gray-300"
                      />
                      <button
                        type="button"
                        onClick={() => togglePasswordVisibility('new')}
                        className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                      >
                        {showPasswords.new ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </button>
                    </div>
                    <p className="text-xs text-gray-500">
                      Must be at least 8 characters with uppercase, lowercase, number, and special character
                    </p>
                  </div>

                  {/* Confirm Password */}
                  <div className="space-y-2">
                    <Label htmlFor="confirm_password">Confirm New Password</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <Input
                        id="confirm_password"
                        type={showPasswords.confirm ? "text" : "password"}
                        value={passwordData.confirm_password}
                        onChange={(e) => setPasswordData(prev => ({
                          ...prev,
                          confirm_password: e.target.value
                        }))}
                        placeholder="Confirm new password"
                        className="pl-10 pr-10 border-gray-300"
                      />
                      <button
                        type="button"
                        onClick={() => togglePasswordVisibility('confirm')}
                        className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                      >
                        {showPasswords.confirm ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </button>
                    </div>
                  </div>

                  <Button type="submit" disabled={loading} className="flex items-center gap-2">
                    <Lock className="h-4 w-4" />
                    {loading ? 'Changing...' : 'Change Password'}
                  </Button>
                </form>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default UserProfile;
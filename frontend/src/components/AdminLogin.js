import React, { useState } from 'react';
import { getBackendURL } from '../config';

const AdminLogin = ({ onLogin, onError }) => {
    const [formData, setFormData] = useState({
        email: '',
        password: ''
    });
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            const backendURL = getBackendURL();
            const response = await fetch(`${backendURL}/api/admin/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                const data = await response.json();
                console.log('🔐 AdminLogin: Successful response:', data);
                
                localStorage.setItem('admin_token', data.token);
                localStorage.setItem('admin_data', JSON.stringify(data.admin));
                
                console.log('🔐 AdminLogin: Calling onLogin callback');
                onLogin(data);
                console.log('🔐 AdminLogin: onLogin callback completed');
            } else {
                const error = await response.json();
                onError(error.detail || 'Login failed');
            }
        } catch (error) {
            onError('Network error. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-white flex items-center justify-center p-4">
            <div className="max-w-md w-full">
                <div className="bg-white shadow-2xl rounded-3xl p-8 border border-gray-200">
                    <div className="text-center mb-8">
                        <h1 className="text-3xl font-bold text-gray-800 mb-2">Administrator Console</h1>
                        <p className="text-gray-600">OnlyMentors.ai Admin Portal</p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div>
                            <label className="block text-gray-700 text-sm font-medium mb-2">
                                Admin Email
                            </label>
                            <input
                                type="email"
                                required
                                className="w-full px-4 py-3 rounded-xl border border-gray-300 text-gray-800 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                                placeholder="admin@onlymentors.ai"
                                value={formData.email}
                                onChange={(e) => setFormData({...formData, email: e.target.value})}
                            />
                        </div>

                        <div>
                            <label className="block text-gray-700 text-sm font-medium mb-2">
                                Password
                            </label>
                            <input
                                type="password"
                                required
                                className="w-full px-4 py-3 rounded-xl border border-gray-300 text-gray-800 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                                placeholder="Enter admin password"
                                value={formData.password}
                                onChange={(e) => setFormData({...formData, password: e.target.value})}
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white py-3 px-6 rounded-xl font-medium hover:from-purple-700 hover:to-blue-700 transform hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? (
                                <div className="flex items-center justify-center">
                                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                                    Signing In...
                                </div>
                            ) : (
                                'Sign In to Admin Console'
                            )}
                        </button>
                    </form>

                    <div className="mt-8 pt-6 border-t border-gray-200">
                        <div className="text-center">
                            <p className="text-gray-600 text-sm">Initial Admin Credentials:</p>
                            <p className="text-gray-800 text-xs mt-1 font-mono bg-gray-100 py-1 px-2 rounded">admin@onlymentors.ai</p>
                            <p className="text-gray-800 text-xs font-mono bg-gray-100 py-1 px-2 rounded mt-1">SuperAdmin2024!</p>
                            <p className="text-yellow-600 text-xs mt-2">⚠️ Change password after first login</p>
                        </div>
                    </div>

                    <div className="mt-6 text-center">
                        <p className="text-gray-500 text-xs">
                            Secure Admin Portal • OnlyMentors.ai
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AdminLogin;
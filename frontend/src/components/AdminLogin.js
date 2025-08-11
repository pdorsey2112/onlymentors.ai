import React, { useState } from 'react';

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
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL}/api/admin/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('adminToken', data.token);
                localStorage.setItem('adminData', JSON.stringify(data.admin));
                onLogin(data.admin);
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
        <div className="min-h-screen bg-gradient-to-br from-red-500 via-purple-600 to-indigo-700 admin-login-bg flex items-center justify-center p-4">
            <div className="max-w-md w-full">
                <div className="bg-white/10 backdrop-blur-lg rounded-3xl p-8 shadow-2xl border border-white/20">
                    <div className="text-center mb-8">
                        <h1 className="text-3xl font-bold text-white mb-2">Administrator Console</h1>
                        <p className="text-white/80">OnlyMentors.ai Admin Portal</p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div>
                            <label className="block text-white/90 text-sm font-medium mb-2">
                                Admin Email
                            </label>
                            <input
                                type="email"
                                required
                                className="w-full px-4 py-3 rounded-xl bg-white/20 border border-white/30 text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-white/50"
                                placeholder="admin@onlymentors.ai"
                                value={formData.email}
                                onChange={(e) => setFormData({...formData, email: e.target.value})}
                            />
                        </div>

                        <div>
                            <label className="block text-white/90 text-sm font-medium mb-2">
                                Password
                            </label>
                            <input
                                type="password"
                                required
                                className="w-full px-4 py-3 rounded-xl bg-white/20 border border-white/30 text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-white/50"
                                placeholder="Enter admin password"
                                value={formData.password}
                                onChange={(e) => setFormData({...formData, password: e.target.value})}
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-gradient-to-r from-red-500 to-purple-600 text-white py-3 px-6 rounded-xl font-medium hover:from-red-600 hover:to-purple-700 transform hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
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

                    <div className="mt-8 pt-6 border-t border-white/20">
                        <div className="text-center">
                            <p className="text-white/70 text-sm">Initial Admin Credentials:</p>
                            <p className="text-white/80 text-xs mt-1 font-mono">admin@onlymentors.ai</p>
                            <p className="text-white/80 text-xs font-mono">SuperAdmin2024!</p>
                            <p className="text-yellow-300 text-xs mt-2">⚠️ Change password after first login</p>
                        </div>
                    </div>

                    <div className="mt-6 text-center">
                        <p className="text-white/60 text-xs">
                            Secure Admin Portal • OnlyMentors.ai
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AdminLogin;
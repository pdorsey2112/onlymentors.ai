import React, { useState, useEffect } from 'react';
import UserManagement from './UserManagement';

const AdminDashboard = ({ admin, onLogout }) => {
    const [activeTab, setActiveTab] = useState('overview');
    const [dashboardData, setDashboardData] = useState(null);
    const [mentors, setMentors] = useState([]);
    const [userActivityReport, setUserActivityReport] = useState(null);
    const [financialReport, setFinancialReport] = useState(null);
    const [loading, setLoading] = useState(true);
    const [selectedMentors, setSelectedMentors] = useState([]);

    const getAuthHeaders = () => ({
        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`,
        'Content-Type': 'application/json'
    });

    const fetchDashboardData = async () => {
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL}/api/admin/dashboard`, {
                headers: getAuthHeaders()
            });
            if (response.ok) {
                const data = await response.json();
                setDashboardData(data);
            }
        } catch (error) {
            console.error('Error fetching dashboard data:', error);
        }
    };

    const fetchUsers = async () => {
        try {
            console.log('🔍 Fetching users...');
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL}/api/admin/users?limit=100`, {
                headers: getAuthHeaders()
            });
            console.log('📡 Response status:', response.status);
            if (response.ok) {
                const data = await response.json();
                console.log('📊 Users data received:', data.users?.length, 'users');
                console.log('📋 First user:', data.users?.[0]);
                setUsers(data.users);
            } else {
                console.error('❌ Failed to fetch users:', response.status, response.statusText);
                const errorText = await response.text();
                console.error('Error details:', errorText);
            }
        } catch (error) {
            console.error('❌ Error fetching users:', error);
        }
    };

    const fetchMentors = async () => {
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL}/api/admin/mentors?limit=100`, {
                headers: getAuthHeaders()
            });
            if (response.ok) {
                const data = await response.json();
                setMentors(data.mentors);
            }
        } catch (error) {
            console.error('Error fetching mentors:', error);
        }
    };

    const fetchUserActivityReport = async () => {
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL}/api/admin/reports/user-activity`, {
                headers: getAuthHeaders()
            });
            if (response.ok) {
                const data = await response.json();
                setUserActivityReport(data);
            }
        } catch (error) {
            console.error('Error fetching user activity report:', error);
        }
    };

    const fetchFinancialReport = async () => {
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL}/api/admin/reports/financial`, {
                headers: getAuthHeaders()
            });
            if (response.ok) {
                const data = await response.json();
                setFinancialReport(data);
            }
        } catch (error) {
            console.error('Error fetching financial report:', error);
        }
    };

    const manageUsers = async (action) => {
        if (selectedUsers.length === 0) return;

        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL}/api/admin/users/manage`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify({
                    user_ids: selectedUsers,
                    action: action,
                    reason: `Admin ${action} action`
                })
            });
            if (response.ok) {
                alert(`Successfully ${action}ed ${selectedUsers.length} users`);
                setSelectedUsers([]);
                fetchUsers();
            }
        } catch (error) {
            console.error('Error managing users:', error);
        }
    };

    const manageMentors = async (action) => {
        if (selectedMentors.length === 0) return;

        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL}/api/admin/mentors/manage`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify({
                    creator_ids: selectedMentors,
                    action: action,
                    reason: `Admin ${action} action`
                })
            });
            if (response.ok) {
                alert(`Successfully ${action}ed ${selectedMentors.length} mentors`);
                setSelectedMentors([]);
                fetchMentors();
            }
        } catch (error) {
            console.error('Error managing mentors:', error);
        }
    };

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            await Promise.all([
                fetchDashboardData(),
                fetchMentors(),
                fetchUserActivityReport(),
                fetchFinancialReport()
            ]);
            setLoading(false);
        };
        loadData();
    }, []);

    const tabs = [
        { id: 'overview', name: 'Overview', icon: '📊' },
        { id: 'users', name: 'Users', icon: '👥' },
        { id: 'mentors', name: 'Mentors', icon: '🎓' },
        { id: 'content-moderation', name: 'Content Moderation', icon: '🔍' },
        { id: 'payouts', name: 'Payouts', icon: '💰' },
        { id: 'user-reports', name: 'User Reports', icon: '📈' },
        { id: 'financial-reports', name: 'Financial Reports', icon: '💵' },
        { id: 'ai-agents', name: 'AI Agents', icon: '🤖' }
    ];

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-blue-900 flex items-center justify-center">
                <div className="text-white text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
                    <p>Loading Admin Dashboard...</p>
                </div>
            </div>
        );
    }

    const renderOverview = () => (
        <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {dashboardData && (
                    <>
                        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                            <h3 className="text-white/70 text-sm font-medium">Total Users</h3>
                            <p className="text-3xl font-bold text-white">{dashboardData.platform_stats.total_users?.toLocaleString() || 0}</p>
                        </div>
                        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                            <h3 className="text-white/70 text-sm font-medium">Total Mentors</h3>
                            <p className="text-3xl font-bold text-white">{dashboardData.platform_stats.total_mentors?.toLocaleString() || 0}</p>
                        </div>
                        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                            <h3 className="text-white/70 text-sm font-medium">Total Revenue</h3>
                            <p className="text-3xl font-bold text-green-400">${dashboardData.platform_stats.total_revenue?.toFixed(2) || 0}</p>
                        </div>
                        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                            <h3 className="text-white/70 text-sm font-medium">Active Subscriptions</h3>
                            <p className="text-3xl font-bold text-blue-400">{dashboardData.platform_stats.active_subscriptions?.toLocaleString() || 0}</p>
                        </div>
                    </>
                )}
            </div>

            {dashboardData && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                        <h3 className="text-xl font-bold text-white mb-4">User Metrics</h3>
                        <div className="space-y-3">
                            <div className="flex justify-between">
                                <span className="text-white/70">New Users (Week):</span>
                                <span className="text-white font-medium">{dashboardData.user_metrics.new_users_week}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-white/70">Active Users (Week):</span>
                                <span className="text-white font-medium">{dashboardData.user_metrics.active_users}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-white/70">Subscribed Users:</span>
                                <span className="text-green-400 font-medium">{dashboardData.user_metrics.subscribed_users}</span>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                        <h3 className="text-xl font-bold text-white mb-4">Mentor Metrics</h3>
                        <div className="space-y-3">
                            <div className="flex justify-between">
                                <span className="text-white/70">Approved Mentors:</span>
                                <span className="text-green-400 font-medium">{dashboardData.mentor_metrics.approved_mentors}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-white/70">Pending Approval:</span>
                                <span className="text-yellow-400 font-medium">{dashboardData.mentor_metrics.pending_mentors}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-white/70">Total Earnings:</span>
                                <span className="text-green-400 font-medium">${dashboardData.mentor_metrics.total_earnings?.toFixed(2) || 0}</span>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );

    const renderUsers = () => (
        <div className="space-y-6">
            <UserManagement admin={admin} />
        </div>
    );

    const renderMentors = () => (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-white">Mentor Management</h2>
                <div className="flex gap-3">
                    <button
                        onClick={() => manageMentors('approve')}
                        disabled={selectedMentors.length === 0}
                        className="px-4 py-2 bg-green-600 text-white rounded-lg disabled:opacity-50 hover:bg-green-700"
                    >
                        Approve ({selectedMentors.length})
                    </button>
                    <button
                        onClick={() => manageMentors('suspend')}
                        disabled={selectedMentors.length === 0}
                        className="px-4 py-2 bg-yellow-600 text-white rounded-lg disabled:opacity-50 hover:bg-yellow-700"
                    >
                        Suspend ({selectedMentors.length})
                    </button>
                    <button
                        onClick={() => manageMentors('delete')}
                        disabled={selectedMentors.length === 0}
                        className="px-4 py-2 bg-red-600 text-white rounded-lg disabled:opacity-50 hover:bg-red-700"
                    >
                        Delete ({selectedMentors.length})
                    </button>
                </div>
            </div>

            <div className="bg-white/10 backdrop-blur-lg rounded-2xl border border-white/20 overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-white/5">
                            <tr>
                                <th className="px-4 py-3 text-left">
                                    <input
                                        type="checkbox"
                                        onChange={(e) => {
                                            if (e.target.checked) {
                                                setSelectedMentors(mentors.map(m => m.creator_id));
                                            } else {
                                                setSelectedMentors([]);
                                            }
                                        }}
                                        className="rounded"
                                    />
                                </th>
                                <th className="px-4 py-3 text-left text-white/90 font-medium">Account Name</th>
                                <th className="px-4 py-3 text-left text-white/90 font-medium">Email</th>
                                <th className="px-4 py-3 text-left text-white/90 font-medium">Category</th>
                                <th className="px-4 py-3 text-left text-white/90 font-medium">Price</th>
                                <th className="px-4 py-3 text-left text-white/90 font-medium">Status</th>
                                <th className="px-4 py-3 text-left text-white/90 font-medium">Earnings</th>
                            </tr>
                        </thead>
                        <tbody>
                            {mentors.map(mentor => (
                                <tr key={mentor.creator_id} className="border-t border-white/10">
                                    <td className="px-4 py-3">
                                        <input
                                            type="checkbox"
                                            checked={selectedMentors.includes(mentor.creator_id)}
                                            onChange={(e) => {
                                                if (e.target.checked) {
                                                    setSelectedMentors([...selectedMentors, mentor.creator_id]);
                                                } else {
                                                    setSelectedMentors(selectedMentors.filter(id => id !== mentor.creator_id));
                                                }
                                            }}
                                            className="rounded"
                                        />
                                    </td>
                                    <td className="px-4 py-3 text-white">{mentor.account_name}</td>
                                    <td className="px-4 py-3 text-white">{mentor.email}</td>
                                    <td className="px-4 py-3 text-white capitalize">{mentor.category}</td>
                                    <td className="px-4 py-3 text-white">${mentor.monthly_price}/mo</td>
                                    <td className="px-4 py-3">
                                        <span className={`px-2 py-1 rounded-full text-xs ${
                                            mentor.status === 'approved' ? 'bg-green-600' : 
                                            mentor.status === 'pending' ? 'bg-yellow-600' : 
                                            'bg-red-600'
                                        } text-white`}>
                                            {mentor.status}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3 text-white">${mentor.total_earnings?.toFixed(2) || 0}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );

    const renderUserReports = () => (
        <div className="space-y-6">
            <h2 className="text-2xl font-bold text-white">User Activity Reports</h2>
            
            {userActivityReport && (
                <>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                            <h3 className="text-white/70 text-sm font-medium">Total Users</h3>
                            <p className="text-3xl font-bold text-white">{userActivityReport.summary.total_users}</p>
                        </div>
                        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                            <h3 className="text-white/70 text-sm font-medium">Total Questions</h3>
                            <p className="text-3xl font-bold text-blue-400">{userActivityReport.summary.total_questions}</p>
                        </div>
                        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                            <h3 className="text-white/70 text-sm font-medium">Subscribed Users</h3>
                            <p className="text-3xl font-bold text-green-400">{userActivityReport.summary.subscribed_users}</p>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {Object.entries(userActivityReport.period_activity).map(([period, data]) => (
                            <div key={period} className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                                <h3 className="text-xl font-bold text-white mb-4 capitalize">{period} Activity</h3>
                                <div className="space-y-3">
                                    <div className="flex justify-between">
                                        <span className="text-white/70">New Users:</span>
                                        <span className="text-white font-medium">{data.new_users}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-white/70">Active Users:</span>
                                        <span className="text-white font-medium">{data.active_users}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-white/70">Questions Asked:</span>
                                        <span className="text-blue-400 font-medium">{data.questions_asked}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-white/70">Avg Questions/User:</span>
                                        <span className="text-purple-400 font-medium">{data.avg_questions_per_user.toFixed(1)}</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                        <h3 className="text-xl font-bold text-white mb-4">Top Users by Questions</h3>
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead>
                                    <tr className="border-b border-white/20">
                                        <th className="px-4 py-2 text-left text-white/90">Email</th>
                                        <th className="px-4 py-2 text-left text-white/90">Full Name</th>
                                        <th className="px-4 py-2 text-left text-white/90">Questions Asked</th>
                                        <th className="px-4 py-2 text-left text-white/90">Subscription</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {userActivityReport.top_users.map((user, index) => (
                                        <tr key={user.user_id} className="border-b border-white/10">
                                            <td className="px-4 py-2 text-white">{user.email}</td>
                                            <td className="px-4 py-2 text-white">{user.full_name}</td>
                                            <td className="px-4 py-2 text-blue-400 font-medium">{user.questions_asked}</td>
                                            <td className="px-4 py-2">
                                                <span className={`px-2 py-1 rounded-full text-xs ${user.is_subscribed ? 'bg-green-600' : 'bg-gray-600'} text-white`}>
                                                    {user.is_subscribed ? 'Premium' : 'Free'}
                                                </span>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </>
            )}
        </div>
    );

    const renderFinancialReports = () => (
        <div className="space-y-6">
            <h2 className="text-2xl font-bold text-white">Financial Reports</h2>
            
            {financialReport && (
                <>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                            <h3 className="text-white/70 text-sm font-medium">Total Revenue</h3>
                            <p className="text-3xl font-bold text-green-400">${financialReport.summary.total_revenue?.toFixed(2)}</p>
                        </div>
                        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                            <h3 className="text-white/70 text-sm font-medium">Platform Commission</h3>
                            <p className="text-3xl font-bold text-blue-400">${financialReport.summary.platform_commission?.toFixed(2)}</p>
                        </div>
                        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                            <h3 className="text-white/70 text-sm font-medium">Creator Payouts</h3>
                            <p className="text-3xl font-bold text-purple-400">${financialReport.summary.creator_payouts?.toFixed(2)}</p>
                        </div>
                        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                            <h3 className="text-white/70 text-sm font-medium">Active Subscriptions</h3>
                            <p className="text-3xl font-bold text-yellow-400">{financialReport.summary.active_subscriptions}</p>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                        {Object.entries(financialReport.period_revenue).map(([period, data]) => (
                            <div key={period} className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                                <h3 className="text-lg font-bold text-white mb-4 capitalize">{period} Revenue</h3>
                                <div className="space-y-2">
                                    <div className="flex justify-between">
                                        <span className="text-white/70 text-sm">Revenue:</span>
                                        <span className="text-green-400 font-medium">${data.revenue?.toFixed(2)}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-white/70 text-sm">Transactions:</span>
                                        <span className="text-white font-medium">{data.transaction_count}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-white/70 text-sm">Avg/Transaction:</span>
                                        <span className="text-purple-400 font-medium">${data.avg_transaction?.toFixed(2)}</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                            <h3 className="text-xl font-bold text-white mb-4">Revenue Breakdown</h3>
                            <div className="space-y-3">
                                <div className="flex justify-between">
                                    <span className="text-white/70">Monthly Subscriptions:</span>
                                    <span className="text-green-400 font-medium">${financialReport.revenue_breakdown.monthly_subscriptions?.toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-white/70">Yearly Subscriptions:</span>
                                    <span className="text-blue-400 font-medium">${financialReport.revenue_breakdown.yearly_subscriptions?.toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-white/70">Total Transactions:</span>
                                    <span className="text-white font-medium">{financialReport.summary.total_transactions}</span>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                            <h3 className="text-xl font-bold text-white mb-4">Top Paying Users</h3>
                            <div className="space-y-3">
                                {financialReport.top_spenders.slice(0, 5).map((user, index) => (
                                    <div key={user.user_id} className="flex justify-between items-center">
                                        <div>
                                            <p className="text-white text-sm">{user.full_name}</p>
                                            <p className="text-white/60 text-xs">{user.email}</p>
                                        </div>
                                        <span className="text-green-400 font-medium">${user.total_spent?.toFixed(2)}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </>
            )}
        </div>
    );

    const renderContent = () => {
        switch (activeTab) {
            case 'overview': return renderOverview();
            case 'users': return renderUsers();
            case 'mentors': return renderMentors();
            case 'content-moderation': return renderContentModeration();
            case 'payouts': return renderPayouts();
            case 'user-reports': return renderUserReports();
            case 'financial-reports': return renderFinancialReports();
            case 'ai-agents': return renderAIAgents();
            default: return renderOverview();
        }
    };

    const renderContentModeration = () => (
        <div className="space-y-6">
            <h2 className="text-2xl font-bold text-white">Content Moderation</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-4 border border-white/20">
                    <h3 className="text-white/70 text-sm font-medium">Pending Review</h3>
                    <p className="text-2xl font-bold text-yellow-400">10</p>
                </div>
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-4 border border-white/20">
                    <h3 className="text-white/70 text-sm font-medium">Approved Today</h3>
                    <p className="text-2xl font-bold text-green-400">25</p>
                </div>
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-4 border border-white/20">
                    <h3 className="text-white/70 text-sm font-medium">Rejected</h3>
                    <p className="text-2xl font-bold text-red-400">3</p>
                </div>
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-4 border border-white/20">
                    <h3 className="text-white/70 text-sm font-medium">Flagged</h3>
                    <p className="text-2xl font-bold text-orange-400">2</p>
                </div>
            </div>

            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                <h3 className="text-xl font-bold text-white mb-4">Recent Content for Review</h3>
                <div className="space-y-3">
                    <div className="flex items-center justify-between bg-white/5 p-3 rounded-lg">
                        <div className="flex items-center space-x-3">
                            <div className="w-12 h-12 bg-purple-600 rounded-lg flex items-center justify-center">
                                <span className="text-white">🎥</span>
                            </div>
                            <div>
                                <p className="text-white font-medium">Sample Video Content 1</p>
                                <p className="text-white/60 text-sm">Video • Creator • High Priority</p>
                            </div>
                        </div>
                        <div className="flex space-x-2">
                            <button className="px-3 py-1 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700">
                                Approve
                            </button>
                            <button className="px-3 py-1 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700">
                                Reject
                            </button>
                            <button className="px-3 py-1 bg-yellow-600 text-white text-sm rounded-lg hover:bg-yellow-700">
                                Flag
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );

    const renderPayouts = () => (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-white">Creator Payouts</h2>
                <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
                    Process Payouts
                </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-4 border border-white/20">
                    <h3 className="text-white/70 text-sm font-medium">Pending Payouts</h3>
                    <p className="text-2xl font-bold text-yellow-400">$2,450.80</p>
                </div>
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-4 border border-white/20">
                    <h3 className="text-white/70 text-sm font-medium">Paid This Month</h3>
                    <p className="text-2xl font-bold text-green-400">$18,920.30</p>
                </div>
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-4 border border-white/20">
                    <h3 className="text-white/70 text-sm font-medium">Total Creators</h3>
                    <p className="text-2xl font-bold text-blue-400">25</p>
                </div>
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-4 border border-white/20">
                    <h3 className="text-white/70 text-sm font-medium">Success Rate</h3>
                    <p className="text-2xl font-bold text-purple-400">98.5%</p>
                </div>
            </div>

            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                <h3 className="text-xl font-bold text-white mb-4">Recent Payouts</h3>
                <div className="space-y-3">
                    <div className="flex items-center justify-between bg-white/5 p-3 rounded-lg">
                        <div className="flex items-center space-x-3">
                            <div className="w-10 h-10 bg-green-600 rounded-full flex items-center justify-center">
                                <span className="text-white text-sm">✓</span>
                            </div>
                            <div>
                                <p className="text-white font-medium">creator1@test.com</p>
                                <p className="text-white/60 text-sm">Processed • Stripe Connect</p>
                            </div>
                        </div>
                        <div className="text-right">
                            <p className="text-green-400 font-medium">$285.60</p>
                            <p className="text-white/60 text-sm">2 hours ago</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );

    const renderAIAgents = () => (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-white">AI Agent Framework</h2>
                <div className="px-3 py-1 bg-green-600/20 text-green-400 text-sm rounded-lg">
                    Framework Active
                </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-4 border border-white/20">
                    <h3 className="text-white/70 text-sm font-medium">Active Agents</h3>
                    <p className="text-2xl font-bold text-green-400">4</p>
                </div>
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-4 border border-white/20">
                    <h3 className="text-white/70 text-sm font-medium">Tasks Today</h3>
                    <p className="text-2xl font-bold text-blue-400">127</p>
                </div>
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-4 border border-white/20">
                    <h3 className="text-white/70 text-sm font-medium">Success Rate</h3>
                    <p className="text-2xl font-bold text-purple-400">94.2%</p>
                </div>
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-4 border border-white/20">
                    <h3 className="text-white/70 text-sm font-medium">Avg Processing</h3>
                    <p className="text-2xl font-bold text-yellow-400">850ms</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                    <h3 className="text-xl font-bold text-white mb-4">AI Agents Status</h3>
                    <div className="space-y-3">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                                <div className="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center">
                                    <span className="text-white text-xs">🔍</span>
                                </div>
                                <div>
                                    <p className="text-white font-medium">Content Moderation AI</p>
                                    <p className="text-white/60 text-sm">Processing content automatically</p>
                                </div>
                            </div>
                            <div className="px-2 py-1 bg-green-600/20 text-green-400 text-xs rounded">Active</div>
                        </div>
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                                    <span className="text-white text-xs">💬</span>
                                </div>
                                <div>
                                    <p className="text-white font-medium">Customer Service AI</p>
                                    <p className="text-white/60 text-sm">Analyzing support tickets</p>
                                </div>
                            </div>
                            <div className="px-2 py-1 bg-green-600/20 text-green-400 text-xs rounded">Active</div>
                        </div>
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                                <div className="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center">
                                    <span className="text-white text-xs">📊</span>
                                </div>
                                <div>
                                    <p className="text-white font-medium">Sales Analytics AI</p>
                                    <p className="text-white/60 text-sm">Generating insights</p>
                                </div>
                            </div>
                            <div className="px-2 py-1 bg-green-600/20 text-green-400 text-xs rounded">Active</div>
                        </div>
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                                <div className="w-8 h-8 bg-orange-600 rounded-full flex items-center justify-center">
                                    <span className="text-white text-xs">🎯</span>
                                </div>
                                <div>
                                    <p className="text-white font-medium">Marketing Analytics AI</p>
                                    <p className="text-white/60 text-sm">Optimizing campaigns</p>
                                </div>
                            </div>
                            <div className="px-2 py-1 bg-green-600/20 text-green-400 text-xs rounded">Active</div>
                        </div>
                    </div>
                </div>

                <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                    <h3 className="text-xl font-bold text-white mb-4">Recent AI Tasks</h3>
                    <div className="space-y-3">
                        <div className="bg-white/5 p-3 rounded-lg">
                            <div className="flex justify-between items-start">
                                <div>
                                    <p className="text-white text-sm font-medium">Content Analysis</p>
                                    <p className="text-white/60 text-xs">Video content reviewed</p>
                                </div>
                                <div className="px-2 py-1 bg-green-600/20 text-green-400 text-xs rounded">Completed</div>
                            </div>
                            <div className="mt-2 text-white/60 text-xs">Processing time: 1.2s • Confidence: 94%</div>
                        </div>
                        <div className="bg-white/5 p-3 rounded-lg">
                            <div className="flex justify-between items-start">
                                <div>
                                    <p className="text-white text-sm font-medium">Sales Prediction</p>
                                    <p className="text-white/60 text-xs">Revenue forecast generated</p>
                                </div>
                                <div className="px-2 py-1 bg-green-600/20 text-green-400 text-xs rounded">Completed</div>
                            </div>
                            <div className="mt-2 text-white/60 text-xs">Processing time: 2.1s • Confidence: 87%</div>
                        </div>
                    </div>
                    
                    <div className="mt-4">
                        <button className="w-full px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700">
                            View All AI Tasks
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-blue-900">
            {/* Header */}
            <div className="bg-white/10 backdrop-blur-lg border-b border-white/20">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center py-4">
                        <div>
                            <h1 className="text-2xl font-bold text-white">Administrator Console</h1>
                            <p className="text-white/70">Welcome back, {admin.full_name}</p>
                        </div>
                        <button
                            onClick={onLogout}
                            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                        >
                            Logout
                        </button>
                    </div>
                </div>
            </div>

            {/* Navigation Tabs */}
            <div className="bg-white/5 backdrop-blur-lg border-b border-white/10">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <nav className="flex space-x-8 py-4">
                        {tabs.map(tab => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`flex items-center space-x-2 px-3 py-2 rounded-lg font-medium transition-colors ${
                                    activeTab === tab.id
                                        ? 'bg-white/20 text-white'
                                        : 'text-white/70 hover:text-white hover:bg-white/10'
                                }`}
                            >
                                <span>{tab.icon}</span>
                                <span>{tab.name}</span>
                            </button>
                        ))}
                    </nav>
                </div>
            </div>

            {/* Main Content */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {renderContent()}
            </div>
        </div>
    );
};

export default AdminDashboard;
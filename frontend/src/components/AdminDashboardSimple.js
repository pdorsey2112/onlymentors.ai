import React, { useState, useEffect } from 'react';

const AdminDashboardSimple = ({ admin, onLogout }) => {
    const [activeTab, setActiveTab] = useState('overview');
    const [dashboardData, setDashboardData] = useState(null);
    const [users, setUsers] = useState([]);
    const [mentors, setMentors] = useState([]);
    const [userActivityReport, setUserActivityReport] = useState(null);
    const [financialReport, setFinancialReport] = useState(null);
    const [loading, setLoading] = useState(true);

    // Helper function to format numbers with commas
    const formatNumber = (num) => {
        if (num == null || num === undefined) return '0';
        return num.toLocaleString();
    };

    // Helper function to format currency with commas
    const formatCurrency = (num) => {
        if (num == null || num === undefined) return '$0.00';
        return `$${num.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    };

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
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL}/api/admin/users?limit=100`, {
                headers: getAuthHeaders()
            });
            if (response.ok) {
                const data = await response.json();
                setUsers(data.users);
            }
        } catch (error) {
            console.error('Error fetching users:', error);
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

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            await Promise.all([
                fetchDashboardData(),
                fetchUsers(),
                fetchMentors(),
                fetchUserActivityReport(),
                fetchFinancialReport()
            ]);
            setLoading(false);
        };
        loadData();
    }, []);

    const tabs = [
        { id: 'overview', name: 'Overview' },
        { id: 'users', name: 'Users' },
        { id: 'mentors', name: 'Mentors' },
        { id: 'content-moderation', name: 'Content Moderation' },
        { id: 'payouts', name: 'Payouts' },
        { id: 'user-reports', name: 'User Reports' },
        { id: 'financial-reports', name: 'Financial Reports' },
        { id: 'ai-agents', name: 'AI Agents' }
    ];

    if (loading) {
        return (
            <div style={{
                minHeight: '100vh',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white'
            }}>
                <div style={{ textAlign: 'center' }}>
                    <div style={{
                        width: '50px',
                        height: '50px',
                        border: '3px solid rgba(255,255,255,0.3)',
                        borderTop: '3px solid white',
                        borderRadius: '50%',
                        animation: 'spin 1s linear infinite',
                        margin: '0 auto 20px'
                    }}></div>
                    <p>Loading Admin Dashboard...</p>
                </div>
            </div>
        );
    }

    const renderOverview = () => (
        <div style={{ padding: '20px' }}>
            <h2 style={{ color: '#333', marginBottom: '30px', fontSize: '28px' }}>Platform Overview</h2>
            
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                gap: '20px',
                marginBottom: '30px'
            }}>
                {dashboardData && (
                    <>
                        <div style={{
                            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                            padding: '25px',
                            borderRadius: '12px',
                            color: 'white',
                            textAlign: 'center'
                        }}>
                            <h3 style={{ margin: '0 0 10px 0', fontSize: '16px', opacity: '0.9' }}>Total Users</h3>
                            <p style={{ margin: '0', fontSize: '32px', fontWeight: 'bold' }}>
                                {formatNumber(dashboardData.platform_stats.total_users)}
                            </p>
                        </div>
                        
                        <div style={{
                            background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                            padding: '25px',
                            borderRadius: '12px',
                            color: 'white',
                            textAlign: 'center'
                        }}>
                            <h3 style={{ margin: '0 0 10px 0', fontSize: '16px', opacity: '0.9' }}>Total Mentors</h3>
                            <p style={{ margin: '0', fontSize: '32px', fontWeight: 'bold' }}>
                                {formatNumber(dashboardData.platform_stats.total_mentors)}
                            </p>
                        </div>
                        
                        <div style={{
                            background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
                            padding: '25px',
                            borderRadius: '12px',
                            color: 'white',
                            textAlign: 'center'
                        }}>
                            <h3 style={{ margin: '0 0 10px 0', fontSize: '16px', opacity: '0.9' }}>Total Revenue</h3>
                            <p style={{ margin: '0', fontSize: '32px', fontWeight: 'bold' }}>
                                {formatCurrency(dashboardData.platform_stats.total_revenue)}
                            </p>
                        </div>
                        
                        <div style={{
                            background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
                            padding: '25px',
                            borderRadius: '12px',
                            color: 'white',
                            textAlign: 'center'
                        }}>
                            <h3 style={{ margin: '0 0 10px 0', fontSize: '16px', opacity: '0.9' }}>Active Subscriptions</h3>
                            <p style={{ margin: '0', fontSize: '32px', fontWeight: 'bold' }}>
                                {formatNumber(dashboardData.platform_stats.active_subscriptions)}
                            </p>
                        </div>
                    </>
                )}
            </div>

            {dashboardData && (
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
                    gap: '20px'
                }}>
                    <div style={{
                        background: 'white',
                        padding: '25px',
                        borderRadius: '12px',
                        boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
                    }}>
                        <h3 style={{ color: '#333', marginBottom: '20px', fontSize: '20px' }}>User Metrics</h3>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ color: '#666' }}>New Users (Week):</span>
                                <span style={{ fontWeight: 'bold', color: '#333' }}>{formatNumber(dashboardData.user_metrics.new_users_week)}</span>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ color: '#666' }}>Active Users:</span>
                                <span style={{ fontWeight: 'bold', color: '#333' }}>{formatNumber(dashboardData.user_metrics.active_users)}</span>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ color: '#666' }}>Subscribed Users:</span>
                                <span style={{ fontWeight: 'bold', color: '#22c55e' }}>{formatNumber(dashboardData.user_metrics.subscribed_users)}</span>
                            </div>
                        </div>
                    </div>

                    <div style={{
                        background: 'white',
                        padding: '25px',
                        borderRadius: '12px',
                        boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
                    }}>
                        <h3 style={{ color: '#333', marginBottom: '20px', fontSize: '20px' }}>Mentor Metrics</h3>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ color: '#666' }}>Approved Mentors:</span>
                                <span style={{ fontWeight: 'bold', color: '#22c55e' }}>{formatNumber(dashboardData.mentor_metrics.approved_mentors)}</span>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ color: '#666' }}>Pending Approval:</span>
                                <span style={{ fontWeight: 'bold', color: '#f59e0b' }}>{formatNumber(dashboardData.mentor_metrics.pending_mentors)}</span>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ color: '#666' }}>Total Earnings:</span>
                                <span style={{ fontWeight: 'bold', color: '#22c55e' }}>{formatCurrency(dashboardData.mentor_metrics.total_earnings)}</span>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );

    const renderUsers = () => (
        <div style={{ padding: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
                <h2 style={{ color: '#333', fontSize: '28px', margin: 0 }}>User Management ({users.length} users)</h2>
            </div>

            <div style={{
                background: 'white',
                borderRadius: '12px',
                boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                overflow: 'hidden'
            }}>
                <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                            <tr style={{ background: '#f8fafc' }}>
                                <th style={{ padding: '15px', textAlign: 'left', color: '#374151', fontWeight: '600' }}>Email</th>
                                <th style={{ padding: '15px', textAlign: 'left', color: '#374151', fontWeight: '600' }}>Full Name</th>
                                <th style={{ padding: '15px', textAlign: 'left', color: '#374151', fontWeight: '600' }}>Questions</th>
                                <th style={{ padding: '15px', textAlign: 'left', color: '#374151', fontWeight: '600' }}>Subscription</th>
                                <th style={{ padding: '15px', textAlign: 'left', color: '#374151', fontWeight: '600' }}>Joined</th>
                            </tr>
                        </thead>
                        <tbody>
                            {users.slice(0, 50).map((user, index) => (
                                <tr key={user.user_id} style={{ 
                                    borderTop: index > 0 ? '1px solid #e5e7eb' : 'none',
                                    ':hover': { background: '#f9fafb' }
                                }}>
                                    <td style={{ padding: '15px', color: '#374151' }}>{user.email}</td>
                                    <td style={{ padding: '15px', color: '#374151' }}>{user.full_name}</td>
                                    <td style={{ padding: '15px', color: '#374151' }}>{formatNumber(user.questions_asked)}</td>
                                    <td style={{ padding: '15px' }}>
                                        <span style={{
                                            padding: '4px 12px',
                                            borderRadius: '20px',
                                            fontSize: '12px',
                                            fontWeight: '600',
                                            background: user.is_subscribed ? '#dcfce7' : '#f3f4f6',
                                            color: user.is_subscribed ? '#166534' : '#374151'
                                        }}>
                                            {user.is_subscribed ? 'Premium' : 'Free'}
                                        </span>
                                    </td>
                                    <td style={{ padding: '15px', color: '#6b7280' }}>
                                        {new Date(user.created_at).toLocaleDateString()}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );

    const renderMentors = () => (
        <div style={{ padding: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
                <h2 style={{ color: '#333', fontSize: '28px', margin: 0 }}>Mentor Management ({mentors.length} mentors)</h2>
            </div>

            <div style={{
                background: 'white',
                borderRadius: '12px',
                boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                overflow: 'hidden'
            }}>
                <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                            <tr style={{ background: '#f8fafc' }}>
                                <th style={{ padding: '15px', textAlign: 'left', color: '#374151', fontWeight: '600' }}>Account Name</th>
                                <th style={{ padding: '15px', textAlign: 'left', color: '#374151', fontWeight: '600' }}>Email</th>
                                <th style={{ padding: '15px', textAlign: 'left', color: '#374151', fontWeight: '600' }}>Category</th>
                                <th style={{ padding: '15px', textAlign: 'left', color: '#374151', fontWeight: '600' }}>Status</th>
                                <th style={{ padding: '15px', textAlign: 'left', color: '#374151', fontWeight: '600' }}>Subscribers</th>
                                <th style={{ padding: '15px', textAlign: 'left', color: '#374151', fontWeight: '600' }}>Earnings</th>
                            </tr>
                        </thead>
                        <tbody>
                            {mentors.map((mentor, index) => (
                                <tr key={mentor.creator_id} style={{ 
                                    borderTop: index > 0 ? '1px solid #e5e7eb' : 'none'
                                }}>
                                    <td style={{ padding: '15px', color: '#374151', fontWeight: '500' }}>{mentor.account_name}</td>
                                    <td style={{ padding: '15px', color: '#374151' }}>{mentor.email}</td>
                                    <td style={{ padding: '15px', color: '#374151', textTransform: 'capitalize' }}>{mentor.category}</td>
                                    <td style={{ padding: '15px' }}>
                                        <span style={{
                                            padding: '4px 12px',
                                            borderRadius: '20px',
                                            fontSize: '12px',
                                            fontWeight: '600',
                                            background: mentor.status === 'approved' ? '#dcfce7' : mentor.status === 'pending' ? '#fef3c7' : '#fecaca',
                                            color: mentor.status === 'approved' ? '#166534' : mentor.status === 'pending' ? '#92400e' : '#991b1b'
                                        }}>
                                            {mentor.status}
                                        </span>
                                    </td>
                                    <td style={{ padding: '15px', color: '#374151' }}>{formatNumber(mentor.subscriber_count)}</td>
                                    <td style={{ padding: '15px', color: '#22c55e', fontWeight: '600' }}>
                                        {formatCurrency(mentor.total_earnings)}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );

    const renderContent = () => {
        switch (activeTab) {
            case 'overview': return renderOverview();
            case 'users': return renderUsers();
            case 'mentors': return renderMentors();
            case 'content-moderation': return (
                <div style={{ padding: '20px', textAlign: 'center' }}>
                    <h2 style={{ color: '#333', fontSize: '28px' }}>Content Moderation</h2>
                    <p style={{ color: '#666', fontSize: '18px', marginTop: '20px' }}>Content moderation system ready for implementation.</p>
                </div>
            );
            case 'payouts': return (
                <div style={{ padding: '20px', textAlign: 'center' }}>
                    <h2 style={{ color: '#333', fontSize: '28px' }}>Creator Payouts</h2>
                    <p style={{ color: '#666', fontSize: '18px', marginTop: '20px' }}>Payout processing system ready for creators.</p>
                </div>
            );
            case 'user-reports': return (
                <div style={{ padding: '20px' }}>
                    <h2 style={{ color: '#333', fontSize: '28px', marginBottom: '30px' }}>User Activity Reports</h2>
                    {userActivityReport && (
                        <div style={{
                            display: 'grid',
                            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                            gap: '20px'
                        }}>
                            <div style={{
                                background: 'white',
                                padding: '25px',
                                borderRadius: '12px',
                                boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                                textAlign: 'center'
                            }}>
                                <h3 style={{ color: '#666', margin: '0 0 10px 0' }}>Total Users</h3>
                                <p style={{ fontSize: '36px', fontWeight: 'bold', color: '#333', margin: 0 }}>
                                    {userActivityReport.summary.total_users}
                                </p>
                            </div>
                            <div style={{
                                background: 'white',
                                padding: '25px',
                                borderRadius: '12px',
                                boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                                textAlign: 'center'
                            }}>
                                <h3 style={{ color: '#666', margin: '0 0 10px 0' }}>Total Questions</h3>
                                <p style={{ fontSize: '36px', fontWeight: 'bold', color: '#3b82f6', margin: 0 }}>
                                    {userActivityReport.summary.total_questions}
                                </p>
                            </div>
                            <div style={{
                                background: 'white',
                                padding: '25px',
                                borderRadius: '12px',
                                boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                                textAlign: 'center'
                            }}>
                                <h3 style={{ color: '#666', margin: '0 0 10px 0' }}>Subscribed Users</h3>
                                <p style={{ fontSize: '36px', fontWeight: 'bold', color: '#22c55e', margin: 0 }}>
                                    {userActivityReport.summary.subscribed_users}
                                </p>
                            </div>
                        </div>
                    )}
                </div>
            );
            case 'financial-reports': return (
                <div style={{ padding: '20px' }}>
                    <h2 style={{ color: '#333', fontSize: '28px', marginBottom: '30px' }}>Financial Reports</h2>
                    {financialReport && (
                        <div style={{
                            display: 'grid',
                            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                            gap: '20px'
                        }}>
                            <div style={{
                                background: 'white',
                                padding: '25px',
                                borderRadius: '12px',
                                boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                                textAlign: 'center'
                            }}>
                                <h3 style={{ color: '#666', margin: '0 0 10px 0' }}>Total Revenue</h3>
                                <p style={{ fontSize: '36px', fontWeight: 'bold', color: '#22c55e', margin: 0 }}>
                                    ${financialReport.summary.total_revenue?.toFixed(2)}
                                </p>
                            </div>
                            <div style={{
                                background: 'white',
                                padding: '25px',
                                borderRadius: '12px',
                                boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                                textAlign: 'center'
                            }}>
                                <h3 style={{ color: '#666', margin: '0 0 10px 0' }}>Platform Commission</h3>
                                <p style={{ fontSize: '36px', fontWeight: 'bold', color: '#3b82f6', margin: 0 }}>
                                    ${financialReport.summary.platform_commission?.toFixed(2)}
                                </p>
                            </div>
                            <div style={{
                                background: 'white',
                                padding: '25px',
                                borderRadius: '12px',
                                boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                                textAlign: 'center'
                            }}>
                                <h3 style={{ color: '#666', margin: '0 0 10px 0' }}>Creator Payouts</h3>
                                <p style={{ fontSize: '36px', fontWeight: 'bold', color: '#8b5cf6', margin: 0 }}>
                                    ${financialReport.summary.creator_payouts?.toFixed(2)}
                                </p>
                            </div>
                        </div>
                    )}
                </div>
            );
            case 'ai-agents': return (
                <div style={{ padding: '20px', textAlign: 'center' }}>
                    <h2 style={{ color: '#333', fontSize: '28px' }}>AI Agent Framework</h2>
                    <p style={{ color: '#666', fontSize: '18px', marginTop: '20px' }}>AI automation system operational with 4 active agents.</p>
                </div>
            );
            default: return renderOverview();
        }
    };

    return (
        <div style={{
            minHeight: '100vh',
            background: '#f3f4f6'
        }}>
            {/* Header */}
            <div style={{
                background: 'white',
                borderBottom: '1px solid #e5e7eb',
                padding: '0 20px'
            }}>
                <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    height: '80px',
                    maxWidth: '1400px',
                    margin: '0 auto'
                }}>
                    <div>
                        <h1 style={{
                            fontSize: '32px',
                            fontWeight: 'bold',
                            color: '#333',
                            margin: 0,
                            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                            WebkitBackgroundClip: 'text',
                            WebkitTextFillColor: 'transparent'
                        }}>
                            Administrator Console
                        </h1>
                        <p style={{ color: '#666', margin: '5px 0 0 0' }}>Welcome back, {admin.full_name}</p>
                    </div>
                    <button
                        onClick={onLogout}
                        style={{
                            padding: '12px 24px',
                            background: '#dc2626',
                            color: 'white',
                            border: 'none',
                            borderRadius: '8px',
                            fontSize: '16px',
                            cursor: 'pointer',
                            fontWeight: '600'
                        }}
                    >
                        Logout
                    </button>
                </div>
            </div>

            {/* Navigation Tabs */}
            <div style={{
                background: 'white',
                borderBottom: '1px solid #e5e7eb'
            }}>
                <div style={{
                    maxWidth: '1400px',
                    margin: '0 auto',
                    padding: '0 20px'
                }}>
                    <nav style={{
                        display: 'flex',
                        gap: '0',
                        overflowX: 'auto'
                    }}>
                        {tabs.map(tab => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                style={{
                                    padding: '16px 24px',
                                    background: 'none',
                                    border: 'none',
                                    fontSize: '16px',
                                    fontWeight: '600',
                                    cursor: 'pointer',
                                    borderBottom: activeTab === tab.id ? '3px solid #667eea' : '3px solid transparent',
                                    color: activeTab === tab.id ? '#667eea' : '#6b7280',
                                    whiteSpace: 'nowrap',
                                    transition: 'all 0.2s ease'
                                }}
                            >
                                {tab.name}
                            </button>
                        ))}
                    </nav>
                </div>
            </div>

            {/* Main Content */}
            <div style={{
                maxWidth: '1400px',
                margin: '0 auto',
                minHeight: 'calc(100vh - 161px)'
            }}>
                {renderContent()}
            </div>

            <style jsx>{`
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            `}</style>
        </div>
    );
};

export default AdminDashboardSimple;
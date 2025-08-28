import React, { useState, useEffect } from 'react';
import { getBackendURL } from '../config';
import EnhancedContextDemo from './EnhancedContextDemo';

const AdminDashboardSimple = ({ admin, onLogout }) => {
    const [activeTab, setActiveTab] = useState('overview');
    const [dashboardData, setDashboardData] = useState(null);
    const [users, setUsers] = useState([]);
    const [mentors, setMentors] = useState([]);
    const [userActivityReport, setUserActivityReport] = useState(null);
    const [financialReport, setFinancialReport] = useState(null);
    const [loading, setLoading] = useState(true);
    const [showContextDemo, setShowContextDemo] = useState(false);

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
        'Authorization': `Bearer ${localStorage.getItem('admin_token')}`,
        'Content-Type': 'application/json'
    });

    const fetchDashboardData = async () => {
        try {
            const backendURL = getBackendURL();
            const response = await fetch(`${backendURL}/api/admin/dashboard`, {
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
            const backendURL = getBackendURL();
            const response = await fetch(`${backendURL}/api/admin/users?limit=100`, {
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
            const backendURL = getBackendURL();
            const response = await fetch(`${backendURL}/api/admin/mentors?limit=100`, {
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
            const backendURL = getBackendURL();
            const response = await fetch(`${backendURL}/api/admin/reports/user-activity`, {
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
            const backendURL = getBackendURL();
            const response = await fetch(`${backendURL}/api/admin/reports/financial`, {
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

    const [resetPasswordModal, setResetPasswordModal] = useState({ show: false, userId: null });
    const [resetPasswordReason, setResetPasswordReason] = useState('');
    const [suspendUserModal, setSuspendUserModal] = useState({ show: false, userId: null, isSuspended: false });
    const [suspendUserReason, setSuspendUserReason] = useState('');
    const [deleteUserModal, setDeleteUserModal] = useState({ show: false, userId: null });
    const [deleteUserReason, setDeleteUserReason] = useState('');
    
    // Mentor management modals
    const [resetMentorPasswordModal, setResetMentorPasswordModal] = useState({ show: false, mentorId: null });
    const [resetMentorPasswordReason, setResetMentorPasswordReason] = useState('');
    const [suspendMentorModal, setSuspendMentorModal] = useState({ show: false, mentorId: null, isSuspended: false });
    const [suspendMentorReason, setSuspendMentorReason] = useState('');
    const [deleteMentorModal, setDeleteMentorModal] = useState({ show: false, mentorId: null });
    const [deleteMentorReason, setDeleteMentorReason] = useState('');

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

    // User management action functions (Step 2: Updated reset password with dropdown)
    const handleResetPassword = (userId) => {
        setResetPasswordModal({ show: true, userId: userId });
        setResetPasswordReason('');
    };

    const confirmResetPassword = async () => {
        if (!resetPasswordReason) {
            alert('Please select a reason for resetting the password.');
            return;
        }

        try {
            const backendURL = getBackendURL();
            const response = await fetch(`${backendURL}/api/admin/users/${resetPasswordModal.userId}/reset-password`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify({ reason: resetPasswordReason })
            });

            if (response.ok) {
                const data = await response.json();
                const emailStatus = data.email_status === 'sent' ? '✅' : '⚠️';
                const statusText = data.email_status === 'sent' ? 'sent successfully' : 'initiated (delivery pending)';
                
                alert(`${emailStatus} Password reset ${statusText}!\n\n📧 Email: ${data.email}\n⏰ Link expires in: ${data.expires_in}\n🔒 ${data.note}\n\nThe user will receive an email with a secure link to set their new password.`);
                setResetPasswordModal({ show: false, userId: null });
                setResetPasswordReason('');
                fetchUsers(); // Refresh users to show locked status
            } else {
                const errorData = await response.json();
                alert(`Error sending password reset email: ${errorData.detail || 'Unknown error'}`);
            }
        } catch (error) {
            console.error('Error sending password reset email:', error);
            alert('Network error. Please try again.');
        }
    };

    const cancelResetPassword = () => {
        setResetPasswordModal({ show: false, userId: null });
        setResetPasswordReason('');
    };

    const handleSuspendUser = (userId, isSuspended = false) => {
        setSuspendUserModal({ show: true, userId: userId, isSuspended: isSuspended });
        setSuspendUserReason('');
    };

    const confirmSuspendUser = async () => {
        if (!suspendUserReason) {
            alert('Please select a reason for suspending the user.');
            return;
        }

        try {
            const backendURL = getBackendURL();
            const response = await fetch(`${backendURL}/api/admin/users/${suspendUserModal.userId}/suspend`, {
                method: 'PUT',
                headers: getAuthHeaders(),
                body: JSON.stringify({ 
                    suspend: !suspendUserModal.isSuspended, // Toggle suspend status
                    reason: suspendUserReason 
                })
            });

            if (response.ok) {
                const data = await response.json();
                const emailStatus = data.email_sent ? '📧 Notification email sent to user' : '⚠️ Notification email pending';
                const action = suspendUserModal.isSuspended ? 'reactivated' : 'suspended';
                alert(`✅ User ${action} successfully!\n${emailStatus}\n\nReason: ${suspendUserReason}\n\nThe user has been ${action} and will receive an email explaining the action.`);
                setSuspendUserModal({ show: false, userId: null, isSuspended: false });
                setSuspendUserReason('');
                fetchUsers();
            } else {
                let errorMessage = 'Unknown error';
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorData.message || JSON.stringify(errorData);
                } catch (parseError) {
                    // If JSON parsing fails, use response text
                    try {
                        errorMessage = await response.text() || `HTTP ${response.status}`;
                    } catch (textError) {
                        errorMessage = `HTTP ${response.status} - ${response.statusText}`;
                    }
                }
                alert(`Error suspending user: ${errorMessage}`);
            }
        } catch (error) {
            console.error('Error suspending user:', error);
            alert(`Network error suspending user: ${error.message || error.toString()}`);
        }
    };

    const cancelSuspendUser = () => {
        setSuspendUserModal({ show: false, userId: null });
        setSuspendUserReason('');
    };

    const handleDeleteUser = (userId) => {
        setDeleteUserModal({ show: true, userId: userId });
        setDeleteUserReason('');
    };

    const confirmDeleteUser = async () => {
        if (!deleteUserReason) {
            alert('Please select a reason for deleting the user.');
            return;
        }

        try {
            const backendURL = getBackendURL();
            const response = await fetch(`${backendURL}/api/admin/users/${deleteUserModal.userId}`, {
                method: 'DELETE',
                headers: getAuthHeaders(),
                body: JSON.stringify({ reason: deleteUserReason })
            });

            if (response.ok) {
                const data = await response.json();
                const emailStatus = data.email_sent ? '📧 Notification email sent to user' : '⚠️ Notification email pending';
                alert(`✅ ${data.message}\n${emailStatus}\n\nReason: ${deleteUserReason}\n\n⚠️ This action cannot be undone. The user has been notified via email about the account deletion.`);
                setDeleteUserModal({ show: false, userId: null });
                setDeleteUserReason('');
                fetchUsers();
            } else {
                let errorMessage = 'Unknown error';
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorData.message || JSON.stringify(errorData);
                } catch (parseError) {
                    // If JSON parsing fails, use response text
                    try {
                        errorMessage = await response.text() || `HTTP ${response.status}`;
                    } catch (textError) {
                        errorMessage = `HTTP ${response.status} - ${response.statusText}`;
                    }
                }
                alert(`Error deleting user: ${errorMessage}`);
            }
        } catch (error) {
            console.error('Error deleting user:', error);
            alert(`Network error deleting user: ${error.message || error.toString()}`);
        }
    };

    const cancelDeleteUser = () => {
        setDeleteUserModal({ show: false, userId: null });
        setDeleteUserReason('');
    };

    // Mentor management action functions
    const handleResetMentorPassword = (mentorId) => {
        setResetMentorPasswordModal({ show: true, mentorId: mentorId });
        setResetMentorPasswordReason('');
    };

    const confirmResetMentorPassword = async () => {
        if (!resetMentorPasswordReason) {
            alert('Please select a reason for resetting the mentor password.');
            return;
        }

        try {
            const backendURL = getBackendURL();
            const response = await fetch(`${backendURL}/api/admin/mentors/${resetMentorPasswordModal.mentorId}/reset-password`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify({ reason: resetMentorPasswordReason })
            });

            if (response.ok) {
                const data = await response.json();
                const emailStatus = data.email_status === 'sent' ? '✅' : '⚠️';
                const statusText = data.email_status === 'sent' ? 'sent successfully' : 'initiated (delivery pending)';
                
                alert(`${emailStatus} Mentor password reset ${statusText}!\n\n📧 Email: ${data.email}\n⏰ Link expires in: ${data.expires_in}\n🔒 ${data.note}\n\nThe mentor will receive an email with a secure link to set their new password.`);
                setResetMentorPasswordModal({ show: false, mentorId: null });
                setResetMentorPasswordReason('');
                fetchMentors(); // Refresh mentors to show locked status
            } else {
                const errorData = await response.json();
                alert(`Error sending mentor password reset email: ${errorData.detail || 'Unknown error'}`);
            }
        } catch (error) {
            console.error('Error sending mentor password reset email:', error);
            alert('Network error. Please try again.');
        }
    };

    const cancelResetMentorPassword = () => {
        setResetMentorPasswordModal({ show: false, mentorId: null });
        setResetMentorPasswordReason('');
    };

    const handleSuspendMentor = (mentorId, isSuspended = false) => {
        setSuspendMentorModal({ show: true, mentorId: mentorId, isSuspended: isSuspended });
        setSuspendMentorReason('');
    };

    const confirmSuspendMentor = async () => {
        if (!suspendMentorReason) {
            alert('Please select a reason for the mentor action.');
            return;
        }

        try {
            const backendURL = getBackendURL();
            const response = await fetch(`${backendURL}/api/admin/mentors/${suspendMentorModal.mentorId}/suspend`, {
                method: 'PUT',
                headers: getAuthHeaders(),
                body: JSON.stringify({ 
                    suspend: !suspendMentorModal.isSuspended, // Toggle suspend status
                    reason: suspendMentorReason 
                })
            });

            if (response.ok) {
                const data = await response.json();
                const emailStatus = data.email_sent ? '📧 Notification email sent to mentor' : '⚠️ Notification email pending';
                const action = suspendMentorModal.isSuspended ? 'reactivated' : 'suspended';
                alert(`✅ Mentor ${action} successfully!\n${emailStatus}\n\nReason: ${suspendMentorReason}\n\nThe mentor has been ${action} and will receive an email explaining the action.`);
                setSuspendMentorModal({ show: false, mentorId: null, isSuspended: false });
                setSuspendMentorReason('');
                fetchMentors();
            } else {
                let errorMessage = 'Unknown error';
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorData.message || JSON.stringify(errorData);
                } catch (parseError) {
                    try {
                        errorMessage = await response.text() || `HTTP ${response.status}`;
                    } catch (textError) {
                        errorMessage = `HTTP ${response.status} - ${response.statusText}`;
                    }
                }
                alert(`Error updating mentor status: ${errorMessage}`);
            }
        } catch (error) {
            console.error('Error updating mentor status:', error);
            alert(`Network error updating mentor status: ${error.message || error.toString()}`);
        }
    };

    const cancelSuspendMentor = () => {
        setSuspendMentorModal({ show: false, mentorId: null });
        setSuspendMentorReason('');
    };

    const handleDeleteMentor = (mentorId) => {
        setDeleteMentorModal({ show: true, mentorId: mentorId });
        setDeleteMentorReason('');
    };

    const confirmDeleteMentor = async () => {
        if (!deleteMentorReason) {
            alert('Please select a reason for deleting the mentor.');
            return;
        }

        try {
            const backendURL = getBackendURL();
            const response = await fetch(`${backendURL}/api/admin/mentors/${deleteMentorModal.mentorId}`, {
                method: 'DELETE',
                headers: getAuthHeaders(),
                body: JSON.stringify({ reason: deleteMentorReason })
            });

            if (response.ok) {
                const data = await response.json();
                const emailStatus = data.email_sent ? '📧 Notification email sent to mentor' : '⚠️ Notification email pending';
                alert(`✅ ${data.message}\n${emailStatus}\n\nReason: ${deleteMentorReason}\n\n⚠️ This action cannot be undone. The mentor has been notified via email about the account deletion.`);
                setDeleteMentorModal({ show: false, mentorId: null });
                setDeleteMentorReason('');
                fetchMentors();
            } else {
                let errorMessage = 'Unknown error';
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorData.message || JSON.stringify(errorData);
                } catch (parseError) {
                    try {
                        errorMessage = await response.text() || `HTTP ${response.status}`;
                    } catch (textError) {
                        errorMessage = `HTTP ${response.status} - ${response.statusText}`;
                    }
                }
                alert(`Error deleting mentor: ${errorMessage}`);
            }
        } catch (error) {
            console.error('Error deleting mentor:', error);
            alert(`Network error deleting mentor: ${error.message || error.toString()}`);
        }
    };

    const cancelDeleteMentor = () => {
        setDeleteMentorModal({ show: false, mentorId: null });
        setDeleteMentorReason('');
    };

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
                            background: 'white',
                            padding: '25px',
                            borderRadius: '12px',
                            boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                            textAlign: 'center',
                            border: '1px solid #e5e7eb'
                        }}>
                            <h3 style={{ margin: '0 0 10px 0', fontSize: '16px', color: '#666' }}>Total Users</h3>
                            <p style={{ margin: '0', fontSize: '32px', fontWeight: 'bold', color: '#333' }}>
                                {formatNumber(dashboardData.platform_stats.total_users)}
                            </p>
                        </div>
                        
                        <div style={{
                            background: 'white',
                            padding: '25px',
                            borderRadius: '12px',
                            boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                            textAlign: 'center',
                            border: '1px solid #e5e7eb'
                        }}>
                            <h3 style={{ margin: '0 0 10px 0', fontSize: '16px', color: '#666' }}>Total Mentors</h3>
                            <p style={{ margin: '0', fontSize: '32px', fontWeight: 'bold', color: '#333' }}>
                                {formatNumber(dashboardData.platform_stats.total_mentors)}
                            </p>
                        </div>
                        
                        <div style={{
                            background: 'white',
                            padding: '25px',
                            borderRadius: '12px',
                            boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                            textAlign: 'center',
                            border: '1px solid #e5e7eb'
                        }}>
                            <h3 style={{ margin: '0 0 10px 0', fontSize: '16px', color: '#666' }}>Total Revenue</h3>
                            <p style={{ margin: '0', fontSize: '32px', fontWeight: 'bold', color: '#333' }}>
                                {formatCurrency(dashboardData.platform_stats.total_revenue)}
                            </p>
                        </div>
                        
                        <div style={{
                            background: 'white',
                            padding: '25px',
                            borderRadius: '12px',
                            boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                            textAlign: 'center',
                            border: '1px solid #e5e7eb'
                        }}>
                            <h3 style={{ margin: '0 0 10px 0', fontSize: '16px', color: '#666' }}>Active Subscriptions</h3>
                            <p style={{ margin: '0', fontSize: '32px', fontWeight: 'bold', color: '#333' }}>
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
                                <span style={{ fontWeight: 'bold', color: '#333' }}>{formatNumber(dashboardData.user_metrics.subscribed_users)}</span>
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
                                <span style={{ fontWeight: 'bold', color: '#333' }}>{formatNumber(dashboardData.mentor_metrics.approved_mentors)}</span>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ color: '#666' }}>Pending Approval:</span>
                                <span style={{ fontWeight: 'bold', color: '#333' }}>{formatNumber(dashboardData.mentor_metrics.pending_mentors)}</span>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ color: '#666' }}>Total Earnings:</span>
                                <span style={{ fontWeight: 'bold', color: '#333' }}>{formatCurrency(dashboardData.mentor_metrics.total_earnings)}</span>
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
                                <th style={{ padding: '15px', textAlign: 'left', color: '#374151', fontWeight: '600' }}>Status</th>
                                <th style={{ padding: '15px', textAlign: 'left', color: '#374151', fontWeight: '600' }}>Questions</th>
                                <th style={{ padding: '15px', textAlign: 'left', color: '#374151', fontWeight: '600' }}>Subscription</th>
                                <th style={{ padding: '15px', textAlign: 'left', color: '#374151', fontWeight: '600' }}>Joined</th>
                                <th style={{ padding: '15px', textAlign: 'left', color: '#374151', fontWeight: '600' }}>Actions</th>
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
                                    <td style={{ padding: '15px' }}>
                                        <span style={{
                                            padding: '4px 12px',
                                            borderRadius: '20px',
                                            fontSize: '12px',
                                            fontWeight: '600',
                                            background: user.is_suspended ? '#fee2e2' : '#dcfce7',
                                            color: user.is_suspended ? '#b91c1c' : '#166534'
                                        }}>
                                            {user.is_suspended ? '🚫 Suspended' : '✅ Active'}
                                        </span>
                                    </td>
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
                                    <td style={{ padding: '15px' }}>
                                        <div style={{ display: 'flex', gap: '8px' }}>
                                            <button
                                                onClick={() => handleResetPassword(user.user_id)}
                                                style={{
                                                    padding: '6px 12px',
                                                    backgroundColor: '#3b82f6',
                                                    color: 'white',
                                                    border: 'none',
                                                    borderRadius: '6px',
                                                    fontSize: '12px',
                                                    fontWeight: '600',
                                                    cursor: 'pointer'
                                                }}
                                            >
                                                Reset Password
                                            </button>
                                            {user.is_suspended ? (
                                                <button
                                                    onClick={() => handleSuspendUser(user.user_id, true)}
                                                    style={{
                                                        padding: '6px 12px',
                                                        backgroundColor: '#10b981',
                                                        color: 'white',
                                                        border: 'none',
                                                        borderRadius: '6px',
                                                        fontSize: '12px',
                                                        fontWeight: '600',
                                                        cursor: 'pointer'
                                                    }}
                                                >
                                                    Unsuspend
                                                </button>
                                            ) : (
                                                <button
                                                    onClick={() => handleSuspendUser(user.user_id, false)}
                                                    style={{
                                                        padding: '6px 12px',
                                                        backgroundColor: '#f59e0b',
                                                        color: 'white',
                                                        border: 'none',
                                                        borderRadius: '6px',
                                                        fontSize: '12px',
                                                        fontWeight: '600',
                                                        cursor: 'pointer'
                                                    }}
                                                >
                                                    Suspend
                                                </button>
                                            )}
                                            <button
                                                onClick={() => handleDeleteUser(user.user_id)}
                                                style={{
                                                    padding: '6px 12px',
                                                    backgroundColor: '#dc2626',
                                                    color: 'white',
                                                    border: 'none',
                                                    borderRadius: '6px',
                                                    fontSize: '12px',
                                                    fontWeight: '600',
                                                    cursor: 'pointer'
                                                }}
                                            >
                                                Delete
                                            </button>
                                        </div>
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
                                    <td style={{ padding: '15px', color: '#333', fontWeight: '600' }}>
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
                                    {formatNumber(userActivityReport.summary.total_users)}
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
                                <p style={{ fontSize: '36px', fontWeight: 'bold', color: '#333', margin: 0 }}>
                                    {formatNumber(userActivityReport.summary.total_questions)}
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
                                <p style={{ fontSize: '36px', fontWeight: 'bold', color: '#333', margin: 0 }}>
                                    {formatNumber(userActivityReport.summary.subscribed_users)}
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
                                <p style={{ fontSize: '36px', fontWeight: 'bold', color: '#333', margin: 0 }}>
                                    {formatCurrency(financialReport.summary.total_revenue)}
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
                                <p style={{ fontSize: '36px', fontWeight: 'bold', color: '#333', margin: 0 }}>
                                    {formatCurrency(financialReport.summary.platform_commission)}
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
                                <p style={{ fontSize: '36px', fontWeight: 'bold', color: '#333', margin: 0 }}>
                                    {formatCurrency(financialReport.summary.creator_payouts)}
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
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <button
                            onClick={() => setShowContextDemo(true)}
                            style={{
                                padding: '12px 24px',
                                background: '#3b82f6',
                                color: 'white',
                                border: 'none',
                                borderRadius: '8px',
                                fontSize: '16px',
                                cursor: 'pointer',
                                fontWeight: '600'
                            }}
                        >
                            Context System
                        </button>
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

            {/* Enhanced Context System Demo */}
            {showContextDemo && (
                <EnhancedContextDemo
                    onClose={() => setShowContextDemo(false)}
                />
            )}

            {/* Reset Password Modal */}
            {resetPasswordModal.show && (
                <div style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundColor: 'rgba(0, 0, 0, 0.5)',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    zIndex: 1000
                }}>
                    <div style={{
                        backgroundColor: 'white',
                        padding: '30px',
                        borderRadius: '12px',
                        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
                        width: '400px',
                        maxWidth: '90vw'
                    }}>
                        <h3 style={{
                            margin: '0 0 20px 0',
                            fontSize: '18px',
                            fontWeight: '600',
                            color: '#1f2937'
                        }}>
                            Reset User Password
                        </h3>
                        
                        <p style={{
                            margin: '0 0 20px 0',
                            color: '#6b7280',
                            fontSize: '14px'
                        }}>
                            Please select a reason for resetting this user's password:
                        </p>

                        <select
                            value={resetPasswordReason}
                            onChange={(e) => setResetPasswordReason(e.target.value)}
                            style={{
                                width: '100%',
                                padding: '10px',
                                border: '1px solid #d1d5db',
                                borderRadius: '6px',
                                fontSize: '14px',
                                marginBottom: '20px',
                                backgroundColor: 'white'
                            }}
                        >
                            <option value="">Select a reason...</option>
                            <option value="Customer Service">Customer Service</option>
                            <option value="Internal User">Internal User</option>
                            <option value="Admin">Admin</option>
                        </select>

                        <div style={{
                            display: 'flex',
                            gap: '10px',
                            justifyContent: 'flex-end'
                        }}>
                            <button
                                onClick={cancelResetPassword}
                                style={{
                                    padding: '8px 16px',
                                    backgroundColor: '#f3f4f6',
                                    color: '#374151',
                                    border: 'none',
                                    borderRadius: '6px',
                                    fontSize: '14px',
                                    fontWeight: '600',
                                    cursor: 'pointer'
                                }}
                            >
                                Cancel
                            </button>
                            <button
                                onClick={confirmResetPassword}
                                style={{
                                    padding: '8px 16px',
                                    backgroundColor: '#3b82f6',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '6px',
                                    fontSize: '14px',
                                    fontWeight: '600',
                                    cursor: 'pointer'
                                }}
                            >
                                Reset Password
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Suspend User Modal */}
            {suspendUserModal.show && (
                <div style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundColor: 'rgba(0, 0, 0, 0.5)',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    zIndex: 1000
                }}>
                    <div style={{
                        backgroundColor: 'white',
                        padding: '30px',
                        borderRadius: '12px',
                        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
                        width: '400px',
                        maxWidth: '90vw'
                    }}>
                        <h3 style={{
                            margin: '0 0 20px 0',
                            fontSize: '18px',
                            fontWeight: '600',
                            color: '#1f2937'
                        }}>
                            {suspendUserModal.isSuspended ? 'Reactivate User' : 'Suspend User'}
                        </h3>
                        
                        <p style={{
                            margin: '0 0 20px 0',
                            color: '#6b7280',
                            fontSize: '14px'
                        }}>
                            {suspendUserModal.isSuspended 
                                ? 'Please select a reason for reactivating this user:' 
                                : 'Please select a reason for suspending this user:'}
                        </p>

                        <select
                            value={suspendUserReason}
                            onChange={(e) => setSuspendUserReason(e.target.value)}
                            style={{
                                width: '100%',
                                padding: '10px',
                                border: '1px solid #d1d5db',
                                borderRadius: '6px',
                                fontSize: '14px',
                                marginBottom: '20px',
                                backgroundColor: 'white'
                            }}
                        >
                            <option value="">Select a reason...</option>
                            {suspendUserModal.isSuspended ? (
                                <>
                                    <option value="Account review completed">Account review completed</option>
                                    <option value="Appeal approved">Appeal approved</option>
                                    <option value="Administrative decision">Administrative decision</option>
                                </>
                            ) : (
                                <>
                                    <option value="Policy violation">Policy violation</option>
                                    <option value="Non-Payment">Non-Payment</option>
                                    <option value="Internal user">Internal user</option>
                                </>
                            )}
                        </select>

                        <div style={{
                            display: 'flex',
                            gap: '10px',
                            justifyContent: 'flex-end'
                        }}>
                            <button
                                onClick={cancelSuspendUser}
                                style={{
                                    padding: '8px 16px',
                                    backgroundColor: '#f3f4f6',
                                    color: '#374151',
                                    border: 'none',
                                    borderRadius: '6px',
                                    fontSize: '14px',
                                    fontWeight: '600',
                                    cursor: 'pointer'
                                }}
                            >
                                Cancel
                            </button>
                            <button
                                onClick={confirmSuspendUser}
                                style={{
                                    padding: '8px 16px',
                                    backgroundColor: suspendUserModal.isSuspended ? '#10b981' : '#f59e0b',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '6px',
                                    fontSize: '14px',
                                    fontWeight: '600',
                                    cursor: 'pointer'
                                }}
                            >
                                {suspendUserModal.isSuspended ? 'Reactivate User' : 'Suspend User'}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Delete User Modal */}
            {deleteUserModal.show && (
                <div style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundColor: 'rgba(0, 0, 0, 0.5)',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    zIndex: 1000
                }}>
                    <div style={{
                        backgroundColor: 'white',
                        padding: '30px',
                        borderRadius: '12px',
                        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
                        width: '400px',
                        maxWidth: '90vw'
                    }}>
                        <h3 style={{
                            margin: '0 0 20px 0',
                            fontSize: '18px',
                            fontWeight: '600',
                            color: '#1f2937'
                        }}>
                            Delete User
                        </h3>
                        
                        <p style={{
                            margin: '0 0 20px 0',
                            color: '#6b7280',
                            fontSize: '14px'
                        }}>
                            Please select a reason for deleting this user. <strong>This action cannot be undone.</strong>
                        </p>

                        <select
                            value={deleteUserReason}
                            onChange={(e) => setDeleteUserReason(e.target.value)}
                            style={{
                                width: '100%',
                                padding: '10px',
                                border: '1px solid #d1d5db',
                                borderRadius: '6px',
                                fontSize: '14px',
                                marginBottom: '20px',
                                backgroundColor: 'white'
                            }}
                        >
                            <option value="">Select a reason...</option>
                            <option value="Policy violations">Policy violations</option>
                            <option value="Non-Payment">Non-Payment</option>
                            <option value="Employee Termination">Employee Termination</option>
                        </select>

                        <div style={{
                            display: 'flex',
                            gap: '10px',
                            justifyContent: 'flex-end'
                        }}>
                            <button
                                onClick={cancelDeleteUser}
                                style={{
                                    padding: '8px 16px',
                                    backgroundColor: '#f3f4f6',
                                    color: '#374151',
                                    border: 'none',
                                    borderRadius: '6px',
                                    fontSize: '14px',
                                    fontWeight: '600',
                                    cursor: 'pointer'
                                }}
                            >
                                Cancel
                            </button>
                            <button
                                onClick={confirmDeleteUser}
                                style={{
                                    padding: '8px 16px',
                                    backgroundColor: '#dc2626',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '6px',
                                    fontSize: '14px',
                                    fontWeight: '600',
                                    cursor: 'pointer'
                                }}
                            >
                                Delete User
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AdminDashboardSimple;
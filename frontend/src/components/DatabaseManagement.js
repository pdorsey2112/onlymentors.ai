import React, { useState, useEffect } from 'react';
import { getBackendURL } from '../config';

const DatabaseManagement = () => {
    const [activeTab, setActiveTab] = useState('overview');
    const [overview, setOverview] = useState(null);
    const [collections, setCollections] = useState([]);
    const [selectedCollection, setSelectedCollection] = useState(null);
    const [collectionData, setCollectionData] = useState(null);
    const [userAnalytics, setUserAnalytics] = useState(null);
    const [mentorAnalytics, setMentorAnalytics] = useState(null);
    const [platformHealth, setPlatformHealth] = useState(null);
    const [loading, setLoading] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [currentPage, setCurrentPage] = useState(1);

    const getAuthHeaders = () => {
        const token = localStorage.getItem('admin_token');
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        };
    };

    const fetchDatabaseOverview = async () => {
        try {
            setLoading(true);
            const backendURL = getBackendURL();
            const response = await fetch(`${backendURL}/api/admin/database/overview`, {
                headers: getAuthHeaders()
            });

            if (response.ok) {
                const data = await response.json();
                setOverview(data);
                setCollections(data.collections || []);
            } else {
                alert('Failed to fetch database overview');
            }
        } catch (error) {
            console.error('Error fetching database overview:', error);
            alert('Error fetching database overview');
        } finally {
            setLoading(false);
        }
    };

    const fetchCollectionData = async (collectionName, page = 1) => {
        try {
            setLoading(true);
            const backendURL = getBackendURL();
            const params = new URLSearchParams({
                page: page.toString(),
                limit: '20'
            });
            
            if (searchTerm) {
                params.append('search', searchTerm);
            }

            const response = await fetch(`${backendURL}/api/admin/database/collections/${collectionName}?${params}`, {
                headers: getAuthHeaders()
            });

            if (response.ok) {
                const data = await response.json();
                setCollectionData(data);
                setCurrentPage(page);
            } else {
                alert('Failed to fetch collection data');
            }
        } catch (error) {
            console.error('Error fetching collection data:', error);
            alert('Error fetching collection data');
        } finally {
            setLoading(false);
        }
    };

    const exportCollection = async (collectionName, format) => {
        try {
            setLoading(true);
            const backendURL = getBackendURL();
            const response = await fetch(`${backendURL}/api/admin/database/export`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify({
                    collection_name: collectionName,
                    format: format,
                    search: searchTerm || null
                })
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = `${collectionName}_${new Date().toISOString().split('T')[0]}.${format}`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                alert(`${format.toUpperCase()} export completed successfully!`);
            } else {
                alert('Failed to export collection');
            }
        } catch (error) {
            console.error('Error exporting collection:', error);
            alert('Error exporting collection');
        } finally {
            setLoading(false);
        }
    };

    const createBackup = async () => {
        try {
            setLoading(true);
            const backendURL = getBackendURL();
            const response = await fetch(`${backendURL}/api/admin/database/backup`, {
                headers: getAuthHeaders()
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = `onlymentors_backup_${new Date().toISOString().split('T')[0]}.zip`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                alert('Database backup completed successfully!');
            } else {
                alert('Failed to create database backup');
            }
        } catch (error) {
            console.error('Error creating backup:', error);
            alert('Error creating backup');
        } finally {
            setLoading(false);
        }
    };

    const fetchAnalytics = async () => {
        try {
            setLoading(true);
            const backendURL = getBackendURL();
            
            // Fetch all analytics in parallel
            const [userResponse, mentorResponse, healthResponse] = await Promise.all([
                fetch(`${backendURL}/api/admin/analytics/users`, { headers: getAuthHeaders() }),
                fetch(`${backendURL}/api/admin/analytics/mentors`, { headers: getAuthHeaders() }),
                fetch(`${backendURL}/api/admin/analytics/platform-health`, { headers: getAuthHeaders() })
            ]);

            if (userResponse.ok) {
                const userData = await userResponse.json();
                setUserAnalytics(userData);
            }

            if (mentorResponse.ok) {
                const mentorData = await mentorResponse.json();
                setMentorAnalytics(mentorData);
            }

            if (healthResponse.ok) {
                const healthData = await healthResponse.json();
                setPlatformHealth(healthData);
            }
        } catch (error) {
            console.error('Error fetching analytics:', error);
            alert('Error fetching analytics');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchDatabaseOverview();
    }, []);

    useEffect(() => {
        if (activeTab === 'analytics') {
            fetchAnalytics();
        }
    }, [activeTab]);

    const renderOverview = () => (
        <div style={{ padding: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h2 style={{ color: '#333', fontSize: '24px', margin: 0 }}>Database Overview</h2>
                <button
                    onClick={createBackup}
                    disabled={loading}
                    style={{
                        padding: '10px 20px',
                        backgroundColor: '#10b981',
                        color: 'white',
                        border: 'none',
                        borderRadius: '6px',
                        fontSize: '14px',
                        fontWeight: '600',
                        cursor: loading ? 'not-allowed' : 'pointer',
                        opacity: loading ? 0.6 : 1
                    }}
                >
                    {loading ? 'Creating...' : 'Create Full Backup'}
                </button>
            </div>

            {overview && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
                    <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
                        <h3 style={{ color: '#374151', fontSize: '18px', marginBottom: '15px' }}>Database Info</h3>
                        <div style={{ fontSize: '14px', color: '#6b7280' }}>
                            <p><strong>Database:</strong> {overview.database_name}</p>
                            <p><strong>Size:</strong> {overview.database_size_mb} MB</p>
                            <p><strong>Collections:</strong> {overview.collections.length}</p>
                            <p><strong>Total Documents:</strong> {overview.total_documents.toLocaleString()}</p>
                            <p><strong>Status:</strong> <span style={{ color: '#10b981', fontWeight: '600' }}>✅ {overview.status}</span></p>
                        </div>
                    </div>

                    <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
                        <h3 style={{ color: '#374151', fontSize: '18px', marginBottom: '15px' }}>Top Collections</h3>
                        <div style={{ fontSize: '14px' }}>
                            {collections.slice(0, 5).map((collection, index) => (
                                <div key={index} style={{ 
                                    display: 'flex', 
                                    justifyContent: 'space-between', 
                                    padding: '8px 0',
                                    borderBottom: index < 4 ? '1px solid #f3f4f6' : 'none'
                                }}>
                                    <span style={{ color: '#374151', fontWeight: '500' }}>{collection.name}</span>
                                    <span style={{ color: '#6b7280' }}>{collection.document_count.toLocaleString()} docs</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            <div style={{ marginTop: '30px' }}>
                <h3 style={{ color: '#374151', fontSize: '18px', marginBottom: '15px' }}>All Collections</h3>
                <div style={{ backgroundColor: 'white', borderRadius: '8px', border: '1px solid #e5e7eb', overflow: 'hidden' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                            <tr style={{ backgroundColor: '#f9fafb' }}>
                                <th style={{ padding: '12px', textAlign: 'left', color: '#374151', fontWeight: '600' }}>Collection Name</th>
                                <th style={{ padding: '12px', textAlign: 'left', color: '#374151', fontWeight: '600' }}>Documents</th>
                                <th style={{ padding: '12px', textAlign: 'left', color: '#374151', fontWeight: '600' }}>Status</th>
                                <th style={{ padding: '12px', textAlign: 'left', color: '#374151', fontWeight: '600' }}>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {collections.map((collection, index) => (
                                <tr key={index} style={{ borderTop: index > 0 ? '1px solid #e5e7eb' : 'none' }}>
                                    <td style={{ padding: '12px', color: '#374151', fontWeight: '500' }}>{collection.name}</td>
                                    <td style={{ padding: '12px', color: '#6b7280' }}>{collection.document_count.toLocaleString()}</td>
                                    <td style={{ padding: '12px' }}>
                                        <span style={{
                                            padding: '4px 8px',
                                            borderRadius: '12px',
                                            fontSize: '12px',
                                            fontWeight: '600',
                                            backgroundColor: collection.status === 'active' ? '#dcfce7' : '#f3f4f6',
                                            color: collection.status === 'active' ? '#166534' : '#6b7280'
                                        }}>
                                            {collection.status}
                                        </span>
                                    </td>
                                    <td style={{ padding: '12px' }}>
                                        <div style={{ display: 'flex', gap: '8px' }}>
                                            <button
                                                onClick={() => {
                                                    setSelectedCollection(collection.name);
                                                    setActiveTab('browse');
                                                    fetchCollectionData(collection.name);
                                                }}
                                                style={{
                                                    padding: '6px 12px',
                                                    backgroundColor: '#3b82f6',
                                                    color: 'white',
                                                    border: 'none',
                                                    borderRadius: '4px',
                                                    fontSize: '12px',
                                                    cursor: 'pointer'
                                                }}
                                            >
                                                Browse
                                            </button>
                                            <button
                                                onClick={() => exportCollection(collection.name, 'json')}
                                                style={{
                                                    padding: '6px 12px',
                                                    backgroundColor: '#10b981',
                                                    color: 'white',
                                                    border: 'none',
                                                    borderRadius: '4px',
                                                    fontSize: '12px',
                                                    cursor: 'pointer'
                                                }}
                                            >
                                                Export JSON
                                            </button>
                                            <button
                                                onClick={() => exportCollection(collection.name, 'csv')}
                                                style={{
                                                    padding: '6px 12px',
                                                    backgroundColor: '#f59e0b',
                                                    color: 'white',
                                                    border: 'none',
                                                    borderRadius: '4px',
                                                    fontSize: '12px',
                                                    cursor: 'pointer'
                                                }}
                                            >
                                                Export CSV
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

    const renderBrowse = () => (
        <div style={{ padding: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h2 style={{ color: '#333', fontSize: '24px', margin: 0 }}>
                    Browse Collection: {selectedCollection}
                </h2>
                <button
                    onClick={() => setActiveTab('overview')}
                    style={{
                        padding: '8px 16px',
                        backgroundColor: '#6b7280',
                        color: 'white',
                        border: 'none',
                        borderRadius: '6px',
                        fontSize: '14px',
                        cursor: 'pointer'
                    }}
                >
                    ← Back to Overview
                </button>
            </div>

            <div style={{ marginBottom: '20px', display: 'flex', gap: '10px', alignItems: 'center' }}>
                <input
                    type="text"
                    placeholder="Search in collection..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    style={{
                        padding: '10px',
                        border: '1px solid #d1d5db',
                        borderRadius: '6px',
                        fontSize: '14px',
                        width: '300px'
                    }}
                />
                <button
                    onClick={() => fetchCollectionData(selectedCollection, 1)}
                    style={{
                        padding: '10px 15px',
                        backgroundColor: '#3b82f6',
                        color: 'white',
                        border: 'none',
                        borderRadius: '6px',
                        fontSize: '14px',
                        cursor: 'pointer'
                    }}
                >
                    Search
                </button>
                <button
                    onClick={() => {
                        setSearchTerm('');
                        fetchCollectionData(selectedCollection, 1);
                    }}
                    style={{
                        padding: '10px 15px',
                        backgroundColor: '#6b7280',
                        color: 'white',
                        border: 'none',
                        borderRadius: '6px',
                        fontSize: '14px',
                        cursor: 'pointer'
                    }}
                >
                    Clear
                </button>
            </div>

            {collectionData && (
                <div>
                    <div style={{ marginBottom: '15px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ color: '#6b7280', fontSize: '14px' }}>
                            Showing {collectionData.documents.length} of {collectionData.total_documents.toLocaleString()} documents
                            {searchTerm && ` (filtered by "${searchTerm}")`}
                        </span>
                        <div style={{ display: 'flex', gap: '10px' }}>
                            <button
                                onClick={() => exportCollection(selectedCollection, 'json')}
                                style={{
                                    padding: '6px 12px',
                                    backgroundColor: '#10b981',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '4px',
                                    fontSize: '12px',
                                    cursor: 'pointer'
                                }}
                            >
                                Export JSON
                            </button>
                            <button
                                onClick={() => exportCollection(selectedCollection, 'csv')}
                                style={{
                                    padding: '6px 12px',
                                    backgroundColor: '#f59e0b',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '4px',
                                    fontSize: '12px',
                                    cursor: 'pointer'
                                }}
                            >
                                Export CSV
                            </button>
                        </div>
                    </div>

                    {/* Pagination */}
                    {collectionData.total_pages > 1 && (
                        <div style={{ marginBottom: '20px', display: 'flex', justifyContent: 'center', gap: '5px' }}>
                            <button
                                onClick={() => fetchCollectionData(selectedCollection, Math.max(1, currentPage - 1))}
                                disabled={currentPage <= 1}
                                style={{
                                    padding: '8px 12px',
                                    backgroundColor: currentPage <= 1 ? '#f3f4f6' : '#3b82f6',
                                    color: currentPage <= 1 ? '#9ca3af' : 'white',
                                    border: 'none',
                                    borderRadius: '4px',
                                    fontSize: '12px',
                                    cursor: currentPage <= 1 ? 'not-allowed' : 'pointer'
                                }}
                            >
                                Previous
                            </button>
                            <span style={{ 
                                padding: '8px 12px', 
                                color: '#374151', 
                                fontSize: '14px',
                                display: 'flex',
                                alignItems: 'center'
                            }}>
                                Page {currentPage} of {collectionData.total_pages}
                            </span>
                            <button
                                onClick={() => fetchCollectionData(selectedCollection, Math.min(collectionData.total_pages, currentPage + 1))}
                                disabled={currentPage >= collectionData.total_pages}
                                style={{
                                    padding: '8px 12px',
                                    backgroundColor: currentPage >= collectionData.total_pages ? '#f3f4f6' : '#3b82f6',
                                    color: currentPage >= collectionData.total_pages ? '#9ca3af' : 'white',
                                    border: 'none',
                                    borderRadius: '4px',
                                    fontSize: '12px',
                                    cursor: currentPage >= collectionData.total_pages ? 'not-allowed' : 'pointer'
                                }}
                            >
                                Next
                            </button>
                        </div>
                    )}

                    {/* Documents Display */}
                    <div style={{ backgroundColor: 'white', borderRadius: '8px', border: '1px solid #e5e7eb', padding: '20px' }}>
                        {collectionData.documents.length > 0 ? (
                            <div>
                                {collectionData.documents.map((doc, index) => (
                                    <div 
                                        key={index} 
                                        style={{ 
                                            marginBottom: '20px', 
                                            padding: '15px', 
                                            backgroundColor: '#f9fafb', 
                                            borderRadius: '6px',
                                            border: '1px solid #e5e7eb'
                                        }}
                                    >
                                        <div style={{ marginBottom: '10px', fontSize: '14px', fontWeight: '600', color: '#374151' }}>
                                            Document #{index + 1 + (currentPage - 1) * 20}
                                        </div>
                                        <pre style={{ 
                                            backgroundColor: 'white', 
                                            padding: '10px', 
                                            borderRadius: '4px', 
                                            fontSize: '12px', 
                                            overflow: 'auto',
                                            border: '1px solid #d1d5db',
                                            maxHeight: '300px'
                                        }}>
                                            {JSON.stringify(doc, null, 2)}
                                        </pre>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div style={{ textAlign: 'center', color: '#6b7280', fontSize: '16px', padding: '40px' }}>
                                No documents found
                                {searchTerm && ` matching "${searchTerm}"`}
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );

    const renderAnalytics = () => (
        <div style={{ padding: '20px' }}>
            <h2 style={{ color: '#333', fontSize: '24px', marginBottom: '20px' }}>Platform Analytics</h2>
            
            {/* Platform Health */}
            {platformHealth && (
                <div style={{ marginBottom: '30px' }}>
                    <h3 style={{ color: '#374151', fontSize: '18px', marginBottom: '15px' }}>Platform Health</h3>
                    <div style={{ 
                        backgroundColor: 'white', 
                        padding: '20px', 
                        borderRadius: '8px', 
                        border: '1px solid #e5e7eb',
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                        gap: '15px'
                    }}>
                        <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#10b981' }}>
                                {platformHealth.health_score}/100
                            </div>
                            <div style={{ fontSize: '14px', color: '#6b7280' }}>Health Score</div>
                            <div style={{ 
                                fontSize: '12px', 
                                fontWeight: '600',
                                color: platformHealth.overall_health === 'excellent' ? '#10b981' : 
                                      platformHealth.overall_health === 'good' ? '#f59e0b' : '#ef4444'
                            }}>
                                {platformHealth.overall_health.toUpperCase()}
                            </div>
                        </div>
                        
                        {Object.entries(platformHealth.components).map(([component, data]) => (
                            <div key={component} style={{ textAlign: 'center' }}>
                                <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#374151' }}>
                                    {data.score}/25
                                </div>
                                <div style={{ fontSize: '14px', color: '#6b7280' }}>
                                    {component.replace('_', ' ').toUpperCase()}
                                </div>
                                <div style={{ 
                                    fontSize: '12px', 
                                    fontWeight: '600',
                                    color: data.status === 'excellent' ? '#10b981' : 
                                          data.status === 'good' ? '#f59e0b' : '#ef4444'
                                }}>
                                    {data.status.toUpperCase()}
                                </div>
                            </div>
                        ))}
                    </div>
                    
                    {platformHealth.recommendations && platformHealth.recommendations.length > 0 && (
                        <div style={{ 
                            marginTop: '15px', 
                            backgroundColor: '#fef3c7', 
                            padding: '15px', 
                            borderRadius: '6px',
                            border: '1px solid #f59e0b'
                        }}>
                            <div style={{ fontSize: '14px', fontWeight: '600', color: '#92400e', marginBottom: '8px' }}>
                                Recommendations:
                            </div>
                            <ul style={{ margin: 0, color: '#92400e', fontSize: '14px' }}>
                                {platformHealth.recommendations.map((rec, index) => (
                                    <li key={index}>{rec}</li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            )}

            {/* User Analytics */}
            {userAnalytics && (
                <div style={{ marginBottom: '30px' }}>
                    <h3 style={{ color: '#374151', fontSize: '18px', marginBottom: '15px' }}>User Analytics</h3>
                    <div style={{ 
                        display: 'grid', 
                        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
                        gap: '20px' 
                    }}>
                        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
                            <h4 style={{ color: '#374151', fontSize: '16px', marginBottom: '15px' }}>User Metrics</h4>
                            <div style={{ fontSize: '14px', lineHeight: '1.6' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                    <span>Total Users:</span>
                                    <span style={{ fontWeight: '600' }}>{userAnalytics.user_metrics.total_users.toLocaleString()}</span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                    <span>Subscribed:</span>
                                    <span style={{ fontWeight: '600', color: '#10b981' }}>{userAnalytics.user_metrics.subscribed_users.toLocaleString()}</span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                    <span>Free Users:</span>
                                    <span style={{ fontWeight: '600' }}>{userAnalytics.user_metrics.free_users.toLocaleString()}</span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                    <span>Subscription Rate:</span>
                                    <span style={{ fontWeight: '600', color: '#3b82f6' }}>{userAnalytics.user_metrics.subscription_rate}%</span>
                                </div>
                            </div>
                        </div>

                        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
                            <h4 style={{ color: '#374151', fontSize: '16px', marginBottom: '15px' }}>Engagement Metrics</h4>
                            <div style={{ fontSize: '14px', lineHeight: '1.6' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                    <span>Total Questions:</span>
                                    <span style={{ fontWeight: '600' }}>{userAnalytics.engagement_metrics.total_questions.toLocaleString()}</span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                    <span>Engaged Users:</span>
                                    <span style={{ fontWeight: '600', color: '#10b981' }}>{userAnalytics.engagement_metrics.users_with_questions.toLocaleString()}</span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                    <span>Engagement Rate:</span>
                                    <span style={{ fontWeight: '600', color: '#3b82f6' }}>{userAnalytics.engagement_metrics.engagement_rate}%</span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                    <span>Avg Q/User:</span>
                                    <span style={{ fontWeight: '600' }}>{userAnalytics.engagement_metrics.avg_questions_per_user}</span>
                                </div>
                            </div>
                        </div>

                        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
                            <h4 style={{ color: '#374151', fontSize: '16px', marginBottom: '15px' }}>Growth Metrics</h4>
                            <div style={{ fontSize: '14px', lineHeight: '1.6' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                    <span>New Users (30d):</span>
                                    <span style={{ fontWeight: '600', color: '#10b981' }}>{userAnalytics.growth_metrics.new_users_30d.toLocaleString()}</span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                    <span>New Users (7d):</span>
                                    <span style={{ fontWeight: '600' }}>{userAnalytics.growth_metrics.new_users_7d.toLocaleString()}</span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                    <span>New Questions (30d):</span>
                                    <span style={{ fontWeight: '600', color: '#3b82f6' }}>{userAnalytics.growth_metrics.new_questions_30d.toLocaleString()}</span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                    <span>New Questions (7d):</span>
                                    <span style={{ fontWeight: '600' }}>{userAnalytics.growth_metrics.new_questions_7d.toLocaleString()}</span>
                                </div>
                            </div>
                        </div>

                        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
                            <h4 style={{ color: '#374151', fontSize: '16px', marginBottom: '15px' }}>Revenue Metrics</h4>
                            <div style={{ fontSize: '14px', lineHeight: '1.6' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                    <span>Total Revenue:</span>
                                    <span style={{ fontWeight: '600', color: '#10b981' }}>${userAnalytics.subscription_metrics.total_revenue.toLocaleString()}</span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                    <span>Monthly Est.:</span>
                                    <span style={{ fontWeight: '600' }}>${userAnalytics.subscription_metrics.monthly_revenue_estimate.toLocaleString()}</span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                    <span>ARPU:</span>
                                    <span style={{ fontWeight: '600', color: '#3b82f6' }}>${userAnalytics.subscription_metrics.average_revenue_per_user}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Mentor Analytics */}
            {mentorAnalytics && (
                <div style={{ marginBottom: '30px' }}>
                    <h3 style={{ color: '#374151', fontSize: '18px', marginBottom: '15px' }}>Mentor Analytics</h3>
                    <div style={{ 
                        display: 'grid', 
                        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
                        gap: '20px' 
                    }}>
                        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
                            <h4 style={{ color: '#374151', fontSize: '16px', marginBottom: '15px' }}>Mentor Metrics</h4>
                            <div style={{ fontSize: '14px', lineHeight: '1.6' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                    <span>Total Mentors:</span>
                                    <span style={{ fontWeight: '600' }}>{mentorAnalytics.mentor_metrics.total_mentors.toLocaleString()}</span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                    <span>Approved:</span>
                                    <span style={{ fontWeight: '600', color: '#10b981' }}>{mentorAnalytics.mentor_metrics.approved_mentors.toLocaleString()}</span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                    <span>Pending:</span>
                                    <span style={{ fontWeight: '600', color: '#f59e0b' }}>{mentorAnalytics.mentor_metrics.pending_mentors.toLocaleString()}</span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                    <span>Approval Rate:</span>
                                    <span style={{ fontWeight: '600', color: '#3b82f6' }}>{mentorAnalytics.mentor_metrics.approval_rate}%</span>
                                </div>
                            </div>
                        </div>

                        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
                            <h4 style={{ color: '#374151', fontSize: '16px', marginBottom: '15px' }}>Categories</h4>
                            <div style={{ fontSize: '14px', lineHeight: '1.6' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                    <span>Total Categories:</span>
                                    <span style={{ fontWeight: '600' }}>{mentorAnalytics.category_metrics.total_categories}</span>
                                </div>
                                {Object.entries(mentorAnalytics.category_metrics.category_distribution).map(([category, count]) => (
                                    <div key={category} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                                        <span style={{ textTransform: 'capitalize' }}>{category}:</span>
                                        <span style={{ fontWeight: '600' }}>{count}</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
                            <h4 style={{ color: '#374151', fontSize: '16px', marginBottom: '15px' }}>Earnings</h4>
                            <div style={{ fontSize: '14px', lineHeight: '1.6' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                    <span>Total Earnings:</span>
                                    <span style={{ fontWeight: '600', color: '#10b981' }}>${mentorAnalytics.performance_metrics.total_platform_earnings.toLocaleString()}</span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                    <span>Avg per Mentor:</span>
                                    <span style={{ fontWeight: '600' }}>${mentorAnalytics.performance_metrics.average_earnings_per_mentor}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );

    return (
        <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb' }}>
            {/* Tab Navigation */}
            <div style={{ backgroundColor: 'white', borderBottom: '1px solid #e5e7eb' }}>
                <div style={{ padding: '0 20px' }}>
                    <div style={{ display: 'flex', gap: '30px' }}>
                        {[
                            { key: 'overview', label: 'Database Overview' },
                            { key: 'browse', label: 'Browse Collections' },
                            { key: 'analytics', label: 'Analytics & Health' }
                        ].map((tab) => (
                            <button
                                key={tab.key}
                                onClick={() => setActiveTab(tab.key)}
                                style={{
                                    padding: '15px 0',
                                    fontSize: '16px',
                                    fontWeight: '600',
                                    color: activeTab === tab.key ? '#3b82f6' : '#6b7280',
                                    backgroundColor: 'transparent',
                                    border: 'none',
                                    borderBottom: activeTab === tab.key ? '2px solid #3b82f6' : '2px solid transparent',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s'
                                }}
                            >
                                {tab.label}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Loading Indicator */}
            {loading && (
                <div style={{ 
                    position: 'fixed', 
                    top: 0, 
                    left: 0, 
                    right: 0, 
                    bottom: 0, 
                    backgroundColor: 'rgba(0,0,0,0.5)', 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center',
                    zIndex: 1000
                }}>
                    <div style={{ 
                        backgroundColor: 'white', 
                        padding: '20px', 
                        borderRadius: '8px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '15px'
                    }}>
                        <div style={{
                            width: '20px',
                            height: '20px',
                            border: '2px solid #f3f4f6',
                            borderTop: '2px solid #3b82f6',
                            borderRadius: '50%',
                            animation: 'spin 1s linear infinite'
                        }}></div>
                        <span>Loading...</span>
                    </div>
                </div>
            )}

            {/* Tab Content */}
            {activeTab === 'overview' && renderOverview()}
            {activeTab === 'browse' && renderBrowse()}
            {activeTab === 'analytics' && renderAnalytics()}

            <style>
                {`
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                `}
            </style>
        </div>
    );
};

export default DatabaseManagement;
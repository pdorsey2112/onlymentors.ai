import React, { useState, useEffect } from 'react';
import { getBackendURL } from '../config';

const PremiumContentManagement = ({ creator }) => {
    const [activeTab, setActiveTab] = useState('content');
    const [premiumContent, setPremiumContent] = useState([]);
    const [analytics, setAnalytics] = useState(null);
    const [loading, setLoading] = useState(false);
    const [showUploadModal, setShowUploadModal] = useState(false);
    const [uploadForm, setUploadForm] = useState({
        title: '',
        description: '',
        content_type: 'document',
        category: '',
        price: '',
        tags: [],
        preview_available: false
    });

    const getAuthHeaders = () => {
        const token = localStorage.getItem('creatorToken');
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        };
    };

    const fetchPremiumContent = async () => {
        try {
            setLoading(true);
            const backendURL = getBackendURL();
            const response = await fetch(`${backendURL}/api/creators/${creator.creator_id}/content`, {
                headers: getAuthHeaders()
            });

            if (response.ok) {
                const data = await response.json();
                setPremiumContent(data || []); // Direct array response from creator endpoint
            } else {
                console.error('Failed to fetch premium content');
            }
        } catch (error) {
            console.error('Error fetching premium content:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchAnalytics = async () => {
        try {
            setLoading(true);
            const backendURL = getBackendURL();
            const response = await fetch(`${backendURL}/api/creator/content/analytics`, {
                headers: getAuthHeaders()
            });

            if (response.ok) {
                const data = await response.json();
                setAnalytics(data);
            } else {
                console.error('Failed to fetch analytics');
            }
        } catch (error) {
            console.error('Error fetching analytics:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleUploadContent = async () => {
        try {
            setLoading(true);
            const backendURL = getBackendURL();
            
            // Validate required fields
            if (!uploadForm.title || !uploadForm.description || !uploadForm.category || !uploadForm.price) {
                alert('Please fill in all required fields');
                return;
            }

            const price = parseFloat(uploadForm.price);
            if (isNaN(price) || price < 0.01 || price > 50) {
                alert('Price must be between $0.01 and $50.00');
                return;
            }

            const response = await fetch(`${backendURL}/api/creator/content/upload`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify({
                    ...uploadForm,
                    price: price,
                    tags: uploadForm.tags.filter(tag => tag.trim() !== '')
                })
            });

            if (response.ok) {
                const data = await response.json();
                alert(`Content uploaded successfully! You'll earn $${data.pricing_breakdown.creator_earnings.toFixed(2)} per purchase.`);
                setShowUploadModal(false);
                setUploadForm({
                    title: '',
                    description: '',
                    content_type: 'document',
                    category: '',
                    price: '',
                    tags: [],
                    preview_available: false
                });
                fetchPremiumContent();
            } else {
                const errorData = await response.json();
                alert(`Failed to upload content: ${errorData.detail || 'Unknown error'}`);
            }
        } catch (error) {
            console.error('Error uploading content:', error);
            alert('Error uploading content');
        } finally {
            setLoading(false);
        }
    };

    const calculateEarnings = (price) => {
        const numPrice = parseFloat(price) || 0;
        const commission = numPrice * 0.20;
        const platformFee = Math.max(commission, 2.99);
        const creatorEarnings = numPrice - platformFee;
        
        return {
            price: numPrice,
            platformFee: platformFee,
            creatorEarnings: Math.max(0, creatorEarnings)
        };
    };

    const addTag = (tag) => {
        if (tag.trim() && !uploadForm.tags.includes(tag.trim())) {
            setUploadForm(prev => ({
                ...prev,
                tags: [...prev.tags, tag.trim()]
            }));
        }
    };

    const removeTag = (index) => {
        setUploadForm(prev => ({
            ...prev,
            tags: prev.tags.filter((_, i) => i !== index)
        }));
    };

    useEffect(() => {
        if (activeTab === 'content') {
            fetchPremiumContent();
        } else if (activeTab === 'analytics') {
            fetchAnalytics();
        }
    }, [activeTab]);

    const renderContentList = () => (
        <div style={{ padding: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h3 style={{ color: '#374151', fontSize: '20px', margin: 0 }}>My Premium Content ({premiumContent.length})</h3>
                <button
                    onClick={() => setShowUploadModal(true)}
                    style={{
                        padding: '10px 20px',
                        backgroundColor: '#3b82f6',
                        color: 'white',
                        border: 'none',
                        borderRadius: '6px',
                        fontSize: '14px',
                        fontWeight: '600',
                        cursor: 'pointer'
                    }}
                >
                    + Upload New Content
                </button>
            </div>

            {premiumContent.length === 0 ? (
                <div style={{ 
                    textAlign: 'center', 
                    padding: '60px 20px',
                    backgroundColor: 'white',
                    borderRadius: '8px',
                    border: '1px solid #e5e7eb'
                }}>
                    <div style={{ fontSize: '48px', marginBottom: '16px' }}>📄</div>
                    <h3 style={{ color: '#374151', fontSize: '18px', marginBottom: '8px' }}>No Premium Content Yet</h3>
                    <p style={{ color: '#6b7280', fontSize: '14px', marginBottom: '20px' }}>
                        Upload your first premium content to start earning from your expertise
                    </p>
                    <button
                        onClick={() => setShowUploadModal(true)}
                        style={{
                            padding: '12px 24px',
                            backgroundColor: '#3b82f6',
                            color: 'white',
                            border: 'none',
                            borderRadius: '6px',
                            fontSize: '16px',
                            fontWeight: '600',
                            cursor: 'pointer'
                        }}
                    >
                        Upload Your First Content
                    </button>
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
                    {premiumContent.map((content, index) => (
                        <div key={index} style={{
                            backgroundColor: 'white',
                            padding: '20px',
                            borderRadius: '8px',
                            border: '1px solid #e5e7eb',
                            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
                        }}>
                            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
                                <div style={{
                                    width: '40px',
                                    height: '40px',
                                    backgroundColor: content.content_type === 'video' ? '#ef4444' :
                                                   content.content_type === 'document' ? '#3b82f6' :
                                                   content.content_type === 'audio' ? '#10b981' : '#f59e0b',
                                    borderRadius: '8px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    color: 'white',
                                    fontSize: '18px',
                                    marginRight: '12px'
                                }}>
                                    {content.content_type === 'video' ? '🎥' :
                                     content.content_type === 'document' ? '📄' :
                                     content.content_type === 'audio' ? '🎵' : '📁'}
                                </div>
                                <div>
                                    <h4 style={{ color: '#374151', fontSize: '16px', margin: 0, fontWeight: '600' }}>
                                        {content.title}
                                    </h4>
                                    <p style={{ color: '#6b7280', fontSize: '12px', margin: '4px 0 0 0', textTransform: 'capitalize' }}>
                                        {content.content_type} • {content.category}
                                    </p>
                                </div>
                            </div>

                            <p style={{ color: '#6b7280', fontSize: '14px', marginBottom: '16px', lineHeight: '1.5' }}>
                                {content.description.length > 100 ? `${content.description.substring(0, 100)}...` : content.description}
                            </p>

                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#374151' }}>
                                    ${content.price.toFixed(2)}
                                </div>
                                <div style={{ textAlign: 'right' }}>
                                    <div style={{ fontSize: '12px', color: '#6b7280' }}>
                                        You earn: <span style={{ fontWeight: '600', color: '#10b981' }}>
                                            ${content.creator_earnings.toFixed(2)}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                                <div style={{ fontSize: '14px', color: '#6b7280' }}>
                                    <span style={{ fontWeight: '600' }}>{content.total_purchases || 0}</span> sales
                                </div>
                                <div style={{ fontSize: '14px', color: '#6b7280' }}>
                                    Revenue: <span style={{ fontWeight: '600', color: '#10b981' }}>
                                        ${(content.total_revenue || 0).toFixed(2)}
                                    </span>
                                </div>
                            </div>

                            {content.tags && content.tags.length > 0 && (
                                <div style={{ marginBottom: '16px' }}>
                                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                                        {content.tags.slice(0, 3).map((tag, tagIndex) => (
                                            <span key={tagIndex} style={{
                                                backgroundColor: '#f3f4f6',
                                                color: '#6b7280',
                                                fontSize: '12px',
                                                padding: '2px 8px',
                                                borderRadius: '12px'
                                            }}>
                                                {tag}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            <div style={{ display: 'flex', gap: '8px' }}>
                                <button style={{
                                    flex: 1,
                                    padding: '8px 12px',
                                    backgroundColor: '#f3f4f6',
                                    color: '#374151',
                                    border: 'none',
                                    borderRadius: '4px',
                                    fontSize: '14px',
                                    cursor: 'pointer'
                                }}>
                                    Edit
                                </button>
                                <button style={{
                                    flex: 1,
                                    padding: '8px 12px',
                                    backgroundColor: content.is_active ? '#f59e0b' : '#10b981',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '4px',
                                    fontSize: '14px',
                                    cursor: 'pointer'
                                }}>
                                    {content.is_active ? 'Deactivate' : 'Activate'}
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );

    const renderAnalytics = () => (
        <div style={{ padding: '20px' }}>
            <h3 style={{ color: '#374151', fontSize: '20px', marginBottom: '20px' }}>Premium Content Analytics</h3>
            
            {analytics ? (
                <div>
                    {/* Summary Cards */}
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '30px' }}>
                        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
                            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#374151' }}>
                                {analytics.summary.total_content}
                            </div>
                            <div style={{ fontSize: '14px', color: '#6b7280' }}>Total Content</div>
                        </div>
                        
                        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
                            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#10b981' }}>
                                ${analytics.summary.creator_earnings.toFixed(2)}
                            </div>
                            <div style={{ fontSize: '14px', color: '#6b7280' }}>Total Earnings</div>
                        </div>
                        
                        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
                            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#3b82f6' }}>
                                {analytics.summary.total_sales}
                            </div>
                            <div style={{ fontSize: '14px', color: '#6b7280' }}>Total Sales</div>
                        </div>
                        
                        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
                            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#374151' }}>
                                ${analytics.summary.total_revenue.toFixed(2)}
                            </div>
                            <div style={{ fontSize: '14px', color: '#6b7280' }}>Gross Revenue</div>
                        </div>
                    </div>

                    {/* Top Performing Content */}
                    <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', border: '1px solid #e5e7eb', marginBottom: '20px' }}>
                        <h4 style={{ color: '#374151', fontSize: '18px', marginBottom: '16px' }}>Top Performing Content</h4>
                        {analytics.top_performing_content.length > 0 ? (
                            <div style={{ fontSize: '14px' }}>
                                {analytics.top_performing_content.map((content, index) => (
                                    <div key={index} style={{
                                        display: 'flex',
                                        justifyContent: 'space-between',
                                        alignItems: 'center',
                                        padding: '12px 0',
                                        borderBottom: index < analytics.top_performing_content.length - 1 ? '1px solid #f3f4f6' : 'none'
                                    }}>
                                        <div>
                                            <div style={{ color: '#374151', fontWeight: '600' }}>{content.title}</div>
                                            <div style={{ color: '#6b7280', fontSize: '12px' }}>${content.price.toFixed(2)} each</div>
                                        </div>
                                        <div style={{ textAlign: 'right' }}>
                                            <div style={{ color: '#374151', fontWeight: '600' }}>{content.sales} sales</div>
                                            <div style={{ color: '#10b981', fontSize: '12px' }}>${content.revenue.toFixed(2)}</div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div style={{ textAlign: 'center', color: '#6b7280', padding: '20px' }}>
                                No sales data available yet
                            </div>
                        )}
                    </div>
                </div>
            ) : (
                <div style={{ textAlign: 'center', padding: '40px', color: '#6b7280' }}>
                    No analytics data available
                </div>
            )}
        </div>
    );

    const renderUploadModal = () => (
        <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
        }}>
            <div style={{
                backgroundColor: 'white',
                padding: '30px',
                borderRadius: '12px',
                boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
                width: '500px',
                maxWidth: '90vw',
                maxHeight: '90vh',
                overflow: 'auto'
            }}>
                <h3 style={{ color: '#374151', fontSize: '20px', marginBottom: '20px' }}>Upload Premium Content</h3>
                
                <div style={{ marginBottom: '20px' }}>
                    <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '6px' }}>
                        Title *
                    </label>
                    <input
                        type="text"
                        value={uploadForm.title}
                        onChange={(e) => setUploadForm(prev => ({ ...prev, title: e.target.value }))}
                        placeholder="Enter content title"
                        style={{
                            width: '100%',
                            padding: '10px',
                            border: '1px solid #d1d5db',
                            borderRadius: '6px',
                            fontSize: '14px'
                        }}
                    />
                </div>

                <div style={{ marginBottom: '20px' }}>
                    <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '6px' }}>
                        Description *
                    </label>
                    <textarea
                        value={uploadForm.description}
                        onChange={(e) => setUploadForm(prev => ({ ...prev, description: e.target.value }))}
                        placeholder="Describe your premium content"
                        rows="3"
                        style={{
                            width: '100%',
                            padding: '10px',
                            border: '1px solid #d1d5db',
                            borderRadius: '6px',
                            fontSize: '14px',
                            resize: 'vertical'
                        }}
                    />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginBottom: '20px' }}>
                    <div>
                        <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '6px' }}>
                            Content Type *
                        </label>
                        <select
                            value={uploadForm.content_type}
                            onChange={(e) => setUploadForm(prev => ({ ...prev, content_type: e.target.value }))}
                            style={{
                                width: '100%',
                                padding: '10px',
                                border: '1px solid #d1d5db',
                                borderRadius: '6px',
                                fontSize: '14px'
                            }}
                        >
                            <option value="document">Document</option>
                            <option value="video">Video</option>
                            <option value="audio">Audio</option>
                            <option value="image">Image</option>
                            <option value="interactive">Interactive</option>
                        </select>
                    </div>

                    <div>
                        <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '6px' }}>
                            Category *
                        </label>
                        <input
                            type="text"
                            value={uploadForm.category}
                            onChange={(e) => setUploadForm(prev => ({ ...prev, category: e.target.value }))}
                            placeholder="e.g., Business, Health"
                            style={{
                                width: '100%',
                                padding: '10px',
                                border: '1px solid #d1d5db',
                                borderRadius: '6px',
                                fontSize: '14px'
                            }}
                        />
                    </div>
                </div>

                <div style={{ marginBottom: '20px' }}>
                    <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '6px' }}>
                        Price (USD) * <span style={{ color: '#6b7280', fontWeight: 'normal' }}>(Min: $0.01, Max: $50.00)</span>
                    </label>
                    <input
                        type="number"
                        step="0.01"
                        min="0.01"
                        max="50.00"
                        value={uploadForm.price}
                        onChange={(e) => setUploadForm(prev => ({ ...prev, price: e.target.value }))}
                        placeholder="9.99"
                        style={{
                            width: '100%',
                            padding: '10px',
                            border: '1px solid #d1d5db',
                            borderRadius: '6px',
                            fontSize: '14px'
                        }}
                    />
                    {uploadForm.price && (
                        <div style={{ marginTop: '8px', fontSize: '12px', color: '#6b7280' }}>
                            <div>Platform fee: ${calculateEarnings(uploadForm.price).platformFee.toFixed(2)} (20% or min $2.99)</div>
                            <div style={{ color: '#10b981', fontWeight: '600' }}>
                                You earn: ${calculateEarnings(uploadForm.price).creatorEarnings.toFixed(2)} per sale
                            </div>
                        </div>
                    )}
                </div>

                <div style={{ display: 'flex', gap: '15px', marginTop: '30px' }}>
                    <button
                        onClick={() => setShowUploadModal(false)}
                        style={{
                            flex: 1,
                            padding: '12px',
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
                        onClick={handleUploadContent}
                        disabled={loading}
                        style={{
                            flex: 1,
                            padding: '12px',
                            backgroundColor: '#3b82f6',
                            color: 'white',
                            border: 'none',
                            borderRadius: '6px',
                            fontSize: '14px',
                            fontWeight: '600',
                            cursor: loading ? 'not-allowed' : 'pointer',
                            opacity: loading ? 0.6 : 1
                        }}
                    >
                        {loading ? 'Creating...' : 'Create Content'}
                    </button>
                </div>
            </div>
        </div>
    );

    return (
        <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb' }}>
            {/* Tab Navigation */}
            <div style={{ backgroundColor: 'white', borderBottom: '1px solid #e5e7eb' }}>
                <div style={{ padding: '0 20px' }}>
                    <div style={{ display: 'flex', gap: '30px' }}>
                        {[
                            { key: 'content', label: 'My Content' },
                            { key: 'analytics', label: 'Analytics' }
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
                    zIndex: 999
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
            {activeTab === 'content' && renderContentList()}
            {activeTab === 'analytics' && renderAnalytics()}

            {/* Upload Modal */}
            {showUploadModal && renderUploadModal()}

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

export default PremiumContentManagement;
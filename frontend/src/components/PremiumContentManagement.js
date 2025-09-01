import React, { useState, useEffect } from 'react';
import { getBackendURL } from '../config';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { Trash2, Edit, Copy, Eye, DollarSign, Calendar, FileText } from 'lucide-react';

const PremiumContentManagement = ({ creatorId, onClose, onContentUpdate }) => {
  const [content, setContent] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [editingContent, setEditingContent] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  // Edit form state
  const [editForm, setEditForm] = useState({
    title: '',
    description: '',
    category: '',
    price: '',
    tags: '',
    preview_available: false
  });

  useEffect(() => {
    if (creatorId) {
      loadPremiumContent();
    }
  }, [creatorId]);

  const loadPremiumContent = async () => {
    try {
      setLoading(true);
      setError('');
      const token = localStorage.getItem('creatorToken');
      
      if (!token) {
        setError('No authentication token found');
        return;
      }

      const backendURL = getBackendURL();
      const response = await fetch(`${backendURL}/api/creators/${creatorId}/premium-content`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setContent(data.content || []);
        console.log('Premium content loaded:', data.content);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to load premium content');
      }
    } catch (err) {
      console.error('Error loading premium content:', err);
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleEditContent = (contentItem) => {
    setEditingContent(contentItem);
    setEditForm({
      title: contentItem.title,
      description: contentItem.description,
      category: contentItem.category || '',
      price: contentItem.price.toString(),
      tags: (contentItem.tags || []).join(', '),
      preview_available: contentItem.preview_available || false
    });
    setShowEditModal(true);
  };

  const handleUpdateContent = async () => {
    if (!editingContent) return;

    try {
      setLoading(true);
      setError('');

      const token = localStorage.getItem('creatorToken');
      
      const formData = new FormData();
      formData.append('title', editForm.title.trim());
      formData.append('description', editForm.description.trim());
      formData.append('category', editForm.category.trim());
      formData.append('price', parseFloat(editForm.price));
      formData.append('tags', JSON.stringify(editForm.tags.split(',').map(tag => tag.trim()).filter(Boolean)));
      formData.append('preview_available', editForm.preview_available);

      const backendURL = getBackendURL();
      const response = await fetch(
        `${backendURL}/api/creators/${creatorId}/premium-content/${editingContent.content_id}`,
        {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: formData
        }
      );

      if (response.ok) {
        const result = await response.json();
        setSuccess('Premium content updated successfully!');
        setShowEditModal(false);
        setEditingContent(null);
        
        // Update content in local state
        setContent(prev => prev.map(item => 
          item.content_id === editingContent.content_id ? result.content : item
        ));
        
        // Refresh dashboard stats
        if (onContentUpdate) {
          onContentUpdate();
        }
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to update premium content');
      }
    } catch (err) {
      setError('Network error while updating content');
      console.error('Update content error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteContent = async (contentId) => {
    try {
      setLoading(true);
      setError('');

      const token = localStorage.getItem('creatorToken');
      
      const backendURL = getBackendURL();
      const response = await fetch(
        `${backendURL}/api/creators/${creatorId}/premium-content/${contentId}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.ok) {
        setSuccess('Premium content deleted successfully!');
        setDeleteConfirm(null);
        
        // Remove content from local state
        setContent(prev => prev.filter(item => item.content_id !== contentId));
        
        // Refresh dashboard stats
        if (onContentUpdate) {
          onContentUpdate();
        }
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to delete premium content');
      }
    } catch (err) {
      setError('Network error while deleting content');
      console.error('Delete content error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDuplicateContent = async (contentId) => {
    try {
      setLoading(true);
      setError('');

      const token = localStorage.getItem('creatorToken');
      
      const backendURL = getBackendURL();
      const response = await fetch(
        `${backendURL}/api/creators/${creatorId}/premium-content/${contentId}/duplicate`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.ok) {
        const result = await response.json();
        setSuccess('Premium content duplicated successfully!');
        
        // Add duplicated content to local state
        setContent(prev => [result.content, ...prev]);
        
        // Refresh dashboard stats
        if (onContentUpdate) {
          onContentUpdate();
        }
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to duplicate premium content');
      }
    } catch (err) {
      setError('Network error while duplicating content');
      console.error('Duplicate content error:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getContentIcon = (contentType) => {
    switch (contentType) {
      case 'document':
        return <FileText className="h-4 w-4" />;
      case 'video':
        return <FileText className="h-4 w-4" />;
      case 'image':
        return <FileText className="h-4 w-4" />;
      default:
        return <FileText className="h-4 w-4" />;
    }
  };

  if (loading) {
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
              <h2 className="text-2xl font-bold">Manage Premium Content</h2>
              <p className="text-purple-100 mt-1">
                {content.length} premium {content.length === 1 ? 'item' : 'items'} total
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

        {/* Content Area */}
        <div className="p-6 max-h-96 overflow-y-auto">
          {error && (
            <Alert className="mb-6 border-red-200 bg-red-50">
              <AlertDescription className="text-red-700">
                {error}
              </AlertDescription>
            </Alert>
          )}

          {success && (
            <Alert className="mb-6 border-green-200 bg-green-50">
              <AlertDescription className="text-green-700">
                {success}
              </AlertDescription>
            </Alert>
          )}

          {content.length === 0 && !error ? (
            <div className="text-center py-12">
              <div className="text-gray-400 text-6xl mb-4">📦</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No Premium Content Yet</h3>
              <p className="text-gray-600 mb-4">Start creating premium content to earn from your expertise</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {content.map((item) => (
                <Card key={item.content_id} className="hover:shadow-md transition-shadow">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center space-x-2">
                        {getContentIcon(item.content_type)}
                        <CardTitle className="text-lg leading-tight">{item.title}</CardTitle>
                      </div>
                      <div className="text-right">
                        <div className="text-xl font-bold text-purple-600">
                          {formatPrice(item.price)}
                        </div>
                      </div>
                    </div>
                    <CardDescription className="text-sm line-clamp-2">
                      {item.description}
                    </CardDescription>
                  </CardHeader>
                  
                  <CardContent>
                    <div className="space-y-3">
                      {/* Content Type and Category */}
                      <div className="flex flex-wrap gap-2">
                        <Badge variant="secondary" className="text-xs">
                          {item.content_type}
                        </Badge>
                        {item.category && (
                          <Badge variant="outline" className="text-xs">
                            {item.category}
                          </Badge>
                        )}
                        {item.preview_available && (
                          <Badge variant="default" className="text-xs bg-green-100 text-green-700">
                            Preview Available
                          </Badge>
                        )}
                      </div>

                      {/* Stats */}
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <div className="text-gray-500">Sales</div>
                          <div className="font-semibold">{item.total_purchases || 0}</div>
                        </div>
                        <div>
                          <div className="text-gray-500">Revenue</div>
                          <div className="font-semibold text-green-600">
                            {formatPrice(item.total_revenue || 0)}
                          </div>
                        </div>
                      </div>

                      {/* Tags */}
                      {item.tags && item.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {item.tags.slice(0, 3).map((tag, index) => (
                            <span key={index} className="bg-gray-100 text-gray-600 px-2 py-1 rounded text-xs">
                              #{tag}
                            </span>
                          ))}
                          {item.tags.length > 3 && (
                            <span className="text-gray-400 text-xs">+{item.tags.length - 3} more</span>
                          )}
                        </div>
                      )}

                      {/* Creation Date */}
                      <div className="flex items-center text-xs text-gray-500">
                        <Calendar className="h-3 w-3 mr-1" />
                        Created {formatDate(item.created_at)}
                      </div>

                      {/* Action Buttons */}
                      <div className="flex justify-between items-center pt-2 border-t border-gray-100">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleEditContent(item)}
                            className="flex items-center space-x-1 text-blue-600 hover:text-blue-800 text-sm"
                            title="Edit Content"
                          >
                            <Edit className="h-4 w-4" />
                            <span>Edit</span>
                          </button>
                          <button
                            onClick={() => handleDuplicateContent(item.content_id)}
                            disabled={loading}
                            className="flex items-center space-x-1 text-green-600 hover:text-green-800 text-sm disabled:opacity-50"
                            title="Duplicate Content"
                          >
                            <Copy className="h-4 w-4" />
                            <span>Copy</span>
                          </button>
                        </div>
                        <button
                          onClick={() => setDeleteConfirm(item.content_id)}
                          className="flex items-center space-x-1 text-red-600 hover:text-red-800 text-sm"
                          title="Delete Content"
                        >
                          <Trash2 className="h-4 w-4" />
                          <span>Delete</span>
                        </button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 p-4 bg-gray-50 flex justify-between items-center">
          <div className="text-sm text-gray-600">
            Total: {content.length} premium content items
          </div>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            Close
          </button>
        </div>
      </div>

      {/* Edit Modal */}
      {showEditModal && editingContent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-60">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
            <div className="bg-blue-600 text-white p-6">
              <h3 className="text-xl font-bold">Edit Premium Content</h3>
            </div>
            
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
                <Input
                  value={editForm.title}
                  onChange={(e) => setEditForm(prev => ({ ...prev, title: e.target.value }))}
                  placeholder="Content title"
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description *</label>
                <Textarea
                  value={editForm.description}
                  onChange={(e) => setEditForm(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Describe your premium content..."
                  rows={4}
                  className="w-full"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Price * ($0.01 - $50.00)</label>
                  <div className="relative">
                    <span className="absolute left-3 top-3 text-gray-500">$</span>
                    <Input
                      type="number"
                      value={editForm.price}
                      onChange={(e) => setEditForm(prev => ({ ...prev, price: e.target.value }))}
                      placeholder="0.00"
                      step="0.01"
                      min="0.01"
                      max="50.00"
                      className="pl-8"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                  <select
                    value={editForm.category}
                    onChange={(e) => setEditForm(prev => ({ ...prev, category: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select category</option>
                    <option value="business">Business</option>
                    <option value="sports">Sports</option>
                    <option value="health">Health</option>
                    <option value="science">Science</option>
                    <option value="relationships">Relationships</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tags (comma-separated)</label>
                <Input
                  value={editForm.tags}
                  onChange={(e) => setEditForm(prev => ({ ...prev, tags: e.target.value }))}
                  placeholder="tutorial, beginner, advanced, tips"
                  className="w-full"
                />
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="edit_preview_available"
                  checked={editForm.preview_available}
                  onChange={(e) => setEditForm(prev => ({ ...prev, preview_available: e.target.checked }))}
                  className="rounded text-blue-600 focus:ring-blue-500"
                />
                <label htmlFor="edit_preview_available" className="ml-2 text-sm text-gray-700">
                  Offer free preview (recommended to increase sales)
                </label>
              </div>
            </div>

            <div className="border-t border-gray-200 p-6 flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowEditModal(false);
                  setEditingContent(null);
                }}
                disabled={loading}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleUpdateContent}
                disabled={loading || !editForm.title.trim() || !editForm.description.trim() || !editForm.price}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Updating...' : 'Update Content'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-60">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4">
            <div className="bg-red-600 text-white p-6">
              <h3 className="text-xl font-bold">Delete Premium Content</h3>
            </div>
            
            <div className="p-6">
              <p className="text-gray-700 mb-4">
                Are you sure you want to delete this premium content? This action cannot be undone.
              </p>
              <p className="text-sm text-gray-500">
                <strong>Note:</strong> Any users who have purchased this content will lose access.
              </p>
            </div>

            <div className="border-t border-gray-200 p-6 flex justify-end space-x-3">
              <button
                onClick={() => setDeleteConfirm(null)}
                disabled={loading}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDeleteContent(deleteConfirm)}
                disabled={loading}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
              >
                {loading ? 'Deleting...' : 'Delete Content'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PremiumContentManagement;
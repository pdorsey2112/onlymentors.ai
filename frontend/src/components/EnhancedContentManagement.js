import React, { useState, useEffect } from 'react';
import { getBackendURL } from '../config';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { Trash2, Edit, Copy, Eye, EyeOff, Star, Calendar, FileText, Film, Link2 } from 'lucide-react';

const EnhancedContentManagement = ({ creatorId, onClose, onUploadSuccess }) => {
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
    tags: '',
    is_public: true,
    is_featured: false
  });

  useEffect(() => {
    if (creatorId) {
      loadContent();
    }
  }, [creatorId]);

  const loadContent = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('creator_token') || localStorage.getItem('auth_token');
      
      if (!token) {
        setError('No authentication token found');
        return;
      }

      const backendURL = getBackendURL();
      const response = await fetch(`${backendURL}/api/creators/${creatorId}/content?limit=50`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setContent(data.content || []);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to load content');
      }
    } catch (err) {
      setError('Network error while loading content');
      console.error('Load content error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleEditContent = (contentItem) => {
    setEditingContent(contentItem);
    setEditForm({
      title: contentItem.title || '',
      description: contentItem.description || '',
      category: contentItem.category || '',
      tags: Array.isArray(contentItem.tags) ? contentItem.tags.join(', ') : '',
      is_public: contentItem.is_public !== false,
      is_featured: contentItem.is_featured === true
    });
    setShowEditModal(true);
  };

  const handleUpdateContent = async (e) => {
    e.preventDefault();
    if (!editingContent) return;

    try {
      setLoading(true);
      setError('');

      const token = localStorage.getItem('creator_token') || localStorage.getItem('auth_token');
      
      const updateData = {
        title: editForm.title.trim(),
        description: editForm.description.trim(),
        category: editForm.category.trim(),
        tags: editForm.tags.split(',').map(tag => tag.trim()).filter(Boolean),
        is_public: editForm.is_public,
        is_featured: editForm.is_featured
      };

      const backendURL = getBackendURL();
      const response = await fetch(
        `${backendURL}/api/creators/${creatorId}/content/${editingContent.content_id}`,
        {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(updateData)
        }
      );

      if (response.ok) {
        const result = await response.json();
        setSuccess('Content updated successfully!');
        setShowEditModal(false);
        setEditingContent(null);
        
        // Update content in local state
        setContent(prev => prev.map(item => 
          item.content_id === editingContent.content_id 
            ? result.content 
            : item
        ));
        
        if (onUploadSuccess) {
          onUploadSuccess(result);
        }
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to update content');
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

      const token = localStorage.getItem('creator_token') || localStorage.getItem('auth_token');
      
      const backendURL = getBackendURL();
      const response = await fetch(
        `${backendURL}/api/creators/${creatorId}/content/${contentId}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.ok) {
        setSuccess('Content deleted successfully!');
        setDeleteConfirm(null);
        
        // Remove content from local state
        setContent(prev => prev.filter(item => item.content_id !== contentId));
        
        if (onUploadSuccess) {
          onUploadSuccess({ deleted: contentId });
        }
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to delete content');
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

      const token = localStorage.getItem('creator_token') || localStorage.getItem('auth_token');
      
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/creators/${creatorId}/content/${contentId}/duplicate`,
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
        setSuccess('Content duplicated successfully!');
        
        // Add duplicated content to local state
        setContent(prev => [result.content, ...prev]);
        
        if (onUploadSuccess) {
          onUploadSuccess(result);
        }
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to duplicate content');
      }
    } catch (err) {
      setError('Network error while duplicating content');
      console.error('Duplicate content error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getContentIcon = (contentType) => {
    switch (contentType) {
      case 'video': return <Film className="w-5 h-5" />;
      case 'document': return <FileText className="w-5 h-5" />;
      case 'link': return <Link2 className="w-5 h-5" />;
      default: return <FileText className="w-5 h-5" />;
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return 'Unknown size';
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-hidden">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-2xl font-bold text-gray-900">Content Management</h2>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
            aria-label="Close"
          >
            ×
          </button>
        </div>

        <div className="p-6 overflow-y-auto max-h-[calc(90vh-80px)]">
          {error && (
            <Alert className="mb-4 border-red-200 bg-red-50">
              <AlertDescription className="text-red-800">{error}</AlertDescription>
            </Alert>
          )}

          {success && (
            <Alert className="mb-4 border-green-200 bg-green-50">
              <AlertDescription className="text-green-800">{success}</AlertDescription>
            </Alert>
          )}

          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
              <span className="ml-3 text-gray-600">Loading content...</span>
            </div>
          ) : content.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No content yet</h3>
              <p className="text-gray-600 mb-4">Upload your first piece of content to get started</p>
              <Button 
                onClick={onClose}
                className="bg-purple-600 hover:bg-purple-700"
              >
                Upload Content
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {content.map((item) => (
                <Card key={item.content_id} className="relative group hover:shadow-lg transition-shadow">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        {getContentIcon(item.content_type)}
                        <Badge variant="secondary" className="text-xs">
                          {item.content_type}
                        </Badge>
                      </div>
                      <div className="flex items-center space-x-1">
                        {item.is_featured && (
                          <Star className="w-4 h-4 text-yellow-500 fill-current" />
                        )}
                        {item.is_public ? (
                          <Eye className="w-4 h-4 text-green-500" />
                        ) : (
                          <EyeOff className="w-4 h-4 text-gray-400" />
                        )}
                      </div>
                    </div>
                    <CardTitle className="text-lg line-clamp-2">{item.title}</CardTitle>
                    <CardDescription className="line-clamp-2">
                      {item.description || 'No description provided'}
                    </CardDescription>
                  </CardHeader>
                  
                  <CardContent>
                    <div className="space-y-2 mb-4">
                      <div className="flex items-center text-sm text-gray-600">
                        <Calendar className="w-4 h-4 mr-1" />
                        {formatDate(item.created_at)}
                      </div>
                      {item.file_size && (
                        <div className="text-sm text-gray-600">
                          Size: {formatFileSize(item.file_size)}
                        </div>
                      )}
                      <div className="text-sm text-gray-600">
                        Views: {item.view_count || 0} | Likes: {item.like_count || 0}
                      </div>
                      {item.tags && item.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {item.tags.slice(0, 3).map((tag, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                          {item.tags.length > 3 && (
                            <Badge variant="outline" className="text-xs">
                              +{item.tags.length - 3}
                            </Badge>
                          )}
                        </div>
                      )}
                    </div>

                    <div className="flex justify-between items-center">
                      <div className="flex space-x-1">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleEditContent(item)}
                          className="h-8 w-8 p-0"
                          title="Edit content"
                        >
                          <Edit className="w-3 h-3" />
                        </Button>
                        
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDuplicateContent(item.content_id)}
                          className="h-8 w-8 p-0"
                          title="Duplicate content"
                        >
                          <Copy className="w-3 h-3" />
                        </Button>
                        
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setDeleteConfirm(item.content_id)}
                          className="h-8 w-8 p-0 text-red-600 hover:bg-red-50"
                          title="Delete content"
                        >
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                      
                      <div className="text-xs text-gray-500">
                        {item.category}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Edit Modal */}
        {showEditModal && editingContent && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-60 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full">
              <div className="flex items-center justify-between p-6 border-b">
                <h3 className="text-xl font-semibold">Edit Content</h3>
                <button 
                  onClick={() => setShowEditModal(false)}
                  className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
                >
                  ×
                </button>
              </div>
              
              <form onSubmit={handleUpdateContent} className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Title *
                  </label>
                  <Input
                    value={editForm.title}
                    onChange={(e) => setEditForm(prev => ({...prev, title: e.target.value}))}
                    placeholder="Enter content title"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <Textarea
                    value={editForm.description}
                    onChange={(e) => setEditForm(prev => ({...prev, description: e.target.value}))}
                    placeholder="Enter content description"
                    rows={3}
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Category
                    </label>
                    <Input
                      value={editForm.category}
                      onChange={(e) => setEditForm(prev => ({...prev, category: e.target.value}))}
                      placeholder="e.g., Business, Education"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Tags (comma separated)
                    </label>
                    <Input
                      value={editForm.tags}
                      onChange={(e) => setEditForm(prev => ({...prev, tags: e.target.value}))}
                      placeholder="e.g., tutorial, beginner, tips"
                    />
                  </div>
                </div>

                <div className="flex items-center space-x-6">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={editForm.is_public}
                      onChange={(e) => setEditForm(prev => ({...prev, is_public: e.target.checked}))}
                      className="rounded border-gray-300 mr-2"
                    />
                    <span className="text-sm text-gray-700">Make public</span>
                  </label>

                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={editForm.is_featured}
                      onChange={(e) => setEditForm(prev => ({...prev, is_featured: e.target.checked}))}
                      className="rounded border-gray-300 mr-2"
                    />
                    <span className="text-sm text-gray-700">Featured content</span>
                  </label>
                </div>

                <div className="flex justify-end space-x-3 pt-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setShowEditModal(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    className="bg-purple-600 hover:bg-purple-700"
                    disabled={loading}
                  >
                    {loading ? 'Updating...' : 'Update Content'}
                  </Button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Delete Confirmation Modal */}
        {deleteConfirm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-60 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
              <div className="p-6">
                <h3 className="text-lg font-semibold mb-4">Delete Content</h3>
                <p className="text-gray-600 mb-6">
                  Are you sure you want to delete this content? This action cannot be undone.
                </p>
                <div className="flex justify-end space-x-3">
                  <Button
                    variant="outline"
                    onClick={() => setDeleteConfirm(null)}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={() => handleDeleteContent(deleteConfirm)}
                    className="bg-red-600 hover:bg-red-700"
                    disabled={loading}
                  >
                    {loading ? 'Deleting...' : 'Delete'}
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EnhancedContentManagement;
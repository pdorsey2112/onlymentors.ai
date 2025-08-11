import React, { useState } from 'react';

const ContentUpload = ({ creatorId, onClose, onUploadSuccess }) => {
  const [uploadData, setUploadData] = useState({
    title: '',
    description: '',
    content_type: 'video',
    category: '',
    tags: []
  });
  
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [errors, setErrors] = useState({});

  const contentTypes = [
    { id: 'video', name: 'Video', maxSize: '200MB', accept: '.mp4,.avi,.mov,.wmv,.flv,.webm,.mkv' },
    { id: 'document', name: 'Document', maxSize: '50MB', accept: '.pdf,.doc,.docx,.txt' },
    { id: 'article_link', name: 'Article Link', maxSize: 'N/A', accept: '' }
  ];

  const categories = [
    { id: 'business', name: 'Business' },
    { id: 'sports', name: 'Sports' },
    { id: 'health', name: 'Health' },
    { id: 'science', name: 'Science' },
    { id: 'relationships', name: 'Relationships & Dating' }
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setUploadData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleTagsChange = (e) => {
    const tags = e.target.value.split(',').map(tag => tag.trim()).filter(tag => tag);
    setUploadData(prev => ({ ...prev, tags }));
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const contentType = contentTypes.find(type => type.id === uploadData.content_type);
    
    // Validate file type
    if (uploadData.content_type === 'video') {
      const validVideoTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/wmv', 'video/flv', 'video/webm', 'video/x-msvideo'];
      if (!validVideoTypes.includes(file.type)) {
        setErrors({ file: 'Please upload a valid video file (MP4, AVI, MOV, WMV, FLV, WEBM)' });
        return;
      }
      // Check video file size (200MB max)
      if (file.size > 200 * 1024 * 1024) {
        setErrors({ file: 'Video file size must be less than 200MB' });
        return;
      }
    } else if (uploadData.content_type === 'document') {
      const validDocTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
      if (!validDocTypes.includes(file.type)) {
        setErrors({ file: 'Please upload a valid document (PDF, DOC, DOCX, TXT)' });
        return;
      }
      // Check document file size (50MB max)
      if (file.size > 50 * 1024 * 1024) {
        setErrors({ file: 'Document file size must be less than 50MB' });
        return;
      }
    }

    setSelectedFile(file);
    setErrors({ file: '' });
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!uploadData.title) newErrors.title = 'Title is required';
    if (!uploadData.description) newErrors.description = 'Description is required';
    if (uploadData.content_type !== 'article_link' && !selectedFile) {
      newErrors.file = 'Please select a file to upload';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setIsUploading(true);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      
      // Add form data
      formData.append('title', uploadData.title);
      formData.append('description', uploadData.description);
      formData.append('content_type', uploadData.content_type);
      formData.append('category', uploadData.category);
      formData.append('tags', JSON.stringify(uploadData.tags));
      
      // Add file if not article link
      if (uploadData.content_type !== 'article_link' && selectedFile) {
        formData.append('content_file', selectedFile);
      }

      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/creators/${creatorId}/content`, {
        method: 'POST',
        body: formData,
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      if (response.ok) {
        const result = await response.json();
        onUploadSuccess && onUploadSuccess(result);
        onClose && onClose();
      } else {
        const errorData = await response.json();
        setErrors({ submit: errorData.detail || 'Upload failed' });
      }
    } catch (error) {
      setErrors({ submit: 'Network error. Please try again.' });
    }
    
    setIsUploading(false);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Upload New Content</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Content Type Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Content Type
            </label>
            <select
              name="content_type"
              value={uploadData.content_type}
              onChange={handleInputChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              {contentTypes.map(type => (
                <option key={type.id} value={type.id}>
                  {type.name} {type.maxSize !== 'N/A' && `(Max: ${type.maxSize})`}
                </option>
              ))}
            </select>
          </div>

          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Title
            </label>
            <input
              type="text"
              name="title"
              value={uploadData.title}
              onChange={handleInputChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="Enter content title"
            />
            {errors.title && <p className="text-red-500 text-sm mt-1">{errors.title}</p>}
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              name="description"
              value={uploadData.description}
              onChange={handleInputChange}
              rows={4}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              placeholder="Describe your content..."
            />
            {errors.description && <p className="text-red-500 text-sm mt-1">{errors.description}</p>}
          </div>

          {/* File Upload (for video and document) */}
          {uploadData.content_type !== 'article_link' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Upload File
              </label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <div className="mb-4">
                  <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </div>
                
                <div className="mb-4">
                  <label htmlFor="content-upload" className="cursor-pointer">
                    <span className="text-purple-600 font-medium hover:text-purple-500">
                      Click to upload {uploadData.content_type}
                    </span>
                    <input
                      id="content-upload"
                      type="file"
                      className="hidden"
                      onChange={handleFileChange}
                      accept={contentTypes.find(type => type.id === uploadData.content_type)?.accept}
                    />
                  </label>
                  <p className="text-gray-500 text-sm mt-2">
                    {uploadData.content_type === 'video' && 'MP4, AVI, MOV, WMV, FLV, WEBM up to 200MB'}
                    {uploadData.content_type === 'document' && 'PDF, DOC, DOCX, TXT up to 50MB'}
                  </p>
                </div>

                {selectedFile && (
                  <div className="mt-4 p-3 bg-green-50 rounded-lg">
                    <p className="text-green-700 font-medium">✓ {selectedFile.name}</p>
                    <p className="text-green-600 text-sm">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                  </div>
                )}
              </div>
              {errors.file && <p className="text-red-500 text-sm mt-1">{errors.file}</p>}
            </div>
          )}

          {/* Category */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Category (Optional)
            </label>
            <select
              name="category"
              value={uploadData.category}
              onChange={handleInputChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="">Select a category</option>
              {categories.map(cat => (
                <option key={cat.id} value={cat.id}>{cat.name}</option>
              ))}
            </select>
          </div>

          {/* Tags */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tags (comma-separated)
            </label>
            <input
              type="text"
              name="tags"
              value={uploadData.tags.join(', ')}
              onChange={handleTagsChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="tutorial, beginner, tips"
            />
          </div>

          {/* Upload Progress */}
          {isUploading && (
            <div className="mb-4">
              <div className="flex justify-between text-sm text-gray-600 mb-1">
                <span>Uploading...</span>
                <span>{uploadProgress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
            </div>
          )}

          {/* Error Messages */}
          {errors.submit && (
            <div className="text-red-600 text-sm bg-red-50 border border-red-200 rounded-lg p-3">
              {errors.submit}
            </div>
          )}

          {/* Submit Buttons */}
          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={onClose}
              disabled={isUploading}
              className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isUploading}
              className="px-6 py-3 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 disabled:opacity-50"
            >
              {isUploading ? 'Uploading...' : 'Upload Content'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ContentUpload;
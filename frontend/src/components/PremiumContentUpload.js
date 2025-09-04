import React, { useState } from 'react';
import { getBackendURL } from '../config';

const PremiumContentUpload = ({ creatorId, onClose, onUploadSuccess }) => {
  const [uploadData, setUploadData] = useState({
    title: '',
    description: '',
    content_type: 'document',
    category: '',
    price: '',
    tags: [],
    preview_available: false
  });
  
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [errors, setErrors] = useState({});
  const [pricingBreakdown, setPricingBreakdown] = useState(null);

  const contentTypes = [
    { id: 'document', name: 'Document', maxSize: '50MB', accept: 'application/pdf,.pdf,.doc,.docx,.txt' },
    { id: 'video', name: 'Video', maxSize: '200MB', accept: 'video/*,.mp4,.avi,.mov,.wmv,.flv,.webm,.mkv' },
    { id: 'podcast', name: 'Podcast/Audio', maxSize: '500MB', accept: 'audio/*,.mp3,.aac,.m4a,.wav' },
    { id: 'image', name: 'Image', maxSize: '25MB', accept: 'image/*,.jpg,.jpeg,.png,.gif,.bmp' },
    { id: 'interactive', name: 'Interactive Content', maxSize: '100MB', accept: '.html,.zip' }
  ];

  const categories = [
    { id: 'business', name: 'Business' },
    { id: 'sports', name: 'Sports' },
    { id: 'health', name: 'Health' },
    { id: 'science', name: 'Science' },
    { id: 'relationships', name: 'Relationships & Dating' }
  ];

  // Calculate pricing breakdown when price changes
  const calculatePricing = (price) => {
    const numPrice = parseFloat(price);
    if (!numPrice || numPrice < 0.01 || numPrice > 50) return null;
    
    const platformCommission = Math.max(numPrice * 0.2, 2.99);
    const creatorEarnings = numPrice - platformCommission;
    
    return {
      contentPrice: numPrice,
      platformFee: platformCommission,
      creatorEarnings: creatorEarnings,
      commissionRate: 20
    };
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    const newValue = type === 'checkbox' ? checked : value;
    
    setUploadData(prev => ({ ...prev, [name]: newValue }));
    
    // Calculate pricing breakdown when price changes
    if (name === 'price') {
      const breakdown = calculatePricing(value);
      setPricingBreakdown(breakdown);
    }
    
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
    const fileExt = '.' + file.name.split('.').pop().toLowerCase();
    const acceptedExts = contentType.accept.split(',');
    
    if (!acceptedExts.includes(fileExt)) {
      setErrors({ file: `Invalid file type. Accepted: ${contentType.accept}` });
      return;
    }
    
    // Check file size based on content type
    let maxSize;
    switch (uploadData.content_type) {
      case 'video':
        maxSize = 200 * 1024 * 1024; // 200MB
        break;
      case 'audio':
        maxSize = 100 * 1024 * 1024; // 100MB
        break;
      case 'document':
        maxSize = 50 * 1024 * 1024; // 50MB
        break;
      case 'image':
        maxSize = 25 * 1024 * 1024; // 25MB
        break;
      case 'interactive':
        maxSize = 100 * 1024 * 1024; // 100MB
        break;
      default:
        maxSize = 50 * 1024 * 1024;
    }
    
    if (file.size > maxSize) {
      setErrors({ file: `File size must be less than ${contentType.maxSize}` });
      return;
    }

    setSelectedFile(file);
    setErrors({ file: '' });
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!uploadData.title) newErrors.title = 'Title is required';
    if (!uploadData.description) newErrors.description = 'Description is required';
    if (!uploadData.price) {
      newErrors.price = 'Price is required';
    } else {
      const price = parseFloat(uploadData.price);
      if (isNaN(price) || price < 0.01 || price > 50) {
        newErrors.price = 'Price must be between $0.01 and $50.00';
      }
    }
    if (!selectedFile) newErrors.file = 'Please select a file to upload';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setIsUploading(true);
    setUploadProgress(0);

    try {
      // First create the premium content record
      const formData = new FormData();
      formData.append('title', uploadData.title);
      formData.append('description', uploadData.description);
      formData.append('content_type', uploadData.content_type);
      formData.append('category', uploadData.category || '');
      formData.append('price', parseFloat(uploadData.price));
      formData.append('tags', JSON.stringify(uploadData.tags));
      formData.append('preview_available', uploadData.preview_available);
      
      // Add the selected file if available
      if (selectedFile) {
        formData.append('content_file', selectedFile);
      }

      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      const backendURL = getBackendURL();
      const token = localStorage.getItem('creatorToken');
      
      const response = await fetch(`${backendURL}/api/creator/content/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
          // Note: Don't set Content-Type header for FormData, browser will set it with boundary
        },
        body: formData
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
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-3xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Upload Premium Content</h2>
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
                  {type.name} (Max: {type.maxSize})
                </option>
              ))}
            </select>
          </div>

          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Title *
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
              Description *
            </label>
            <textarea
              name="description"
              value={uploadData.description}
              onChange={handleInputChange}
              rows={4}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              placeholder="Describe your premium content..."
            />
            {errors.description && <p className="text-red-500 text-sm mt-1">{errors.description}</p>}
          </div>

          {/* Price and Pricing Breakdown */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Price * ($0.01 - $50.00)
              </label>
              <div className="relative">
                <span className="absolute left-3 top-3 text-gray-500">$</span>
                <input
                  type="number"
                  name="price"
                  value={uploadData.price}
                  onChange={handleInputChange}
                  className="w-full pl-8 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="0.00"
                  step="0.01"
                  min="0.01"
                  max="50.00"
                />
              </div>
              {errors.price && <p className="text-red-500 text-sm mt-1">{errors.price}</p>}
            </div>

            {/* Pricing Breakdown */}
            {pricingBreakdown && (
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                <h4 className="text-sm font-medium text-gray-900 mb-2">Revenue Breakdown</h4>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Content Price:</span>
                    <span className="font-medium">${pricingBreakdown.contentPrice.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Platform Fee (20% min $2.99):</span>
                    <span className="text-red-600">-${pricingBreakdown.platformFee.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between border-t border-purple-200 pt-1">
                    <span className="text-gray-900 font-medium">Your Earnings:</span>
                    <span className="font-bold text-green-600">${pricingBreakdown.creatorEarnings.toFixed(2)}</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* File Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Upload File *
            </label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              <div className="mb-4">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
              
              <div className="mb-4">
                <label htmlFor="premium-content-upload" className="cursor-pointer">
                  <span className="text-purple-600 font-medium hover:text-purple-500">
                    Click to upload {uploadData.content_type}
                  </span>
                  <input
                    id="premium-content-upload"
                    type="file"
                    className="hidden"
                    onChange={handleFileChange}
                    accept={contentTypes.find(type => type.id === uploadData.content_type)?.accept}
                  />
                </label>
                <p className="text-gray-500 text-sm mt-2">
                  {uploadData.content_type === 'video' && 'MP4, AVI, MOV, WMV, FLV, WEBM up to 200MB'}
                  {uploadData.content_type === 'document' && 'PDF, DOC, DOCX, TXT up to 50MB'}
                  {uploadData.content_type === 'podcast' && 'MP3, AAC, M4A, WAV up to 500MB'}
                  {uploadData.content_type === 'image' && 'JPG, PNG, GIF, BMP up to 25MB'}
                  {uploadData.content_type === 'interactive' && 'HTML, ZIP up to 100MB'}
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
              placeholder="tutorial, beginner, advanced, tips"
            />
            <p className="text-gray-500 text-sm mt-1">Add relevant tags to help users find your content</p>
          </div>

          {/* Preview Available */}
          <div className="flex items-center">
            <input
              type="checkbox"
              id="preview_available"
              name="preview_available"
              checked={uploadData.preview_available}
              onChange={handleInputChange}
              className="rounded text-purple-600 focus:ring-purple-500"
            />
            <label htmlFor="preview_available" className="ml-2 text-sm text-gray-700">
              Offer free preview (recommended to increase sales)
            </label>
          </div>

          {/* Upload Progress */}
          {isUploading && (
            <div className="mb-4">
              <div className="flex justify-between text-sm text-gray-600 mb-1">
                <span>Uploading premium content...</span>
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
              {isUploading ? 'Creating...' : 'Create Premium Content'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PremiumContentUpload;
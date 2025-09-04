import React, { useState, useEffect } from 'react';
import { getBackendURL } from '../config';

const DepartmentSelector = ({ user, onDepartmentSelect, selectedDepartment }) => {
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user?.company_id) {
      loadDepartments();
    }
  }, [user]);

  const loadDepartments = async () => {
    try {
      setLoading(true);
      const backendURL = getBackendURL();
      const token = localStorage.getItem('token');
      
      const response = await fetch(`${backendURL}/api/business/company/${user.company_id}/departments`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setDepartments(data.departments || []);
      }
    } catch (error) {
      console.error('Failed to load departments:', error);
    }
    setLoading(false);
  };

  // If user is not a business employee, don't show selector
  if (!user?.company_id || user?.user_type !== 'business_employee') {
    return null;
  }

  return (
    <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-blue-900">Department Code</h3>
        <span className="text-sm text-blue-700">For usage tracking & billing</span>
      </div>
      
      {loading ? (
        <div className="text-sm text-blue-600">Loading departments...</div>
      ) : (
        <div className="space-y-2">
          <select
            value={selectedDepartment || user.department_code || ''}
            onChange={(e) => onDepartmentSelect(e.target.value)}
            className="w-full px-3 py-2 border border-blue-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
          >
            <option value="">Select Department (Optional)</option>
            {user.department_code && (
              <option value={user.department_code}>
                Default: {departments.find(d => d.code === user.department_code)?.name || user.department_code}
              </option>
            )}
            {departments
              .filter(dept => dept.code !== user.department_code)
              .map(dept => (
                <option key={dept.code} value={dept.code}>
                  {dept.name} ({dept.code})
                  {dept.budget_limit && ` - Budget: $${dept.budget_limit.toLocaleString()}`}
                </option>
              ))}
          </select>
          
          <div className="text-xs text-blue-600">
            {selectedDepartment || user.department_code ? (
              <>
                ✓ Questions will be charged to: <strong>
                  {departments.find(d => d.code === (selectedDepartment || user.department_code))?.name || 
                   selectedDepartment || user.department_code}
                </strong>
              </>
            ) : (
              '⚠️ No department selected - costs will be unallocated'
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default DepartmentSelector;
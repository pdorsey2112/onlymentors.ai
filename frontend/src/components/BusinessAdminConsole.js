import React, { useState, useEffect } from 'react';
import { getBackendURL } from '../config';
import DatabaseManagement from './DatabaseManagement';
import EnhancedContextDemo from './EnhancedContextDemo';

const BusinessAdminConsole = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [dashboardData, setDashboardData] = useState(null);
  const [employees, setEmployees] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [invites, setInvites] = useState([]);
  const [aiMentors, setAiMentors] = useState([]);
  const [selectedMentors, setSelectedMentors] = useState([]);
  const [loading, setLoading] = useState(false);

  // Admin console features
  const [users, setUsers] = useState([]);
  const [mentors, setMentors] = useState([]);
  const [userActivityReport, setUserActivityReport] = useState(null);
  const [showContextDemo, setShowContextDemo] = useState(false);
  
  // Business Categories
  const [categories, setCategories] = useState([]);
  const [newCategory, setNewCategory] = useState({
    name: '',
    icon: '📂',
    description: ''
  });
  const [editingCategory, setEditingCategory] = useState(null);
  
  // Mentor Assignment
  const [businessMentors, setBusinessMentors] = useState([]);
  const [selectedMentor, setSelectedMentor] = useState(null);
  const [mentorCategories, setMentorCategories] = useState([]);
  const [showMentorAssignment, setShowMentorAssignment] = useState(false);
  
  // Search functionality
  const [userSearchTerm, setUserSearchTerm] = useState('');
  const [mentorSearchTerm, setMentorSearchTerm] = useState('');

  // New employee invite form
  const [newEmployee, setNewEmployee] = useState({
    email: '',
    full_name: '',
    department_code: '',
    role: 'employee'
  });

  // New department form
  const [newDepartment, setNewDepartment] = useState({
    code: '',
    name: '',
    budget_limit: 0,
    cost_center: ''
  });

  useEffect(() => {
    if (activeTab === 'dashboard') {
      loadDashboard();
    } else if (activeTab === 'employees') {
      loadEmployees();
    } else if (activeTab === 'departments') {
      loadDepartments();
    } else if (activeTab === 'categories') {
      loadCategories();
      loadBusinessMentors();
    } else if (activeTab === 'mentors') {
      loadAiMentors();
    } else if (activeTab === 'admin-users') {
      loadUsers();
    } else if (activeTab === 'admin-mentors') {
      loadMentors();
    } else if (activeTab === 'user-reports') {
      loadUserActivityReport();
    }
  }, [activeTab]);

  // Helper functions
  const formatNumber = (num) => {
    if (num == null || num === undefined) return '0';
    return num.toLocaleString();
  };

  const parseName = (fullName) => {
    if (!fullName || fullName.trim() === '') {
      return { firstName: 'N/A', lastName: 'N/A' };
    }
    
    const nameParts = fullName.trim().split(' ');
    if (nameParts.length === 1) {
      return { firstName: nameParts[0], lastName: '' };
    } else if (nameParts.length === 2) {
      return { firstName: nameParts[0], lastName: nameParts[1] };
    } else {
      return { 
        firstName: nameParts[0], 
        lastName: nameParts.slice(1).join(' ') 
      };
    }
  };

  // Admin load functions
  const loadUsers = async () => {
    try {
      setLoading(true);
      const backendURL = getBackendURL();
      const token = localStorage.getItem('auth_token');
      
      const response = await fetch(`${backendURL}/api/admin/users?limit=100`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setUsers(data);
      }
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadMentors = async () => {
    try {
      setLoading(true);
      const backendURL = getBackendURL();
      const token = localStorage.getItem('auth_token');
      
      const response = await fetch(`${backendURL}/api/admin/mentors?limit=100`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setMentors(data);
      }
    } catch (error) {
      console.error('Error fetching mentors:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadUserActivityReport = async () => {
    try {
      setLoading(true);
      const backendURL = getBackendURL();
      const token = localStorage.getItem('auth_token');
      
      const response = await fetch(`${backendURL}/api/admin/reports/user-activity`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setUserActivityReport(data);
      }
    } catch (error) {
      console.error('Error fetching user activity report:', error);
    } finally {
      setLoading(false);
    }
  };

  // Business Categories Management
  const loadCategories = async () => {
    try {
      setLoading(true);
      const backendURL = getBackendURL();
      const token = localStorage.getItem('auth_token');
      
      const response = await fetch(`${backendURL}/api/business/company/${user.company_id}/categories`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setCategories(data);
      }
    } catch (error) {
      console.error('Error loading categories:', error);
    } finally {
      setLoading(false);
    }
  };

  const addCategory = async () => {
    if (!newCategory.name.trim()) {
      alert('Please enter a category name');
      return;
    }

    try {
      const backendURL = getBackendURL();
      const token = localStorage.getItem('auth_token');
      
      const response = await fetch(`${backendURL}/api/business/company/${user.company_id}/categories`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newCategory)
      });
      
      if (response.ok) {
        setNewCategory({ name: '', icon: '📂', description: '' });
        loadCategories();
        alert('Category added successfully!');
      } else {
        const error = await response.json();
        alert(`Failed to add category: ${error.detail}`);
      }
    } catch (error) {
      alert('Network error. Please try again.');
    }
  };

  const updateCategory = async (categoryId, updatedCategory) => {
    try {
      const backendURL = getBackendURL();
      const token = localStorage.getItem('auth_token');
      
      const response = await fetch(`${backendURL}/api/business/company/${user.company_id}/categories/${categoryId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(updatedCategory)
      });
      
      if (response.ok) {
        setEditingCategory(null);
        loadCategories();
        alert('Category updated successfully!');
      } else {
        const error = await response.json();
        alert(`Failed to update category: ${error.detail}`);
      }
    } catch (error) {
      alert('Network error. Please try again.');
    }
  };

  const deleteCategory = async (categoryId, categoryName) => {
    if (!window.confirm(`Are you sure you want to delete the "${categoryName}" category? This action cannot be undone.`)) {
      return;
    }

    try {
      const backendURL = getBackendURL();
      const token = localStorage.getItem('auth_token');
      
      const response = await fetch(`${backendURL}/api/business/company/${user.company_id}/categories/${categoryId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        loadCategories();
        alert('Category deleted successfully!');
      } else {
        const error = await response.json();
        alert(`Failed to delete category: ${error.detail}`);
      }
    } catch (error) {
      alert('Network error. Please try again.');
    }
  };

  // Mentor Assignment Functions
  const loadBusinessMentors = async () => {
    try {
      setLoading(true);
      const backendURL = getBackendURL();
      const token = localStorage.getItem('auth_token');
      
      const response = await fetch(`${backendURL}/api/business/company/${user.company_id}/mentors`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setBusinessMentors(data);
      }
    } catch (error) {
      console.error('Error loading business mentors:', error);
    } finally {
      setLoading(false);
    }
  };

  const assignMentorToCategories = async (mentorId, mentorType, categoryIds) => {
    try {
      const backendURL = getBackendURL();
      const token = localStorage.getItem('auth_token');
      
      const response = await fetch(`${backendURL}/api/business/company/${user.company_id}/mentors/${mentorId}/categories`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          mentor_type: mentorType,
          category_ids: categoryIds
        })
      });
      
      if (response.ok) {
        loadBusinessMentors();
        loadCategories(); // Refresh category mentor counts
        alert('Mentor assigned to categories successfully!');
      } else {
        const error = await response.json();
        alert(`Failed to assign mentor: ${error.detail}`);
      }
    } catch (error) {
      alert('Network error. Please try again.');
    }
  };

  const removeMentorFromCategories = async (mentorId, mentorType) => {
    if (!window.confirm('Are you sure you want to remove this mentor from all categories?')) {
      return;
    }

    try {
      const backendURL = getBackendURL();
      const token = localStorage.getItem('auth_token');
      
      const response = await fetch(`${backendURL}/api/business/company/${user.company_id}/mentors/${mentorId}/categories?mentor_type=${mentorType}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        loadBusinessMentors();
        loadCategories();
        alert('Mentor removed from categories successfully!');
      } else {
        const error = await response.json();
        alert(`Failed to remove mentor: ${error.detail}`);
      }
    } catch (error) {
      alert('Network error. Please try again.');
    }
  };

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const backendURL = getBackendURL();
      const token = localStorage.getItem('token');
      
      const response = await fetch(`${backendURL}/api/business/company/${user.company_id}/dashboard`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
      }
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    }
    setLoading(false);
  };

  const loadEmployees = async () => {
    try {
      setLoading(true);
      const backendURL = getBackendURL();
      const token = localStorage.getItem('token');
      
      const response = await fetch(`${backendURL}/api/business/company/${user.company_id}/employees`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setEmployees(data.employees || []);
        setInvites(data.invites || []);
      }
    } catch (error) {
      console.error('Failed to load employees:', error);
    }
    setLoading(false);
  };

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

  const loadAiMentors = async () => {
    try {
      setLoading(true);
      const backendURL = getBackendURL();
      
      const response = await fetch(`${backendURL}/api/search/mentors?mentor_type=ai&limit=500`);
      if (response.ok) {
        const data = await response.json();
        setAiMentors(data.results || []);
      }
    } catch (error) {
      console.error('Failed to load AI mentors:', error);
    }
    setLoading(false);
  };

  const handleInviteEmployee = async (e) => {
    e.preventDefault();
    try {
      const backendURL = getBackendURL();
      const token = localStorage.getItem('token');
      
      const response = await fetch(`${backendURL}/api/business/company/${user.company_id}/employees/invite`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newEmployee)
      });
      
      if (response.ok) {
        setNewEmployee({ email: '', full_name: '', department_code: '', role: 'employee' });
        loadEmployees();
        alert('Employee invited successfully!');
      } else {
        const error = await response.json();
        alert(`Failed to invite employee: ${error.detail}`);
      }
    } catch (error) {
      alert('Network error. Please try again.');
    }
  };

  const handleAddDepartment = async (e) => {
    e.preventDefault();
    try {
      const backendURL = getBackendURL();
      const token = localStorage.getItem('token');
      
      const response = await fetch(`${backendURL}/api/business/company/${user.company_id}/departments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newDepartment)
      });
      
      if (response.ok) {
        setNewDepartment({ code: '', name: '', budget_limit: 0, cost_center: '' });
        loadDepartments();
        alert('Department added successfully!');
      } else {
        const error = await response.json();
        alert(`Failed to add department: ${error.detail}`);
      }
    } catch (error) {
      alert('Network error. Please try again.');
    }
  };

  const renderDashboard = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Company Dashboard</h2>
        <div className="text-sm text-gray-500">
          {dashboardData?.company?.name} - {dashboardData?.company?.plan}
        </div>
      </div>

      {dashboardData?.company?.status === 'trial' && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h3 className="font-semibold text-yellow-800">Trial Period</h3>
          <p className="text-yellow-700 text-sm">
            Your trial expires on {new Date(dashboardData.company.trial_ends).toLocaleDateString()}
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow border">
          <div className="text-2xl font-bold text-blue-600">{dashboardData?.stats?.total_employees || 0}</div>
          <div className="text-sm text-gray-600">Total Employees</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow border">
          <div className="text-2xl font-bold text-green-600">{dashboardData?.stats?.active_employees || 0}</div>
          <div className="text-sm text-gray-600">Active Users</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow border">
          <div className="text-2xl font-bold text-purple-600">{dashboardData?.stats?.total_questions_30d || 0}</div>
          <div className="text-sm text-gray-600">Questions (30d)</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow border">
          <div className="text-2xl font-bold text-orange-600">{dashboardData?.stats?.departments || 0}</div>
          <div className="text-sm text-gray-600">Departments</div>
        </div>
      </div>

      {dashboardData?.department_usage && (
        <div className="bg-white rounded-lg shadow border p-6">
          <h3 className="text-lg font-semibold mb-4">Department Usage (30 days)</h3>
          <div className="space-y-3">
            {Object.entries(dashboardData.department_usage).map(([dept, usage]) => (
              <div key={dept} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                <div className="font-medium">{dept}</div>
                <div className="text-sm text-gray-600">
                  {usage.questions} questions • {usage.employees} employees
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const renderEmployees = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Employee Management</h2>
      </div>

      {/* Invite Employee Form */}
      <div className="bg-white rounded-lg shadow border p-6">
        <h3 className="text-lg font-semibold mb-4">Invite New Employee</h3>
        <form onSubmit={handleInviteEmployee} className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <input
            type="email"
            placeholder="Email"
            value={newEmployee.email}
            onChange={(e) => setNewEmployee({...newEmployee, email: e.target.value})}
            className="px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
            required
          />
          <input
            type="text"
            placeholder="Full Name"
            value={newEmployee.full_name}
            onChange={(e) => setNewEmployee({...newEmployee, full_name: e.target.value})}
            className="px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
            required
          />
          <select
            value={newEmployee.department_code}
            onChange={(e) => setNewEmployee({...newEmployee, department_code: e.target.value})}
            className="px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
          >
            <option value="">No Department</option>
            {departments.map(dept => (
              <option key={dept.code} value={dept.code}>{dept.name} ({dept.code})</option>
            ))}
          </select>
          <select
            value={newEmployee.role}
            onChange={(e) => setNewEmployee({...newEmployee, role: e.target.value})}
            className="px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
          >
            <option value="employee">Employee</option>
            <option value="manager">Manager</option>
            <option value="admin">Admin</option>
          </select>
          <button
            type="submit"
            className="md:col-span-2 bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700"
          >
            Send Invitation
          </button>
        </form>
      </div>

      {/* Employee List */}
      <div className="bg-white rounded-lg shadow border">
        <div className="p-6 border-b">
          <h3 className="text-lg font-semibold">Current Employees ({employees.length})</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-500">Name</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-500">Email</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-500">Department</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-500">Role</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-500">Last Login</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {employees.map(emp => (
                <tr key={emp.user_id}>
                  <td className="px-6 py-4 text-sm text-gray-900">{emp.full_name}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{emp.email}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{emp.department_code || 'N/A'}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{emp.business_role || 'employee'}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {emp.last_login ? new Date(emp.last_login).toLocaleDateString() : 'Never'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pending Invites */}
      {invites.length > 0 && (
        <div className="bg-white rounded-lg shadow border">
          <div className="p-6 border-b">
            <h3 className="text-lg font-semibold">Pending Invitations ({invites.length})</h3>
          </div>
          <div className="p-6 space-y-3">
            {invites.map(invite => (
              <div key={invite.invite_id} className="flex justify-between items-center p-3 bg-yellow-50 rounded">
                <div>
                  <div className="font-medium">{invite.full_name}</div>
                  <div className="text-sm text-gray-600">{invite.email}</div>
                </div>
                <div className="text-sm text-gray-500">
                  Sent {new Date(invite.invited_at).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const renderDepartments = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Department Management</h2>
      </div>

      {/* Add Department Form */}
      <div className="bg-white rounded-lg shadow border p-6">
        <h3 className="text-lg font-semibold mb-4">Add New Department</h3>
        <form onSubmit={handleAddDepartment} className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <input
            type="text"
            placeholder="Department Code (e.g., ENG, MKT)"
            value={newDepartment.code}
            onChange={(e) => setNewDepartment({...newDepartment, code: e.target.value.toUpperCase()})}
            className="px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
            required
          />
          <input
            type="text"
            placeholder="Department Name"
            value={newDepartment.name}
            onChange={(e) => setNewDepartment({...newDepartment, name: e.target.value})}
            className="px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
            required
          />
          <input
            type="number"
            placeholder="Monthly Budget Limit ($)"
            value={newDepartment.budget_limit}
            onChange={(e) => setNewDepartment({...newDepartment, budget_limit: parseFloat(e.target.value)})}
            className="px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="text"
            placeholder="Cost Center"
            value={newDepartment.cost_center}
            onChange={(e) => setNewDepartment({...newDepartment, cost_center: e.target.value})}
            className="px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            className="md:col-span-2 bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700"
          >
            Add Department
          </button>
        </form>
      </div>

      {/* Department List */}
      <div className="bg-white rounded-lg shadow border">
        <div className="p-6 border-b">
          <h3 className="text-lg font-semibold">Departments ({departments.length})</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-500">Code</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-500">Name</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-500">Budget Limit</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-500">Cost Center</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-500">Employees</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {departments.map(dept => (
                <tr key={dept.code}>
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">{dept.code}</td>
                  <td className="px-6 py-4 text-sm text-gray-900">{dept.name}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    ${dept.budget_limit?.toLocaleString() || 'N/A'}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">{dept.cost_center || 'N/A'}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{dept.usage_stats?.employee_count || 0}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  // Admin render functions
  const renderAdminUsers = () => {
    const filteredUsers = users.filter(user => 
      user.full_name?.toLowerCase().includes(userSearchTerm.toLowerCase()) ||
      user.email?.toLowerCase().includes(userSearchTerm.toLowerCase())
    );

    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-900">User Management ({users.length} users)</h2>
        </div>

        {/* User Search */}
        <div className="max-w-md">
          <input
            type="text"
            placeholder="Search users by name or email..."
            value={userSearchTerm}
            onChange={(e) => setUserSearchTerm(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Users Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Questions Asked
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredUsers.map(user => {
                const { firstName, lastName } = parseName(user.full_name);
                return (
                  <tr key={user.user_id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {firstName} {lastName}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500">{user.email}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatNumber(user.questions_asked || 0)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  const renderAdminMentors = () => {
    const filteredMentors = mentors.filter(mentor => 
      mentor.full_name?.toLowerCase().includes(mentorSearchTerm.toLowerCase()) ||
      mentor.email?.toLowerCase().includes(mentorSearchTerm.toLowerCase())
    );

    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-900">Mentor Management ({mentors.length} mentors)</h2>
        </div>

        {/* Mentor Search */}
        <div className="max-w-md">
          <input
            type="text"
            placeholder="Search mentors by name or email..."
            value={mentorSearchTerm}
            onChange={(e) => setMentorSearchTerm(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Mentors Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Mentor
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Verification
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredMentors.map(mentor => {
                const { firstName, lastName } = parseName(mentor.full_name);
                return (
                  <tr key={mentor.creator_id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {firstName} {lastName}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500">{mentor.email}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        mentor.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {mentor.status || 'Active'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        mentor.verification?.status === 'verified' ? 'bg-blue-100 text-blue-800' : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {mentor.verification?.status || 'Pending'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {mentor.created_at ? new Date(mentor.created_at).toLocaleDateString() : 'N/A'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  const renderUserReports = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">User Activity Reports</h2>
      </div>

      {userActivityReport ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="text-2xl font-bold text-blue-600">{formatNumber(userActivityReport.total_users)}</div>
            <div className="text-sm text-gray-600">Total Users</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="text-2xl font-bold text-green-600">{formatNumber(userActivityReport.active_users)}</div>
            <div className="text-sm text-gray-600">Active Users</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="text-2xl font-bold text-purple-600">{formatNumber(userActivityReport.total_questions)}</div>
            <div className="text-sm text-gray-600">Total Questions</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="text-2xl font-bold text-orange-600">{formatNumber(userActivityReport.questions_today)}</div>
            <div className="text-sm text-gray-600">Questions Today</div>
          </div>
        </div>
      ) : (
        <div className="text-center py-12">
          <div className="text-2xl text-gray-400 mb-4">📊</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Loading Reports...</h3>
          <p className="text-gray-600">Gathering user activity data.</p>
        </div>
      )}
    </div>
  );

  const renderDatabase = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Database Management</h2>
      </div>
      <DatabaseManagement />
    </div>
  );

  const renderContentModeration = () => (
    <div className="space-y-6">
      <div className="text-center py-12">
        <div className="text-2xl text-gray-400 mb-4">🛡️</div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">Content Moderation</h3>
        <p className="text-gray-600">Content moderation tools will be available soon.</p>
      </div>
    </div>
  );

  const renderAiAgents = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">AI Agents</h2>
        <button
          onClick={() => setShowContextDemo(!showContextDemo)}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          {showContextDemo ? 'Hide Demo' : 'Show Context Demo'}
        </button>
      </div>
      {showContextDemo && <EnhancedContextDemo />}
    </div>
  );

  const renderCategories = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">🗂️ Category Management</h2>
        <div className="text-sm text-gray-500">
          {categories.length} categories
        </div>
      </div>

      {/* Add New Category */}
      <div className="bg-white rounded-lg shadow border p-6">
        <h3 className="text-lg font-semibold mb-4">Add New Category</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Category Name</label>
            <input
              type="text"
              value={newCategory.name}
              onChange={(e) => setNewCategory({...newCategory, name: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              placeholder="e.g., Marketing"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Icon</label>
            <select
              value={newCategory.icon}
              onChange={(e) => setNewCategory({...newCategory, icon: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="📂">📂 Folder</option>
              <option value="⚙️">⚙️ Operations</option>
              <option value="💼">💼 Sales</option>
              <option value="📚">📚 Training</option>
              <option value="👥">👥 HR</option>
              <option value="💰">💰 Payroll</option>
              <option value="📊">📊 Accounting</option>
              <option value="🚀">🚀 Product</option>
              <option value="💻">💻 Technology</option>
              <option value="🛠️">🛠️ Support</option>
              <option value="📈">📈 Analytics</option>
              <option value="🎯">🎯 Strategy</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
            <input
              type="text"
              value={newCategory.description}
              onChange={(e) => setNewCategory({...newCategory, description: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              placeholder="Brief description..."
            />
          </div>
        </div>
        <div className="mt-4">
          <button
            onClick={addCategory}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Add Category
          </button>
        </div>
      </div>

      {/* Categories List */}
      <div className="bg-white rounded-lg shadow border">
        <div className="p-6 border-b">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">Business Categories</h3>
            <button
              onClick={() => setShowMentorAssignment(!showMentorAssignment)}
              className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700"
            >
              {showMentorAssignment ? 'Hide Mentor Assignment' : 'Assign Mentors to Categories'}
            </button>
          </div>
        </div>

        {showMentorAssignment && (
          <div className="p-6 border-b bg-gray-50">
            <h4 className="text-md font-semibold mb-4">Mentor Assignment</h4>
            
            {/* Mentor List for Assignment */}
            <div className="space-y-4">
              {businessMentors.map(mentor => (
                <div key={`${mentor.type}_${mentor.mentor_id}`} className="flex items-center justify-between p-4 bg-white rounded border">
                  <div className="flex items-center space-x-4">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-bold ${
                      mentor.type === 'ai' ? 'bg-blue-500' : 'bg-green-500'
                    }`}>
                      {mentor.type === 'ai' ? '🤖' : '👨‍🏫'}
                    </div>
                    <div>
                      <h5 className="font-medium">{mentor.name}</h5>
                      <p className="text-sm text-gray-600">
                        {mentor.type === 'ai' ? 'AI Mentor' : `Human Mentor • ${mentor.email}`}
                      </p>
                      {mentor.category_ids.length > 0 && (
                        <div className="text-xs text-gray-500 mt-1">
                          Assigned to {mentor.category_ids.length} categories
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex space-x-2">
                    <button
                      onClick={() => {
                        setSelectedMentor(mentor);
                        setMentorCategories(mentor.category_ids);
                      }}
                      className="bg-blue-100 text-blue-600 px-3 py-1 rounded text-sm hover:bg-blue-200"
                    >
                      {mentor.is_assigned ? 'Edit Categories' : 'Assign Categories'}
                    </button>
                    {mentor.is_assigned && (
                      <button
                        onClick={() => removeMentorFromCategories(mentor.mentor_id, mentor.type)}
                        className="bg-red-100 text-red-600 px-3 py-1 rounded text-sm hover:bg-red-200"
                      >
                        Remove All
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Category Assignment Modal */}
            {selectedMentor && (
              <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <div className="bg-white p-6 rounded-lg max-w-md w-full mx-4">
                  <h4 className="text-lg font-semibold mb-4">
                    Assign Categories to {selectedMentor.name}
                  </h4>
                  
                  <div className="space-y-2 max-h-60 overflow-y-auto">
                    {categories.map(category => (
                      <label key={category.category_id} className="flex items-center space-x-3">
                        <input
                          type="checkbox"
                          checked={mentorCategories.includes(category.category_id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setMentorCategories([...mentorCategories, category.category_id]);
                            } else {
                              setMentorCategories(mentorCategories.filter(id => id !== category.category_id));
                            }
                          }}
                          className="rounded border-gray-300"
                        />
                        <span className="text-lg">{category.icon}</span>
                        <span>{category.name}</span>
                      </label>
                    ))}
                  </div>
                  
                  <div className="flex justify-end space-x-2 mt-6">
                    <button
                      onClick={() => {
                        setSelectedMentor(null);
                        setMentorCategories([]);
                      }}
                      className="px-4 py-2 text-gray-600 border border-gray-300 rounded hover:bg-gray-50"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={() => {
                        assignMentorToCategories(selectedMentor.mentor_id, selectedMentor.type, mentorCategories);
                        setSelectedMentor(null);
                        setMentorCategories([]);
                      }}
                      className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      Save Assignment
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        <div className="divide-y divide-gray-200">
          {categories.map(category => (
            <div key={category.category_id} className="p-6">
              {editingCategory === category.category_id ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <input
                      type="text"
                      defaultValue={category.name}
                      className="px-3 py-2 border border-gray-300 rounded-md"
                      onChange={(e) => setEditingCategory({...category, name: e.target.value})}
                    />
                    <select
                      defaultValue={category.icon}
                      className="px-3 py-2 border border-gray-300 rounded-md"
                      onChange={(e) => setEditingCategory({...category, icon: e.target.value})}
                    >
                      <option value="📂">📂 Folder</option>
                      <option value="⚙️">⚙️ Operations</option>
                      <option value="💼">💼 Sales</option>
                      <option value="📚">📚 Training</option>
                      <option value="👥">👥 HR</option>
                      <option value="💰">💰 Payroll</option>
                      <option value="📊">📊 Accounting</option>
                      <option value="🚀">🚀 Product</option>
                      <option value="💻">💻 Technology</option>
                      <option value="🛠️">🛠️ Support</option>
                    </select>
                    <input
                      type="text"
                      defaultValue={category.description}
                      className="px-3 py-2 border border-gray-300 rounded-md"
                      onChange={(e) => setEditingCategory({...category, description: e.target.value})}
                    />
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => updateCategory(category.category_id, editingCategory)}
                      className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
                    >
                      Save
                    </button>
                    <button
                      onClick={() => setEditingCategory(null)}
                      className="bg-gray-600 text-white px-3 py-1 rounded text-sm hover:bg-gray-700"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <div className="flex justify-between items-center">
                  <div className="flex items-center space-x-4">
                    <div className="text-2xl">{category.icon}</div>
                    <div>
                      <h4 className="text-lg font-medium text-gray-900">{category.name}</h4>
                      <p className="text-sm text-gray-600">{category.description}</p>
                      <div className="text-xs text-gray-500 mt-1">
                        {category.mentor_count || 0} mentors assigned
                      </div>
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => setEditingCategory(category.category_id)}
                      className="bg-blue-100 text-blue-600 px-3 py-1 rounded text-sm hover:bg-blue-200"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => deleteCategory(category.category_id, category.name)}
                      className="bg-red-100 text-red-600 px-3 py-1 rounded text-sm hover:bg-red-200"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
          {categories.length === 0 && (
            <div className="p-8 text-center">
              <div className="text-gray-400 text-4xl mb-4">📂</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Categories Yet</h3>
              <p className="text-gray-600">Add your first category to organize mentors by expertise area.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">🏢 Business Console</h1>
              <span className="ml-4 px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                {user?.company_name || 'Enterprise'}
              </span>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600">Welcome, {user?.full_name}</span>
              <button
                onClick={onLogout}
                className="bg-gray-100 text-gray-700 px-4 py-2 rounded hover:bg-gray-200"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {[
              { id: 'dashboard', name: 'Dashboard', icon: '📊' },
              { id: 'employees', name: 'Employees', icon: '👥' },
              { id: 'departments', name: 'Departments', icon: '🏬' },
              { id: 'categories', name: 'Categories', icon: '🗂️' },
              { id: 'mentors', name: 'AI Mentors', icon: '🤖' },
              { id: 'reports', name: 'Reports', icon: '📈' },
              { id: 'admin-users', name: 'Users', icon: '👤' },
              { id: 'admin-mentors', name: 'Mentors', icon: '🎯' },
              { id: 'database', name: 'Database', icon: '🗄️' },
              { id: 'content-moderation', name: 'Moderation', icon: '🛡️' },
              { id: 'user-reports', name: 'User Reports', icon: '📋' },
              { id: 'ai-agents', name: 'AI Agents', icon: '🤖' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.icon} {tab.name}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          <div className="flex justify-center items-center py-12">
            <div className="text-lg text-gray-600">Loading...</div>
          </div>
        ) : (
          <>
            {activeTab === 'dashboard' && renderDashboard()}
            {activeTab === 'employees' && renderEmployees()}
            {activeTab === 'departments' && renderDepartments()}
            {activeTab === 'categories' && renderCategories()}
            {activeTab === 'mentors' && (
              <div className="text-center py-12">
                <div className="text-2xl text-gray-400 mb-4">🤖</div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">AI Mentors Coming Soon</h3>
                <p className="text-gray-600">AI mentor selection and management features will be available soon.</p>
              </div>
            )}
            {activeTab === 'reports' && (
              <div className="text-center py-12">
                <div className="text-2xl text-gray-400 mb-4">📈</div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Reports Coming Soon</h3>
                <p className="text-gray-600">Advanced analytics and reporting features will be available soon.</p>
              </div>
            )}
            {activeTab === 'admin-users' && renderAdminUsers()}
            {activeTab === 'admin-mentors' && renderAdminMentors()}
            {activeTab === 'database' && renderDatabase()}
            {activeTab === 'content-moderation' && renderContentModeration()}
            {activeTab === 'user-reports' && renderUserReports()}
            {activeTab === 'ai-agents' && renderAiAgents()}
          </>
        )}
      </div>
    </div>
  );
};

export default BusinessAdminConsole;
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
              { id: 'mentors', name: 'AI Mentors', icon: '🤖' },
              { id: 'reports', name: 'Reports', icon: '📈' }
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
            {activeTab === 'reports' && (
              <div className="text-center py-12">
                <div className="text-2xl text-gray-400 mb-4">📈</div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Reports Coming Soon</h3>
                <p className="text-gray-600">Advanced analytics and reporting features will be available soon.</p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default BusinessAdminConsole;
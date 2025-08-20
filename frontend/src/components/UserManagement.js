import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from './ui/alert-dialog';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import { Trash2, Edit3, Shield, UserX, History } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

const UserManagement = ({ admin }) => {
    const [users, setUsers] = useState([]);
    const [filteredUsers, setFilteredUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [roleFilter, setRoleFilter] = useState('all');
    const [statusFilter, setStatusFilter] = useState('all');
    
    // Modal states
    const [selectedUser, setSelectedUser] = useState(null);
    const [showRoleDialog, setShowRoleDialog] = useState(false);
    const [showSuspendDialog, setShowSuspendDialog] = useState(false);
    const [showDeleteDialog, setShowDeleteDialog] = useState(false);
    const [showAuditDialog, setShowAuditDialog] = useState(false);
    
    // Form states
    const [newRole, setNewRole] = useState('');
    const [reason, setReason] = useState('');
    const [auditHistory, setAuditHistory] = useState([]);
    const [actionLoading, setActionLoading] = useState(false);

    const getAuthHeaders = () => ({
        'Authorization': `Bearer ${localStorage.getItem('adminToken')}`,
        'Content-Type': 'application/json'
    });

    const fetchUsers = async () => {
        try {
            setLoading(true);
            const response = await fetch(`${BACKEND_URL}/api/admin/users?limit=200`, {
                headers: getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                setUsers(data.users || []);
                setFilteredUsers(data.users || []);
            } else {
                console.error('Failed to fetch users');
            }
        } catch (error) {
            console.error('Error fetching users:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchAuditHistory = async (userId) => {
        try {
            const response = await fetch(`${BACKEND_URL}/api/admin/users/${userId}/audit`, {
                headers: getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                setAuditHistory(data.audit_history || []);
            }
        } catch (error) {
            console.error('Error fetching audit history:', error);
        }
    };

    const changeUserRole = async () => {
        if (!selectedUser || !newRole || !reason.trim()) {
            alert('Please fill in all required fields');
            return;
        }

        try {
            setActionLoading(true);
            const response = await fetch(`${BACKEND_URL}/api/admin/users/${selectedUser.user_id}/role`, {
                method: 'PUT',
                headers: getAuthHeaders(),
                body: JSON.stringify({
                    user_id: selectedUser.user_id,
                    new_role: newRole,
                    reason: reason.trim()
                })
            });

            if (response.ok) {
                await fetchUsers(); // Refresh the list
                setShowRoleDialog(false);
                setNewRole('');
                setReason('');
                setSelectedUser(null);
                alert('User role updated successfully!');
            } else {
                const error = await response.text();
                alert(`Failed to update user role: ${error}`);
            }
        } catch (error) {
            console.error('Error updating user role:', error);
            alert('Error updating user role');
        } finally {
            setActionLoading(false);
        }
    };

    const suspendUser = async (suspend = true) => {
        if (!selectedUser || (!suspend && !reason.trim())) {
            alert('Please provide a reason');
            return;
        }

        try {
            setActionLoading(true);
            const response = await fetch(`${BACKEND_URL}/api/admin/users/${selectedUser.user_id}/suspend`, {
                method: 'PUT',
                headers: getAuthHeaders(),
                body: JSON.stringify({
                    user_id: selectedUser.user_id,
                    suspend: suspend,
                    reason: reason.trim() || 'No reason provided'
                })
            });

            if (response.ok) {
                await fetchUsers(); // Refresh the list
                setShowSuspendDialog(false);
                setReason('');
                setSelectedUser(null);
                alert(`User ${suspend ? 'suspended' : 'reactivated'} successfully!`);
            } else {
                const error = await response.text();
                alert(`Failed to ${suspend ? 'suspend' : 'reactivate'} user: ${error}`);
            }
        } catch (error) {
            console.error(`Error ${suspend ? 'suspending' : 'reactivating'} user:`, error);
            alert(`Error ${suspend ? 'suspending' : 'reactivating'} user`);
        } finally {
            setActionLoading(false);
        }
    };

    const deleteUser = async () => {
        if (!selectedUser || !reason.trim()) {
            alert('Please provide a reason for deletion');
            return;
        }

        try {
            setActionLoading(true);
            const response = await fetch(`${BACKEND_URL}/api/admin/users/${selectedUser.user_id}?reason=${encodeURIComponent(reason.trim())}`, {
                method: 'DELETE',
                headers: getAuthHeaders()
            });

            if (response.ok) {
                await fetchUsers(); // Refresh the list
                setShowDeleteDialog(false);
                setReason('');
                setSelectedUser(null);
                alert('User deleted successfully!');
            } else {
                const error = await response.text();
                alert(`Failed to delete user: ${error}`);
            }
        } catch (error) {
            console.error('Error deleting user:', error);
            alert('Error deleting user');
        } finally {
            setActionLoading(false);
        }
    };

    const filterUsers = () => {
        let filtered = users;

        // Search filter
        if (searchTerm) {
            filtered = filtered.filter(user => 
                user.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                user.email?.toLowerCase().includes(searchTerm.toLowerCase())
            );
        }

        // Role filter
        if (roleFilter !== 'all') {
            filtered = filtered.filter(user => 
                (user.role || 'user') === roleFilter
            );
        }

        // Status filter
        if (statusFilter === 'active') {
            filtered = filtered.filter(user => !user.is_suspended && !user.deleted_at);
        } else if (statusFilter === 'suspended') {
            filtered = filtered.filter(user => user.is_suspended);
        } else if (statusFilter === 'deleted') {
            filtered = filtered.filter(user => user.deleted_at);
        }

        setFilteredUsers(filtered);
    };

    useEffect(() => {
        fetchUsers();
    }, []);

    useEffect(() => {
        filterUsers();
    }, [users, searchTerm, roleFilter, statusFilter]);

    const getRoleBadge = (role) => {
        const roleConfig = {
            admin: { variant: 'destructive', label: 'Admin' },
            mentor: { variant: 'default', label: 'Mentor' },
            user: { variant: 'secondary', label: 'User' }
        };
        
        const config = roleConfig[role] || roleConfig.user;
        return <Badge variant={config.variant}>{config.label}</Badge>;
    };

    const getStatusBadge = (user) => {
        if (user.deleted_at) {
            return <Badge variant="destructive">Deleted</Badge>;
        } else if (user.is_suspended) {
            return <Badge variant="outline">Suspended</Badge>;
        } else {
            return <Badge variant="default">Active</Badge>;
        }
    };

    if (loading) {
        return (
            <Card>
                <CardContent className="p-6">
                    <div className="flex items-center justify-center">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
                        <span className="ml-2">Loading users...</span>
                    </div>
                </CardContent>
            </Card>
        );
    }

    return (
        <div className="space-y-6">
            <Card>
                <CardHeader>
                    <CardTitle>User Management</CardTitle>
                    <CardDescription>
                        Manage user accounts, roles, and permissions
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    {/* Filters */}
                    <div className="flex flex-col sm:flex-row gap-4 mb-6">
                        <div className="flex-1">
                            <Input
                                placeholder="Search by name or email..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                            />
                        </div>
                        <div className="flex gap-2">
                            <Select value={roleFilter} onValueChange={setRoleFilter}>
                                <SelectTrigger className="w-32">
                                    <SelectValue placeholder="Role" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="all">All Roles</SelectItem>
                                    <SelectItem value="user">User</SelectItem>
                                    <SelectItem value="mentor">Mentor</SelectItem>
                                    <SelectItem value="admin">Admin</SelectItem>
                                </SelectContent>
                            </Select>
                            
                            <Select value={statusFilter} onValueChange={setStatusFilter}>
                                <SelectTrigger className="w-32">
                                    <SelectValue placeholder="Status" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="all">All Status</SelectItem>
                                    <SelectItem value="active">Active</SelectItem>
                                    <SelectItem value="suspended">Suspended</SelectItem>
                                    <SelectItem value="deleted">Deleted</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                    </div>

                    {/* Stats */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                        <div className="text-center">
                            <div className="text-2xl font-bold text-purple-600">{users.length}</div>
                            <div className="text-sm text-gray-600">Total Users</div>
                        </div>
                        <div className="text-center">
                            <div className="text-2xl font-bold text-green-600">
                                {users.filter(u => !u.is_suspended && !u.deleted_at).length}
                            </div>
                            <div className="text-sm text-gray-600">Active</div>
                        </div>
                        <div className="text-center">
                            <div className="text-2xl font-bold text-orange-600">
                                {users.filter(u => u.is_suspended).length}
                            </div>
                            <div className="text-sm text-gray-600">Suspended</div>
                        </div>
                        <div className="text-center">
                            <div className="text-2xl font-bold text-red-600">
                                {users.filter(u => u.deleted_at).length}
                            </div>
                            <div className="text-sm text-gray-600">Deleted</div>
                        </div>
                    </div>

                    {/* Users Table */}
                    <div className="border rounded-lg">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>User</TableHead>
                                    <TableHead>Role</TableHead>
                                    <TableHead>Status</TableHead>
                                    <TableHead>Questions</TableHead>
                                    <TableHead>Subscription</TableHead>
                                    <TableHead>Created</TableHead>
                                    <TableHead>Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {filteredUsers.map((user) => (
                                    <TableRow key={user.user_id}>
                                        <TableCell>
                                            <div>
                                                <div className="font-medium">{user.full_name}</div>
                                                <div className="text-sm text-gray-500">{user.email}</div>
                                            </div>
                                        </TableCell>
                                        <TableCell>{getRoleBadge(user.role)}</TableCell>
                                        <TableCell>{getStatusBadge(user)}</TableCell>
                                        <TableCell>{user.questions_asked || 0}</TableCell>
                                        <TableCell>
                                            {user.is_subscribed ? (
                                                <Badge variant="default">Subscribed</Badge>
                                            ) : (
                                                <Badge variant="outline">Free</Badge>
                                            )}
                                        </TableCell>
                                        <TableCell>
                                            {new Date(user.created_at).toLocaleDateString()}
                                        </TableCell>
                                        <TableCell>
                                            <div className="flex gap-2">
                                                {/* Role Change Button */}
                                                <Button
                                                    size="sm"
                                                    variant="outline"
                                                    onClick={() => {
                                                        setSelectedUser(user);
                                                        setNewRole(user.role || 'user');
                                                        setShowRoleDialog(true);
                                                    }}
                                                    disabled={user.user_id === admin.user_id}
                                                >
                                                    <Edit3 className="h-4 w-4" />
                                                </Button>

                                                {/* Suspend/Unsuspend Button */}
                                                <Button
                                                    size="sm"
                                                    variant="outline"
                                                    onClick={() => {
                                                        setSelectedUser(user);
                                                        setShowSuspendDialog(true);
                                                    }}
                                                    disabled={user.user_id === admin.user_id || user.deleted_at}
                                                >
                                                    <UserX className="h-4 w-4" />
                                                </Button>

                                                {/* Delete Button */}
                                                <Button
                                                    size="sm"
                                                    variant="outline"
                                                    onClick={() => {
                                                        setSelectedUser(user);
                                                        setShowDeleteDialog(true);
                                                    }}
                                                    disabled={user.user_id === admin.user_id || user.deleted_at}
                                                >
                                                    <Trash2 className="h-4 w-4" />
                                                </Button>

                                                {/* Audit History Button */}
                                                <Button
                                                    size="sm"
                                                    variant="outline"
                                                    onClick={() => {
                                                        setSelectedUser(user);
                                                        fetchAuditHistory(user.user_id);
                                                        setShowAuditDialog(true);
                                                    }}
                                                >
                                                    <History className="h-4 w-4" />
                                                </Button>
                                            </div>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </div>

                    {filteredUsers.length === 0 && (
                        <div className="text-center py-8 text-gray-500">
                            No users found matching your criteria.
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Role Change Dialog */}
            <Dialog open={showRoleDialog} onOpenChange={setShowRoleDialog}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Change User Role</DialogTitle>
                        <DialogDescription>
                            Change the role for {selectedUser?.full_name} ({selectedUser?.email})
                        </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4">
                        <div>
                            <Label htmlFor="role">New Role</Label>
                            <Select value={newRole} onValueChange={setNewRole}>
                                <SelectTrigger>
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="user">User</SelectItem>
                                    <SelectItem value="mentor">Mentor</SelectItem>
                                    <SelectItem value="admin">Admin</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                        <div>
                            <Label htmlFor="reason">Reason *</Label>
                            <Textarea
                                id="reason"
                                placeholder="Provide a reason for this role change..."
                                value={reason}
                                onChange={(e) => setReason(e.target.value)}
                                required
                            />
                        </div>
                        <div className="flex justify-end gap-2">
                            <Button variant="outline" onClick={() => setShowRoleDialog(false)}>
                                Cancel
                            </Button>
                            <Button 
                                onClick={changeUserRole} 
                                disabled={actionLoading || !reason.trim()}
                            >
                                {actionLoading ? 'Updating...' : 'Update Role'}
                            </Button>
                        </div>
                    </div>
                </DialogContent>
            </Dialog>

            {/* Suspend/Unsuspend Dialog */}
            <Dialog open={showSuspendDialog} onOpenChange={setShowSuspendDialog}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>
                            {selectedUser?.is_suspended ? 'Reactivate' : 'Suspend'} User
                        </DialogTitle>
                        <DialogDescription>
                            {selectedUser?.is_suspended ? 'Reactivate' : 'Suspend'} {selectedUser?.full_name} ({selectedUser?.email})
                        </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4">
                        <div>
                            <Label htmlFor="suspend-reason">Reason *</Label>
                            <Textarea
                                id="suspend-reason"
                                placeholder={`Provide a reason for ${selectedUser?.is_suspended ? 'reactivating' : 'suspending'} this user...`}
                                value={reason}
                                onChange={(e) => setReason(e.target.value)}
                                required
                            />
                        </div>
                        <div className="flex justify-end gap-2">
                            <Button variant="outline" onClick={() => setShowSuspendDialog(false)}>
                                Cancel
                            </Button>
                            <Button 
                                onClick={() => suspendUser(!selectedUser?.is_suspended)}
                                disabled={actionLoading || !reason.trim()}
                                variant={selectedUser?.is_suspended ? 'default' : 'destructive'}
                            >
                                {actionLoading ? 'Processing...' : (selectedUser?.is_suspended ? 'Reactivate' : 'Suspend')}
                            </Button>
                        </div>
                    </div>
                </DialogContent>
            </Dialog>

            {/* Delete User Dialog */}
            <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>Delete User</AlertDialogTitle>
                        <AlertDialogDescription>
                            Are you sure you want to delete {selectedUser?.full_name} ({selectedUser?.email})?
                            This action will soft-delete the user (data preserved for audit purposes).
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <div className="my-4">
                        <Label htmlFor="delete-reason">Reason for Deletion *</Label>
                        <Textarea
                            id="delete-reason"
                            placeholder="Provide a reason for deleting this user..."
                            value={reason}
                            onChange={(e) => setReason(e.target.value)}
                            required
                        />
                    </div>
                    <AlertDialogFooter>
                        <AlertDialogCancel onClick={() => setShowDeleteDialog(false)}>
                            Cancel
                        </AlertDialogCancel>
                        <AlertDialogAction
                            onClick={deleteUser}
                            disabled={actionLoading || !reason.trim()}
                            className="bg-red-600 hover:bg-red-700"
                        >
                            {actionLoading ? 'Deleting...' : 'Delete User'}
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>

            {/* Audit History Dialog */}
            <Dialog open={showAuditDialog} onOpenChange={setShowAuditDialog}>
                <DialogContent className="max-w-4xl max-h-96 overflow-y-auto">
                    <DialogHeader>
                        <DialogTitle>Audit History</DialogTitle>
                        <DialogDescription>
                            Action history for {selectedUser?.full_name} ({selectedUser?.email})
                        </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4">
                        {auditHistory.length > 0 ? (
                            <div className="space-y-2">
                                {auditHistory.map((log, index) => (
                                    <div key={index} className="border rounded-lg p-3">
                                        <div className="flex justify-between items-start">
                                            <div>
                                                <div className="font-medium">{log.action.replace('_', ' ').toUpperCase()}</div>
                                                <div className="text-sm text-gray-600">
                                                    By: {log.admin_name || 'Unknown Admin'}
                                                </div>
                                                {log.reason && (
                                                    <div className="text-sm text-gray-600 mt-1">
                                                        Reason: {log.reason}
                                                    </div>
                                                )}
                                                {log.old_role && log.new_role && (
                                                    <div className="text-sm text-gray-600">
                                                        Role changed: {log.old_role} → {log.new_role}
                                                    </div>
                                                )}
                                            </div>
                                            <div className="text-sm text-gray-500">
                                                {new Date(log.timestamp).toLocaleString()}
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-4 text-gray-500">
                                No audit history available for this user.
                            </div>
                        )}
                    </div>
                </DialogContent>
            </Dialog>
        </div>
    );
};

export default UserManagement;
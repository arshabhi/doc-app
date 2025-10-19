import React from 'react';
import { useDocuments } from '../context/DocumentContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Badge } from './ui/badge';
import { FileText, MessageSquare, Users, HardDrive, TrendingUp, Activity } from 'lucide-react';

export function AdminDashboard() {
  const { documents, chatMessages } = useDocuments();

  // Calculate statistics
  const totalDocuments = documents.length;
  const totalChats = chatMessages.length;
  const totalStorage = documents.reduce((acc, doc) => acc + doc.size, 0);
  const summarizedDocs = documents.filter(doc => doc.summary).length;

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const formatDate = (date: Date) => {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Mock user data
  const mockUsers = [
    { id: '1', name: 'Admin User', email: 'admin@example.com', role: 'admin', documentsCount: 2, lastActive: new Date() },
    { id: '2', name: 'John Doe', email: 'user@example.com', role: 'user', documentsCount: 0, lastActive: new Date(Date.now() - 86400000) },
  ];

  // Recent activity
  const recentActivity = [
    { action: 'Document uploaded', user: 'Admin User', time: new Date(), details: 'Sample Document 1.pdf' },
    { action: 'Document summarized', user: 'Admin User', time: new Date(Date.now() - 3600000), details: 'Research Paper.docx' },
    { action: 'Chat initiated', user: 'Admin User', time: new Date(Date.now() - 7200000), details: 'On Sample Document 1.pdf' },
    { action: 'User login', user: 'John Doe', time: new Date(Date.now() - 86400000), details: 'Successful login' },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1>Admin Dashboard</h1>
        <p className="text-gray-600 mt-2">
          System overview and user management
        </p>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm">Total Documents</CardTitle>
            <FileText className="w-4 h-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl">{totalDocuments}</div>
            <p className="text-xs text-gray-500 mt-1">
              {summarizedDocs} summarized
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm">Chat Messages</CardTitle>
            <MessageSquare className="w-4 h-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl">{totalChats}</div>
            <p className="text-xs text-gray-500 mt-1">
              Total conversations
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm">Storage Used</CardTitle>
            <HardDrive className="w-4 h-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl">{formatFileSize(totalStorage)}</div>
            <p className="text-xs text-gray-500 mt-1">
              Across all documents
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm">Active Users</CardTitle>
            <Users className="w-4 h-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl">{mockUsers.length}</div>
            <p className="text-xs text-gray-500 mt-1">
              Registered users
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Users Table */}
        <Card>
          <CardHeader>
            <CardTitle>Users</CardTitle>
            <CardDescription>Manage system users and their access</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>User</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Documents</TableHead>
                  <TableHead>Last Active</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {mockUsers.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>
                      <div>
                        <p>{user.name}</p>
                        <p className="text-xs text-gray-500">{user.email}</p>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant={user.role === 'admin' ? 'default' : 'secondary'}>
                        {user.role}
                      </Badge>
                    </TableCell>
                    <TableCell>{user.documentsCount}</TableCell>
                    <TableCell className="text-xs text-gray-500">
                      {formatDate(user.lastActive)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5" />
              Recent Activity
            </CardTitle>
            <CardDescription>Latest system events</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivity.map((activity, index) => (
                <div key={index} className="flex items-start gap-3 pb-3 border-b last:border-0">
                  <div className="w-2 h-2 rounded-full bg-indigo-600 mt-2" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm">{activity.action}</p>
                    <p className="text-xs text-gray-500 mt-1">{activity.user}</p>
                    <p className="text-xs text-gray-400 mt-1">{activity.details}</p>
                  </div>
                  <div className="text-xs text-gray-400 whitespace-nowrap">
                    {formatDate(activity.time)}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Document Statistics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Document Statistics
          </CardTitle>
          <CardDescription>Detailed breakdown of uploaded documents</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Document Name</TableHead>
                <TableHead>Size</TableHead>
                <TableHead>Upload Date</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Chats</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {documents.map((doc) => {
                const chatCount = chatMessages.filter(msg => msg.documentId === doc.id).length;
                return (
                  <TableRow key={doc.id}>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4 text-indigo-600" />
                        {doc.name}
                      </div>
                    </TableCell>
                    <TableCell>{formatFileSize(doc.size)}</TableCell>
                    <TableCell>{formatDate(doc.uploadDate)}</TableCell>
                    <TableCell>
                      {doc.summary ? (
                        <Badge variant="secondary">Summarized</Badge>
                      ) : (
                        <Badge variant="outline">Not summarized</Badge>
                      )}
                    </TableCell>
                    <TableCell>{chatCount}</TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
          {documents.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <FileText className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p>No documents uploaded yet</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

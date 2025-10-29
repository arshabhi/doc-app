# Admin API Endpoints

All admin endpoints require the user to have admin role.

## 1. GET /api/admin/users
Get all users in the system.

### Request Headers
```
Authorization: Bearer <accessToken>
X-Admin-Role: required
```

### Query Parameters
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)
- `search` (optional): Search by name or email
- `role` (optional): Filter by role ("user" or "admin")
- `status` (optional): Filter by status ("active" or "inactive")
- `sortBy` (optional): Sort field (default: "createdAt")
- `order` (optional): Sort order "asc" or "desc" (default: "desc")

### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "users": [
      {
        "id": "usr_1a2b3c4d5e",
        "email": "john.doe@example.com",
        "name": "John Doe",
        "role": "user",
        "status": "active",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=John",
        "createdAt": "2025-01-15T10:30:00Z",
        "lastLogin": "2025-10-20T08:15:00Z",
        "stats": {
          "totalDocuments": 15,
          "totalChats": 42,
          "storageUsed": 15728640,
          "lastActivity": "2025-10-20T10:45:00Z"
        }
      },
      {
        "id": "usr_2b3c4d5e6f",
        "email": "jane.smith@example.com",
        "name": "Jane Smith",
        "role": "admin",
        "status": "active",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Jane",
        "createdAt": "2024-12-01T09:00:00Z",
        "lastLogin": "2025-10-20T09:30:00Z",
        "stats": {
          "totalDocuments": 8,
          "totalChats": 23,
          "storageUsed": 8388608,
          "lastActivity": "2025-10-20T09:45:00Z"
        }
      },
      {
        "id": "usr_3c4d5e6f7g",
        "email": "bob.wilson@example.com",
        "name": "Bob Wilson",
        "role": "user",
        "status": "inactive",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Bob",
        "createdAt": "2025-03-10T14:20:00Z",
        "lastLogin": "2025-09-15T16:45:00Z",
        "stats": {
          "totalDocuments": 3,
          "totalChats": 7,
          "storageUsed": 2097152,
          "lastActivity": "2025-09-15T17:00:00Z"
        }
      }
    ],
    "pagination": {
      "currentPage": 1,
      "totalPages": 5,
      "totalItems": 87,
      "itemsPerPage": 20
    },
    "summary": {
      "totalUsers": 87,
      "activeUsers": 78,
      "inactiveUsers": 9,
      "adminUsers": 5,
      "regularUsers": 82
    }
  }
}
```

---

## 2. GET /api/admin/users/:id
Get specific user details.

### Request Headers
```
Authorization: Bearer <accessToken>
X-Admin-Role: required
```

### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "usr_1a2b3c4d5e",
      "email": "john.doe@example.com",
      "name": "John Doe",
      "role": "user",
      "status": "active",
      "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=John",
      "createdAt": "2025-01-15T10:30:00Z",
      "updatedAt": "2025-10-20T08:15:00Z",
      "lastLogin": "2025-10-20T08:15:00Z",
      "preferences": {
        "theme": "light",
        "language": "en",
        "notifications": true,
        "emailDigest": "weekly"
      },
      "stats": {
        "totalDocuments": 15,
        "totalChats": 42,
        "totalComparisons": 8,
        "totalSummaries": 12,
        "storageUsed": 15728640,
        "storageLimit": 1073741824,
        "lastActivity": "2025-10-20T10:45:00Z"
      },
      "activity": {
        "documentsThisMonth": 5,
        "chatsThisMonth": 18,
        "averageSessionDuration": "45 minutes",
        "mostActiveDay": "Monday",
        "mostUsedFeature": "chat"
      }
    }
  }
}
```

---

## 3. PUT /api/admin/users/:id
Update user details.

### Request Headers
```
Authorization: Bearer <accessToken>
X-Admin-Role: required
Content-Type: application/json
```

### Request Body
```json
{
  "name": "John Doe Updated",
  "email": "john.updated@example.com",
  "role": "admin",
  "status": "active",
  "storageLimit": 2147483648
}
```

### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "usr_1a2b3c4d5e",
      "email": "john.updated@example.com",
      "name": "John Doe Updated",
      "role": "admin",
      "status": "active",
      "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=John",
      "createdAt": "2025-01-15T10:30:00Z",
      "updatedAt": "2025-10-20T11:30:00Z",
      "lastLogin": "2025-10-20T08:15:00Z",
      "stats": {
        "storageLimit": 2147483648
      }
    }
  }
}
```

---

## 4. DELETE /api/admin/users/:id
Delete a user.

### Request Headers
```
Authorization: Bearer <accessToken>
X-Admin-Role: required
```

### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "message": "User deleted successfully",
    "userId": "usr_1a2b3c4d5e",
    "deletedResources": {
      "documents": 15,
      "chats": 42,
      "comparisons": 8,
      "summaries": 12
    }
  }
}
```

### Error Response (400 Bad Request)
```json
{
  "success": false,
  "error": {
    "code": "CANNOT_DELETE_SELF",
    "message": "You cannot delete your own account"
  }
}
```

---

## 5. GET /api/admin/analytics
Get analytics data.

### Request Headers
```
Authorization: Bearer <accessToken>
X-Admin-Role: required
```

### Query Parameters
- `period` (optional): "today", "week", "month", "year", "all" (default: "month")
- `startDate` (optional): Custom start date (ISO 8601)
- `endDate` (optional): Custom end date (ISO 8601)

### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "analytics": {
      "period": "month",
      "startDate": "2025-09-20T00:00:00Z",
      "endDate": "2025-10-20T23:59:59Z",
      "users": {
        "total": 87,
        "active": 78,
        "new": 12,
        "growth": 15.9,
        "churnRate": 3.4
      },
      "documents": {
        "total": 1247,
        "uploaded": 156,
        "averageSize": 2097152,
        "totalStorage": 2617245696,
        "byType": {
          "pdf": 678,
          "docx": 342,
          "xlsx": 156,
          "txt": 71
        }
      },
      "chats": {
        "total": 3842,
        "thisMonth": 487,
        "averagePerDocument": 3.1,
        "mostActiveHour": 14,
        "averageResponseTime": 1.8
      },
      "comparisons": {
        "total": 234,
        "thisMonth": 28,
        "averageSimilarityScore": 0.78
      },
      "summaries": {
        "total": 892,
        "thisMonth": 103,
        "byStyle": {
          "executive": 456,
          "technical": 234,
          "simple": 145,
          "bullet-points": 57
        }
      },
      "performance": {
        "averageUploadTime": 2.3,
        "averageProcessingTime": 12.5,
        "averageChatResponseTime": 1.8,
        "systemUptime": 99.87
      },
      "engagement": {
        "dailyActiveUsers": 45,
        "weeklyActiveUsers": 67,
        "monthlyActiveUsers": 78,
        "averageSessionDuration": "42 minutes",
        "averageActionsPerSession": 8.5
      },
      "topUsers": [
        {
          "userId": "usr_1a2b3c4d5e",
          "name": "John Doe",
          "totalDocuments": 45,
          "totalChats": 128,
          "activityScore": 95.5
        },
        {
          "userId": "usr_2b3c4d5e6f",
          "name": "Jane Smith",
          "totalDocuments": 38,
          "totalChats": 112,
          "activityScore": 88.2
        }
      ],
      "systemHealth": {
        "status": "healthy",
        "apiResponseTime": 145,
        "databaseResponseTime": 23,
        "storageUsage": 67.5,
        "cpuUsage": 34.2,
        "memoryUsage": 56.8
      }
    }
  }
}
```

---

## 6. GET /api/admin/documents
Get all documents in the system.

### Request Headers
```
Authorization: Bearer <accessToken>
X-Admin-Role: required
```

### Query Parameters
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)
- `userId` (optional): Filter by user
- `status` (optional): Filter by status
- `search` (optional): Search term

### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "documents": [
      {
        "id": "doc_1a2b3c4d5e",
        "name": "Project Proposal.pdf",
        "size": 2048576,
        "mimeType": "application/pdf",
        "userId": "usr_1a2b3c4d5e",
        "userName": "John Doe",
        "status": "processed",
        "uploadedAt": "2025-10-15T14:30:00Z",
        "tags": ["proposal", "client", "2025"]
      },
      {
        "id": "doc_2b3c4d5e6f",
        "name": "Meeting Notes.docx",
        "size": 524288,
        "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "userId": "usr_2b3c4d5e6f",
        "userName": "Jane Smith",
        "status": "processed",
        "uploadedAt": "2025-10-18T09:15:00Z",
        "tags": ["meeting", "notes"]
      }
    ],
    "pagination": {
      "currentPage": 1,
      "totalPages": 63,
      "totalItems": 1247,
      "itemsPerPage": 20
    },
    "summary": {
      "totalDocuments": 1247,
      "totalSize": 2617245696,
      "processingQueue": 3,
      "failedProcessing": 2
    }
  }
}
```

---

## 7. GET /api/admin/activity
Get recent system activity.

### Request Headers
```
Authorization: Bearer <accessToken>
X-Admin-Role: required
```

### Query Parameters
- `limit` (optional): Number of activities (default: 50)
- `type` (optional): Filter by activity type

### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "activities": [
      {
        "id": "act_1a2b3c4d5e",
        "type": "document_upload",
        "userId": "usr_1a2b3c4d5e",
        "userName": "John Doe",
        "description": "Uploaded document 'Budget Report.xlsx'",
        "timestamp": "2025-10-20T11:30:00Z",
        "metadata": {
          "documentId": "doc_3c4d5e6f7g",
          "documentName": "Budget Report.xlsx",
          "size": 1048576
        }
      },
      {
        "id": "act_2b3c4d5e6f",
        "type": "user_login",
        "userId": "usr_2b3c4d5e6f",
        "userName": "Jane Smith",
        "description": "User logged in",
        "timestamp": "2025-10-20T11:25:00Z",
        "metadata": {
          "ipAddress": "192.168.1.1",
          "userAgent": "Mozilla/5.0..."
        }
      },
      {
        "id": "act_3c4d5e6f7g",
        "type": "chat_query",
        "userId": "usr_1a2b3c4d5e",
        "userName": "John Doe",
        "description": "Chat query on document 'Project Proposal.pdf'",
        "timestamp": "2025-10-20T11:20:00Z",
        "metadata": {
          "documentId": "doc_1a2b3c4d5e",
          "query": "What are the main objectives?"
        }
      },
      {
        "id": "act_4d5e6f7g8h",
        "type": "user_registered",
        "userId": "usr_5e6f7g8h9i",
        "userName": "Alice Johnson",
        "description": "New user registered",
        "timestamp": "2025-10-20T11:15:00Z",
        "metadata": {
          "email": "alice@example.com",
          "role": "user"
        }
      }
    ],
    "pagination": {
      "total": 5428,
      "showing": 50
    }
  }
}
```

---

## 8. POST /api/admin/broadcast
Send broadcast message to users.

### Request Headers
```
Authorization: Bearer <accessToken>
X-Admin-Role: required
Content-Type: application/json
```

### Request Body
```json
{
  "title": "System Maintenance Notice",
  "message": "Scheduled maintenance will occur on Oct 25, 2025 from 2-4 AM UTC.",
  "recipients": "all", // "all", "active", "inactive", or array of user IDs
  "type": "info", // "info", "warning", "alert"
  "expiresAt": "2025-10-25T04:00:00Z"
}
```

### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "broadcastId": "brd_1a2b3c4d5e",
    "recipientCount": 87,
    "sentAt": "2025-10-20T11:35:00Z",
    "expiresAt": "2025-10-25T04:00:00Z"
  }
}
```

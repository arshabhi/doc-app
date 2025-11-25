# Document Management API Documentation

This document outlines all the backend APIs needed for the document management application.

## Base URL
```
http://localhost:3000/api
```

## Authentication
Most endpoints require JWT token authentication. Include the token in the Authorization header:
```
Authorization: Bearer <token>
```

## API Endpoints Overview

### Authentication APIs
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user profile
- `POST /api/auth/refresh` - Refresh access token

### Document Management APIs
- `GET /api/documents` - Get all documents for current user
- `POST /api/documents/upload` - Upload a new document
- `GET /api/documents/:id` - Get specific document details
- `DELETE /api/documents/:id` - Delete a document
- `PUT /api/documents/:id` - Update document metadata
- `GET /api/documents/:id/download` - Download a document

### AI Chat APIs
- `POST /api/chat/query` - Send a chat query about a document
- `GET /api/chat/history/:documentId` - Get chat history for a document
- `DELETE /api/chat/history/:documentId` - Clear chat history for a document

### Document Comparison APIs
- `POST /api/compare` - Compare two documents
- `GET /api/compare/:id` - Get comparison results

### Summarization APIs
- `POST /api/summarize` - Generate document summary
- `GET /api/summarize/:documentId` - Get existing summary

### Admin/User Management APIs (Admin Only)
- `GET /api/admin/users` - Get all users
- `GET /api/admin/users/:id` - Get specific user details
- `PUT /api/admin/users/:id` - Update user details
- `DELETE /api/admin/users/:id` - Delete a user
- `GET /api/admin/analytics` - Get analytics data
- `GET /api/admin/documents` - Get all documents in system

## Error Response Format
All errors follow this format:
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message"
  }
}
```

## Common HTTP Status Codes
- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

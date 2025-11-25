# Document Management API Endpoints

## 1. GET /api/documents
Get all documents for the current user.

### Request Headers
```
Authorization: Bearer <accessToken>
```

### Query Parameters
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)
- `sort` (optional): Sort field (default: "createdAt")
- `order` (optional): Sort order "asc" or "desc" (default: "desc")
- `search` (optional): Search term for document name/content

### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "documents": [
      {
        "id": "doc_1a2b3c4d5e",
        "name": "Project Proposal.pdf",
        "originalName": "Project Proposal.pdf",
        "size": 2048576,
        "mimeType": "application/pdf",
        "url": "https://storage.example.com/documents/doc_1a2b3c4d5e.pdf",
        "thumbnailUrl": "https://storage.example.com/thumbnails/doc_1a2b3c4d5e.jpg",
        "userId": "usr_1a2b3c4d5e",
        "status": "processed",
        "pageCount": 15,
        "wordCount": 3500,
        "uploadedAt": "2025-10-15T14:30:00Z",
        "processedAt": "2025-10-15T14:31:22Z",
        "tags": ["proposal", "client", "2025"],
        "metadata": {
          "author": "John Doe",
          "createdDate": "2025-10-14T10:00:00Z",
          "modifiedDate": "2025-10-15T09:30:00Z"
        }
      },
      {
        "id": "doc_2b3c4d5e6f",
        "name": "Meeting Notes.docx",
        "originalName": "Meeting Notes - Oct 2025.docx",
        "size": 524288,
        "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "url": "https://storage.example.com/documents/doc_2b3c4d5e6f.docx",
        "thumbnailUrl": "https://storage.example.com/thumbnails/doc_2b3c4d5e6f.jpg",
        "userId": "usr_1a2b3c4d5e",
        "status": "processed",
        "pageCount": 5,
        "wordCount": 1200,
        "uploadedAt": "2025-10-18T09:15:00Z",
        "processedAt": "2025-10-18T09:15:45Z",
        "tags": ["meeting", "notes"],
        "metadata": {
          "author": "John Doe",
          "createdDate": "2025-10-18T08:00:00Z",
          "modifiedDate": "2025-10-18T09:00:00Z"
        }
      }
    ],
    "pagination": {
      "currentPage": 1,
      "totalPages": 3,
      "totalItems": 15,
      "itemsPerPage": 20,
      "hasNextPage": true,
      "hasPrevPage": false
    }
  }
}
```

---

## 2. POST /api/documents/upload
Upload a new document.

### Request Headers
```
Authorization: Bearer <accessToken>
Content-Type: multipart/form-data
```

### Request Body (FormData)
```
file: <binary file data>
tags: ["proposal", "client"] (optional)
metadata: {"category": "business"} (optional)
```

### Success Response (201 Created)
```json
{
  "success": true,
  "data": {
    "document": {
      "id": "doc_3c4d5e6f7g",
      "name": "Budget Report.xlsx",
      "originalName": "Q3 Budget Report 2025.xlsx",
      "size": 1048576,
      "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      "url": "https://storage.example.com/documents/doc_3c4d5e6f7g.xlsx",
      "thumbnailUrl": null,
      "userId": "usr_1a2b3c4d5e",
      "status": "processing",
      "uploadedAt": "2025-10-20T10:30:00Z",
      "tags": ["proposal", "client"],
      "metadata": {
        "category": "business"
      }
    }
  }
}
```

### Error Response (400 Bad Request)
```json
{
  "success": false,
  "error": {
    "code": "INVALID_FILE_TYPE",
    "message": "File type not supported. Supported types: PDF, DOCX, XLSX, TXT"
  }
}
```

### Error Response (413 Payload Too Large)
```json
{
  "success": false,
  "error": {
    "code": "FILE_TOO_LARGE",
    "message": "File size exceeds maximum limit of 10MB"
  }
}
```

---

## 3. GET /api/documents/:id
Get specific document details.

### Request Headers
```
Authorization: Bearer <accessToken>
```

### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "document": {
      "id": "doc_1a2b3c4d5e",
      "name": "Project Proposal.pdf",
      "originalName": "Project Proposal.pdf",
      "size": 2048576,
      "mimeType": "application/pdf",
      "url": "https://storage.example.com/documents/doc_1a2b3c4d5e.pdf",
      "thumbnailUrl": "https://storage.example.com/thumbnails/doc_1a2b3c4d5e.jpg",
      "userId": "usr_1a2b3c4d5e",
      "status": "processed",
      "pageCount": 15,
      "wordCount": 3500,
      "uploadedAt": "2025-10-15T14:30:00Z",
      "processedAt": "2025-10-15T14:31:22Z",
      "tags": ["proposal", "client", "2025"],
      "metadata": {
        "author": "John Doe",
        "createdDate": "2025-10-14T10:00:00Z",
        "modifiedDate": "2025-10-15T09:30:00Z"
      },
      "extractedText": "This is a sample extracted text from the document...",
      "summary": "A comprehensive project proposal outlining objectives, timeline, and budget...",
      "entities": [
        {"type": "person", "value": "John Smith", "confidence": 0.95},
        {"type": "organization", "value": "Acme Corp", "confidence": 0.92},
        {"type": "date", "value": "2025-11-01", "confidence": 0.98}
      ]
    }
  }
}
```

---

## 4. PUT /api/documents/:id
Update document metadata.

### Request Headers
```
Authorization: Bearer <accessToken>
Content-Type: application/json
```

### Request Body
```json
{
  "name": "Updated Project Proposal.pdf",
  "tags": ["proposal", "client", "2025", "approved"],
  "metadata": {
    "author": "John Doe",
    "category": "business",
    "priority": "high"
  }
}
```

### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "document": {
      "id": "doc_1a2b3c4d5e",
      "name": "Updated Project Proposal.pdf",
      "originalName": "Project Proposal.pdf",
      "size": 2048576,
      "mimeType": "application/pdf",
      "url": "https://storage.example.com/documents/doc_1a2b3c4d5e.pdf",
      "thumbnailUrl": "https://storage.example.com/thumbnails/doc_1a2b3c4d5e.jpg",
      "userId": "usr_1a2b3c4d5e",
      "status": "processed",
      "pageCount": 15,
      "wordCount": 3500,
      "uploadedAt": "2025-10-15T14:30:00Z",
      "processedAt": "2025-10-15T14:31:22Z",
      "updatedAt": "2025-10-20T11:00:00Z",
      "tags": ["proposal", "client", "2025", "approved"],
      "metadata": {
        "author": "John Doe",
        "category": "business",
        "priority": "high"
      }
    }
  }
}
```

---

## 5. DELETE /api/documents/:id
Delete a document.

### Request Headers
```
Authorization: Bearer <accessToken>
```

### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "message": "Document deleted successfully",
    "documentId": "doc_1a2b3c4d5e"
  }
}
```

### Error Response (404 Not Found)
```json
{
  "success": false,
  "error": {
    "code": "DOCUMENT_NOT_FOUND",
    "message": "Document not found or you don't have permission to delete it"
  }
}
```

---

## 6. GET /api/documents/:id/download
Download a document.

### Request Headers
```
Authorization: Bearer <accessToken>
```

### Success Response (200 OK)
Returns the file as binary data with appropriate headers:
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="Project Proposal.pdf"
Content-Length: 2048576
```

### Error Response (404 Not Found)
```json
{
  "success": false,
  "error": {
    "code": "DOCUMENT_NOT_FOUND",
    "message": "Document not found or you don't have permission to access it"
  }
}
```

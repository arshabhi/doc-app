# AI Chat API Endpoints

## 1. POST /api/chat/query
Send a chat query about a document.

### Request Headers
```
Authorization: Bearer <accessToken>
Content-Type: application/json
```

### Request Body
```json
{
  "documentId": "doc_1a2b3c4d5e",
  "query": "What are the main objectives outlined in this proposal?",
  "conversationId": "conv_1a2b3c4d5e" // optional, for continuing conversation
}
```

### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "response": {
      "id": "msg_1a2b3c4d5e",
      "conversationId": "conv_1a2b3c4d5e",
      "documentId": "doc_1a2b3c4d5e",
      "query": "What are the main objectives outlined in this proposal?",
      "answer": "Based on the document, the main objectives are:\n\n1. Develop a comprehensive marketing strategy for Q4 2025\n2. Increase brand awareness by 30% through digital channels\n3. Launch three new product lines by end of year\n4. Expand market reach to two new geographic regions\n5. Achieve a 25% increase in customer engagement metrics\n\nThese objectives are detailed on pages 3-5 of the proposal.",
      "confidence": 0.92,
      "sources": [
        {
          "pageNumber": 3,
          "excerpt": "Our primary objective is to develop a comprehensive marketing strategy...",
          "relevance": 0.95
        },
        {
          "pageNumber": 4,
          "excerpt": "We aim to increase brand awareness by 30%...",
          "relevance": 0.89
        },
        {
          "pageNumber": 5,
          "excerpt": "The launch of three new product lines...",
          "relevance": 0.87
        }
      ],
      "timestamp": "2025-10-20T10:45:00Z",
      "metadata": {
        "model": "gpt-4",
        "tokens": 256,
        "processingTime": 1.2
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
    "code": "EMPTY_QUERY",
    "message": "Query cannot be empty"
  }
}
```

### Error Response (404 Not Found)
```json
{
  "success": false,
  "error": {
    "code": "DOCUMENT_NOT_FOUND",
    "message": "Document not found or not accessible"
  }
}
```

---

## 2. GET /api/chat/history/:documentId
Get chat history for a specific document.

### Request Headers
```
Authorization: Bearer <accessToken>
```

### Query Parameters
- `conversationId` (optional): Filter by specific conversation
- `limit` (optional): Number of messages to return (default: 50)
- `before` (optional): Get messages before this timestamp

### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "history": [
      {
        "id": "msg_1a2b3c4d5e",
        "conversationId": "conv_1a2b3c4d5e",
        "documentId": "doc_1a2b3c4d5e",
        "type": "user",
        "content": "What are the main objectives outlined in this proposal?",
        "timestamp": "2025-10-20T10:45:00Z"
      },
      {
        "id": "msg_2b3c4d5e6f",
        "conversationId": "conv_1a2b3c4d5e",
        "documentId": "doc_1a2b3c4d5e",
        "type": "assistant",
        "content": "Based on the document, the main objectives are:\n\n1. Develop a comprehensive marketing strategy for Q4 2025\n2. Increase brand awareness by 30% through digital channels...",
        "confidence": 0.92,
        "sources": [
          {
            "pageNumber": 3,
            "excerpt": "Our primary objective is to develop a comprehensive marketing strategy...",
            "relevance": 0.95
          }
        ],
        "timestamp": "2025-10-20T10:45:02Z"
      },
      {
        "id": "msg_3c4d5e6f7g",
        "conversationId": "conv_1a2b3c4d5e",
        "documentId": "doc_1a2b3c4d5e",
        "type": "user",
        "content": "What is the proposed budget for this project?",
        "timestamp": "2025-10-20T10:46:30Z"
      },
      {
        "id": "msg_4d5e6f7g8h",
        "conversationId": "conv_1a2b3c4d5e",
        "documentId": "doc_1a2b3c4d5e",
        "type": "assistant",
        "content": "According to page 12 of the proposal, the total proposed budget is $450,000, broken down as follows:\n\n- Marketing & Advertising: $200,000\n- Product Development: $150,000\n- Operations: $75,000\n- Contingency: $25,000",
        "confidence": 0.96,
        "sources": [
          {
            "pageNumber": 12,
            "excerpt": "Total Budget: $450,000",
            "relevance": 0.98
          }
        ],
        "timestamp": "2025-10-20T10:46:33Z"
      }
    ],
    "metadata": {
      "totalMessages": 8,
      "conversationStarted": "2025-10-20T10:45:00Z",
      "lastActivity": "2025-10-20T10:46:33Z"
    }
  }
}
```

---

## 3. DELETE /api/chat/history/:documentId
Clear chat history for a document.

### Request Headers
```
Authorization: Bearer <accessToken>
```

### Query Parameters
- `conversationId` (optional): Delete specific conversation only

### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "message": "Chat history cleared successfully",
    "deletedMessages": 8,
    "documentId": "doc_1a2b3c4d5e"
  }
}
```

---

## 4. GET /api/chat/conversations
Get all conversations for the current user.

### Request Headers
```
Authorization: Bearer <accessToken>
```

### Query Parameters
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)

### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "conversations": [
      {
        "id": "conv_1a2b3c4d5e",
        "documentId": "doc_1a2b3c4d5e",
        "documentName": "Project Proposal.pdf",
        "messageCount": 8,
        "startedAt": "2025-10-20T10:45:00Z",
        "lastActivity": "2025-10-20T10:46:33Z",
        "preview": {
          "lastMessage": "According to page 12 of the proposal, the total proposed budget is $450,000...",
          "lastQuery": "What is the proposed budget for this project?"
        }
      },
      {
        "id": "conv_2b3c4d5e6f",
        "documentId": "doc_2b3c4d5e6f",
        "documentName": "Meeting Notes.docx",
        "messageCount": 4,
        "startedAt": "2025-10-19T14:20:00Z",
        "lastActivity": "2025-10-19T14:25:15Z",
        "preview": {
          "lastMessage": "The key action items from the meeting are...",
          "lastQuery": "What are the action items from this meeting?"
        }
      }
    ],
    "pagination": {
      "currentPage": 1,
      "totalPages": 1,
      "totalItems": 2
    }
  }
}
```

---

## 5. POST /api/chat/feedback
Submit feedback on a chat response.

### Request Headers
```
Authorization: Bearer <accessToken>
Content-Type: application/json
```

### Request Body
```json
{
  "messageId": "msg_2b3c4d5e6f",
  "rating": "positive", // "positive" or "negative"
  "comment": "Very accurate and helpful response" // optional
}
```

### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "message": "Feedback submitted successfully",
    "feedbackId": "fb_1a2b3c4d5e"
  }
}
```

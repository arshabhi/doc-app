# Document Comparison API Endpoints

## 1. POST /api/compare
Compare two documents.

### Request Headers
```
Authorization: Bearer <accessToken>
Content-Type: application/json
```

### Request Body
```json
{
  "documentId1": "doc_1a2b3c4d5e",
  "documentId2": "doc_2b3c4d5e6f",
  "comparisonType": "full", // "full", "structure", "content", or "metadata"
  "options": {
    "ignoreFormatting": true,
    "caseSensitive": false,
    "highlightChanges": true
  }
}
```

### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "comparison": {
      "id": "cmp_1a2b3c4d5e",
      "documentId1": "doc_1a2b3c4d5e",
      "documentId2": "doc_2b3c4d5e6f",
      "document1Name": "Project Proposal v1.pdf",
      "document2Name": "Project Proposal v2.pdf",
      "comparisonType": "full",
      "status": "completed",
      "createdAt": "2025-10-20T11:00:00Z",
      "completedAt": "2025-10-20T11:00:15Z",
      "summary": {
        "totalChanges": 47,
        "additions": 23,
        "deletions": 12,
        "modifications": 12,
        "similarityScore": 0.87,
        "changesPercentage": 13.2
      },
      "changes": [
        {
          "id": "chg_1",
          "type": "addition",
          "location": {
            "document": 2,
            "page": 3,
            "section": "Budget Overview",
            "lineNumber": 45
          },
          "content": "Additional budget allocation of $50,000 for marketing initiatives",
          "context": {
            "before": "Total Marketing Budget: $200,000",
            "after": "Total Marketing Budget: $250,000\nAdditional budget allocation of $50,000 for marketing initiatives"
          },
          "severity": "major",
          "category": "financial"
        },
        {
          "id": "chg_2",
          "type": "modification",
          "location": {
            "document": 2,
            "page": 5,
            "section": "Timeline",
            "lineNumber": 78
          },
          "content": {
            "original": "Project completion: December 31, 2025",
            "modified": "Project completion: January 15, 2026"
          },
          "context": {
            "before": "Project completion: December 31, 2025",
            "after": "Project completion: January 15, 2026"
          },
          "severity": "major",
          "category": "timeline"
        },
        {
          "id": "chg_3",
          "type": "deletion",
          "location": {
            "document": 1,
            "page": 7,
            "section": "Risk Assessment",
            "lineNumber": 124
          },
          "content": "Minor risk: Potential delay in third-party vendor delivery",
          "context": {
            "before": "Minor risk: Potential delay in third-party vendor delivery\nMitigation: Establish backup vendors",
            "after": "Mitigation: Establish backup vendors"
          },
          "severity": "minor",
          "category": "content"
        }
      ],
      "categoryBreakdown": {
        "financial": 8,
        "timeline": 5,
        "content": 28,
        "structure": 6
      },
      "diffUrl": "https://storage.example.com/comparisons/cmp_1a2b3c4d5e_diff.pdf",
      "sideBySideUrl": "https://storage.example.com/comparisons/cmp_1a2b3c4d5e_sidebyside.pdf"
    }
  }
}
```

### Success Response (202 Accepted) - For large documents
```json
{
  "success": true,
  "data": {
    "comparison": {
      "id": "cmp_1a2b3c4d5e",
      "documentId1": "doc_1a2b3c4d5e",
      "documentId2": "doc_2b3c4d5e6f",
      "status": "processing",
      "createdAt": "2025-10-20T11:00:00Z",
      "estimatedCompletionTime": "2025-10-20T11:02:00Z",
      "message": "Comparison is being processed. Use the comparison ID to check status."
    }
  }
}
```

### Error Response (400 Bad Request)
```json
{
  "success": false,
  "error": {
    "code": "INCOMPATIBLE_DOCUMENTS",
    "message": "Documents must be of the same type for comparison"
  }
}
```

---

## 2. GET /api/compare/:id
Get comparison results.

### Request Headers
```
Authorization: Bearer <accessToken>
```

### Query Parameters
- `includeDetails` (optional): Include full change details (default: true)
- `format` (optional): "json" or "summary" (default: "json")

### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "comparison": {
      "id": "cmp_1a2b3c4d5e",
      "documentId1": "doc_1a2b3c4d5e",
      "documentId2": "doc_2b3c4d5e6f",
      "document1Name": "Project Proposal v1.pdf",
      "document2Name": "Project Proposal v2.pdf",
      "comparisonType": "full",
      "status": "completed",
      "createdAt": "2025-10-20T11:00:00Z",
      "completedAt": "2025-10-20T11:00:15Z",
      "summary": {
        "totalChanges": 47,
        "additions": 23,
        "deletions": 12,
        "modifications": 12,
        "similarityScore": 0.87,
        "changesPercentage": 13.2
      },
      "changes": [
        {
          "id": "chg_1",
          "type": "addition",
          "location": {
            "document": 2,
            "page": 3,
            "section": "Budget Overview",
            "lineNumber": 45
          },
          "content": "Additional budget allocation of $50,000 for marketing initiatives",
          "severity": "major",
          "category": "financial"
        }
      ],
      "categoryBreakdown": {
        "financial": 8,
        "timeline": 5,
        "content": 28,
        "structure": 6
      },
      "diffUrl": "https://storage.example.com/comparisons/cmp_1a2b3c4d5e_diff.pdf",
      "sideBySideUrl": "https://storage.example.com/comparisons/cmp_1a2b3c4d5e_sidebyside.pdf"
    }
  }
}
```

### Success Response (202 Accepted) - Still processing
```json
{
  "success": true,
  "data": {
    "comparison": {
      "id": "cmp_1a2b3c4d5e",
      "status": "processing",
      "progress": 67,
      "message": "Analyzing document differences...",
      "estimatedCompletionTime": "2025-10-20T11:02:00Z"
    }
  }
}
```

---

## 3. GET /api/compare/history
Get comparison history for the current user.

### Request Headers
```
Authorization: Bearer <accessToken>
```

### Query Parameters
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)
- `documentId` (optional): Filter by specific document

### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "comparisons": [
      {
        "id": "cmp_1a2b3c4d5e",
        "document1Name": "Project Proposal v1.pdf",
        "document2Name": "Project Proposal v2.pdf",
        "status": "completed",
        "createdAt": "2025-10-20T11:00:00Z",
        "summary": {
          "totalChanges": 47,
          "similarityScore": 0.87
        }
      },
      {
        "id": "cmp_2b3c4d5e6f",
        "document1Name": "Contract Draft 1.docx",
        "document2Name": "Contract Draft 2.docx",
        "status": "completed",
        "createdAt": "2025-10-18T14:30:00Z",
        "summary": {
          "totalChanges": 15,
          "similarityScore": 0.95
        }
      }
    ],
    "pagination": {
      "currentPage": 1,
      "totalPages": 2,
      "totalItems": 8
    }
  }
}
```

---

## 4. DELETE /api/compare/:id
Delete a comparison result.

### Request Headers
```
Authorization: Bearer <accessToken>
```

### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "message": "Comparison deleted successfully",
    "comparisonId": "cmp_1a2b3c4d5e"
  }
}
```

---

## 5. POST /api/compare/batch
Compare multiple documents in batch.

### Request Headers
```
Authorization: Bearer <accessToken>
Content-Type: application/json
```

### Request Body
```json
{
  "comparisons": [
    {
      "documentId1": "doc_1a2b3c4d5e",
      "documentId2": "doc_2b3c4d5e6f",
      "comparisonType": "full"
    },
    {
      "documentId1": "doc_3c4d5e6f7g",
      "documentId2": "doc_4d5e6f7g8h",
      "comparisonType": "content"
    }
  ]
}
```

### Success Response (202 Accepted)
```json
{
  "success": true,
  "data": {
    "batchId": "batch_1a2b3c4d5e",
    "comparisons": [
      {
        "id": "cmp_1a2b3c4d5e",
        "status": "queued"
      },
      {
        "id": "cmp_2b3c4d5e6f",
        "status": "queued"
      }
    ],
    "message": "Batch comparison initiated. Check status for updates."
  }
}
```

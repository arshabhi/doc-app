# Document Summarization API Endpoints

## 1. POST /api/summarize
Generate a document summary.

### Request Headers
```
Authorization: Bearer <accessToken>
Content-Type: application/json
```

### Request Body
```json
{
  "documentId": "doc_1a2b3c4d5e",
  "options": {
    "length": "medium", // "short" (1-2 paragraphs), "medium" (3-5 paragraphs), "long" (6+ paragraphs)
    "style": "executive", // "executive", "technical", "simple", "bullet-points"
    "focusAreas": ["objectives", "timeline", "budget"], // optional
    "language": "en" // optional, default: "en"
  }
}
```

### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "summary": {
      "id": "sum_1a2b3c4d5e",
      "documentId": "doc_1a2b3c4d5e",
      "documentName": "Project Proposal.pdf",
      "style": "executive",
      "length": "medium",
      "content": "This project proposal outlines a comprehensive marketing strategy for Q4 2025 with a total budget of $450,000. The primary objectives include developing a robust marketing framework, increasing brand awareness by 30% through digital channels, and launching three new product lines by year-end.\n\nThe proposal details a phased approach spanning October through December 2025, with key milestones including market research completion by October 31, campaign launch by November 15, and final evaluation by December 31. The budget allocation prioritizes marketing and advertising ($200,000), product development ($150,000), and operational expenses ($75,000), with a $25,000 contingency fund.\n\nKey success metrics include a 30% increase in brand awareness, 25% improvement in customer engagement, and successful market expansion into two new geographic regions. The proposal identifies potential risks and mitigation strategies, ensuring project viability and alignment with organizational goals.",
      "keyPoints": [
        "Total project budget: $450,000",
        "Target: 30% increase in brand awareness",
        "Timeline: October - December 2025",
        "Launch of three new product lines",
        "Expansion to two new geographic regions",
        "Phased implementation approach"
      ],
      "wordCount": 156,
      "readingTime": "45 seconds",
      "confidence": 0.94,
      "createdAt": "2025-10-20T11:15:00Z",
      "metadata": {
        "model": "gpt-4",
        "processingTime": 3.5,
        "sourcePages": [1, 2, 3, 4, 5, 12, 15]
      }
    }
  }
}
```

### Success Response (202 Accepted) - For large documents
```json
{
  "success": true,
  "data": {
    "summary": {
      "id": "sum_1a2b3c4d5e",
      "documentId": "doc_1a2b3c4d5e",
      "status": "processing",
      "createdAt": "2025-10-20T11:15:00Z",
      "estimatedCompletionTime": "2025-10-20T11:17:00Z",
      "message": "Summary is being generated. Use the summary ID to check status."
    }
  }
}
```

### Error Response (400 Bad Request)
```json
{
  "success": false,
  "error": {
    "code": "DOCUMENT_NOT_PROCESSED",
    "message": "Document must be fully processed before summarization"
  }
}
```

---

## 2. GET /api/summarize/:documentId
Get existing summary for a document.

### Request Headers
```
Authorization: Bearer <accessToken>
```

### Query Parameters
- `summaryId` (optional): Get specific summary version
- `style` (optional): Filter by summary style

### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "summaries": [
      {
        "id": "sum_1a2b3c4d5e",
        "documentId": "doc_1a2b3c4d5e",
        "documentName": "Project Proposal.pdf",
        "style": "executive",
        "length": "medium",
        "content": "This project proposal outlines a comprehensive marketing strategy for Q4 2025...",
        "keyPoints": [
          "Total project budget: $450,000",
          "Target: 30% increase in brand awareness",
          "Timeline: October - December 2025"
        ],
        "wordCount": 156,
        "readingTime": "45 seconds",
        "confidence": 0.94,
        "createdAt": "2025-10-20T11:15:00Z",
        "isLatest": true
      },
      {
        "id": "sum_2b3c4d5e6f",
        "documentId": "doc_1a2b3c4d5e",
        "documentName": "Project Proposal.pdf",
        "style": "bullet-points",
        "length": "short",
        "content": "• Q4 2025 Marketing Strategy\n• Budget: $450,000\n• Objectives: 30% brand awareness increase, 3 new product launches\n• Timeline: Oct-Dec 2025\n• Target: 2 new geographic regions",
        "keyPoints": [
          "Budget: $450,000",
          "30% brand awareness increase",
          "3 new product launches"
        ],
        "wordCount": 42,
        "readingTime": "15 seconds",
        "confidence": 0.91,
        "createdAt": "2025-10-19T15:30:00Z",
        "isLatest": false
      }
    ]
  }
}
```

### Success Response (404 Not Found)
```json
{
  "success": false,
  "error": {
    "code": "NO_SUMMARIES_FOUND",
    "message": "No summaries found for this document"
  }
}
```

---

## 3. GET /api/summarize/summary/:summaryId
Get specific summary by ID.

### Request Headers
```
Authorization: Bearer <accessToken>
```

### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "summary": {
      "id": "sum_1a2b3c4d5e",
      "documentId": "doc_1a2b3c4d5e",
      "documentName": "Project Proposal.pdf",
      "style": "executive",
      "length": "medium",
      "content": "This project proposal outlines a comprehensive marketing strategy for Q4 2025 with a total budget of $450,000...",
      "keyPoints": [
        "Total project budget: $450,000",
        "Target: 30% increase in brand awareness",
        "Timeline: October - December 2025",
        "Launch of three new product lines",
        "Expansion to two new geographic regions"
      ],
      "wordCount": 156,
      "readingTime": "45 seconds",
      "confidence": 0.94,
      "createdAt": "2025-10-20T11:15:00Z",
      "metadata": {
        "model": "gpt-4",
        "processingTime": 3.5,
        "sourcePages": [1, 2, 3, 4, 5, 12, 15]
      }
    }
  }
}
```

---

## 4. DELETE /api/summarize/:summaryId
Delete a summary.

### Request Headers
```
Authorization: Bearer <accessToken>
```

### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "message": "Summary deleted successfully",
    "summaryId": "sum_1a2b3c4d5e"
  }
}
```

---

## 5. POST /api/summarize/batch
Generate summaries for multiple documents.

### Request Headers
```
Authorization: Bearer <accessToken>
Content-Type: application/json
```

### Request Body
```json
{
  "documentIds": ["doc_1a2b3c4d5e", "doc_2b3c4d5e6f", "doc_3c4d5e6f7g"],
  "options": {
    "length": "medium",
    "style": "executive",
    "language": "en"
  }
}
```

### Success Response (202 Accepted)
```json
{
  "success": true,
  "data": {
    "batchId": "batch_1a2b3c4d5e",
    "summaries": [
      {
        "documentId": "doc_1a2b3c4d5e",
        "status": "queued",
        "estimatedCompletionTime": "2025-10-20T11:17:00Z"
      },
      {
        "documentId": "doc_2b3c4d5e6f",
        "status": "queued",
        "estimatedCompletionTime": "2025-10-20T11:18:00Z"
      },
      {
        "documentId": "doc_3c4d5e6f7g",
        "status": "queued",
        "estimatedCompletionTime": "2025-10-20T11:19:00Z"
      }
    ],
    "message": "Batch summarization initiated. Check individual document summaries for updates."
  }
}
```

---

## 6. POST /api/summarize/custom
Generate custom summary with advanced options.

### Request Headers
```
Authorization: Bearer <accessToken>
Content-Type: application/json
```

### Request Body
```json
{
  "documentId": "doc_1a2b3c4d5e",
  "prompt": "Create a summary focusing on financial aspects and timeline, written for C-level executives",
  "maxLength": 300,
  "includeQuotes": true,
  "extractEntities": true,
  "tone": "professional"
}
```

### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "summary": {
      "id": "sum_3c4d5e6f7g",
      "documentId": "doc_1a2b3c4d5e",
      "documentName": "Project Proposal.pdf",
      "style": "custom",
      "content": "Financial Overview: This proposal requests $450,000 in funding, with strategic allocation across marketing ($200K), product development ($150K), and operations ($75K). As stated in the document, \"This investment represents a 15% increase over our current quarterly budget, justified by projected 30% revenue growth.\"\n\nTimeline: The project spans Q4 2025 (October-December), with critical milestones including market research completion (Oct 31), campaign launch (Nov 15), and full deployment (Dec 31). Early indicators suggest a potential ROI of 250% within the first fiscal year post-implementation.",
      "keyQuotes": [
        "This investment represents a 15% increase over our current quarterly budget",
        "projected 30% revenue growth",
        "potential ROI of 250% within the first fiscal year"
      ],
      "entities": [
        {"type": "money", "value": "$450,000", "context": "total budget"},
        {"type": "percentage", "value": "30%", "context": "revenue growth"},
        {"type": "date", "value": "Q4 2025", "context": "project timeline"}
      ],
      "wordCount": 98,
      "readingTime": "30 seconds",
      "confidence": 0.96,
      "createdAt": "2025-10-20T11:20:00Z"
    }
  }
}
```

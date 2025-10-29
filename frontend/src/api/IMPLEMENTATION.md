# API Implementation Guide

This document provides guidance on implementing the backend APIs for the document management application.

## Technology Stack Recommendations

### Backend Framework
- **Node.js + Express.js**: Fast, scalable, and well-suited for RESTful APIs
- **Python + FastAPI**: Excellent for AI/ML integration, async support
- **Java + Spring Boot**: Enterprise-grade, robust, strongly-typed

### Database
- **PostgreSQL**: Primary relational database for structured data (users, documents, metadata)
- **MongoDB**: Document storage for flexible schemas (chat history, analytics)
- **Redis**: Caching layer for session management and frequently accessed data

### File Storage
- **AWS S3** or **Azure Blob Storage**: Scalable object storage for documents
- **Local storage**: For development/testing

### AI/ML Services
- **OpenAI API**: For chat, summarization, and text analysis
- **Azure AI**: Alternative for document processing
- **Custom ML Models**: For specific document analysis tasks

### Authentication
- **JWT (JSON Web Tokens)**: For stateless authentication
- **OAuth 2.0**: For third-party integrations
- **bcrypt**: For password hashing

### Additional Services
- **RabbitMQ/Apache Kafka**: Message queue for async processing
- **WebSockets**: Real-time updates for chat and processing status
- **Docker**: Containerization for easy deployment
- **Nginx**: Reverse proxy and load balancing

## Directory Structure

```
backend/
├── src/
│   ├── config/
│   │   ├── database.js
│   │   ├── storage.js
│   │   └── ai.js
│   ├── controllers/
│   │   ├── auth.controller.js
│   │   ├── document.controller.js
│   │   ├── chat.controller.js
│   │   ├── compare.controller.js
│   │   ├── summarize.controller.js
│   │   └── admin.controller.js
│   ├── models/
│   │   ├── User.js
│   │   ├── Document.js
│   │   ├── Chat.js
│   │   ├── Comparison.js
│   │   └── Summary.js
│   ├── routes/
│   │   ├── auth.routes.js
│   │   ├── document.routes.js
│   │   ├── chat.routes.js
│   │   ├── compare.routes.js
│   │   ├── summarize.routes.js
│   │   └── admin.routes.js
│   ├── middleware/
│   │   ├── auth.middleware.js
│   │   ├── admin.middleware.js
│   │   ├── upload.middleware.js
│   │   ├── validation.middleware.js
│   │   └── error.middleware.js
│   ├── services/
│   │   ├── auth.service.js
│   │   ├── document.service.js
│   │   ├── ai.service.js
│   │   ├── storage.service.js
│   │   └── email.service.js
│   ├── utils/
│   │   ├── jwt.js
│   │   ├── validators.js
│   │   └── helpers.js
│   └── app.js
├── tests/
│   ├── unit/
│   └── integration/
├── uploads/
├── .env.example
├── package.json
└── README.md
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
  id VARCHAR(36) PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  role ENUM('user', 'admin') DEFAULT 'user',
  status ENUM('active', 'inactive') DEFAULT 'active',
  avatar VARCHAR(500),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  last_login TIMESTAMP,
  preferences JSON,
  storage_used BIGINT DEFAULT 0,
  storage_limit BIGINT DEFAULT 1073741824
);
```

### Documents Table
```sql
CREATE TABLE documents (
  id VARCHAR(36) PRIMARY KEY,
  user_id VARCHAR(36) NOT NULL,
  name VARCHAR(255) NOT NULL,
  original_name VARCHAR(255) NOT NULL,
  size BIGINT NOT NULL,
  mime_type VARCHAR(100) NOT NULL,
  url VARCHAR(500) NOT NULL,
  thumbnail_url VARCHAR(500),
  status ENUM('uploading', 'processing', 'processed', 'failed', 'deleted') DEFAULT 'uploading',
  page_count INT,
  word_count INT,
  uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  processed_at TIMESTAMP,
  tags JSON,
  metadata JSON,
  extracted_text LONGTEXT,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_user_id (user_id),
  INDEX idx_status (status),
  INDEX idx_uploaded_at (uploaded_at)
);
```

### Chat Messages Table
```sql
CREATE TABLE chat_messages (
  id VARCHAR(36) PRIMARY KEY,
  conversation_id VARCHAR(36) NOT NULL,
  document_id VARCHAR(36) NOT NULL,
  user_id VARCHAR(36) NOT NULL,
  type ENUM('user', 'assistant') NOT NULL,
  content TEXT NOT NULL,
  confidence FLOAT,
  sources JSON,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  metadata JSON,
  FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_conversation_id (conversation_id),
  INDEX idx_document_id (document_id),
  INDEX idx_timestamp (timestamp)
);
```

### Comparisons Table
```sql
CREATE TABLE comparisons (
  id VARCHAR(36) PRIMARY KEY,
  user_id VARCHAR(36) NOT NULL,
  document_id1 VARCHAR(36) NOT NULL,
  document_id2 VARCHAR(36) NOT NULL,
  comparison_type ENUM('full', 'structure', 'content', 'metadata') NOT NULL,
  status ENUM('queued', 'processing', 'completed', 'failed') DEFAULT 'queued',
  summary JSON,
  changes JSON,
  diff_url VARCHAR(500),
  side_by_side_url VARCHAR(500),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  completed_at TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (document_id1) REFERENCES documents(id) ON DELETE CASCADE,
  FOREIGN KEY (document_id2) REFERENCES documents(id) ON DELETE CASCADE,
  INDEX idx_user_id (user_id),
  INDEX idx_status (status)
);
```

### Summaries Table
```sql
CREATE TABLE summaries (
  id VARCHAR(36) PRIMARY KEY,
  document_id VARCHAR(36) NOT NULL,
  user_id VARCHAR(36) NOT NULL,
  style ENUM('executive', 'technical', 'simple', 'bullet-points', 'custom') NOT NULL,
  length ENUM('short', 'medium', 'long') NOT NULL,
  content TEXT NOT NULL,
  key_points JSON,
  word_count INT,
  confidence FLOAT,
  is_latest BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  metadata JSON,
  FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_document_id (document_id),
  INDEX idx_user_id (user_id),
  INDEX idx_is_latest (is_latest)
);
```

## Authentication Flow

1. **Registration**
   - Validate email format and password strength
   - Hash password using bcrypt
   - Create user record in database
   - Generate JWT access and refresh tokens
   - Return user data and tokens

2. **Login**
   - Validate credentials
   - Compare password hash
   - Generate new JWT tokens
   - Update last_login timestamp
   - Return user data and tokens

3. **Token Refresh**
   - Validate refresh token
   - Generate new access token
   - Return new access token

4. **Protected Routes**
   - Verify JWT token in Authorization header
   - Extract user information from token
   - Check user permissions (role-based)
   - Proceed with request or return 401/403

## Document Processing Pipeline

1. **Upload**
   - Validate file type and size
   - Generate unique document ID
   - Upload to storage service (S3)
   - Create document record in database
   - Queue for processing

2. **Processing**
   - Extract text content (PDF, DOCX, XLSX)
   - Count pages and words
   - Generate thumbnail
   - Extract metadata (author, dates, etc.)
   - Perform entity extraction (optional)
   - Update document status

3. **Storage**
   - Store original file
   - Store extracted text
   - Store thumbnail
   - Update user storage quota

## AI Integration

### Chat Implementation
```javascript
// Pseudo-code for chat query processing
async function processChatQuery(documentId, query, conversationId) {
  // 1. Retrieve document text
  const document = await getDocument(documentId);
  
  // 2. Get conversation history
  const history = await getChatHistory(conversationId);
  
  // 3. Build context for AI
  const context = buildContext(document.extractedText, history);
  
  // 4. Call AI service (e.g., OpenAI)
  const response = await aiService.chat({
    model: 'gpt-4',
    messages: [
      { role: 'system', content: 'You are a helpful document assistant.' },
      { role: 'user', content: context + '\n\n' + query }
    ]
  });
  
  // 5. Extract sources/references
  const sources = extractSources(response, document);
  
  // 6. Save to database
  await saveChatMessage({
    conversationId,
    documentId,
    query,
    answer: response.content,
    sources,
    confidence: response.confidence
  });
  
  return response;
}
```

### Summarization Implementation
```javascript
// Pseudo-code for document summarization
async function generateSummary(documentId, options) {
  // 1. Retrieve document text
  const document = await getDocument(documentId);
  
  // 2. Build prompt based on style and length
  const prompt = buildSummaryPrompt(
    document.extractedText,
    options.style,
    options.length,
    options.focusAreas
  );
  
  // 3. Call AI service
  const response = await aiService.summarize({
    model: 'gpt-4',
    prompt: prompt,
    maxTokens: getMaxTokens(options.length)
  });
  
  // 4. Extract key points
  const keyPoints = extractKeyPoints(response.content);
  
  // 5. Save summary
  await saveSummary({
    documentId,
    style: options.style,
    length: options.length,
    content: response.content,
    keyPoints,
    confidence: response.confidence
  });
  
  return response;
}
```

### Document Comparison Implementation
```javascript
// Pseudo-code for document comparison
async function compareDocuments(doc1Id, doc2Id, comparisonType) {
  // 1. Retrieve both documents
  const [doc1, doc2] = await Promise.all([
    getDocument(doc1Id),
    getDocument(doc2Id)
  ]);
  
  // 2. Perform diff based on type
  let changes;
  if (comparisonType === 'full') {
    changes = await performFullComparison(doc1, doc2);
  } else if (comparisonType === 'content') {
    changes = await performContentComparison(doc1.extractedText, doc2.extractedText);
  }
  
  // 3. Calculate similarity score
  const similarityScore = calculateSimilarity(changes);
  
  // 4. Categorize changes
  const categorized = categorizeChanges(changes);
  
  // 5. Generate diff documents
  const diffUrl = await generateDiffPdf(doc1, doc2, changes);
  const sideBySideUrl = await generateSideBySide(doc1, doc2);
  
  // 6. Save comparison
  await saveComparison({
    document1Id: doc1Id,
    document2Id: doc2Id,
    summary: {
      totalChanges: changes.length,
      similarityScore,
      ...categorized
    },
    changes,
    diffUrl,
    sideBySideUrl
  });
  
  return comparison;
}
```

## Security Considerations

1. **Input Validation**
   - Validate all user inputs
   - Sanitize file names and content
   - Check file types and sizes
   - Prevent SQL injection and XSS

2. **File Upload Security**
   - Scan files for malware
   - Restrict file types
   - Set maximum file size
   - Use unique file names
   - Store files outside web root

3. **Authentication & Authorization**
   - Use strong password requirements
   - Implement rate limiting
   - Protect against brute force
   - Verify JWT signatures
   - Implement role-based access control

4. **Data Protection**
   - Encrypt sensitive data at rest
   - Use HTTPS for data in transit
   - Secure database connections
   - Regular security audits
   - GDPR compliance for PII

5. **API Security**
   - Implement rate limiting
   - Use API keys for external services
   - CORS configuration
   - Request validation
   - Error handling (don't expose internals)

## Environment Variables

```env
# Server
NODE_ENV=development
PORT=3000
API_BASE_URL=http://localhost:3000

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=docmanagement
DB_USER=postgres
DB_PASSWORD=your_password

# JWT
JWT_SECRET=your_jwt_secret_key
JWT_EXPIRES_IN=1h
REFRESH_TOKEN_SECRET=your_refresh_token_secret
REFRESH_TOKEN_EXPIRES_IN=7d

# Storage (AWS S3)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your_bucket_name

# AI Service (OpenAI)
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# Email (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_email_password

# File Upload
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=pdf,docx,xlsx,txt

# Rate Limiting
RATE_LIMIT_WINDOW=15
RATE_LIMIT_MAX_REQUESTS=100
```

## Deployment Considerations

1. **Docker Setup**
   - Create Dockerfile for backend
   - Use docker-compose for multi-container setup
   - Include database, Redis, and backend services

2. **CI/CD Pipeline**
   - Automated testing
   - Code quality checks
   - Automated deployments
   - Environment-specific configurations

3. **Monitoring**
   - Application performance monitoring
   - Error tracking (Sentry, Rollbar)
   - Logging (Winston, Morgan)
   - Health check endpoints

4. **Scaling**
   - Horizontal scaling with load balancer
   - Database replication
   - Caching strategy
   - CDN for static assets

## Testing Strategy

1. **Unit Tests**
   - Test individual functions
   - Mock external dependencies
   - Test edge cases

2. **Integration Tests**
   - Test API endpoints
   - Test database operations
   - Test file uploads

3. **End-to-End Tests**
   - Test complete workflows
   - Test authentication flows
   - Test document processing pipeline

## Mock API Server (Development)

For development, you can create a mock API server using the provided JSON files:

```javascript
// mock-server.js
const express = require('express');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.json());

const authData = require('./api/mock-data/auth.json');
const documentsData = require('./api/mock-data/documents.json');
const chatsData = require('./api/mock-data/chats.json');
const comparisonsData = require('./api/mock-data/comparisons.json');
const summariesData = require('./api/mock-data/summaries.json');
const analyticsData = require('./api/mock-data/analytics.json');

// Auth endpoints
app.post('/api/auth/login', (req, res) => {
  const { email, password } = req.body;
  const user = authData.users.find(u => u.email === email && u.password === password);
  
  if (user) {
    const { password, ...userWithoutPassword } = user;
    res.json({
      success: true,
      data: {
        user: userWithoutPassword,
        tokens: {
          accessToken: 'mock_access_token',
          refreshToken: 'mock_refresh_token',
          expiresIn: 3600
        }
      }
    });
  } else {
    res.status(401).json({
      success: false,
      error: {
        code: 'INVALID_CREDENTIALS',
        message: 'Invalid email or password'
      }
    });
  }
});

// Document endpoints
app.get('/api/documents', (req, res) => {
  res.json({
    success: true,
    data: {
      documents: documentsData.documents,
      pagination: {
        currentPage: 1,
        totalPages: 1,
        totalItems: documentsData.documents.length
      }
    }
  });
});

// Add more endpoints as needed...

app.listen(3000, () => {
  console.log('Mock API server running on http://localhost:3000');
});
```

## Next Steps

1. Choose your technology stack
2. Set up the development environment
3. Implement database schema
4. Create authentication system
5. Implement document upload and processing
6. Integrate AI services
7. Add chat functionality
8. Implement comparison and summarization
9. Build admin dashboard APIs
10. Test thoroughly
11. Deploy to production

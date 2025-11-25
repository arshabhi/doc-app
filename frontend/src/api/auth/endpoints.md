# Authentication API Endpoints

## 1. POST /api/auth/login
User login endpoint.

### Request
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "usr_1a2b3c4d5e",
      "email": "user@example.com",
      "name": "John Doe",
      "role": "user",
      "createdAt": "2025-01-15T10:30:00Z",
      "updatedAt": "2025-10-20T08:15:00Z"
    },
    "tokens": {
      "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "expiresIn": 3600
    }
  }
}
```

### Error Response (401 Unauthorized)
```json
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password"
  }
}
```

---

## 2. POST /api/auth/register
User registration endpoint.

### Request
```json
{
  "email": "newuser@example.com",
  "password": "SecurePassword123!",
  "name": "Jane Smith",
  "confirmPassword": "SecurePassword123!"
}
```

### Success Response (201 Created)
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "usr_2b3c4d5e6f",
      "email": "newuser@example.com",
      "name": "Jane Smith",
      "role": "user",
      "createdAt": "2025-10-20T10:30:00Z",
      "updatedAt": "2025-10-20T10:30:00Z"
    },
    "tokens": {
      "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "expiresIn": 3600
    }
  }
}
```

### Error Response (400 Bad Request)
```json
{
  "success": false,
  "error": {
    "code": "EMAIL_ALREADY_EXISTS",
    "message": "An account with this email already exists"
  }
}
```

---

## 3. POST /api/auth/logout
User logout endpoint.

### Request Headers
```
Authorization: Bearer <accessToken>
```

### Request Body
```json
{
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "message": "Logged out successfully"
  }
}
```

---

## 4. GET /api/auth/me
Get current user profile.

### Request Headers
```
Authorization: Bearer <accessToken>
```

### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "usr_1a2b3c4d5e",
      "email": "user@example.com",
      "name": "John Doe",
      "role": "user",
      "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=John",
      "createdAt": "2025-01-15T10:30:00Z",
      "updatedAt": "2025-10-20T08:15:00Z",
      "preferences": {
        "theme": "light",
        "language": "en",
        "notifications": true
      },
      "stats": {
        "totalDocuments": 15,
        "totalChats": 42,
        "storageUsed": 1048576
      }
    }
  }
}
```

---

## 5. POST /api/auth/refresh
Refresh access token.

### Request
```json
{
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresIn": 3600
  }
}
```

### Error Response (401 Unauthorized)
```json
{
  "success": false,
  "error": {
    "code": "INVALID_REFRESH_TOKEN",
    "message": "Invalid or expired refresh token"
  }
}
```

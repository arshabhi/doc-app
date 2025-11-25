# Document Management System

A comprehensive AI-powered document management application with authentication, chat capabilities, document comparison, and admin dashboard.

## Features

### User Features
- **Document Upload**: Upload multiple documents (PDF, DOC, DOCX, TXT)
- **Document Chat**: Ask questions and get AI-powered insights from your documents
- **Document Comparison**: Compare two documents to find similarities and differences
- **Document Summarization**: Generate AI summaries of your documents
- **User Authentication**: Secure login system with role-based access

### Admin Features
- **Admin Dashboard**: Comprehensive system overview
- **User Management**: View and manage all system users
- **Activity Monitoring**: Track recent system activities
- **Document Statistics**: Detailed analytics on document usage
- **Storage Metrics**: Monitor storage usage across the system

## Technology Stack

- **Frontend**: React 18 with TypeScript
- **UI Components**: Shadcn/ui
- **Styling**: Tailwind CSS
- **State Management**: React Context API
- **Icons**: Lucide React
- **Notifications**: Sonner

## Getting Started

### Prerequisites
- Node.js 20 or higher
- Docker and Docker Compose (for containerized deployment)
- Python 3.11.9+ (for backend)
- PostgreSQL 13+ (or use Docker)

### Quick Start

⚠️ **Important**: This application requires both frontend and backend to run.

1. **Start the Backend** (see [BACKEND-SETUP.md](./BACKEND-SETUP.md) for details):
```bash
# Start PostgreSQL
docker-compose up -d postgres

# Start the backend API
cd backend
python main.py
```

2. **Start the Frontend**:
```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

3. Open your browser and navigate to `http://localhost:5173`

### Troubleshooting

If you see "Failed to connect to the server" error:

1. **Verify backend is running**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check the browser console** (F12) for diagnostic information

3. **See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** for detailed troubleshooting steps

### Development Setup

1. Install dependencies:
```bash
npm install
```

2. Environment variables are pre-configured in `.env`:
   - No configuration needed for development
   - See [ENVIRONMENT-SETUP.md](./ENVIRONMENT-SETUP.md) for customization

3. Start the development server:
```bash
npm run dev
```

4. Open your browser and navigate to `http://localhost:5173`

### Docker Deployment

1. Build and run with Docker Compose:
```bash
docker-compose up -d
```

2. Access the application at `http://localhost:3000`

### Using Docker manually:

1. Build the Docker image:
```bash
docker build -t document-management-app .
```

2. Run the container:
```bash
docker run -p 3000:3000 document-management-app
```

## Default Users

The application comes with demo users for testing:

### Admin User
- Email: `admin@example.com`
- Password: `admin123`
- Access: Full system access including admin dashboard

### Regular User
- Email: `user@example.com`
- Password: `user123`
- Access: Document management features only

## Project Structure

```
/
├── components/
│   ├── ui/                    # Shadcn UI components
│   ├── AdminDashboard.tsx     # Admin dashboard view
│   ├── Dashboard.tsx          # Main user dashboard
│   ├── DocumentChat.tsx       # Chat interface
│   ├── DocumentCompare.tsx    # Document comparison tool
│   ├── DocumentList.tsx       # Document list view
│   ├── DocumentUpload.tsx     # File upload interface
│   ├── Login.tsx              # Login page
│   └── Navbar.tsx             # Navigation bar
├── context/
│   ├── AuthContext.tsx        # Authentication state
│   └── DocumentContext.tsx    # Document management state
├── services/
│   ├── api.ts                 # API service layer
│   └── healthCheck.ts         # Backend health monitoring
├── config/
│   └── environment.ts         # Environment configuration
├── styles/
│   └── globals.css            # Global styles
├── .env                       # Environment variables
├── .env.example               # Environment template
├── App.tsx                    # Main application component
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose configuration
└── package.json               # Project dependencies

```

## Features in Detail

### Document Upload
- Support for multiple file formats
- Drag and drop interface
- File size validation
- Batch upload capability

### AI Chat
- Context-aware responses based on document content
- Chat history per document
- Real-time message updates
- Clear chat functionality

### Document Comparison
- Side-by-side comparison
- Similarity and difference analysis
- Structured comparison results
- Visual comparison interface

### Admin Dashboard
- System statistics overview
- User management table
- Recent activity feed
- Document usage analytics
- Storage monitoring

## Backend Integration

This application is designed to work with a FastAPI backend running on `localhost:8000`. The frontend communicates with the backend through:

- **Authentication**: JWT-based authentication with refresh tokens
- **Document Management**: File upload, download, and metadata management
- **AI Features**: Chat, comparison, and summarization via backend AI services
- **Admin Operations**: User management and system analytics

### API Documentation

- See [API-INTEGRATION.md](./API-INTEGRATION.md) for API details
- Backend API docs available at: `http://localhost:8000/docs` (when running)

## Documentation

- 📚 [STARTUP-GUIDE.md](./STARTUP-GUIDE.md) - Step-by-step startup instructions
- 🔧 [ENVIRONMENT-SETUP.md](./ENVIRONMENT-SETUP.md) - Environment configuration guide
- 🔍 [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Common issues and solutions
- 🚀 [QUICK-START.md](./QUICK-START.md) - Quick start guide
- 📡 [API-INTEGRATION.md](./API-INTEGRATION.md) - API integration details
- 🐛 [FIXED-CONNECTION-ERROR.md](./FIXED-CONNECTION-ERROR.md) - Recent fixes

## Production Deployment

For production deployment:

1. Set `VITE_API_BASE_URL` to your production backend URL
2. Configure CORS on the backend to allow your frontend domain
3. Set up proper SSL/TLS certificates
4. Configure environment variables for security
5. Set up proper logging and monitoring
6. Implement rate limiting and security measures

## License

MIT License - Feel free to use this project for your own purposes.

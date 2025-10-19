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

### Development Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your browser and navigate to `http://localhost:5173`

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
├── styles/
│   └── globals.css            # Global styles
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

## Note

This is a frontend demonstration application with mock data and simulated AI responses. In a production environment, you would need to:

1. Connect to a real authentication service
2. Implement actual file storage (e.g., AWS S3, Azure Blob Storage)
3. Integrate with AI services for document processing (e.g., OpenAI, Claude)
4. Set up a backend API for data persistence
5. Implement proper security measures
6. Add environment-specific configurations

## License

MIT License - Feel free to use this project for your own purposes.

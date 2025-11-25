# 📄 Doc-App
### AI-Powered Document Analysis, Summarization, Comparison, and Chat

<p align="left"> <img src="https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white" /> <img src="https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react&logoColor=black" /> <img src="https://img.shields.io/badge/PostgreSQL-16-31648C?style=for-the-badge&logo=postgresql&logoColor=white" /> <img src="https://img.shields.io/badge/Qdrant-Vector%20DB-FF4F8B?style=for-the-badge&logo=qdrant&logoColor=white" /> <img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white" /> </p> <p align="left"> <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" /> <img src="https://img.shields.io/badge/Status-Active-success?style=flat-square" /> </p>

Doc-App is a full-stack application designed to process documents, extract insights, compare versions, generate summaries, and enable contextual chat using RAG (Retrieval Augmented Generation) powered by Qdrant vector search and LLMs.

The system includes a FastAPI backend, a React (Vite) frontend, and PostgreSQL + Qdrant for persistent + vector storage.

## 🚀 Features
### Document Operations

- Upload, process, and store documents
- Extract text & metadata
- Download documents
- Generate summaries (multi-style, multi-length)
- Chat over selected document
- Compare two documents (structure, content, metadata, full diff)

## Chat & RAG

- Chat with any uploaded document
- RAG using HuggingFace embeddings and Qdrant vector search
- Chat history & conversations
- Source citations + confidence scores

## Admin Dashboard
- Manage all users
- Admin analytics (users, documents, chats, processing health)
- View system activity

## Architecture
- Full async FastAPI backend
- React + Vite frontend
- PostgreSQL for users, documents, chat & summaries
- Qdrant vector DB for high-performance semantic search
- Dockerized for production deployment

## 🏗️ Tech Stack
### Frontend
- React + Vite
- TailwindCSS
- Axios
- Docker

### Backend
- FastAPI
- SQLAlchemy (async)
- Uvicorn
- HuggingFace Transformers (embeddings)
- LangGraph workflows

### Databases
- PostgreSQL
- Qdrant (vector search)

### Deployment
- Docker
- docker-compose
- Multi-container orchestration

## 📂 Project Structure
```
doc-app/
│
├── backend/
│   ├── app/
│   │   ├── api/             # API routers
│   │   ├── db/              # Database models & CRUD
│   │   ├── services/        # Document processing, RAG, etc.
│   │   ├── utils/           # Qdrant utils, helpers
│   │   ├── core/            # Config, security, auth
│   │   └── main.py          # FastAPI entrypoint
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── config/
│   │   ├── context/
│   │   ├── services/
│   │   ├── styles/
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   ├── tailwind.config.ts
│   │   └── main.tsx
│   └── Dockerfile
│
├── docker-compose.yml
└── README.md
```


## 🐳 Running with Docker (Recommended)
### 1. Build + start all services
```
docker compose up --build
```

Services started:
- frontend → http://localhost:5173
- backend → http://localhost:8000
- postgres → http://localhost:5432
- qdrant → http://localhost:6333

### 2. Stop & remove all containers
```
docker compose down
```

### 3. Rebuild without cache
```
docker compose build --no-cache
```

## 🖥️ Run Backend Locally (without Docker)
```
cd backend
uvicorn app.main:app --reload
```

Backend runs at:
👉 `http://localhost:8000`

👉 Swagger Docs: `http://localhost:8000/docs`

## 💻 Run Frontend Locally
```
cd frontend/src
npm install     # only first time
npm run dev
```


Frontend runs at:
👉 `http://localhost:5173`

## 🗃️ Run Postgres + Qdrant (locally only)

If you want only DBs without frontend/backend:

Edit docker-compose.yml and comment out frontend + backend services.

Then run:

```
docker compose up -d
```

## ⚙️ Environment Variables

### Backend .env example:

```
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/chatapp
QDRANT_URL=http://qdrant:6333
SECRET_KEY=your_jwt_secret
GEMINI_API_KEY=your_api_key_here
```

### Frontend .env example:
```
VITE_API_BASE_URL=http://backend:8000
```

## 🧠 RAG Pipeline

Doc-App uses:
- HuggingFace all-MiniLM-L6-v2 for embeddings
- Qdrant for semantic search
- LangChain for prompt chaining
- Gemini (or any LLM) for answer generation

## 🔍 API Overview
### Documents
- Upload
- List
- Download
- Update metadata
- Summaries
- Comparison

### Chat
- Query
- Get chat history
- Get conversations
- Admin APIs

### Users
- Documents
- Analytics
- Activity
- Broadcast messages

Full API documentation is available at:
👉 ```/docs``` (Swagger UI)

## Upcoming Features and Enhancements
- Support for multiple doc types (images)
- Document Extraction pipeline
- Download option in pdf/doc format
- Compare Document API
- Selection of embeddings and models

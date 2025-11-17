# doc-app
A document app for all kinds of document insights and comparison.

# to run the FE, BE, postgres and qdrant docker via docker-compose
docker compose up --build

# to remove container
docker compose down

# to run backend
cd backend
uvicorn app.main:app --reload

# to run frontend
cd frontend/src
npm install (optional)
npm run dev

# to run postgres and qdrant
comment out the Front end and Backend from compose and run
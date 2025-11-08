# doc-app
A document app for all kinds of document insights and comparison.

# to run the postgres and qdrant docker via docker-compose
docker-compose-up -d

# to run backend
uvicorn app.main:app --reload

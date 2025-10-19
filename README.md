# doc-app
A document app for all kinds of document insights and comparison.

# to run the postgres docker
docker run --name=chatapp-db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=pass -e POSTGRES_DB=chatapp -p 5432:5432 -d postgres:16

# to run backend
uvicorn app.main:app --reload

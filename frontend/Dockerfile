# ======================
#  FRONTEND (React + Vite)
# ======================
FROM node:18-alpine

# Set workdir
WORKDIR /app

# Copy dependencies first (cache layer)
COPY src/package.json src/package-lock.json* ./ 

# Install dependencies
RUN npm install

# Copy all files
COPY src/ .

# Expose frontend port
EXPOSE 5173

# Start Vite dev server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

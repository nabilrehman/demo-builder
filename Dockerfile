# Stage 1: Build the React frontend
FROM node:18-slim AS build-frontend

WORKDIR /app/frontend

# Copy frontend project files
COPY newfrontend/conversational-api-demo-frontend/package.json ./
COPY newfrontend/conversational-api-demo-frontend/package-lock.json ./
COPY newfrontend/conversational-api-demo-frontend/vite.config.ts ./
COPY newfrontend/conversational-api-demo-frontend/tsconfig.json ./
COPY newfrontend/conversational-api-demo-frontend/tsconfig.node.json ./
COPY newfrontend/conversational-api-demo-frontend/tsconfig.app.json ./
COPY newfrontend/conversational-api-demo-frontend/tailwind.config.ts ./
COPY newfrontend/conversational-api-demo-frontend/postcss.config.js ./
COPY newfrontend/conversational-api-demo-frontend/.env.local ./
COPY newfrontend/conversational-api-demo-frontend/src ./src
COPY newfrontend/conversational-api-demo-frontend/public ./public
COPY newfrontend/conversational-api-demo-frontend/index.html ./

# Install dependencies and build
RUN npm install
RUN npm run build

# Stage 2: Build the Python backend
FROM python:3.11-slim

WORKDIR /app

# Copy backend requirements and install dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the built frontend from the previous stage
COPY --from=build-frontend /app/frontend/dist ./newfrontend/conversational-api-demo-frontend/dist

# Copy the backend code
COPY backend/ ./

# Expose the port the app runs on (Cloud Run uses PORT env var, defaults to 8080)
EXPOSE 8080

# Run the application (use PORT env var for Cloud Run compatibility)
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT:-8080}"]

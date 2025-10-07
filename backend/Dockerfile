FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy frontend build
COPY ../newfrontend/conversational-api-demo-frontend/dist ./static 2>/dev/null || true

# Expose port
EXPOSE 8080

# Run the application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]

# Deployment Plan: Integrating React App into CAPI Repository

This document outlines exactly where to place this React app in your `capi` repository and how to structure everything.

## 📁 Final Repository Structure

```
capi/
├── ca-api-codelab/                 # Your existing Python backend
│   ├── chat.py
│   ├── create_agent.py
│   ├── create_conversation.py
│   ├── chat_utils.py
│   ├── main.py
│   ├── api.py                      # NEW - REST API wrapper
│   ├── requirements.txt            # Updated with API dependencies
│   └── README.md
│
├── web-app/                        # NEW - This React frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── BrandingSetup.tsx
│   │   │   ├── ChatHeader.tsx
│   │   │   ├── ChatInput.tsx
│   │   │   ├── ChatMessage.tsx
│   │   │   ├── ChartMessage.tsx
│   │   │   ├── LoadingState.tsx
│   │   │   ├── DeveloperMode.tsx
│   │   │   └── ui/                 # shadcn components
│   │   ├── pages/
│   │   │   ├── Index.tsx
│   │   │   └── NotFound.tsx
│   │   ├── hooks/
│   │   ├── lib/
│   │   ├── index.css
│   │   └── main.tsx
│   ├── public/
│   │   └── robots.txt
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── .env.example
│   └── README.md
│
├── docs/                           # Documentation (optional but recommended)
│   ├── INTEGRATION_GUIDE.md
│   ├── LLM_INTEGRATION_GUIDE.md
│   └── API_REFERENCE.md
│
├── .gitignore                      # Updated for both Python and Node
├── README.md                       # Main project README
└── DEPLOYMENT_PLAN.md              # This file
```

## 🚀 Step-by-Step Integration

### Step 1: Create Directory Structure

```bash
cd /path/to/capi

# Create web-app directory
mkdir -p web-app/src

# Create docs directory (optional)
mkdir docs
```

### Step 2: Copy React App Files

Copy from your Lovable project to `capi/web-app/`:

```bash
# From Lovable project root
cp -r src/ ../capi/web-app/
cp -r public/ ../capi/web-app/
cp index.html ../capi/web-app/
cp package.json ../capi/web-app/
cp vite.config.ts ../capi/web-app/
cp tailwind.config.ts ../capi/web-app/
cp tsconfig.json ../capi/web-app/
cp tsconfig.app.json ../capi/web-app/
cp tsconfig.node.json ../capi/web-app/
cp postcss.config.js ../capi/web-app/
cp components.json ../capi/web-app/

# Copy documentation
cp INTEGRATION_GUIDE.md ../capi/docs/
cp LLM_INTEGRATION_GUIDE.md ../capi/docs/
cp DEPLOYMENT_PLAN.md ../capi/
```

### Step 3: Create Backend API Wrapper

Create `ca-api-codelab/api.py`:

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.auth
from google.auth.transport.requests import Request
from googleapiclient import discovery
from typing import Optional
import json

app = FastAPI(title="Conversational Analytics API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",   # Alternative port
        "https://*.lovable.app",   # Lovable deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    question: str
    website: Optional[str] = None
    agent_id: Optional[str] = None
    conversation_id: Optional[str] = None

class ChartData(BaseModel):
    type: str  # "bar", "line", "pie"
    title: str
    data: list
    xKey: Optional[str] = None
    yKey: Optional[str] = None
    nameKey: Optional[str] = None

class ChatResponse(BaseModel):
    success: bool
    response: str
    chartData: Optional[dict] = None
    sqlQuery: Optional[str] = None
    error: Optional[str] = None

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """
    Main chat endpoint that processes natural language questions
    and returns AI-generated responses with optional chart data.
    """
    try:
        # Get Google Cloud credentials
        credentials, project_id = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        credentials.refresh(Request())
        
        # Build Conversational Analytics API client
        service = discovery.build(
            'geminidataanalytics',
            'v1alpha',
            credentials=credentials,
            discoveryServiceUrl='https://geminidataanalytics.googleapis.com/$discovery/rest?version=v1alpha'
        )
        
        # TODO: Implement agent/conversation management
        # For now, use default IDs or create based on website
        agent_id = req.agent_id or "default-agent"
        conversation_id = req.conversation_id or "default-conversation"
        
        # Call Conversational Analytics API
        parent = f"projects/{project_id}/locations/us-central1"
        conversation_path = f"{parent}/dataAgents/{agent_id}/conversations/{conversation_id}"
        
        request_body = {
            "content": req.question,
            "role": "user"
        }
        
        response = service.projects().locations().dataAgents()\
            .conversations().messages().create(
                parent=conversation_path,
                body=request_body
            ).execute()
        
        # Parse response
        assistant_content = response.get('content', 'No response generated')
        sql_query = response.get('sqlQuery', None)
        
        # Extract chart data if present
        chart_data = parse_chart_data_from_response(response)
        
        return ChatResponse(
            success=True,
            response=assistant_content,
            chartData=chart_data,
            sqlQuery=sql_query
        )
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return ChatResponse(
            success=False,
            response="",
            error=str(e)
        )

def parse_chart_data_from_response(api_response):
    """
    Parse Conversational Analytics API response to extract chart data.
    Adapt this based on your actual API response format.
    """
    # TODO: Implement based on actual API response structure
    # This is a placeholder
    
    if 'queryResults' in api_response:
        results = api_response['queryResults']
        # Transform to chart format
        # Return appropriate chart type based on data structure
        pass
    
    return None

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "conversational-analytics-api"}

@app.get("/")
async def root():
    """API info endpoint"""
    return {
        "name": "Conversational Analytics API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/chat",
            "health": "/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
```

### Step 4: Update Backend Requirements

Update `ca-api-codelab/requirements.txt`:

```txt
# Existing dependencies
google-cloud-aiplatform==1.38.0
google-auth==2.23.4
google-api-python-client==2.108.0

# New API dependencies
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
```

### Step 5: Create Environment Files

**Backend `.env` (`ca-api-codelab/.env`):**
```env
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

**Frontend `.env` (`web-app/.env`):**
```env
# Development
VITE_API_URL=http://localhost:8000

# Production - update after deployment
# VITE_API_URL=https://your-api-service.run.app
```

**Frontend `.env.example` (`web-app/.env.example`):**
```env
# Backend API URL
VITE_API_URL=http://localhost:8000
```

### Step 6: Update .gitignore

Update root `.gitignore`:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
*.egg-info/
dist/
build/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*

# Build outputs
web-app/dist/
web-app/build/

# Environment files
.env
.env.local
.env.*.local
*.env

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log
```

### Step 7: Create Main README

Update `README.md` at repository root:

```markdown
# Conversational Analytics Platform (CAPI)

A full-stack conversational analytics platform combining Google's Conversational Analytics API with a modern React frontend.

## 🏗️ Architecture

- **Backend**: Python (FastAPI) → Google Conversational Analytics API → BigQuery
- **Frontend**: React + TypeScript + Vite

## 📁 Structure

- `ca-api-codelab/` - Python backend and API server
- `web-app/` - React frontend application
- `docs/` - Documentation and guides

## 🚀 Quick Start

### Backend
\`\`\`bash
cd ca-api-codelab
pip install -r requirements.txt
python api.py
\`\`\`

### Frontend
\`\`\`bash
cd web-app
npm install
npm run dev
\`\`\`

Visit `http://localhost:5173` to use the application.

## 📖 Documentation

- [Integration Guide](docs/INTEGRATION_GUIDE.md) - Full integration setup
- [LLM Guide](docs/LLM_INTEGRATION_GUIDE.md) - AI-assisted development guide
- [Deployment Plan](DEPLOYMENT_PLAN.md) - This file

## 🔗 Links

- Backend scripts and examples: `ca-api-codelab/`
- Frontend application: `web-app/`
- Google Cloud Docs: https://cloud.google.com/gemini/docs/conversational-analytics
```

## 🧪 Testing the Integration

### Test Backend Separately

```bash
# Terminal 1: Start backend
cd ca-api-codelab
python api.py

# Terminal 2: Test with curl
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the top selling products?",
    "website": "shopify.com"
  }'
```

### Test Full Stack

```bash
# Terminal 1: Backend
cd ca-api-codelab
python api.py

# Terminal 2: Frontend
cd web-app
npm run dev

# Browser: http://localhost:5173
```

## 🚢 Deployment

### Backend → Cloud Run

```bash
cd ca-api-codelab

# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
EOF

# Build and deploy
gcloud builds submit --tag gcr.io/YOUR_PROJECT/capi-backend
gcloud run deploy capi-backend \
  --image gcr.io/YOUR_PROJECT/capi-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Frontend → Lovable (Easiest)

1. Keep code in Lovable project
2. Click "Share" → "Publish"
3. Update `VITE_API_URL` to your Cloud Run URL

### Or Deploy Frontend Manually

```bash
cd web-app
npm run build

# Deploy dist/ to:
# - Netlify: netlify deploy --prod --dir=dist
# - Vercel: vercel --prod
# - Firebase: firebase deploy
```

## 📋 Checklist

- [ ] Backend API created (`api.py`)
- [ ] Requirements updated
- [ ] Frontend copied to `web-app/`
- [ ] Environment files configured
- [ ] `.gitignore` updated
- [ ] Main `README.md` created
- [ ] Backend tested locally
- [ ] Frontend tested locally
- [ ] Full stack tested together
- [ ] Backend deployed to Cloud Run
- [ ] Frontend deployed
- [ ] Production environment variables set

## 🤖 For AI Assistants

When asked to integrate or modify this codebase:

1. **Backend changes**: Modify `ca-api-codelab/api.py`
2. **Frontend changes**: Modify files in `web-app/src/`
3. **API contract**: Ensure backend returns the format frontend expects (see `ChatResponse`)
4. **New features**: Consider both frontend UX and backend API changes

See [LLM_INTEGRATION_GUIDE.md](docs/LLM_INTEGRATION_GUIDE.md) for detailed instructions.

## 🆘 Support

- **Backend issues**: Check `ca-api-codelab/README.md`
- **Frontend issues**: Check `web-app/README.md`
- **Integration issues**: Check `docs/INTEGRATION_GUIDE.md`
- **Google Cloud**: https://cloud.google.com/gemini/docs/conversational-analytics

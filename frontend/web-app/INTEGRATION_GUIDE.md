# Integration Guide: React Frontend + Python Backend

This guide explains how to integrate this React-based analytics chatbot with your BigQuery Conversational Analytics API Python backend.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        User Browser                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │     React App (This Project)                         │   │
│  │  - Branding extraction                               │   │
│  │  - Chat UI                                           │   │
│  │  - Chart visualization                               │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ HTTP Requests
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Python FastAPI/Flask Backend                    │
│                (Your ca-api-codelab)                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  POST /api/chat                                      │   │
│  │  - Receives user questions                           │   │
│  │  - Manages agent/conversation                        │   │
│  │  - Returns AI responses + chart data                 │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Google Cloud API
                           ▼
┌─────────────────────────────────────────────────────────────┐
│        Google Conversational Analytics API                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  - Data Agent Management                             │   │
│  │  - Natural Language to SQL                           │   │
│  │  - BigQuery Execution                                │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Repository Structure

Your main repository should look like this:

```
capi/
├── ca-api-codelab/          # Python backend (existing)
│   ├── chat.py
│   ├── create_agent.py
│   ├── create_conversation.py
│   ├── main.py
│   └── api.py               # NEW - REST API wrapper
│
├── web-app/                 # React frontend (new - this project)
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── docs/
│   ├── INTEGRATION_GUIDE.md
│   └── LLM_INTEGRATION_GUIDE.md
│
└── README.md
```

## Step 1: Place the Web App in Your Repository

1. Create a `web-app` directory in your `capi` repository:
   ```bash
   cd /path/to/capi
   mkdir web-app
   ```

2. Copy all files from this Lovable project into `web-app/`:
   - Copy `src/`, `public/`, `index.html`
   - Copy `package.json`, `vite.config.ts`, `tsconfig.json`
   - Copy `tailwind.config.ts`, `postcss.config.js`

3. Install dependencies:
   ```bash
   cd web-app
   npm install
   ```

## Step 2: Update Python Backend for Web Integration

Your Python backend needs to expose a REST API that the React frontend can call.

### Create API Wrapper (FastAPI Recommended)

Create a new file `ca-api-codelab/api.py`:

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.auth
from google.auth.transport.requests import Request
from googleapiclient import discovery

app = FastAPI()

# Enable CORS for React app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str
    agent_id: str = None
    conversation_id: str = None
    website: str = None

class ChatResponse(BaseModel):
    success: bool
    response: str
    chartData: dict = None
    sqlQuery: str = None
    error: str = None

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Get credentials
        credentials, project_id = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        credentials.refresh(Request())
        
        # Initialize Conversational Analytics API client
        service = discovery.build(
            'geminidataanalytics',
            'v1alpha',
            credentials=credentials,
            discoveryServiceUrl='https://geminidataanalytics.googleapis.com/$discovery/rest?version=v1alpha'
        )
        
        # Use existing agent or create new one based on website
        agent_id = request.agent_id or f"agent-{request.website.replace('.', '-')}"
        conversation_id = request.conversation_id or f"conv-{agent_id}"
        
        # Call the Conversational Analytics API
        parent = f"projects/{project_id}/locations/us-central1"
        response = service.projects().locations().conversations().messages().create(
            parent=f"{parent}/conversations/{conversation_id}",
            body={
                "content": request.question,
                "role": "user"
            }
        ).execute()
        
        # Parse response to extract chart data if present
        chart_data = parse_chart_data(response)
        sql_query = response.get('sqlQuery', None)
        
        return ChatResponse(
            success=True,
            response=response.get('content', 'No response'),
            chartData=chart_data,
            sqlQuery=sql_query
        )
        
    except Exception as e:
        return ChatResponse(
            success=False,
            response="",
            error=str(e)
        )

def parse_chart_data(api_response):
    """Parse API response to extract chart data"""
    # Implement logic to convert API response to chart format
    # This depends on your API response structure
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Step 3: Update React Frontend to Call Python Backend

Remove Supabase edge function calls and point to your Python API.

Update `web-app/src/pages/Index.tsx`:

```typescript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const handleSendMessage = async (content: string) => {
  const userMessage: Message = {
    id: Date.now().toString(),
    role: "user",
    content
  };
  setMessages(prev => [...prev, userMessage]);
  setIsLoading(true);

  try {
    setLoadingMessage("Analyzing your question...");
    
    // Call Python backend API
    const response = await fetch(`${API_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question: content,
        website: branding?.websiteUrl,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    if (!data.success) {
      throw new Error(data.error || 'Failed to get response');
    }

    setLoadingMessage("Generating insights...");
    await new Promise(resolve => setTimeout(resolve, 300));

    const botMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: "assistant",
      content: data.response,
      chartData: data.chartData
    };
    
    const responseData = {
      query: content,
      response: data.response,
      chartData: data.chartData || null,
      sqlQuery: data.sqlQuery || null,
      source: "BigQuery Conversational Analytics API"
    };
    
    setLastResponse(JSON.stringify(responseData, null, 2));
    setMessages(prev => [...prev, botMessage]);
    
  } catch (error) {
    console.error('Error sending message:', error);
    toast({
      title: "Error",
      description: error instanceof Error ? error.message : "Failed to send message",
      variant: "destructive",
    });
    
    setMessages(prev => prev.filter(m => m.id !== userMessage.id));
  } finally {
    setIsLoading(false);
    setLoadingMessage("");
  }
};
```

## Step 4: Environment Configuration

Create `.env` files for both frontend and backend:

### Frontend `.env` (`web-app/.env`):
```env
VITE_API_URL=http://localhost:8000
```

### Backend requirements (`ca-api-codelab/requirements.txt`):
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
google-cloud-aiplatform==1.38.0
google-auth==2.23.4
google-api-python-client==2.108.0
pydantic==2.5.0
```

## Step 5: Running the Full Stack

### Terminal 1 - Python Backend:
```bash
cd ca-api-codelab
pip install -r requirements.txt
python api.py
```

### Terminal 2 - React Frontend:
```bash
cd web-app
npm install
npm run dev
```

The app will be available at `http://localhost:5173`

## Step 6: Production Deployment

### Backend Deployment (Cloud Run):
```bash
# Build container
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/analytics-api

# Deploy to Cloud Run
gcloud run deploy analytics-api \
  --image gcr.io/YOUR_PROJECT_ID/analytics-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Frontend Deployment (Lovable):
Simply click "Publish" in Lovable to deploy the frontend. Update `VITE_API_URL` to your Cloud Run URL.

## Troubleshooting

### CORS Issues
If you see CORS errors, ensure your Python backend has proper CORS headers:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Be more specific in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Authentication Issues
Make sure your service account has these permissions:
- `roles/aiplatform.user`
- `roles/bigquery.dataViewer`

```bash
# Set up Application Default Credentials
gcloud auth application-default login
```

### API Endpoint Not Found
Verify the backend is running on port 8000 and the frontend is pointing to the correct URL.

## Next Steps

1. **Add authentication**: Implement user authentication if needed
2. **Add agent management**: Allow users to create/manage their own agents
3. **Add conversation history**: Store conversations in a database
4. **Add rate limiting**: Protect your API from abuse
5. **Add monitoring**: Use Cloud Logging for production monitoring

## Support

For issues specific to:
- **Google Conversational Analytics API**: Check [official documentation](https://cloud.google.com/gemini/docs/conversational-analytics)
- **React frontend**: Refer to the project README
- **Integration**: See LLM_INTEGRATION_GUIDE.md for AI-assisted modifications

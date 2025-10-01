# LLM Integration Guide: Connect React App to BigQuery Backend

This document is designed to help AI assistants (like Claude, GPT, or Gemini) make the necessary code changes to integrate this React analytics chatbot with a Python backend that uses Google's Conversational Analytics API.

## Quick Context

**Current State:**
- React app with mock data responses
- Branding extraction from websites
- Chat interface with chart visualization
- Currently uses mock/fake data

**Target State:**
- Connect to Python FastAPI/Flask backend
- Backend calls Google Conversational Analytics API
- Real-time analytics from BigQuery
- Dynamic chart generation from actual data

## Architecture Summary

```
[React App] --HTTP--> [Python API] --Google API--> [Conversational Analytics API] --SQL--> [BigQuery]
```

## Key Files to Modify

### 1. Backend: Create REST API Endpoint

**File: `ca-api-codelab/api.py` (NEW FILE)**

Create a FastAPI server that wraps the existing Python scripts:

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.auth
from google.auth.transport.requests import Request
from googleapiclient import discovery
import json

app = FastAPI()

# IMPORTANT: Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str
    website: str = None
    agent_id: str = None
    conversation_id: str = None

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    """
    Main endpoint that the React app calls.
    This replicates the logic from chat.py but as an API.
    """
    try:
        # 1. Get credentials
        credentials, project_id = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        credentials.refresh(Request())
        
        # 2. Build service
        service = discovery.build(
            'geminidataanalytics',
            'v1alpha',
            credentials=credentials,
            discoveryServiceUrl='https://geminidataanalytics.googleapis.com/$discovery/rest?version=v1alpha'
        )
        
        # 3. Construct the API call
        # Use the agent and conversation IDs from request or defaults
        agent_id = req.agent_id or "your-default-agent-id"
        conversation_id = req.conversation_id or "your-default-conversation-id"
        
        parent = f"projects/{project_id}/locations/us-central1"
        conversation_path = f"{parent}/dataAgents/{agent_id}/conversations/{conversation_id}"
        
        # 4. Send message to Conversational Analytics API
        request_body = {
            "content": req.question,
            "role": "user"
        }
        
        response = service.projects().locations().dataAgents().conversations().messages().create(
            parent=conversation_path,
            body=request_body
        ).execute()
        
        # 5. Parse response
        assistant_content = response.get('content', '')
        
        # 6. Extract chart data if present
        # The API may return structured data or SQL queries
        chart_data = None
        sql_query = response.get('sqlQuery', None)
        
        # Check if response contains data suitable for charts
        if 'data' in response or 'rows' in response:
            chart_data = parse_to_chart_format(response)
        
        return {
            "success": True,
            "response": assistant_content,
            "chartData": chart_data,
            "sqlQuery": sql_query
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "response": None
        }

def parse_to_chart_format(api_response):
    """
    Convert API response data to chart format expected by frontend.
    
    Frontend expects:
    {
        "type": "bar" | "line" | "pie",
        "title": "Chart Title",
        "data": [{...}],
        "xKey": "field_name",
        "yKey": "value_field"
    }
    """
    # TODO: Implement based on your actual API response format
    # This is a placeholder - adjust based on actual response structure
    
    if 'queryResults' in api_response:
        rows = api_response['queryResults'].get('rows', [])
        if not rows:
            return None
            
        # Detect chart type based on data structure
        # Example logic - adapt to your needs
        return {
            "type": "bar",
            "title": "Query Results",
            "data": rows,
            "xKey": rows[0].keys()[0] if rows else None,
            "yKey": rows[0].keys()[1] if rows and len(rows[0]) > 1 else None
        }
    
    return None

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**To run:**
```bash
cd ca-api-codelab
pip install fastapi uvicorn
python api.py
```

### 2. Frontend: Update API Calls

**File: `src/pages/Index.tsx`**

Modify the `handleSendMessage` function to call the Python backend:

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
  setLastQuery(content);

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
        // Optional: include agent/conversation IDs if you manage them
        // agent_id: localStorage.getItem('agent_id'),
        // conversation_id: localStorage.getItem('conversation_id'),
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

### 3. Environment Configuration

**File: `web-app/.env`**

```env
# Development
VITE_API_URL=http://localhost:8000

# Production - update this when deployed
# VITE_API_URL=https://your-api.run.app
```

### 4. Remove Supabase Dependencies (Optional)

If you want to completely remove Supabase:

1. **Remove Supabase function call** in `src/pages/Index.tsx`
2. **Remove import**: `import { supabase } from "@/integrations/supabase/client";`
3. **Uninstall package**: `npm uninstall @supabase/supabase-js`

## Agent and Conversation Management

The Python backend scripts (`create_agent.py`, `create_conversation.py`) need to be adapted:

### Option 1: Create on First Request

Modify `api.py` to create agent/conversation if they don't exist:

```python
async def ensure_agent_exists(service, project_id, website):
    """Create agent if it doesn't exist"""
    agent_id = f"agent-{website.replace('.', '-')}"
    
    try:
        # Try to get existing agent
        parent = f"projects/{project_id}/locations/us-central1"
        service.projects().locations().dataAgents().get(
            name=f"{parent}/dataAgents/{agent_id}"
        ).execute()
        return agent_id
    except:
        # Create new agent
        # Implementation based on create_agent.py logic
        pass
```

### Option 2: Pre-create Agents

Use the existing scripts to pre-create agents for common use cases:

```bash
# Run once to create agent
python create_agent.py
python create_conversation.py

# Note the agent_id and conversation_id
# Pass these to the React app via URL params or config
```

## Chart Data Transformation

The Conversational Analytics API returns data in BigQuery format. Transform it for the frontend:

```python
def transform_bigquery_to_chart(query_results):
    """
    Transform BigQuery results to frontend chart format
    
    Input (BigQuery format):
    {
        "rows": [
            {"f": [{"v": "2024-01"}, {"v": "1250"}]},
            {"f": [{"v": "2024-02"}, {"v": "1580"}]}
        ],
        "schema": {
            "fields": [
                {"name": "month", "type": "STRING"},
                {"name": "sales", "type": "INTEGER"}
            ]
        }
    }
    
    Output (Chart format):
    {
        "type": "line",
        "title": "Sales Over Time",
        "data": [
            {"month": "2024-01", "sales": 1250},
            {"month": "2024-02", "sales": 1580}
        ],
        "xKey": "month",
        "yKey": "sales"
    }
    """
    if not query_results or 'rows' not in query_results:
        return None
    
    rows = query_results['rows']
    schema = query_results.get('schema', {}).get('fields', [])
    
    # Transform to object format
    data = []
    for row in rows:
        obj = {}
        for i, field in enumerate(schema):
            field_name = field['name']
            value = row['f'][i]['v']
            obj[field_name] = value
        data.append(obj)
    
    # Detect appropriate chart type
    if len(schema) == 2:
        # Two columns: likely x-y chart
        return {
            "type": "bar",  # or "line" based on data type
            "title": "Query Results",
            "data": data,
            "xKey": schema[0]['name'],
            "yKey": schema[1]['name']
        }
    
    return None
```

## Testing the Integration

### 1. Test Backend Independently

```bash
# Terminal 1: Start backend
cd ca-api-codelab
python api.py

# Terminal 2: Test with curl
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the top selling products?"}'
```

### 2. Test Full Stack

```bash
# Terminal 1: Backend
cd ca-api-codelab
python api.py

# Terminal 2: Frontend
cd web-app
npm run dev

# Open browser to http://localhost:5173
# Enter a website URL (e.g., "shopify.com")
# Try asking questions about the data
```

## Common Issues and Solutions

### CORS Errors

**Problem:** Browser blocks requests from React to Python API

**Solution:** Ensure `CORSMiddleware` is configured in `api.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Authentication Errors

**Problem:** "Could not automatically determine credentials"

**Solution:** Set up Application Default Credentials:
```bash
gcloud auth application-default login
```

### API Not Found

**Problem:** 404 errors when calling `/api/chat`

**Solution:** Verify:
1. Backend is running on port 8000
2. Frontend `VITE_API_URL` points to `http://localhost:8000`
3. Route is correctly defined in `api.py`

## Deployment Checklist

- [ ] Backend deployed to Cloud Run or similar
- [ ] Environment variables configured
- [ ] Service account has proper permissions
- [ ] Frontend `.env` updated with production API URL
- [ ] CORS configured for production domain
- [ ] API rate limiting implemented
- [ ] Error monitoring set up

## AI Assistant Quick Reference

When an AI assistant needs to:

1. **Add new analytics query:** Modify the backend `chat_endpoint` function
2. **Change chart types:** Update `parse_to_chart_format` function
3. **Add authentication:** Add middleware in `api.py` and update frontend fetch calls
4. **Modify UI:** Work with React components in `web-app/src/components/`
5. **Debug issues:** Check both backend logs (terminal) and frontend console (browser)

## Resources

- [Google Conversational Analytics API](https://cloud.google.com/gemini/docs/conversational-analytics)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React + Vite](https://vitejs.dev/guide/)
- [Recharts (for charts)](https://recharts.org/)

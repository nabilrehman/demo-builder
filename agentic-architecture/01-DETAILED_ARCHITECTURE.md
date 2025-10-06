# Detailed Technical Architecture

## System Architecture Overview

### Core Technology Stack

```yaml
Frontend:
  - Framework: React + Vite (existing)
  - New Features: Provisioning UI, Progress Tracker, Demo Dashboard
  - State Management: React Query / TanStack Query
  - Real-time Updates: Server-Sent Events (SSE) or WebSockets

Backend:
  - API Framework: FastAPI (existing)
  - Orchestration: LangGraph
  - Agent Intelligence: Claude 3.5 Sonnet (Anthropic SDK)
  - State Persistence: PostgreSQL or SQLite
  - Task Queue: Built-in LangGraph checkpointing
  - Logging: Python logging + Google Cloud Logging

Google Cloud Services:
  - BigQuery: Data storage
  - Conversational Analytics API: Final data agent
  - Cloud Storage: Temporary data storage
  - Secret Manager: API keys
  - Cloud Run: Deployment (optional)

External Services:
  - Anthropic API: Claude for agentic workflows
  - Web Scraping: BeautifulSoup4, Playwright, or Firecrawl
```

## Detailed Component Architecture

### 1. Frontend Enhancement (`newfrontend/`)

#### New Components

```
newfrontend/conversational-api-demo-frontend/src/
├── pages/
│   ├── CEDashboard.tsx           # Main CE interface (NEW)
│   ├── ProvisioningView.tsx      # Provisioning progress (NEW)
│   └── ChatInterface.tsx         # Existing chat interface
│
├── components/
│   ├── provisioning/
│   │   ├── URLInputForm.tsx      # Customer URL input
│   │   ├── ProvisioningProgress.tsx  # Real-time progress
│   │   ├── AgentStatusCard.tsx   # Individual agent status
│   │   └── ErrorDisplay.tsx      # Error handling UI
│   │
│   ├── demo-assets/
│   │   ├── GoldenQueriesPanel.tsx    # Generated queries
│   │   ├── DemoScriptViewer.tsx      # Demo script display
│   │   └── DataSchemaView.tsx        # Schema visualization
│   │
│   └── existing chat components...
│
└── services/
    ├── provisioningService.ts    # API calls for provisioning
    └── sseService.ts             # Server-Sent Events handler
```

#### Key Features

1. **CE Dashboard**
   - Input field for customer URL
   - List of previous provisioning jobs
   - Quick access to deployed demos

2. **Provisioning Progress Tracker**
   - Real-time updates from backend
   - Visual progress indicators for each agent
   - Logs viewer for debugging
   - Cancel/retry functionality

3. **Demo Assets Viewer**
   - Generated golden queries
   - Demo script suggestions
   - Data schema visualization
   - Sample Q&A pairs

### 2. Backend Architecture (`backend/`)

```
backend/
├── api.py                        # Existing FastAPI app
│
├── agentic_service/              # NEW - Agentic orchestration
│   ├── __init__.py
│   │
│   ├── orchestrator/             # LangGraph workflow
│   │   ├── __init__.py
│   │   ├── graph.py              # Main LangGraph definition
│   │   ├── state.py              # Shared state schema
│   │   └── checkpointer.py       # Persistence config
│   │
│   ├── agents/                   # Individual agents
│   │   ├── __init__.py
│   │   ├── base_agent.py         # Base agent class
│   │   ├── research_agent.py     # Agent 1: Research
│   │   ├── data_modeling_agent.py # Agent 2: Data Modeling
│   │   ├── infra_agent.py        # Agent 3: Infrastructure
│   │   ├── capi_agent.py         # Agent 4: CAPI Creator
│   │   └── demo_content_agent.py # Agent 5: Demo Content
│   │
│   ├── tools/                    # Agent tools
│   │   ├── __init__.py
│   │   ├── web_research.py       # Web scraping & analysis
│   │   ├── bigquery_ops.py       # BigQuery operations
│   │   ├── capi_ops.py           # Conversational API ops
│   │   ├── data_generation.py    # Synthetic data generation
│   │   └── schema_analysis.py    # Schema inference
│   │
│   ├── models/                   # Data models
│   │   ├── __init__.py
│   │   ├── provisioning.py       # Provisioning job models
│   │   ├── customer.py           # Customer data models
│   │   └── demo_assets.py        # Demo asset models
│   │
│   └── utils/
│       ├── __init__.py
│       ├── llm_client.py         # Claude client wrapper
│       ├── prompt_templates.py   # Agent prompts
│       └── validators.py         # Input validation
│
├── routes/                       # NEW - API routes
│   ├── __init__.py
│   ├── provisioning.py           # Provisioning endpoints
│   ├── chat.py                   # Existing chat (refactored)
│   └── assets.py                 # Demo assets endpoints
│
├── requirements.txt              # Updated dependencies
└── config.py                     # Configuration management
```

### 3. LangGraph Workflow Definition

#### State Schema

```python
from typing import TypedDict, List, Dict, Optional, Literal
from datetime import datetime

class ProvisioningState(TypedDict):
    # Input
    customer_url: str
    project_id: str
    job_id: str
    ce_email: str

    # Research Phase
    customer_info: Optional[Dict]
    business_domain: Optional[str]
    industry: Optional[str]
    key_entities: Optional[List[str]]

    # Data Modeling Phase
    schema_design: Optional[Dict]
    table_definitions: Optional[List[Dict]]
    sample_data: Optional[Dict[str, List[Dict]]]

    # Infrastructure Phase
    dataset_id: Optional[str]
    tables_created: Optional[List[str]]
    data_loaded: Optional[bool]

    # CAPI Agent Phase
    data_agent_id: Optional[str]
    agent_config: Optional[Dict]
    agent_tested: Optional[bool]

    # Demo Content Phase
    golden_queries: Optional[List[Dict]]
    demo_script: Optional[str]
    sample_qa: Optional[List[Dict]]

    # Metadata
    current_phase: Literal[
        "research", "data_modeling", "infrastructure",
        "capi_creation", "demo_content", "completed", "failed"
    ]
    progress_percentage: int
    errors: List[str]
    logs: List[Dict]
    created_at: datetime
    updated_at: datetime
```

#### Graph Structure

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

def create_provisioning_graph():
    """Creates the main LangGraph workflow."""

    # Initialize checkpointer for state persistence
    checkpointer = SqliteSaver.from_conn_string("provisioning.db")

    # Create the graph
    workflow = StateGraph(ProvisioningState)

    # Add nodes (agents)
    workflow.add_node("research", research_agent_node)
    workflow.add_node("data_modeling", data_modeling_agent_node)
    workflow.add_node("infrastructure", infrastructure_agent_node)
    workflow.add_node("capi_creation", capi_creation_agent_node)
    workflow.add_node("demo_content", demo_content_agent_node)
    workflow.add_node("error_handler", error_handler_node)

    # Define edges (flow)
    workflow.set_entry_point("research")

    # Sequential flow with error handling
    workflow.add_conditional_edges(
        "research",
        lambda state: "data_modeling" if not state.get("errors") else "error_handler"
    )
    workflow.add_conditional_edges(
        "data_modeling",
        lambda state: "infrastructure" if not state.get("errors") else "error_handler"
    )
    workflow.add_conditional_edges(
        "infrastructure",
        lambda state: "capi_creation" if not state.get("errors") else "error_handler"
    )
    workflow.add_conditional_edges(
        "capi_creation",
        lambda state: "demo_content" if not state.get("errors") else "error_handler"
    )
    workflow.add_edge("demo_content", END)
    workflow.add_edge("error_handler", END)

    # Compile with checkpointer
    return workflow.compile(checkpointer=checkpointer)
```

### 4. Agent Node Implementations

#### Example: Research Agent Node

```python
from anthropic import Anthropic
from typing import Dict
import logging

async def research_agent_node(state: ProvisioningState) -> ProvisioningState:
    """
    Agent 1: Research customer's business domain.

    Tasks:
    1. Scrape customer website
    2. Analyze business model
    3. Identify key entities and relationships
    4. Determine industry and domain
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Starting research for {state['customer_url']}")

    try:
        # Update state
        state["current_phase"] = "research"
        state["progress_percentage"] = 10
        state["logs"].append({
            "timestamp": datetime.now().isoformat(),
            "phase": "research",
            "message": "Starting customer research..."
        })

        # Initialize Claude client
        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        # Scrape website
        website_content = await scrape_website(state["customer_url"])

        # Define tools for Claude
        tools = [
            {
                "name": "analyze_webpage",
                "description": "Analyzes webpage content to extract business information",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "analysis_type": {
                            "type": "string",
                            "enum": ["business_model", "products", "services", "entities"]
                        }
                    },
                    "required": ["analysis_type"]
                }
            }
        ]

        # Claude analyzes the content
        messages = [
            {
                "role": "user",
                "content": f"""Analyze this company website and extract:
1. Business domain (e.g., e-commerce, SaaS, healthcare)
2. Industry
3. Key business entities (e.g., customers, orders, products)
4. Data model suggestions

Website content:
{website_content[:10000]}  # Limit content

Provide structured JSON output."""
            }
        ]

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            tools=tools,
            messages=messages
        )

        # Extract analysis from Claude
        analysis = parse_claude_response(response)

        # Update state with research results
        state["customer_info"] = analysis
        state["business_domain"] = analysis.get("domain")
        state["industry"] = analysis.get("industry")
        state["key_entities"] = analysis.get("entities", [])
        state["progress_percentage"] = 20
        state["logs"].append({
            "timestamp": datetime.now().isoformat(),
            "phase": "research",
            "message": f"Research completed. Domain: {state['business_domain']}"
        })

        return state

    except Exception as e:
        logger.error(f"Research agent error: {str(e)}")
        state["errors"].append(f"Research failed: {str(e)}")
        state["current_phase"] = "failed"
        return state
```

### 5. API Endpoints

#### Provisioning Endpoints

```python
# routes/provisioning.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, HttpUrl
import asyncio
from typing import AsyncGenerator

router = APIRouter(prefix="/api/provision", tags=["provisioning"])

class ProvisionRequest(BaseModel):
    customer_url: HttpUrl
    ce_email: Optional[str] = None
    project_id: Optional[str] = None

class ProvisionResponse(BaseModel):
    job_id: str
    status: str
    message: str

@router.post("/start", response_model=ProvisionResponse)
async def start_provisioning(
    request: ProvisionRequest,
    background_tasks: BackgroundTasks
):
    """
    Start a new provisioning job.
    Returns job_id for tracking progress.
    """
    job_id = str(uuid.uuid4())

    # Initialize state
    initial_state = {
        "customer_url": str(request.customer_url),
        "project_id": request.project_id or os.getenv("DEVSHELL_PROJECT_ID"),
        "job_id": job_id,
        "ce_email": request.ce_email,
        "current_phase": "research",
        "progress_percentage": 0,
        "errors": [],
        "logs": [],
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

    # Start workflow in background
    background_tasks.add_task(run_provisioning_workflow, initial_state)

    return ProvisionResponse(
        job_id=job_id,
        status="started",
        message="Provisioning workflow started"
    )

@router.get("/status/{job_id}")
async def get_provisioning_status(job_id: str):
    """Get current status of a provisioning job."""
    state = await get_workflow_state(job_id)
    if not state:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": job_id,
        "current_phase": state["current_phase"],
        "progress_percentage": state["progress_percentage"],
        "errors": state["errors"],
        "recent_logs": state["logs"][-10:]  # Last 10 logs
    }

@router.get("/stream/{job_id}")
async def stream_provisioning_progress(job_id: str):
    """
    Stream real-time updates using Server-Sent Events.
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        while True:
            state = await get_workflow_state(job_id)
            if not state:
                yield f"data: {json.dumps({'error': 'Job not found'})}\n\n"
                break

            yield f"data: {json.dumps({
                'phase': state['current_phase'],
                'progress': state['progress_percentage'],
                'latest_log': state['logs'][-1] if state['logs'] else None
            })}\n\n"

            # Stop streaming if completed or failed
            if state["current_phase"] in ["completed", "failed"]:
                break

            await asyncio.sleep(2)  # Update every 2 seconds

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )

@router.get("/assets/{job_id}")
async def get_demo_assets(job_id: str):
    """Get generated demo assets for a completed job."""
    state = await get_workflow_state(job_id)
    if not state:
        raise HTTPException(status_code=404, detail="Job not found")

    if state["current_phase"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed yet")

    return {
        "job_id": job_id,
        "data_agent_id": state["data_agent_id"],
        "dataset_id": state["dataset_id"],
        "golden_queries": state["golden_queries"],
        "demo_script": state["demo_script"],
        "sample_qa": state["sample_qa"],
        "schema": state["table_definitions"]
    }
```

## Data Flow Sequence

```
1. CE enters customer URL
   └─> POST /api/provision/start

2. Backend creates initial state
   └─> Starts LangGraph workflow

3. Research Agent executes
   ├─> Scrapes customer website
   ├─> Claude analyzes business domain
   └─> Updates state with findings

4. Data Modeling Agent executes
   ├─> Claude designs schema based on domain
   ├─> Generates synthetic data definitions
   └─> Updates state with schema

5. Infrastructure Agent executes
   ├─> Creates BigQuery dataset
   ├─> Creates tables from schema
   ├─> Loads synthetic data
   └─> Updates state with resource IDs

6. CAPI Agent executes
   ├─> Creates Conversational Analytics agent
   ├─> Configures system instructions
   ├─> Links to BigQuery datasources
   └─> Tests agent with sample query

7. Demo Content Agent executes
   ├─> Generates golden queries
   ├─> Creates demo script
   ├─> Generates sample Q&A
   └─> Finalizes provisioning

8. Frontend polls/streams progress
   └─> Displays real-time updates

9. Completion
   └─> CE can access demo interface with generated assets
```

## Error Handling & Retry Strategy

```python
class ErrorHandler:
    """Centralized error handling for agents."""

    @staticmethod
    def should_retry(error: Exception, attempt: int) -> bool:
        """Determine if error is retryable."""
        retryable_errors = [
            "RateLimitError",
            "APIConnectionError",
            "ServiceUnavailable"
        ]
        return (
            any(err in str(type(error)) for err in retryable_errors)
            and attempt < 3
        )

    @staticmethod
    async def handle_agent_error(
        agent_name: str,
        error: Exception,
        state: ProvisioningState
    ) -> ProvisioningState:
        """Handle agent execution errors."""
        logger.error(f"{agent_name} failed: {str(error)}")

        state["errors"].append({
            "agent": agent_name,
            "error": str(error),
            "timestamp": datetime.now().isoformat()
        })

        # Add to logs
        state["logs"].append({
            "timestamp": datetime.now().isoformat(),
            "phase": state["current_phase"],
            "level": "ERROR",
            "message": f"{agent_name} encountered an error: {str(error)}"
        })

        return state
```

## Security Considerations

1. **API Key Management**
   - Use Google Secret Manager for Anthropic API keys
   - Rotate keys regularly
   - Never expose in logs or client-side code

2. **Input Validation**
   - Validate customer URLs (whitelist domains if needed)
   - Sanitize web scraping outputs
   - Rate limit provisioning requests per CE

3. **BigQuery Permissions**
   - Use service accounts with minimal permissions
   - Separate datasets per customer
   - Implement data retention policies

4. **CAPI Access Control**
   - Assign appropriate IAM roles to agents
   - Implement audit logging
   - Monitor for unusual activity

## Performance Optimization

1. **Parallel Execution** (where possible)
   - Research and initial setup can run in parallel
   - Data generation for multiple tables in parallel
   - BigQuery table creation in parallel

2. **Caching**
   - Cache website scraping results (1 hour TTL)
   - Cache schema templates for common domains
   - Cache Claude responses for similar inputs

3. **Async Operations**
   - All I/O operations async
   - Use asyncio for concurrent tasks
   - Stream large responses

4. **Resource Management**
   - Connection pooling for BigQuery
   - Rate limiting for external APIs
   - Cleanup temporary resources

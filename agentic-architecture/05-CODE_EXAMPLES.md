# Code Examples & Prototypes

This document provides concrete code examples for implementing the agentic provisioning system.

---

## 1. Complete LangGraph Workflow

### `backend/agentic_service/orchestrator/graph.py`

```python
"""
Main LangGraph workflow for autonomous demo provisioning.
"""
from typing import TypedDict, List, Dict, Optional, Literal, Annotated
from datetime import datetime
import operator

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# State Definition
# ============================================================================

class ProvisioningState(TypedDict):
    """Shared state across all agents."""

    # Input
    customer_url: str
    project_id: str
    job_id: str
    ce_email: Optional[str]

    # Research Phase
    customer_info: Optional[Dict]
    business_domain: Optional[str]
    industry: Optional[str]
    key_entities: Annotated[List[str], operator.add]  # Append-only

    # Data Modeling Phase
    schema_design: Optional[Dict]
    table_definitions: Optional[List[Dict]]
    sample_data: Optional[Dict[str, List[Dict]]]

    # Infrastructure Phase
    dataset_id: Optional[str]
    tables_created: Annotated[List[str], operator.add]
    data_loaded: Optional[bool]

    # CAPI Agent Phase
    data_agent_id: Optional[str]
    agent_config: Optional[Dict]
    agent_tested: Optional[bool]

    # Demo Content Phase
    golden_queries: Optional[List[Dict]]
    demo_script: Optional[Dict]
    sample_qa: Optional[List[Dict]]

    # Metadata
    current_phase: Literal[
        "research", "data_modeling", "infrastructure",
        "capi_creation", "demo_content", "completed", "failed"
    ]
    progress_percentage: int
    errors: Annotated[List[Dict], operator.add]
    logs: Annotated[List[Dict], operator.add]
    created_at: datetime
    updated_at: datetime


# ============================================================================
# Agent Node Functions
# ============================================================================

async def research_agent_node(state: ProvisioningState) -> ProvisioningState:
    """Node 1: Research customer's business."""
    from ..agents.research_agent import CustomerResearchAgent

    logger.info(f"[{state['job_id']}] Starting research phase")

    try:
        state["current_phase"] = "research"
        state["progress_percentage"] = 10
        state["logs"].append({
            "timestamp": datetime.now().isoformat(),
            "phase": "research",
            "level": "INFO",
            "message": f"Analyzing {state['customer_url']}"
        })

        # Execute agent
        agent = CustomerResearchAgent()
        updated_state = await agent.execute(state)

        updated_state["progress_percentage"] = 20
        updated_state["logs"].append({
            "timestamp": datetime.now().isoformat(),
            "phase": "research",
            "level": "SUCCESS",
            "message": f"Identified domain: {updated_state.get('business_domain')}"
        })

        return updated_state

    except Exception as e:
        logger.error(f"Research failed: {str(e)}", exc_info=True)
        state["errors"].append({
            "phase": "research",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })
        state["current_phase"] = "failed"
        return state


async def data_modeling_agent_node(state: ProvisioningState) -> ProvisioningState:
    """Node 2: Design schema and generate data."""
    from ..agents.data_modeling_agent import DataModelingAgent

    logger.info(f"[{state['job_id']}] Starting data modeling phase")

    try:
        state["current_phase"] = "data_modeling"
        state["progress_percentage"] = 25
        state["logs"].append({
            "timestamp": datetime.now().isoformat(),
            "phase": "data_modeling",
            "level": "INFO",
            "message": "Designing database schema"
        })

        agent = DataModelingAgent()
        updated_state = await agent.execute(state)

        updated_state["progress_percentage"] = 45
        updated_state["logs"].append({
            "timestamp": datetime.now().isoformat(),
            "phase": "data_modeling",
            "level": "SUCCESS",
            "message": f"Created {len(updated_state['table_definitions'])} table schemas"
        })

        return updated_state

    except Exception as e:
        logger.error(f"Data modeling failed: {str(e)}", exc_info=True)
        state["errors"].append({
            "phase": "data_modeling",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })
        state["current_phase"] = "failed"
        return state


async def infrastructure_agent_node(state: ProvisioningState) -> ProvisioningState:
    """Node 3: Provision BigQuery infrastructure."""
    from ..agents.infra_agent import InfrastructureAgent

    logger.info(f"[{state['job_id']}] Starting infrastructure phase")

    try:
        state["current_phase"] = "infrastructure"
        state["progress_percentage"] = 50
        state["logs"].append({
            "timestamp": datetime.now().isoformat(),
            "phase": "infrastructure",
            "level": "INFO",
            "message": "Creating BigQuery dataset and tables"
        })

        agent = InfrastructureAgent(state["project_id"])
        updated_state = await agent.execute(state)

        updated_state["progress_percentage"] = 70
        updated_state["logs"].append({
            "timestamp": datetime.now().isoformat(),
            "phase": "infrastructure",
            "level": "SUCCESS",
            "message": f"Dataset {updated_state['dataset_id']} created with {len(updated_state['tables_created'])} tables"
        })

        return updated_state

    except Exception as e:
        logger.error(f"Infrastructure provisioning failed: {str(e)}", exc_info=True)
        state["errors"].append({
            "phase": "infrastructure",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })
        state["current_phase"] = "failed"
        return state


async def capi_creation_agent_node(state: ProvisioningState) -> ProvisioningState:
    """Node 4: Create Conversational Analytics API agent."""
    from ..agents.capi_agent import CAPIAgentCreator

    logger.info(f"[{state['job_id']}] Starting CAPI agent creation")

    try:
        state["current_phase"] = "capi_creation"
        state["progress_percentage"] = 75
        state["logs"].append({
            "timestamp": datetime.now().isoformat(),
            "phase": "capi_creation",
            "level": "INFO",
            "message": "Creating data agent"
        })

        agent = CAPIAgentCreator(state["project_id"])
        updated_state = await agent.execute(state)

        updated_state["progress_percentage"] = 85
        updated_state["logs"].append({
            "timestamp": datetime.now().isoformat(),
            "phase": "capi_creation",
            "level": "SUCCESS",
            "message": f"Data agent {updated_state['data_agent_id']} created and tested"
        })

        return updated_state

    except Exception as e:
        logger.error(f"CAPI agent creation failed: {str(e)}", exc_info=True)
        state["errors"].append({
            "phase": "capi_creation",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })
        state["current_phase"] = "failed"
        return state


async def demo_content_agent_node(state: ProvisioningState) -> ProvisioningState:
    """Node 5: Generate demo content."""
    from ..agents.demo_content_agent import DemoContentGenerator

    logger.info(f"[{state['job_id']}] Starting demo content generation")

    try:
        state["current_phase"] = "demo_content"
        state["progress_percentage"] = 90
        state["logs"].append({
            "timestamp": datetime.now().isoformat(),
            "phase": "demo_content",
            "level": "INFO",
            "message": "Generating golden queries and demo script"
        })

        agent = DemoContentGenerator()
        updated_state = await agent.execute(state)

        updated_state["current_phase"] = "completed"
        updated_state["progress_percentage"] = 100
        updated_state["logs"].append({
            "timestamp": datetime.now().isoformat(),
            "phase": "demo_content",
            "level": "SUCCESS",
            "message": f"Generated {len(updated_state['golden_queries'])} golden queries"
        })

        return updated_state

    except Exception as e:
        logger.error(f"Demo content generation failed: {str(e)}", exc_info=True)
        state["errors"].append({
            "phase": "demo_content",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })
        state["current_phase"] = "failed"
        return state


async def error_handler_node(state: ProvisioningState) -> ProvisioningState:
    """Handle errors and determine if retry is possible."""
    logger.error(f"[{state['job_id']}] Workflow failed: {state['errors']}")

    state["current_phase"] = "failed"
    state["logs"].append({
        "timestamp": datetime.now().isoformat(),
        "phase": "error_handler",
        "level": "ERROR",
        "message": f"Provisioning failed: {state['errors'][-1]['error']}"
    })

    return state


# ============================================================================
# Graph Construction
# ============================================================================

def create_provisioning_graph():
    """
    Creates the main LangGraph workflow.

    Returns:
        Compiled graph with checkpointing enabled.
    """

    # Initialize SQLite checkpointer for state persistence
    checkpointer = SqliteSaver.from_conn_string("provisioning_state.db")

    # Create the graph
    workflow = StateGraph(ProvisioningState)

    # Add nodes
    workflow.add_node("research", research_agent_node)
    workflow.add_node("data_modeling", data_modeling_agent_node)
    workflow.add_node("infrastructure", infrastructure_agent_node)
    workflow.add_node("capi_creation", capi_creation_agent_node)
    workflow.add_node("demo_content", demo_content_agent_node)
    workflow.add_node("error_handler", error_handler_node)

    # Set entry point
    workflow.set_entry_point("research")

    # Define conditional edges (error handling)
    def route_after_research(state: ProvisioningState) -> str:
        if state.get("errors"):
            return "error_handler"
        return "data_modeling"

    def route_after_data_modeling(state: ProvisioningState) -> str:
        if state.get("errors"):
            return "error_handler"
        return "infrastructure"

    def route_after_infrastructure(state: ProvisioningState) -> str:
        if state.get("errors"):
            return "error_handler"
        return "capi_creation"

    def route_after_capi(state: ProvisioningState) -> str:
        if state.get("errors"):
            return "error_handler"
        return "demo_content"

    # Add conditional edges
    workflow.add_conditional_edges(
        "research",
        route_after_research,
        {
            "data_modeling": "data_modeling",
            "error_handler": "error_handler"
        }
    )

    workflow.add_conditional_edges(
        "data_modeling",
        route_after_data_modeling,
        {
            "infrastructure": "infrastructure",
            "error_handler": "error_handler"
        }
    )

    workflow.add_conditional_edges(
        "infrastructure",
        route_after_infrastructure,
        {
            "capi_creation": "capi_creation",
            "error_handler": "error_handler"
        }
    )

    workflow.add_conditional_edges(
        "capi_creation",
        route_after_capi,
        {
            "demo_content": "demo_content",
            "error_handler": "error_handler"
        }
    )

    # Terminal edges
    workflow.add_edge("demo_content", END)
    workflow.add_edge("error_handler", END)

    # Compile with checkpointer
    return workflow.compile(checkpointer=checkpointer)


# ============================================================================
# Execution Functions
# ============================================================================

async def run_provisioning_workflow(initial_state: Dict):
    """
    Run the complete provisioning workflow.

    Args:
        initial_state: Initial state dictionary

    Returns:
        Final state after workflow completion
    """
    graph = create_provisioning_graph()

    # Run the graph
    config = {"configurable": {"thread_id": initial_state["job_id"]}}

    final_state = None
    async for state in graph.astream(initial_state, config):
        final_state = state
        logger.info(f"State update: {state.get('current_phase')} - {state.get('progress_percentage')}%")

    return final_state


async def get_workflow_state(job_id: str) -> Optional[ProvisioningState]:
    """
    Retrieve current state for a job.

    Args:
        job_id: The provisioning job ID

    Returns:
        Current state or None if not found
    """
    graph = create_provisioning_graph()
    config = {"configurable": {"thread_id": job_id}}

    try:
        state = graph.get_state(config)
        return state.values if state else None
    except Exception as e:
        logger.error(f"Failed to retrieve state for {job_id}: {e}")
        return None
```

---

## 2. Research Agent Implementation

### `backend/agentic_service/agents/research_agent.py`

```python
"""
Customer Research Agent - Analyzes customer website to understand business domain.
"""
import os
import json
import logging
from typing import Dict
from anthropic import Anthropic

from ..tools.web_research import scrape_website
from ..utils.prompt_templates import RESEARCH_AGENT_PROMPT

logger = logging.getLogger(__name__)


class CustomerResearchAgent:
    """Agent for researching customer business domain."""

    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-3-5-sonnet-20241022"

    async def execute(self, state: Dict) -> Dict:
        """
        Execute research phase.

        Args:
            state: Current provisioning state

        Returns:
            Updated state with research findings
        """
        logger.info(f"Researching {state['customer_url']}")

        # 1. Scrape website
        website_content = await scrape_website(state["customer_url"])
        logger.info(f"Scraped {len(website_content)} characters from website")

        # 2. Analyze with Claude
        analysis = await self._analyze_business(website_content)

        # 3. Update state
        state["customer_info"] = analysis
        state["business_domain"] = analysis.get("business_domain")
        state["industry"] = analysis.get("industry")
        state["key_entities"] = [e["name"] for e in analysis.get("key_entities", [])]

        logger.info(f"Research complete. Domain: {state['business_domain']}")
        return state

    async def _analyze_business(self, website_content: str) -> Dict:
        """
        Use Claude to analyze business from website content.

        Args:
            website_content: Scraped website text

        Returns:
            Structured business analysis
        """
        # Truncate content if too long
        max_chars = 15000
        if len(website_content) > max_chars:
            website_content = website_content[:max_chars] + "\n\n[Content truncated...]"

        # Call Claude
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            temperature=0.2,  # Lower temperature for more consistent analysis
            messages=[{
                "role": "user",
                "content": RESEARCH_AGENT_PROMPT.format(
                    website_content=website_content
                )
            }]
        )

        # Extract JSON from response
        response_text = response.content[0].text

        # Parse JSON (handle potential markdown code blocks)
        if "```json" in response_text:
            json_start = response_text.index("```json") + 7
            json_end = response_text.rindex("```")
            json_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.index("```") + 3
            json_end = response_text.rindex("```")
            json_text = response_text[json_start:json_end].strip()
        else:
            json_text = response_text

        try:
            analysis = json.loads(json_text)
            return analysis
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response: {e}")
            logger.error(f"Response text: {response_text}")
            raise ValueError(f"Failed to parse business analysis: {str(e)}")
```

---

## 3. Web Scraping Tool

### `backend/agentic_service/tools/web_research.py`

```python
"""
Web research tools for scraping and analyzing websites.
"""
import asyncio
import logging
from typing import Optional
from urllib.parse import urlparse

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


async def scrape_website(url: str, timeout: int = 30) -> str:
    """
    Scrape website content and extract main text.

    Args:
        url: Website URL to scrape
        timeout: Request timeout in seconds

    Returns:
        Extracted text content

    Raises:
        ValueError: If URL is invalid
        aiohttp.ClientError: If request fails
    """
    # Validate URL
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Invalid URL: {url}")

    logger.info(f"Scraping {url}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=timeout),
                headers={"User-Agent": "Mozilla/5.0 (compatible; DemoBot/1.0)"}
            ) as response:
                response.raise_for_status()
                html = await response.text()

        # Parse HTML
        soup = BeautifulSoup(html, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style", "noscript"]):
            script.decompose()

        # Extract text
        text = soup.get_text(separator='\n', strip=True)

        # Clean up whitespace
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = '\n'.join(lines)

        logger.info(f"Scraped {len(clean_text)} characters from {url}")
        return clean_text

    except asyncio.TimeoutError:
        raise ValueError(f"Timeout while scraping {url}")
    except aiohttp.ClientError as e:
        raise ValueError(f"Failed to scrape {url}: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error scraping {url}: {e}", exc_info=True)
        raise


async def fetch_multiple_pages(base_url: str, paths: list[str]) -> dict[str, str]:
    """
    Fetch multiple pages from a website in parallel.

    Args:
        base_url: Base URL of the website
        paths: List of paths to fetch (e.g., ['/about', '/products'])

    Returns:
        Dictionary mapping path to content
    """
    tasks = []
    for path in paths:
        url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
        tasks.append(scrape_website(url))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    return {
        path: result if not isinstance(result, Exception) else ""
        for path, result in zip(paths, results)
    }
```

---

## 4. FastAPI Provisioning Endpoints

### `backend/routes/provisioning.py`

```python
"""
API endpoints for agentic provisioning.
"""
import asyncio
import json
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, HttpUrl

from ..agentic_service.orchestrator.graph import (
    run_provisioning_workflow,
    get_workflow_state
)

router = APIRouter(prefix="/api/provision", tags=["provisioning"])


# ============================================================================
# Request/Response Models
# ============================================================================

class ProvisionRequest(BaseModel):
    """Request to start provisioning."""
    customer_url: HttpUrl
    ce_email: Optional[str] = None
    project_id: Optional[str] = None


class ProvisionResponse(BaseModel):
    """Response after starting provisioning."""
    job_id: str
    status: str
    message: str


class StatusResponse(BaseModel):
    """Current status of a provisioning job."""
    job_id: str
    current_phase: str
    progress_percentage: int
    errors: list[dict]
    recent_logs: list[dict]


class AssetsResponse(BaseModel):
    """Generated demo assets."""
    job_id: str
    data_agent_id: str
    dataset_id: str
    golden_queries: list[dict]
    demo_script: dict
    sample_qa: list[dict]
    schema: list[dict]


# ============================================================================
# Endpoints
# ============================================================================

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
        "key_entities": [],
        "tables_created": [],
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

    # Start workflow in background
    background_tasks.add_task(run_provisioning_workflow, initial_state)

    return ProvisionResponse(
        job_id=job_id,
        status="started",
        message="Provisioning workflow started successfully"
    )


@router.get("/status/{job_id}", response_model=StatusResponse)
async def get_status(job_id: str):
    """Get current status of a provisioning job."""
    state = await get_workflow_state(job_id)

    if not state:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return StatusResponse(
        job_id=job_id,
        current_phase=state["current_phase"],
        progress_percentage=state["progress_percentage"],
        errors=state["errors"],
        recent_logs=state["logs"][-10:]  # Last 10 logs
    )


@router.get("/stream/{job_id}")
async def stream_progress(job_id: str):
    """
    Stream real-time updates using Server-Sent Events.
    """
    async def event_generator():
        previous_phase = None
        previous_progress = -1

        while True:
            state = await get_workflow_state(job_id)

            if not state:
                yield f"data: {json.dumps({'error': 'Job not found'})}\n\n"
                break

            # Only send update if something changed
            current_phase = state["current_phase"]
            current_progress = state["progress_percentage"]

            if current_phase != previous_phase or current_progress != previous_progress:
                yield f"data: {json.dumps({
                    'phase': current_phase,
                    'progress': current_progress,
                    'latest_log': state['logs'][-1] if state['logs'] else None,
                    'errors': state['errors']
                })}\n\n"

                previous_phase = current_phase
                previous_progress = current_progress

            # Stop streaming if completed or failed
            if current_phase in ["completed", "failed"]:
                break

            await asyncio.sleep(2)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.get("/assets/{job_id}", response_model=AssetsResponse)
async def get_demo_assets(job_id: str):
    """Get generated demo assets for a completed job."""
    state = await get_workflow_state(job_id)

    if not state:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    if state["current_phase"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job not completed yet. Current phase: {state['current_phase']}"
        )

    return AssetsResponse(
        job_id=job_id,
        data_agent_id=state["data_agent_id"],
        dataset_id=state["dataset_id"],
        golden_queries=state["golden_queries"],
        demo_script=state["demo_script"],
        sample_qa=state["sample_qa"],
        schema=state["table_definitions"]
    )


@router.delete("/cancel/{job_id}")
async def cancel_job(job_id: str):
    """Cancel a running provisioning job."""
    # Implementation depends on how we want to handle cancellation
    # Could mark state as "cancelled" and stop processing
    raise HTTPException(status_code=501, detail="Cancellation not implemented yet")
```

---

## 5. Frontend React Component

### `newfrontend/src/pages/CEDashboard.tsx`

```typescript
import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ProvisioningProgress } from '@/components/provisioning/ProvisioningProgress';
import { provisioningService } from '@/services/provisioningService';

export function CEDashboard() {
  const [customerUrl, setCustomerUrl] = useState('');
  const [activeJobId, setActiveJobId] = useState<string | null>(null);

  const startProvisioningMutation = useMutation({
    mutationFn: (url: string) => provisioningService.startProvisioning(url),
    onSuccess: (data) => {
      setActiveJobId(data.job_id);
    },
  });

  const handleStart = () => {
    if (customerUrl) {
      startProvisioningMutation.mutate(customerUrl);
    }
  };

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Customer Engineer Dashboard</h1>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Start New Demo Provisioning</CardTitle>
          <CardDescription>
            Enter a customer's website URL to automatically generate a personalized demo
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <Input
              placeholder="https://example-company.com"
              value={customerUrl}
              onChange={(e) => setCustomerUrl(e.target.value)}
              className="flex-1"
            />
            <Button
              onClick={handleStart}
              disabled={!customerUrl || startProvisioningMutation.isPending}
            >
              {startProvisioningMutation.isPending ? 'Starting...' : 'Start Provisioning'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {activeJobId && (
        <ProvisioningProgress jobId={activeJobId} />
      )}
    </div>
  );
}
```

### `newfrontend/src/components/provisioning/ProvisioningProgress.tsx`

```typescript
import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';

interface ProvisioningProgressProps {
  jobId: string;
}

interface ProgressUpdate {
  phase: string;
  progress: number;
  latest_log?: {
    message: string;
    level: string;
  };
  errors?: any[];
}

export function ProvisioningProgress({ jobId }: ProvisioningProgressProps) {
  const [progress, setProgress] = useState<ProgressUpdate | null>(null);

  useEffect(() => {
    // Connect to SSE stream
    const eventSource = new EventSource(`/api/provision/stream/${jobId}`);

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setProgress(data);

      // Close connection when done
      if (data.phase === 'completed' || data.phase === 'failed') {
        eventSource.close();
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [jobId]);

  if (!progress) {
    return <div>Connecting...</div>;
  }

  const phaseLabels = {
    research: 'Researching Customer',
    data_modeling: 'Designing Data Model',
    infrastructure: 'Provisioning Infrastructure',
    capi_creation: 'Creating Data Agent',
    demo_content: 'Generating Demo Content',
    completed: 'Completed',
    failed: 'Failed'
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Provisioning Progress</span>
          <Badge variant={progress.phase === 'completed' ? 'success' : 'default'}>
            {phaseLabels[progress.phase as keyof typeof phaseLabels]}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <div className="flex justify-between mb-2">
              <span className="text-sm font-medium">Progress</span>
              <span className="text-sm text-muted-foreground">{progress.progress}%</span>
            </div>
            <Progress value={progress.progress} />
          </div>

          {progress.latest_log && (
            <div className="text-sm p-3 bg-muted rounded-md">
              {progress.latest_log.message}
            </div>
          )}

          {progress.errors && progress.errors.length > 0 && (
            <div className="text-sm p-3 bg-destructive/10 text-destructive rounded-md">
              Error: {progress.errors[0].error}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
```

---

These code examples provide a solid foundation for implementing the agentic provisioning system. They can be used as starting points and customized based on specific requirements.

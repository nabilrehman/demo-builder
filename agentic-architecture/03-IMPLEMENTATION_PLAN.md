# Implementation Plan

## Phased Development Approach

This document outlines a pragmatic, phased approach to implementing the agentic provisioning system.

---

## Phase 1: Foundation (Week 1-2)

### Goals
- Set up basic infrastructure
- Implement core dependencies
- Create minimal viable orchestration

### Tasks

#### 1.1 Project Setup
```bash
# Install dependencies
pip install \
    anthropic \
    langgraph \
    langchain-core \
    google-cloud-bigquery \
    google-cloud-geminidataanalytics \
    beautifulsoup4 \
    playwright \
    faker \
    pydantic \
    python-dotenv

# Create directory structure
mkdir -p backend/agentic_service/{orchestrator,agents,tools,models,utils}
mkdir -p backend/routes
```

#### 1.2 Configuration Management
- [ ] Create `backend/config.py` for centralized config
- [ ] Set up environment variables for API keys
- [ ] Configure Google Cloud authentication
- [ ] Set up logging infrastructure

#### 1.3 Base Agent Class
- [ ] Implement `backend/agentic_service/agents/base_agent.py`
- [ ] Define common agent interface
- [ ] Add error handling utilities
- [ ] Create logging decorators

#### 1.4 LangGraph State Definition
- [ ] Define `ProvisioningState` TypedDict
- [ ] Create state validator
- [ ] Set up checkpointer (SQLite initially)

### Deliverables
- ✅ Development environment configured
- ✅ Base agent class implemented
- ✅ State management working
- ✅ Basic logging functional

### Success Metrics
- All dependencies install without errors
- Base agent can execute and log
- State persists across restarts

---

## Phase 2: Agent Development (Week 3-4)

### Goals
- Implement all 5 agents
- Create agent-specific tools
- Test individual agents

### Tasks

#### 2.1 Research Agent
- [ ] Implement web scraping tool (`tools/web_research.py`)
- [ ] Create research agent logic
- [ ] Test with 5 different company websites
- [ ] Validate output structure

#### 2.2 Data Modeling Agent
- [ ] Implement schema generation tool
- [ ] Create synthetic data generator
- [ ] Test with various business domains
- [ ] Validate BigQuery schema compatibility

#### 2.3 Infrastructure Agent
- [ ] Implement BigQuery operations (`tools/bigquery_ops.py`)
- [ ] Create dataset creation logic
- [ ] Implement table creation and loading
- [ ] Test with sample schemas

#### 2.4 CAPI Agent Creator
- [ ] Implement CAPI operations (`tools/capi_ops.py`)
- [ ] Create agent creation logic
- [ ] Implement agent testing
- [ ] Validate agent functionality

#### 2.5 Demo Content Generator
- [ ] Implement content generation prompts
- [ ] Create query generator
- [ ] Test with various industries
- [ ] Validate output quality

### Testing Strategy

```python
# test_agents.py
import pytest
from agentic_service.agents import *

@pytest.fixture
def sample_state():
    return {
        "customer_url": "https://example-ecommerce.com",
        "project_id": "test-project",
        "job_id": "test-123",
        # ... other fields
    }

async def test_research_agent(sample_state):
    agent = CustomerResearchAgent(anthropic_client)
    result = await agent.execute(sample_state)

    assert "customer_info" in result
    assert "business_domain" in result
    assert len(result["key_entities"]) > 0

async def test_data_modeling_agent(sample_state):
    # Add research results to state
    sample_state["customer_info"] = {...}

    agent = DataModelingAgent(anthropic_client)
    result = await agent.execute(sample_state)

    assert "schema_design" in result
    assert len(result["table_definitions"]) > 0

# ... more tests
```

### Deliverables
- ✅ All 5 agents implemented
- ✅ Unit tests for each agent
- ✅ Integration tests passing
- ✅ Documentation for each agent

### Success Metrics
- Each agent passes unit tests
- Integration tests show agents work with real APIs
- End-to-end agent chain completes successfully

---

## Phase 3: Orchestration (Week 5)

### Goals
- Implement LangGraph workflow
- Connect all agents
- Add error handling and retries

### Tasks

#### 3.1 LangGraph Workflow
- [ ] Implement `orchestrator/graph.py`
- [ ] Define agent nodes
- [ ] Create edges and conditional routing
- [ ] Add error handler node

```python
# Example implementation
from langgraph.graph import StateGraph, END

def create_provisioning_graph():
    workflow = StateGraph(ProvisioningState)

    # Add nodes
    workflow.add_node("research", research_agent_node)
    workflow.add_node("data_modeling", data_modeling_agent_node)
    workflow.add_node("infrastructure", infrastructure_agent_node)
    workflow.add_node("capi_creation", capi_creation_agent_node)
    workflow.add_node("demo_content", demo_content_agent_node)

    # Define flow
    workflow.set_entry_point("research")
    workflow.add_edge("research", "data_modeling")
    workflow.add_edge("data_modeling", "infrastructure")
    workflow.add_edge("infrastructure", "capi_creation")
    workflow.add_edge("capi_creation", "demo_content")
    workflow.add_edge("demo_content", END)

    return workflow.compile()
```

#### 3.2 State Persistence
- [ ] Configure checkpointer
- [ ] Test state recovery
- [ ] Implement state cleanup

#### 3.3 Error Handling
- [ ] Implement retry logic
- [ ] Add fallback strategies
- [ ] Create error notifications

### Deliverables
- ✅ Complete LangGraph workflow
- ✅ State persistence working
- ✅ Error handling robust

### Success Metrics
- Full workflow completes end-to-end
- State persists correctly
- Errors are handled gracefully

---

## Phase 4: API Development (Week 6)

### Goals
- Create FastAPI endpoints
- Implement progress streaming
- Add job management

### Tasks

#### 4.1 Provisioning Endpoints
- [ ] Implement `POST /api/provision/start`
- [ ] Implement `GET /api/provision/status/{job_id}`
- [ ] Implement `GET /api/provision/stream/{job_id}`
- [ ] Implement `GET /api/provision/assets/{job_id}`

#### 4.2 Background Task Management
- [ ] Set up background task executor
- [ ] Implement job queue
- [ ] Add job cancellation

#### 4.3 Progress Streaming
- [ ] Implement Server-Sent Events
- [ ] Create progress update mechanism
- [ ] Test with long-running jobs

```python
# Example SSE implementation
from fastapi.responses import StreamingResponse

@router.get("/stream/{job_id}")
async def stream_progress(job_id: str):
    async def generate():
        while True:
            state = await get_workflow_state(job_id)
            yield f"data: {json.dumps({
                'phase': state['current_phase'],
                'progress': state['progress_percentage']
            })}\n\n"

            if state['current_phase'] in ['completed', 'failed']:
                break

            await asyncio.sleep(2)

    return StreamingResponse(generate(), media_type="text/event-stream")
```

### Deliverables
- ✅ All API endpoints implemented
- ✅ Progress streaming working
- ✅ API documentation generated

### Success Metrics
- API endpoints respond correctly
- Progress updates stream in real-time
- Job management works reliably

---

## Phase 5: Frontend Development (Week 7-8)

### Goals
- Build CE dashboard
- Implement provisioning UI
- Create demo assets viewer

### Tasks

#### 5.1 CE Dashboard
- [ ] Create URL input form
- [ ] Add provisioning history list
- [ ] Implement job status cards

#### 5.2 Provisioning Progress UI
- [ ] Build progress tracker component
- [ ] Add real-time updates via SSE
- [ ] Create error display
- [ ] Add cancel/retry buttons

#### 5.3 Demo Assets Viewer
- [ ] Build golden queries panel
- [ ] Create demo script viewer
- [ ] Add data schema visualization
- [ ] Implement copy-to-clipboard

#### 5.4 Integration
- [ ] Connect frontend to backend APIs
- [ ] Test end-to-end flow
- [ ] Add loading states
- [ ] Implement error handling

### Deliverables
- ✅ CE dashboard functional
- ✅ Provisioning UI complete
- ✅ Demo assets displayed correctly

### Success Metrics
- CE can start provisioning from UI
- Progress updates display correctly
- Demo assets are accessible

---

## Phase 6: Testing & Optimization (Week 9-10)

### Goals
- Comprehensive testing
- Performance optimization
- Security hardening

### Tasks

#### 6.1 Testing
- [ ] End-to-end testing with 10+ websites
- [ ] Load testing (concurrent jobs)
- [ ] Error scenario testing
- [ ] Edge case handling

```python
# E2E test example
async def test_full_provisioning_flow():
    # Start provisioning
    response = await client.post("/api/provision/start", json={
        "customer_url": "https://test-company.com"
    })
    job_id = response.json()["job_id"]

    # Poll until complete
    while True:
        status = await client.get(f"/api/provision/status/{job_id}")
        if status.json()["current_phase"] in ["completed", "failed"]:
            break
        await asyncio.sleep(5)

    # Verify assets
    assets = await client.get(f"/api/provision/assets/{job_id}")
    assert "golden_queries" in assets.json()
    assert "data_agent_id" in assets.json()
```

#### 6.2 Performance Optimization
- [ ] Profile agent execution times
- [ ] Optimize slow operations
- [ ] Implement caching where appropriate
- [ ] Parallelize independent tasks

#### 6.3 Security
- [ ] Input validation hardening
- [ ] API key rotation setup
- [ ] Rate limiting implementation
- [ ] Audit logging

### Deliverables
- ✅ Comprehensive test suite
- ✅ Performance benchmarks
- ✅ Security audit completed

### Success Metrics
- 90%+ test coverage
- Average provisioning time < 5 minutes
- Zero critical security issues

---

## Phase 7: Documentation & Deployment (Week 11-12)

### Goals
- Complete documentation
- Deploy to production
- Train CEs

### Tasks

#### 7.1 Documentation
- [ ] API documentation (OpenAPI/Swagger)
- [ ] User guide for CEs
- [ ] Architecture documentation
- [ ] Troubleshooting guide

#### 7.2 Deployment
- [ ] Containerize application (Docker)
- [ ] Set up Cloud Run deployment
- [ ] Configure CI/CD pipeline
- [ ] Set up monitoring and alerting

```dockerfile
# Dockerfile example
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY newfrontend/conversational-api-demo-frontend/dist/ ./frontend/dist/

EXPOSE 8000

CMD ["uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 7.3 Training
- [ ] Create demo videos
- [ ] Write CE playbook
- [ ] Conduct training sessions
- [ ] Gather feedback

### Deliverables
- ✅ Complete documentation
- ✅ Production deployment
- ✅ CEs trained

### Success Metrics
- Application deployed successfully
- CEs can use system independently
- Positive feedback from CEs

---

## Development Milestones

| Milestone | Week | Description | Success Criteria |
|-----------|------|-------------|------------------|
| M1: Foundation | 2 | Basic infrastructure ready | Base agent executes |
| M2: Agents | 4 | All agents implemented | Agents pass unit tests |
| M3: Orchestration | 5 | LangGraph workflow complete | E2E workflow runs |
| M4: API | 6 | Backend API functional | API tests pass |
| M5: Frontend | 8 | UI complete | CE can provision from UI |
| M6: Testing | 10 | System tested & optimized | 90%+ success rate |
| M7: Launch | 12 | Production deployment | CEs using in demos |

---

## Risk Mitigation

### Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| API rate limits | High | Medium | Implement caching, queue requests |
| Web scraping failures | Medium | High | Multiple scraping strategies, fallback to manual input |
| BigQuery quota limits | High | Low | Request quota increase, implement cleanup |
| Claude API costs | Medium | Medium | Cache responses, optimize prompts |
| Schema generation errors | High | Medium | Provide template fallbacks, manual override |

### Operational Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Concurrent job overload | Medium | Medium | Implement job queue, rate limiting |
| State data growth | Low | High | Implement data retention policy |
| Failed provisioning cleanup | Medium | Medium | Implement cleanup jobs, manual tools |
| CE training gaps | Medium | Low | Comprehensive documentation, training |

---

## Resource Requirements

### Development Team
- 1 Backend Engineer (full-time, 12 weeks)
- 1 Frontend Engineer (part-time, 4 weeks)
- 1 QA Engineer (part-time, 4 weeks)

### Infrastructure
- Google Cloud project with:
  - BigQuery enabled
  - Conversational Analytics API enabled
  - Cloud Run (for deployment)
  - Secret Manager
- Anthropic API account (Claude access)

### Budget Estimates
- Anthropic API: ~$200-500/month (development + testing)
- Google Cloud: ~$100-300/month (BigQuery, API calls)
- Development time: 12 weeks

---

## Success Criteria

### MVP Success Criteria (Phase 1-4)
- [ ] Single CE can provision a demo from a URL
- [ ] Provisioning completes in < 10 minutes
- [ ] Generated demo is usable for customer presentation
- [ ] System handles at least 3 common business domains

### Production Success Criteria (Phase 7)
- [ ] 10+ CEs can use the system
- [ ] 90%+ provisioning success rate
- [ ] Average provisioning time < 5 minutes
- [ ] Supports 15+ business domains
- [ ] < 5% manual intervention rate

### Long-term Success Criteria (3 months post-launch)
- [ ] 50+ demos generated
- [ ] 95%+ success rate
- [ ] < 2% manual intervention
- [ ] Positive CE feedback (4+/5 rating)
- [ ] Expanded to support custom data sources

---

## Next Steps

1. **Get approval** for the architecture and plan
2. **Set up development environment** (Phase 1)
3. **Start with Research Agent** as proof of concept
4. **Iterate based on feedback**
5. **Scale to full system**

---

## Questions to Address

1. **Budget**: What's the approved budget for API costs?
2. **Timeline**: Is 12 weeks acceptable, or do we need to accelerate?
3. **Scope**: Should we support custom data upload in v1?
4. **Deployment**: Cloud Run or other Google Cloud service?
5. **Access**: Who should have access to the CE dashboard?
6. **Data Retention**: How long should we keep provisioned demos?

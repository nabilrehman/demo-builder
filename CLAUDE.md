# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Demo Generation System** for Google Cloud's Conversational API (CAPI). It automatically provisions end-to-end conversational analytics demos by:

1. Analyzing a customer's website
2. Generating a compelling demo narrative
3. Designing a BigQuery schema tailored to the business
4. Creating realistic synthetic data
5. Provisioning BigQuery resources and CAPI agents
6. Generating YAML system instructions
7. Validating the demo with test queries

The system uses a **7-agent LangGraph pipeline** coordinated by `demo_orchestrator.py`, with each agent specialized for a specific task.

## Architecture

### Frontend (React + Vite + TypeScript)
- **Location**: `newfrontend/conversational-api-demo-frontend/`
- **Tech Stack**: React, Vite, TypeScript, shadcn/ui, TailwindCSS, Firebase Auth
- **Key Components**:
  - `CEDashboard.tsx` - Main provisioning interface
  - `ProvisionProgress.tsx` - Real-time job progress tracking
  - `DemoAssets.tsx` - Display generated demo artifacts
  - Firebase auth integration for Google-only access

### Backend (FastAPI + Python)
- **Location**: `backend/`
- **Entry Point**: `api.py` - Serves both API and static frontend files
- **Key Routes**:
  - `/api/provision/*` - Demo provisioning endpoints (routes/provisioning.py)
  - `/api/user/*` - User management endpoints (routes/user_management.py)
- **Services**:
  - `firestore_service.py` - Job persistence and user data
  - `user_service.py` - User profile management

### Agentic Service (7-Agent Pipeline)
- **Location**: `backend/agentic_service/`
- **Orchestrator**: `demo_orchestrator.py` - LangGraph state machine
- **Agents** (in order of execution):
  1. **Research Agent** (`research_agent_v2_*.py`) - Crawls customer website, analyzes business model
  2. **Demo Story Agent** (`demo_story_agent*.py`) - Creates narrative and golden queries
  3. **Data Modeling Agent** (`data_modeling_agent*.py`) - Designs BigQuery schema
  4. **Synthetic Data Generator** (`synthetic_data_generator_markdown.py`) - LLM-generated realistic data
  5. **Infrastructure Agent** (`infrastructure_agent*.py`) - Provisions BigQuery dataset/tables/CAPI agent
  6. **CAPI Instruction Generator** (`capi_instruction_generator*.py`) - Generates YAML system instructions
  7. **Demo Validator** (`demo_validator*.py`) - Tests golden queries (non-blocking)

### Agent Model Selection
Agents support **dynamic model selection** (Gemini vs Claude) via environment variables:
- `RESEARCH_AGENT_MODEL` - Default: gemini (2x faster)
- `DEMO_STORY_AGENT_MODEL` - Default: gemini (identical quality, 2x faster)
- `DATA_MODELING_AGENT_MODEL` - Default: claude (user preference)
- `CAPI_AGENT_MODEL` - Default: claude (quality critical)

Configuration is centralized in `backend/agentic_service/config/agent_config.py`.

## Common Development Commands

### Local Development

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your PROJECT_ID, GEMINI_API_KEY, etc.

# Run backend server
uvicorn api:app --reload --host 0.0.0.0 --port 8080
```

#### Frontend
```bash
cd newfrontend/conversational-api-demo-frontend
npm install
npm run dev  # Development server on port 5173
npm run build  # Production build to dist/
```

### Testing

#### Manual Testing Flow
1. Start backend: `uvicorn api:app --reload --port 8080`
2. Start frontend: `cd newfrontend/... && npm run dev`
3. Open http://localhost:5173
4. Enter customer URL (e.g., https://www.nike.com)
5. Monitor progress at `/provision-progress?jobId=<id>`
6. View results at `/demo-assets?jobId=<id>`

#### API Testing
```bash
# Start a provisioning job
curl -X POST http://localhost:8080/api/provision/start \
  -H "Content-Type: application/json" \
  -d '{"customer_url": "https://www.nike.com"}'

# Check job status
curl http://localhost:8080/api/provision/status/<job_id>
```

### Deployment (Cloud Run)

#### Build and Deploy

**Production deployment to demo-gen-capi-prod:**

```bash
# 1. Build Docker image with tag
gcloud builds submit \
  --tag us-central1-docker.pkg.dev/bq-demos-469816/capi-demo/capi-demo:firebase-auth-persistence \
  --project=bq-demos-469816

# 2. Deploy to Cloud Run with all environment variables
gcloud run deploy demo-gen-capi-prod \
  --image us-central1-docker.pkg.dev/bq-demos-469816/capi-demo/capi-demo:firebase-auth-persistence \
  --region us-central1 \
  --project bq-demos-469816 \
  --platform managed \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars="ENABLE_AUTH=true,FIREBASE_PROJECT_ID=bq-demos-469816,PROJECT_ID=bq-demos-469816,LOCATION=global,ENVIRONMENT=production,GEMINI_API_KEY=AIzaSyCo3lMlWXexEQW45mS3nH9J-C6Cf9XZmZk,DATA_AGENT_ID=nike_demo_agent_20251005,DATASET_ID=nike_capi_demo_20251005,DISPLAY_NAME=Nike Analytics Assistant,DEMO_NUM_QUERIES=1,DEMO_NUM_SCENES=1,DEMO_NUM_ENTITIES=4,RESEARCH_AGENT_MODEL=gemini,DEMO_STORY_AGENT_MODEL=gemini,DATA_MODELING_AGENT_MODEL=claude,CAPI_AGENT_MODEL=claude,V2_MAX_PAGES=30,V2_MAX_DEPTH=3,V2_ENABLE_BLOG=false,V2_ENABLE_LINKEDIN=false,V2_ENABLE_YOUTUBE=false"
```

**Note:**
- Service name: `demo-gen-capi-prod`
- Production URL: https://demo-gen-capi-prod-549403515075.us-central1.run.app/
- Docker repository: `us-central1-docker.pkg.dev/bq-demos-469816/capi-demo/capi-demo`
- Tag format: Use branch names or version tags (e.g., `:firebase-auth-persistence`, `:auth-final`, `:v1.0.0`)
- Environment: All env vars must be explicitly set (Cloud Run doesn't read .env files)

#### Required IAM Permissions
The Cloud Run service account needs:
- `BigQuery Data Viewer` - Read BigQuery data
- `BigQuery Data Editor` - Create datasets/tables
- `Gemini Data Analytics Data Agent Creator` - Create CAPI agents
- `Gemini Data Analytics Data Agent User` - Create conversations
- `Gemini for Google Cloud User` - LLM access

### Firebase Configuration

Firebase is used for authentication (Google Sign-In only) and job persistence:

1. Enable Firebase Authentication with Google provider
2. Add authorized domains to Firebase Console → Authentication → Settings
3. Service account credentials are auto-detected from GCP environment

## Key Configuration Files

### Environment Variables (backend/.env)
```bash
PROJECT_ID=bq-demos-469816          # GCP project
LOCATION=global                      # CAPI region
GEMINI_API_KEY=<key>                 # Gemini API access

# Demo complexity controls
DEMO_NUM_QUERIES=6                   # Golden queries (1-20)
DEMO_NUM_SCENES=4                    # Story scenes (1-7)
DEMO_NUM_ENTITIES=8                  # Data entities (3-20)

# Agent model selection
RESEARCH_AGENT_MODEL=gemini          # gemini|claude
DEMO_STORY_AGENT_MODEL=gemini        # gemini|claude
DATA_MODELING_AGENT_MODEL=claude     # gemini|claude
CAPI_AGENT_MODEL=claude              # gemini|claude

# Research agent V2 configuration
V2_MAX_PAGES=30                      # Website crawl depth
V2_MAX_DEPTH=3                       # Crawl depth
```

## Important Implementation Details

### Frontend-Backend Integration
The backend serves the built React frontend as static files. The `api.py` file contains absolute path logic to locate the frontend `dist/` directory in both local and containerized environments:

```python
if os.path.exists(os.path.join(APP_ROOT, "newfrontend", ...)):
    FRONTEND_DIST_DIR = ...  # Docker structure
else:
    FRONTEND_DIST_DIR = ...  # Local structure
```

**Critical**: Always build the frontend before testing the integrated setup.

### Job State Management
Jobs are tracked in-memory via `JobStateManager` singleton and persisted to Firestore. Each job has:
- **Real-time progress tracking**: 7 agents × 100% = overall progress
- **Streaming logs**: Agents emit structured log events
- **Non-blocking validation**: Demo Validator failures don't stop pipeline

### LLM Optimization Strategy
The system uses **Gemini 2.5 Pro** for most agents (speed) and **Claude Sonnet 4.5** for quality-critical tasks (CAPI YAML generation). This is based on benchmarks in `benchmarks/AGENT_SELECTOR_GUIDE.md`.

**Unified LLM client**: `backend/agentic_service/utils/vertex_llm_client.py` supports:
- Gemini via API (uses `GEMINI_API_KEY`)
- Gemini via Vertex AI
- Claude via Vertex AI (uses `anthropic[vertex]` SDK)

### Synthetic Data Generation
**ALWAYS uses LLM-based generation** (no Faker fallback). The markdown-based generator (`synthetic_data_generator_markdown.py`) produces business-realistic data by:
1. Passing demo story context to LLM
2. Generating data as markdown tables
3. Parsing and validating output
4. Uploading to BigQuery

### CORS and Static File Serving
The backend has permissive CORS (`allow_origins=["*"]`) for development. In the Dockerfile:
1. **Stage 1**: Builds React app → `dist/` folder
2. **Stage 2**: Copies `dist/` to Python container, mounts at `/assets`

## Common Issues and Solutions

### "Directory does not exist" error on Cloud Run
- **Cause**: Incorrect file path logic in `api.py`
- **Fix**: Use absolute paths via `os.path.abspath(__file__)`

### IAM Permission Denied
- **Cause**: Missing Cloud Run service account roles
- **Fix**: Grant all required roles listed in "Deployment" section

### Frontend not loading on Cloud Run
- **Cause**: Static files not copied or mounted correctly
- **Fix**: Verify Dockerfile `COPY --from=build-frontend` and `app.mount("/assets", ...)`

### Validation failures blocking pipeline
- **Cause**: Demo Validator errors stop job completion
- **Fix**: Validator is non-blocking by design (check `demo_validator_optimized.py`)

### Agent timeout errors
- **Cause**: LLM calls timing out (default 2min)
- **Fix**: Increase timeout in `vertex_llm_client.py` (currently 10min for Claude)

## File Structure Quick Reference

```
demo-gen-capi/
├── backend/
│   ├── api.py                          # Main FastAPI app + static file serving
│   ├── requirements.txt                # Python dependencies
│   ├── .env                            # Environment configuration
│   ├── routes/                         # API route handlers
│   │   ├── provisioning.py             # Demo provisioning endpoints
│   │   └── user_management.py          # User profile endpoints
│   ├── services/                       # Business logic
│   │   ├── firestore_service.py        # Job/user persistence
│   │   └── user_service.py             # User management
│   ├── middleware/
│   │   └── auth.py                     # Firebase auth middleware
│   └── agentic_service/
│       ├── demo_orchestrator.py        # LangGraph state machine
│       ├── agents/                     # 7 specialized agents
│       ├── utils/
│       │   ├── vertex_llm_client.py    # Unified LLM client
│       │   └── job_state_manager.py    # In-memory job tracking
│       └── config/
│           └── agent_config.py         # Dynamic model selection
├── newfrontend/conversational-api-demo-frontend/
│   ├── src/
│   │   ├── components/                 # React components
│   │   │   ├── CEDashboard.tsx         # Main UI
│   │   │   ├── ProvisionProgress.tsx   # Job progress view
│   │   │   └── DemoAssets.tsx          # Results view
│   │   └── lib/
│   │       └── firebase.ts             # Firebase config
│   └── package.json                    # Node dependencies
├── Dockerfile                           # Multi-stage build
└── CLAUDE.md                            # This file
```

## Testing Checklist for New Changes

1. **Backend changes**: Test with `uvicorn api:app --reload` + manual API calls
2. **Agent changes**: Run single-agent tests or full pipeline with test URL
3. **Frontend changes**: Test with `npm run dev`, verify API integration
4. **Full integration**: Build frontend (`npm run build`), run backend, test end-to-end
5. **Cloud Run**: Deploy with `gcloud run deploy`, test public URL
6. **Firebase auth**: Test Google Sign-In flow, verify Firestore writes
7. **Performance**: Monitor agent execution times, check for timeouts

## Development Workflow

When adding new features:
1. Update agent logic in `backend/agentic_service/agents/`
2. Update orchestrator if adding new agents (`demo_orchestrator.py`)
3. Update state schema if new data fields needed (`DemoGenerationState`)
4. Update frontend to display new data/features
5. Update `.env.example` for new configuration options
6. Test locally → Deploy to Cloud Run → Verify in production

## Debugging Tips

- **Backend logs**: Check `backend.log` or Cloud Run logs
- **Agent execution**: Look for emoji markers (🔍, ✅, ❌) in logs
- **LLM responses**: Enable debug logging in `vertex_llm_client.py`
- **Job state**: Call `/api/provision/status/<job_id>` to inspect
- **Firestore data**: Check Firebase Console → Firestore Database

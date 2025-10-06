# Agentic Application Architecture - Executive Summary

## 🎯 Vision

Transform the current Conversational Analytics API demo from a **manual, CLI-driven boilerplate** into a **fully autonomous agentic application** where Customer Engineers (CEs) simply input a customer's website URL and the system automatically:

1. **Researches** the customer's business domain
2. **Generates** synthetic data matching their business model
3. **Provisions** BigQuery datasets and tables
4. **Creates** a Conversational Analytics API agent
5. **Generates** golden queries for demo purposes
6. **Deploys** a ready-to-use conversational analytics interface

## 🔄 Current vs. Future State

### Current State (Manual Workflow)
```
CE manually:
├── Reads GEMINI.md instructions
├── Runs Gemini CLI commands to understand business
├── Manually configures environment variables
├── Runs Python scripts to generate data
├── Manually creates BigQuery datasets
├── Manually loads CSV files to BigQuery
├── Configures data agent settings
└── Starts frontend/backend manually
```

### Future State (Agentic Workflow)
```
CE:
└── Enters customer URL in web interface

System Autonomously:
├── Agent 1: Customer Research Agent
│   ├── Scrapes and analyzes customer website
│   ├── Identifies business domain and data model
│   └── Generates business context
│
├── Agent 2: Data Modeling Agent
│   ├── Designs appropriate database schema
│   ├── Generates realistic synthetic data
│   └── Creates sample records
│
├── Agent 3: Infrastructure Provisioning Agent
│   ├── Creates BigQuery dataset
│   ├── Creates and loads tables
│   ├── Validates data integrity
│   └── Sets up permissions
│
├── Agent 4: Conversational Analytics Agent Creator
│   ├── Creates data agent via API
│   ├── Configures system instructions
│   ├── Links to BigQuery datasources
│   └── Tests agent functionality
│
├── Agent 5: Demo Content Generator Agent
│   ├── Generates golden queries
│   ├── Creates demo script
│   ├── Prepares sample Q&A
│   └── Generates documentation
│
└── Orchestrator Agent
    ├── Coordinates all sub-agents
    ├── Manages state across workflow
    ├── Handles errors and retries
    └── Provides progress updates to UI
```

## 🏗️ Recommended Architecture

**Framework Choice: LangGraph + Claude SDK**

### Why This Combination?

1. **LangGraph** for orchestration:
   - Robust state management across multi-step workflow
   - Graph-based workflow with conditional routing
   - Built-in checkpointing for long-running processes
   - Perfect for complex, branching agent workflows
   - Excellent error handling and retry logic

2. **Claude (via Anthropic SDK)** for agent intelligence:
   - Superior reasoning for complex tasks
   - Excellent tool use capabilities
   - Strong performance on code generation
   - Great at structured data extraction
   - Can handle web research and analysis

3. **Google Conversational Analytics API** for the final data agent:
   - Already integrated in current system
   - Specialized for data querying
   - Works with BigQuery natively

## 📊 High-Level System Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     Customer Engineer UI                     │
│              (React Frontend - Enhanced)                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ POST /api/provision
                       │ { "customer_url": "..." }
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              FastAPI Backend + LangGraph                     │
│                   (Orchestrator)                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼─────┐ ┌─────▼──────┐ ┌────▼─────┐
│  Research   │ │   Data     │ │ Infra    │
│   Agent     │ │  Modeling  │ │Provision │
│  (Claude)   │ │  Agent     │ │ Agent    │
└─────────────┘ └────────────┘ └──────────┘
        │              │              │
        └──────────────┼──────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼─────┐ ┌─────▼──────┐       │
│CAPI Agent   │ │   Demo     │       │
│  Creator    │ │ Content    │       │
│   Agent     │ │  Generator │       │
└─────────────┘ └────────────┘       │
                                     │
                       ┌─────────────▼──────────────┐
                       │     Google Cloud           │
                       │  - BigQuery                │
                       │  - Conversational API      │
                       └────────────────────────────┘
```

## 🎯 Success Metrics

1. **Time Reduction**: Manual setup (~2-3 hours) → Automated (<15 minutes)
2. **Accuracy**: 95%+ data schema accuracy for common business domains
3. **CE Efficiency**: 1 input (URL) vs. 15+ manual configuration steps
4. **Scalability**: Support 10+ concurrent provisioning requests
5. **Reliability**: 90%+ success rate for end-to-end provisioning

## 📁 Deliverables

1. **Enhanced Backend** (`backend/agentic_service/`)
   - LangGraph workflow orchestrator
   - 5 specialized Claude-powered agents
   - State management and persistence
   - Progress tracking API

2. **Enhanced Frontend** (`newfrontend/`)
   - URL input interface for CEs
   - Real-time provisioning progress tracker
   - Generated demo script viewer
   - Golden queries dashboard

3. **Documentation**
   - Architecture decision records
   - Agent design specifications
   - API documentation
   - Deployment guide

## 🚀 Next Steps

See detailed planning documents:
- `01-DETAILED_ARCHITECTURE.md` - Technical architecture
- `02-AGENT_SPECIFICATIONS.md` - Individual agent designs
- `03-IMPLEMENTATION_PLAN.md` - Phased development approach
- `04-FRAMEWORK_COMPARISON.md` - Framework evaluation (including ADK research)
- `05-CODE_EXAMPLES.md` - Sample implementations

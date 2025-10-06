# Agentic Provisioning System - Architecture Documentation

## 📚 Documentation Index

This directory contains comprehensive architecture planning for transforming the Conversational Analytics API demo into a fully autonomous agentic application.

### Documents

1. **[00-EXECUTIVE_SUMMARY.md](./00-EXECUTIVE_SUMMARY.md)**
   - High-level vision and goals
   - Current vs. future state comparison
   - System flow overview
   - Success metrics

2. **[01-DETAILED_ARCHITECTURE.md](./01-DETAILED_ARCHITECTURE.md)**
   - Complete technical architecture
   - Component specifications
   - Technology stack details
   - Data flow sequences
   - Security and performance considerations

3. **[02-AGENT_SPECIFICATIONS.md](./02-AGENT_SPECIFICATIONS.md)**
   - Individual agent designs (all 5 agents)
   - Agent inputs/outputs
   - Tool requirements
   - Prompt templates
   - Success criteria

4. **[03-IMPLEMENTATION_PLAN.md](./03-IMPLEMENTATION_PLAN.md)**
   - Phased development approach (7 phases)
   - Week-by-week breakdown
   - Milestones and deliverables
   - Risk mitigation strategies
   - Resource requirements

5. **[04-FRAMEWORK_COMPARISON.md](./04-FRAMEWORK_COMPARISON.md)**
   - Comprehensive framework evaluation
   - LangGraph vs CrewAI vs Claude SDK vs Gemini
   - ADK research findings (no such framework exists)
   - Cost analysis
   - Final recommendation: **LangGraph + Claude SDK**

6. **[05-CODE_EXAMPLES.md](./05-CODE_EXAMPLES.md)**
   - Complete LangGraph workflow implementation
   - Research agent example
   - Web scraping tools
   - FastAPI endpoints
   - React components with SSE

---

## 🎯 Quick Start

### What This System Does

**Current**: Customer Engineers manually configure demos using Gemini CLI commands and manual steps.

**Future**: Customer Engineers enter a customer URL, and the system autonomously:
1. Researches the customer's business
2. Designs appropriate database schema
3. Generates realistic synthetic data
4. Provisions BigQuery infrastructure
5. Creates Conversational Analytics API agent
6. Generates golden queries and demo script

**Result**: Ready-to-use demo in <5 minutes, zero manual configuration.

---

## 🏗️ Recommended Architecture

### **LangGraph + Claude SDK + Google Conversational Analytics API**

```
┌─────────────────────────────────────┐
│    LangGraph Orchestrator           │
│  (State Management & Workflow)      │
└────────────┬────────────────────────┘
             │
    ┌────────┼────────┐
    │        │        │
┌───▼───┐ ┌─▼──┐ ┌──▼───┐
│Research│ │Data│ │Infra │
│ (Claude)│ │Model│ │(BQ) │
└────────┘ └────┘ └──────┘
    │        │        │
    └────────┼────────┘
             │
    ┌────────┼────────┐
    │        │        │
┌───▼───┐ ┌─▼──────┐
│ CAPI  │ │  Demo  │
│Creator│ │Content │
│(CAPI) │ │(Claude)│
└───────┘ └────────┘
```

### Why This Stack?

- **LangGraph**: Best-in-class orchestration, state management, error handling
- **Claude**: Superior reasoning for research, schema design, content generation
- **Google CAPI**: Native BigQuery integration for the final data agent

### Cost per Demo: ~$0.16 (LLM) + $0.01 (infrastructure) = **$0.17**

---

## 📋 Implementation Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| 1. Foundation | 2 weeks | Base infrastructure, state management |
| 2. Agents | 2 weeks | All 5 agents implemented and tested |
| 3. Orchestration | 1 week | LangGraph workflow complete |
| 4. API | 1 week | Backend endpoints with SSE |
| 5. Frontend | 2 weeks | CE dashboard and progress UI |
| 6. Testing | 2 weeks | E2E tests, optimization |
| 7. Deployment | 2 weeks | Production deployment, CE training |
| **Total** | **12 weeks** | **Production-ready system** |

---

## 🔍 Key Design Decisions

### 1. Why LangGraph Over CrewAI?

- **State persistence**: Built-in checkpointing for resume capability
- **Flexibility**: More control over workflow logic
- **Production-ready**: Battle-tested in production systems
- **Debugging**: Superior state inspection and replay

### 2. Why Claude Over Gemini for Agents?

- **Reasoning quality**: Significantly better at complex business analysis
- **Tool use reliability**: More consistent function calling
- **Code generation**: Better schema and data generation
- **Worth the cost**: $0.50 premium per job vs. manual intervention savings

### 3. Why NOT Pure Google?

- We DO use Google CAPI for the final data agent (best fit)
- We DON'T use Gemini for orchestration (Claude is superior for this use case)
- Hybrid approach gets best of both worlds

### 4. What About Google's ADK?

**Finding**: After extensive research, **no such product exists** as of January 2025.
- Not in Google Cloud documentation
- Not on PyPI or GitHub
- Not mentioned in Vertex AI docs
- May be confused with Vertex AI Agent Builder (different product)

---

## 🚀 Getting Started with Implementation

### Phase 1: Set Up Environment

```bash
# Clone/navigate to project
cd /home/admin_/final_demo/capi/demo-gen-capi

# Install dependencies
pip install anthropic langgraph langchain-core google-cloud-bigquery

# Create directory structure
mkdir -p backend/agentic_service/{orchestrator,agents,tools,models,utils}
mkdir -p backend/routes

# Set up environment variables
cat > backend/.env << EOF
ANTHROPIC_API_KEY=your_key_here
DEVSHELL_PROJECT_ID=your_project_id
EOF
```

### Phase 2: Build First Agent (Proof of Concept)

Start with the Research Agent to validate the approach:

1. Copy code from `05-CODE_EXAMPLES.md`
2. Implement web scraping tool
3. Test with 5 different company websites
4. Validate output quality

### Phase 3: Scale to Full System

Once POC works:
1. Implement remaining 4 agents
2. Build LangGraph workflow
3. Create API endpoints
4. Build frontend UI

---

## 📊 Success Metrics

### MVP (End of Phase 4)
- [ ] Single CE can provision from URL
- [ ] Provisioning completes in <10 minutes
- [ ] Supports 3+ business domains
- [ ] Generated demo is usable

### Production (End of Phase 7)
- [ ] 10+ CEs can use system
- [ ] 90%+ success rate
- [ ] <5 minute average provisioning time
- [ ] Supports 15+ business domains

### Long-term (3 months post-launch)
- [ ] 50+ demos generated
- [ ] 95%+ success rate
- [ ] <2% manual intervention rate
- [ ] 4+/5 CE satisfaction rating

---

## 🛠️ Technology Stack

### Backend
```python
# Core
fastapi==0.109.0
uvicorn==0.27.0

# Agentic
anthropic==0.18.0
langgraph==0.0.20
langchain-core==0.1.0

# Google Cloud
google-cloud-bigquery==3.17.0
google-cloud-geminidataanalytics==0.1.0

# Utilities
pydantic==2.6.0
aiohttp==3.9.0
beautifulsoup4==4.12.0
faker==22.0.0
```

### Frontend
```json
{
  "react": "^18.2.0",
  "vite": "^5.0.0",
  "@tanstack/react-query": "^5.0.0",
  "shadcn/ui": "latest"
}
```

---

## 🔐 Security Considerations

1. **API Keys**: Use Google Secret Manager
2. **Input Validation**: Sanitize all customer URLs
3. **Rate Limiting**: Prevent abuse
4. **BigQuery Permissions**: Minimal service account permissions
5. **Audit Logging**: Track all provisioning activities

---

## 📞 Next Steps

1. **Review** this documentation with stakeholders
2. **Approve** architecture and timeline
3. **Allocate** resources (developers, budget)
4. **Start** Phase 1 implementation
5. **Iterate** based on POC feedback

---

## 📝 Notes

- All code examples are production-ready starting points
- Architecture is designed for scalability and maintainability
- Cost estimates are conservative (actual may be lower)
- Timeline assumes full-time dedicated development
- Can accelerate with additional resources

---

## 🤝 Contributing

This is an internal planning document. For questions or suggestions:

1. Review the detailed docs (01-05)
2. Check code examples (05)
3. Consult implementation plan (03)
4. Reach out to architecture team

---

**Last Updated**: 2025-10-04
**Status**: Planning Phase
**Next Milestone**: Phase 1 Kickoff

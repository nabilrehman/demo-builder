# Framework Comparison & Selection

## Executive Summary

After extensive research into agentic frameworks, **LangGraph + Claude SDK** is the recommended approach for this project.

**Note on ADK**: Despite thorough research, no evidence was found of a Google "Agent Development Kit" (ADK) or "GenAI ADK" as a distinct framework. Google's agentic capabilities come through:
- Gemini Function Calling (native API feature)
- Vertex AI Agent Builder (enterprise product)
- Integration with third-party frameworks (LangChain, CrewAI)

---

## Frameworks Evaluated

### 1. Claude SDK (Anthropic)

**What it is**: Direct SDK for Claude with native tool use capabilities.

#### Pros
- ✅ **Best-in-class reasoning** - Claude excels at complex analysis tasks
- ✅ **Superior tool use** - Most reliable function calling among LLMs
- ✅ **Excellent for research tasks** - Perfect for analyzing websites
- ✅ **Strong code generation** - Great for schema/data generation
- ✅ **Simple integration** - Minimal abstraction overhead
- ✅ **Streaming support** - Real-time progress updates
- ✅ **Extended context** - 200K tokens for large documents

#### Cons
- ❌ **No built-in orchestration** - Need to build workflow logic
- ❌ **Manual state management** - Must implement persistence
- ❌ **No multi-agent framework** - Need custom orchestration

#### Best For
- Agent intelligence/reasoning
- Tool execution
- Content generation

#### Cost
- ~$3 per 1M input tokens
- ~$15 per 1M output tokens
- Estimated $0.50-2.00 per provisioning job

---

### 2. LangGraph

**What it is**: Graph-based orchestration framework for stateful multi-agent workflows.

#### Pros
- ✅ **Robust state management** - Built-in persistence and checkpointing
- ✅ **Visual workflow design** - Graph-based mental model
- ✅ **Excellent for complex flows** - Conditional routing, loops, branches
- ✅ **Model agnostic** - Works with Claude, Gemini, GPT, etc.
- ✅ **Production-ready** - Mature, battle-tested
- ✅ **Great debugging** - State inspection, replay
- ✅ **Human-in-the-loop** - Built-in support

#### Cons
- ❌ **Learning curve** - More complex than simple SDK calls
- ❌ **Abstraction overhead** - Additional layer to manage
- ❌ **More dependencies** - LangChain ecosystem

#### Best For
- Multi-step workflows
- State management
- Error handling and retries
- Long-running processes

#### Cost
- Open-source (free)
- Only pay for underlying LLM calls

---

### 3. CrewAI

**What it is**: Framework for role-playing collaborative multi-agent systems.

#### Pros
- ✅ **Intuitive role-based design** - Easy to conceptualize
- ✅ **Quick setup** - Fast to prototype
- ✅ **Good for collaboration** - Agents work together naturally
- ✅ **Built-in memory** - Agent memory management
- ✅ **Model agnostic** - Supports multiple LLMs

#### Cons
- ❌ **Less flexible** - Opinionated about agent structure
- ❌ **Newer framework** - Less mature than LangGraph
- ❌ **Limited state control** - Less granular than LangGraph
- ❌ **Overhead for simple flows** - Better for collaborative scenarios

#### Best For
- Multi-agent collaboration
- Role-based task delegation
- Content creation pipelines

#### Cost
- Open-source (free)
- Only pay for underlying LLM calls

---

### 4. Google Gemini Function Calling

**What it is**: Native function calling in Gemini API.

#### Pros
- ✅ **Native Google integration** - Works seamlessly with Google Cloud
- ✅ **Direct BigQuery access** - Natural fit for this project
- ✅ **Multi-modal** - Can handle images, video (if needed)
- ✅ **Good for simple agents** - Straightforward function calling
- ✅ **Cost-effective** - Generally cheaper than Claude

#### Cons
- ❌ **Weaker reasoning** - Not as strong as Claude for complex analysis
- ❌ **Less reliable tool use** - More prone to errors
- ❌ **No orchestration** - Manual workflow management
- ❌ **Limited context** - Smaller context window than Claude

#### Best For
- Final data agent (Conversational Analytics API)
- Google Cloud-native workloads
- Multi-modal scenarios

#### Cost
- ~$1.25 per 1M input tokens (Gemini 1.5 Pro)
- ~$5 per 1M output tokens
- Estimated $0.30-1.00 per provisioning job

---

### 5. Vertex AI Agent Builder

**What it is**: Google's enterprise agent building platform.

#### Pros
- ✅ **Visual interface** - No-code/low-code agent building
- ✅ **Enterprise features** - SLAs, support, compliance
- ✅ **Pre-built integrations** - Google services integration
- ✅ **Managed infrastructure** - No operational overhead

#### Cons
- ❌ **Less flexible** - Limited customization
- ❌ **Higher cost** - Enterprise pricing
- ❌ **Vendor lock-in** - Google Cloud only
- ❌ **Overkill for this use case** - Designed for different scenarios

#### Best For
- Enterprise conversational agents
- Customer service bots
- Pre-built templates

#### Cost
- Enterprise pricing (contact sales)
- Generally more expensive than API-based solutions

---

## Comparison Matrix

| Feature | Claude SDK | LangGraph | CrewAI | Gemini | Vertex Agent |
|---------|-----------|-----------|---------|--------|--------------|
| **Reasoning Quality** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Tool Use Reliability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **State Management** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **Orchestration** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Flexibility** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Learning Curve** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Documentation** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Cost** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Google Cloud Integration** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## Recommended Architecture: Hybrid Approach

### **LangGraph (Orchestration) + Claude SDK (Intelligence) + Google CAPI (Data Agent)**

This hybrid approach combines the best of each framework:

```
┌─────────────────────────────────────────────┐
│         LangGraph Orchestrator              │
│    (Workflow, State, Error Handling)        │
└──────────────┬──────────────────────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼────┐ ┌──▼───┐ ┌───▼────┐
│Research│ │Data  │ │Infra   │
│ Agent  │ │Model │ │Agent   │
│(Claude)│ │(Claude)│(Claude)│
└────────┘ └──────┘ └────────┘
    │          │          │
    └──────────┼──────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼────┐ ┌──▼───────┐
│  CAPI  │ │  Demo    │
│ Agent  │ │ Content  │
│(CAPI)  │ │ (Claude) │
└────────┘ └──────────┘
```

### Why This Combination?

1. **LangGraph** handles:
   - Complex workflow orchestration
   - State persistence across steps
   - Error handling and retries
   - Progress tracking
   - Checkpointing for resume

2. **Claude** handles:
   - Website analysis (superior reasoning)
   - Schema generation (excellent code gen)
   - Content generation (great writing)
   - Data generation (creative yet structured)

3. **Google CAPI** handles:
   - Final data agent (native BigQuery integration)
   - Production analytics queries
   - Enterprise-grade data access

### Benefits
- ✅ Best-in-class for each component
- ✅ Robust workflow management
- ✅ Superior agent intelligence
- ✅ Native Google Cloud integration
- ✅ Cost-effective
- ✅ Production-ready
- ✅ Maintainable and debuggable

---

## Why NOT Pure Google (Gemini + Vertex)?

While tempting given the Google Cloud environment:

1. **Reasoning Quality**: Claude significantly outperforms Gemini for:
   - Complex business analysis
   - Schema design
   - Code generation
   - Structured output

2. **Tool Use Reliability**: Claude's function calling is more reliable for:
   - Multi-step workflows
   - Complex tool chains
   - Error recovery

3. **Cost-Benefit**: The marginal cost increase (~$0.50/job) is worth it for:
   - Higher success rate
   - Better quality outputs
   - Less manual intervention
   - Better CE demos

4. **Best of Both**: We still use Google CAPI for the final data agent, leveraging:
   - Native BigQuery integration
   - Optimized for data queries
   - Enterprise support

---

## Cost Analysis

### Per Provisioning Job Estimate

**Research Agent (Claude)**
- Input: ~5K tokens (website content)
- Output: ~1K tokens (analysis)
- Cost: ~$0.03

**Data Modeling Agent (Claude)**
- Input: ~2K tokens (context)
- Output: ~3K tokens (schema + data specs)
- Cost: ~$0.05

**Infrastructure Agent (Python)**
- No LLM cost (BigQuery API only)
- Cost: $0.00 (LLM), ~$0.01 (BigQuery)

**CAPI Agent (Google API)**
- Agent creation cost
- Cost: ~$0.02

**Demo Content Agent (Claude)**
- Input: ~3K tokens (context)
- Output: ~2K tokens (queries + script)
- Cost: ~$0.04

**Total per job: ~$0.15 (LLM) + $0.01 (infrastructure) = $0.16**

### Monthly Cost Projection

| Scenario | Jobs/Month | LLM Cost | Infrastructure | Total |
|----------|-----------|----------|----------------|-------|
| Light (10 CEs, 5 demos each) | 50 | $8 | $5 | $13 |
| Medium (20 CEs, 10 demos each) | 200 | $32 | $20 | $52 |
| Heavy (50 CEs, 20 demos each) | 1000 | $160 | $100 | $260 |

**Very affordable** for the value provided to CEs and customers.

---

## Alternative Considered: Pure Claude + Custom Orchestration

### Pros
- Simpler dependency tree
- More control over workflow
- Potentially lower abstraction overhead

### Cons
- Need to build state management from scratch
- No built-in checkpointing
- More code to maintain
- Reinventing proven patterns

### Verdict
**LangGraph provides too much value** to skip. Its state management, error handling, and checkpointing are production-ready and would take weeks to replicate.

---

## Decision Matrix

| Criteria | Weight | LangGraph+Claude | Pure Claude | CrewAI+Claude | Pure Gemini |
|----------|--------|------------------|-------------|---------------|-------------|
| **Reasoning Quality** | 25% | 5 | 5 | 5 | 3 |
| **Workflow Robustness** | 20% | 5 | 3 | 4 | 3 |
| **Development Speed** | 15% | 4 | 3 | 4 | 3 |
| **Maintainability** | 15% | 5 | 3 | 4 | 4 |
| **Cost** | 10% | 4 | 4 | 4 | 5 |
| **Google Integration** | 10% | 4 | 3 | 3 | 5 |
| **Production Ready** | 5% | 5 | 3 | 4 | 4 |
| ****Total Score** | **100%** | **4.7** | **3.6** | **4.3** | **3.6** |

**Winner: LangGraph + Claude** 🏆

---

## Final Recommendation

### Primary Stack
```python
# Orchestration
langgraph==0.0.20
langchain-core==0.1.0

# Agent Intelligence
anthropic==0.18.0

# Google Cloud (Data Agent)
google-cloud-geminidataanalytics
google-cloud-bigquery

# Supporting
pydantic==2.6.0
python-dotenv==1.0.0
```

### Architecture Pattern
```
LangGraph State Machine
  ├── Research Agent (Claude 3.5 Sonnet)
  ├── Data Modeling Agent (Claude 3.5 Sonnet)
  ├── Infrastructure Agent (Python + BigQuery)
  ├── CAPI Agent Creator (Google CAPI)
  └── Demo Content Agent (Claude 3.5 Sonnet)
```

### Rationale
1. **Proven** - LangGraph is battle-tested in production
2. **Powerful** - Claude provides best-in-class reasoning
3. **Pragmatic** - Uses best tool for each job
4. **Cost-effective** - ~$0.16 per provisioning job
5. **Maintainable** - Well-documented, active communities
6. **Scalable** - Handles concurrent jobs gracefully

---

## Migration Path (If Needed)

If Google releases a proper "ADK" or if requirements change:

1. **LangGraph nodes are modular** - Can swap Claude for Gemini per-node
2. **State schema is independent** - No lock-in to specific LLM
3. **Tools are abstracted** - Easy to point at different APIs
4. **Graph structure remains** - Workflow logic is preserved

**We're not locked in** - the architecture allows flexibility while optimizing for current best-in-class tools.

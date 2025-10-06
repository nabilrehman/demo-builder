# Agent Selector Guide: Which Version to Use?

This guide helps you choose the right agent version for your orchestrator based on your priorities: **Speed vs Quality**.

---

## 🚀 Quick Selector

| Agent | Speed Priority | Quality Priority |
|-------|---------------|------------------|
| **Research Agent V2** | `research_agent_v2_gemini_pro.py` (2x faster) | `research_agent_v2_optimized.py` (more thorough) |
| **Demo Story** | `demo_story_agent_gemini_pro.py` (2.13x faster, same quality) | `demo_story_agent_gemini_pro.py` (2.13x faster, same quality) |
| **Data Modeling** | `data_modeling_agent.py` (Claude - user preference) | `data_modeling_agent.py` (Claude - user preference) |
| **Synthetic Data** | `synthetic_data_generator_optimized.py` (3x faster) | `synthetic_data_generator_optimized.py` (3x faster) |
| **Infrastructure** | `infrastructure_agent_optimized.py` (4-5x faster) | `infrastructure_agent_optimized.py` (4-5x faster) |
| **Demo Validator** | `demo_validator_optimized.py` (3-4x faster) | `demo_validator_optimized.py` (3-4x faster) |
| **CAPI Instructions** | `capi_instruction_generator_optimized.py` (Claude - quality critical) | `capi_instruction_generator_optimized.py` (Claude - quality critical) |

---

## 📊 Research Agent V2 - Detailed Comparison

### Option 1: Gemini 2.5 Pro (FASTEST - 2x speedup)

**File:** `backend/agentic_service/agents/research_agent_v2_gemini_pro.py`

**Performance:**
- ⏱️ **Total Time:** 131.72s (~2.2 minutes)
- 📊 **Entities Found:** 5 key entities, 5 data entities
- ⚡ **Speedup:** 2x faster than Claude

**When to Use:**
- ✅ Rapid prototyping and demos
- ✅ Development environment
- ✅ Cost optimization important
- ✅ Quick iteration cycles
- ✅ Basic entity extraction sufficient

**Trade-off:**
- ⚠️ May find fewer entities (5 vs 8)
- ⚠️ Less detailed architecture (5 vs 12 data entities)

**Import:**
```python
from backend.agentic_service.agents.research_agent_v2_gemini_pro import CustomerResearchAgentV2GeminiPro
agent = CustomerResearchAgentV2GeminiPro()
```

---

### Option 2: Claude Sonnet 4.5 (MOST THOROUGH)

**File:** `backend/agentic_service/agents/research_agent_v2_optimized.py`

**Performance:**
- ⏱️ **Total Time:** 262.82s (~4.4 minutes)
- 📊 **Entities Found:** 8 key entities, 12 data entities
- 🎯 **Quality:** More comprehensive analysis

**When to Use:**
- ✅ Production environment
- ✅ Comprehensive analysis required
- ✅ Detailed data architecture needed
- ✅ Quality > Speed
- ✅ Complex business models

**Trade-off:**
- ⚠️ 2x slower than Gemini
- ⚠️ Higher cost per run

**Import:**
```python
from backend.agentic_service.agents.research_agent_v2_optimized import CustomerResearchAgentV2Optimized
agent = CustomerResearchAgentV2Optimized()
```

---

## 📊 Demo Story Agent - Detailed Comparison

### Option 1: Gemini 2.5 Pro (FASTEST - 2.13x speedup, SAME QUALITY)

**File:** `backend/agentic_service/agents/demo_story_agent_gemini_pro.py`

**Performance:**
- ⏱️ **Total Time:** 43.33s (~43 seconds)
- 📊 **Golden Queries:** 6 queries
- 🎬 **Story Scenes:** 4 scenes
- 📋 **Data Entities:** 8 entities
- ⚡ **Speedup:** 2.13x faster than Claude

**When to Use:**
- ✅ **ALWAYS** - Both speed AND quality win!
- ✅ Production environment (faster + same quality)
- ✅ Development environment (rapid iteration)
- ✅ Cost optimization (faster = cheaper)
- ✅ Customer demos (faster demo generation)

**Trade-off:**
- ✅ **NO TRADE-OFFS** - Identical output quality, just faster!

**Import:**
```python
from backend.agentic_service.agents.demo_story_agent_gemini_pro import DemoStoryAgentGeminiPro
agent = DemoStoryAgentGeminiPro()
```

---

### Option 2: Claude Sonnet 4.5 (SLOWER, SAME QUALITY)

**File:** `backend/agentic_service/agents/demo_story_agent.py`

**Performance:**
- ⏱️ **Total Time:** 92.35s (~92 seconds)
- 📊 **Golden Queries:** 6 queries (same as Gemini)
- 🎬 **Story Scenes:** 4 scenes (same as Gemini)
- 📋 **Data Entities:** 8 entities (same as Gemini)
- 🐢 **Slowdown:** 2.13x slower than Gemini

**When to Use:**
- ⚠️ Only if you have a specific preference for Claude's writing style
- ⚠️ No performance or quality advantage over Gemini

**Import:**
```python
from backend.agentic_service.agents.demo_story_agent import DemoStoryAgent
agent = DemoStoryAgent()
```

**Recommendation:** Use Gemini 2.5 Pro version instead for 2x speedup with no quality loss.

---

## 🎯 Recommended Configurations

### Configuration 1: SPEED (Development/Demos)

**Target: Fastest execution, acceptable quality**

```python
# Research V2: Gemini 2.5 Pro (2x faster)
from backend.agentic_service.agents.research_agent_v2_gemini_pro import CustomerResearchAgentV2GeminiPro

# Data Modeling: Claude (user preference)
from backend.agentic_service.agents.data_modeling_agent import DataModelingAgent

# Synthetic Data: Optimized
from backend.agentic_service.agents.synthetic_data_generator_optimized import SyntheticDataGeneratorOptimized

# Infrastructure: Optimized
from backend.agentic_service.agents.infrastructure_agent_optimized import InfrastructureAgentOptimized

# Validator: Optimized
from backend.agentic_service.agents.demo_validator_optimized import DemoValidatorOptimized

# CAPI: Optimized
from backend.agentic_service.agents.capi_instruction_generator_optimized import CAPIInstructionGeneratorOptimized

# Demo Story: Gemini 2.5 Pro (2.13x faster, same quality)
from backend.agentic_service.agents.demo_story_agent_gemini_pro import DemoStoryAgentGeminiPro
```

**Expected Total Time: ~2-3 minutes** (with Gemini for Research + Demo Story)

---

### Configuration 2: QUALITY (Production)

**Target: Most comprehensive analysis, slower**

```python
# Research V2: Claude (more thorough)
from backend.agentic_service.agents.research_agent_v2_optimized import CustomerResearchAgentV2Optimized

# Data Modeling: Claude (user preference)
from backend.agentic_service.agents.data_modeling_agent import DataModelingAgent

# Synthetic Data: Optimized
from backend.agentic_service.agents.synthetic_data_generator_optimized import SyntheticDataGeneratorOptimized

# Infrastructure: Optimized
from backend.agentic_service.agents.infrastructure_agent_optimized import InfrastructureAgentOptimized

# Validator: Optimized
from backend.agentic_service.agents.demo_validator_optimized import DemoValidatorOptimized

# CAPI: Optimized
from backend.agentic_service.agents.capi_instruction_generator_optimized import CAPIInstructionGeneratorOptimized

# Demo Story: Gemini 2.5 Pro (2.13x faster, same quality)
from backend.agentic_service.agents.demo_story_agent_gemini_pro import DemoStoryAgentGeminiPro
```

**Expected Total Time: ~4-5 minutes** (Claude for Research, Gemini for Demo Story recommended)

---

### Configuration 3: HYBRID (Best of Both)

**Target: Use Gemini for speed, Claude for critical analysis**

```python
# Research V2: Gemini (2x faster initial research)
from backend.agentic_service.agents.research_agent_v2_gemini_pro import CustomerResearchAgentV2GeminiPro

# Data Modeling: Claude (critical for schema quality)
from backend.agentic_service.agents.data_modeling_agent import DataModelingAgent

# Synthetic Data: Optimized
from backend.agentic_service.agents.synthetic_data_generator_optimized import SyntheticDataGeneratorOptimized

# Infrastructure: Optimized
from backend.agentic_service.agents.infrastructure_agent_optimized import InfrastructureAgentOptimized

# Validator: Optimized
from backend.agentic_service.agents.demo_validator_optimized import DemoValidatorOptimized

# CAPI: Optimized
from backend.agentic_service.agents.capi_instruction_generator_optimized import CAPIInstructionGeneratorOptimized

# Demo Story: Gemini 2.5 Pro (2.13x faster, same quality)
from backend.agentic_service.agents.demo_story_agent_gemini_pro import DemoStoryAgentGeminiPro
```

**Expected Total Time: ~3-4 minutes** (balanced approach with Gemini for Demo Story)

---

## 📈 Performance Impact by Phase

### Research Agent V2 Phase Breakdown

| Phase | Gemini 2.5 Pro | Claude Sonnet 4.5 | Difference |
|-------|----------------|-------------------|------------|
| **Phase 1: Intelligence** | 12.79s | 13.04s | ~same |
| **Phase 2: Business Analysis** | 30.72s | 36.29s | 1.2x slower (Claude) |
| **Phase 3: Architecture** | 88.20s | 213.49s | 2.4x slower (Claude) |
| **TOTAL** | **131.72s** | **262.82s** | **2x slower (Claude)** |

**Key Insight:** Phase 1 (web scraping) is the same for both. The difference is in LLM inference (Phases 2 & 3).

---

## 💰 Cost Considerations

### Gemini 2.5 Pro
- **Faster inference** = Lower compute time
- **Lower token costs** (generally)
- **Best for high-volume demos**

### Claude Sonnet 4.5
- **Slower inference** = Higher compute time
- **Higher token costs** (generally)
- **Best for production/quality-critical use**

---

## 🔄 How to Switch Agents

### In Your Orchestrator

1. **Locate your agent imports** (usually in `orchestrator.py` or `workflow.py`)

2. **Replace the import statement:**

**For Speed (Gemini 2.5 Pro):**
```python
# OLD
from backend.agentic_service.agents.research_agent_v2_optimized import CustomerResearchAgentV2Optimized

# NEW (2x faster)
from backend.agentic_service.agents.research_agent_v2_gemini_pro import CustomerResearchAgentV2GeminiPro
```

3. **Update the initialization:**
```python
# OLD
research_agent = CustomerResearchAgentV2Optimized()

# NEW
research_agent = CustomerResearchAgentV2GeminiPro()
```

4. **No other changes needed** - same `execute(state)` interface!

---

## ⚠️ Important Caveats

### Data Modeling Agent
- **User explicitly chose Claude Sonnet 4.5** over Gemini
- Do NOT switch without user approval
- Quote: *"lets stick to Claude Sonnet for now"*

### Demo Story Agent
- **Gemini 2.5 Pro version created** - 2.13x faster with identical quality
- ✅ **Clear winner**: Use `demo_story_agent_gemini_pro.py` for both speed AND quality
- No trade-offs - Gemini produces same number of queries, scenes, and entities

### CAPI Instruction Generator
- **Gemini 2.5 Pro version tested** - 1.26x faster BUT incomplete output
- ❌ **Use Claude**: Gemini produces 50% smaller YAML, missing tables and golden queries
- Quality critical - incomplete YAML would break CAPI functionality

---

## 📁 Reference Files

- **Research V2 Benchmark:** `benchmarks/RESEARCH_V2_GEMINI_PRO_RESULTS.md`
- **Demo Story Benchmark:** `benchmarks/DEMO_STORY_GEMINI_PRO_RESULTS.md`
- **CAPI Instructions Benchmark:** `benchmarks/CAPI_INSTRUCTION_GEMINI_PRO_RESULTS.md`
- **Full Optimization Summary:** `benchmarks/OPTIMIZATION_SUMMARY.md`
- **Quick Reference:** `benchmarks/QUICK_REFERENCE.md`
- **Code Changes:** `benchmarks/CODE_CHANGES.md`

---

## 🎓 Decision Tree

```
Need to optimize Research Agent V2?
│
├─ YES, need SPEED (demos/dev)
│  └─ Use: research_agent_v2_gemini_pro.py (2x faster)
│
├─ YES, need QUALITY (prod)
│  └─ Use: research_agent_v2_optimized.py (more entities)
│
└─ NO optimization needed
   └─ Use: research_agent_v2.py (original, not recommended)
```

---

**Last Updated:** 2025-10-05
**Benchmark Dates:**
- Research V2: 2025-10-05 (https://www.offerup.com)
- Demo Story: 2025-10-05 (OfferUp sample data)
- CAPI Instructions: 2025-10-05 (OfferUp 3 tables)

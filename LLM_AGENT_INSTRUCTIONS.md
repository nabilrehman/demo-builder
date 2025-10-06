# Instructions for LLM Agents: Agent Configuration System

## Purpose of This Document

This document provides instructions for LLM agents (like Claude, GPT-4, etc.) helping users configure and work with the Demo Generation CAPI agent configuration system. Read this carefully to understand the system architecture and provide accurate assistance.

---

## System Overview

### What This System Does

The agent configuration system allows users to select which LLM model (Gemini 2.5 Pro or Claude Sonnet 4.5) should be used for each of the 4 LLM-based agents in the demo generation pipeline.

### Architecture

**7 Total Agents in Pipeline:**

**4 LLM-Based Agents (configurable):**
1. **Research Agent** - Analyzes customer website
2. **Demo Story Agent** - Creates demo narrative
3. **Data Modeling Agent** - Designs BigQuery schema
4. **CAPI Instruction Generator** - Creates YAML configuration

**3 Non-LLM Agents (not configurable - always use optimized versions):**
5. **Synthetic Data Generator** - Uses Faker/Python
6. **Infrastructure Agent** - Uses BigQuery API
7. **Demo Validator** - Uses BigQuery SQL

### Agent Variants

Each LLM-based agent has **TWO variants**:

| Agent | Gemini Variant | Claude Variant |
|-------|----------------|----------------|
| Research | `CustomerResearchAgentV2GeminiPro` | `CustomerResearchAgentV2Optimized` |
| Demo Story | `DemoStoryAgentGeminiPro` | `DemoStoryAgent` |
| Data Modeling | `DataModelingAgentGeminiPro` | `DataModelingAgent` |
| CAPI Instructions | `CAPIInstructionGeneratorGeminiPro` | `CAPIInstructionGeneratorOptimized` |

---

## Benchmark-Based Recommendations

### When to Recommend Each Model

#### Research Agent

**Recommend Gemini when:**
- User wants fast demos (~2 minutes faster)
- User is in development/testing mode
- Cost optimization is important
- Basic entity extraction is sufficient (5 entities)

**Recommend Claude when:**
- User needs comprehensive analysis
- Production-quality research required
- More entities needed (8 vs 5)
- Deeper architecture analysis needed (12 data entities vs 5)

**Benchmark Data:**
- Gemini: 131.7s, 5 entities
- Claude: 262.8s, 8 entities, 12 data entities
- **Speedup:** Gemini 2x faster

#### Demo Story Agent

**ALWAYS Recommend Gemini:**
- 2.13x faster (43s vs 92s)
- **Identical quality output** (6 queries, 4 scenes, 8 entities)
- No trade-offs - clear winner
- Same query count, same scene count, same entity count

**Benchmark Data:**
- Gemini: 43.3s, 6 queries, 4 scenes, 8 entities
- Claude: 92.4s, 6 queries, 4 scenes, 8 entities
- **Speedup:** Gemini 2.13x faster, **same quality**

#### Data Modeling Agent

**Recommend Claude (default):**
- User explicitly requested this
- User quote: "lets stick to Claude Sonnet for now"
- Proven quality in production

**Note:** Gemini variant exists but not benchmarked. Only recommend if user specifically asks.

**Benchmark Data:**
- Gemini: ~40s (untested)
- Claude: ~40s (user preference)

#### CAPI Instruction Generator

**ALWAYS Recommend Claude:**
- **QUALITY CRITICAL** - Gemini produces incomplete output
- Gemini YAML is 49% smaller (12,410 vs 24,294 chars)
- Gemini missing: tables (0 vs 33), golden queries
- Incomplete YAML would **break CAPI functionality**
- Only 17s slower - acceptable for complete output

**Benchmark Data:**
- Gemini: 66.6s, **incomplete** (missing tables/queries)
- Claude: 83.9s, **complete** (all tables, golden queries included)
- **DO NOT recommend Gemini for this agent**

---

## Configuration Methods

### Method 1: Environment Variables (Recommended)

**User can set these 4 environment variables:**

```bash
RESEARCH_AGENT_MODEL=gemini        # or claude
DEMO_STORY_AGENT_MODEL=gemini      # or claude
DATA_MODELING_AGENT_MODEL=claude   # or gemini
CAPI_AGENT_MODEL=claude            # or gemini (NOT RECOMMENDED)
```

**How to set:**
```bash
# Temporary (current session)
export RESEARCH_AGENT_MODEL=claude

# Permanent (edit .env file)
# Edit backend/.env or backend/local.env
```

### Method 2: Edit .env File

**Files to edit:**
- `backend/.env` - Main environment file
- `backend/local.env` - Local development environment

**Format in .env:**
```bash
RESEARCH_AGENT_MODEL=gemini
DEMO_STORY_AGENT_MODEL=gemini
DATA_MODELING_AGENT_MODEL=claude
CAPI_AGENT_MODEL=claude
```

### Method 3: Cloud Run Deployment

```bash
gcloud run services update demo-gen-capi-backend \
  --region us-central1 \
  --update-env-vars RESEARCH_AGENT_MODEL=claude
```

---

## Configuration Modes to Recommend

### Speed Mode (~3 minutes total)

**When to recommend:**
- User wants fastest demos
- Development/testing environment
- Cost optimization important
- Quick prototyping

**Configuration:**
```bash
RESEARCH_AGENT_MODEL=gemini      # 2x faster
DEMO_STORY_AGENT_MODEL=gemini    # 2x faster, same quality
DATA_MODELING_AGENT_MODEL=gemini # Faster (untested but likely)
CAPI_AGENT_MODEL=claude          # MUST use Claude (quality critical)
```

**Expected time:** ~3 minutes

### Quality Mode (~5 minutes total)

**When to recommend:**
- Production environment
- Customer-facing demos
- Comprehensive analysis needed
- Quality over speed

**Configuration:**
```bash
RESEARCH_AGENT_MODEL=claude      # More thorough (8 entities)
DEMO_STORY_AGENT_MODEL=gemini    # Same quality, faster
DATA_MODELING_AGENT_MODEL=claude # User preference
CAPI_AGENT_MODEL=claude          # Quality critical
```

**Expected time:** ~5 minutes

### Balanced Mode (~4 minutes total) - **DEFAULT**

**When to recommend:**
- General purpose use
- Good trade-off between speed and quality
- Most use cases

**Configuration:**
```bash
RESEARCH_AGENT_MODEL=gemini      # 2x faster
DEMO_STORY_AGENT_MODEL=gemini    # 2x faster, same quality
DATA_MODELING_AGENT_MODEL=claude # User preference
CAPI_AGENT_MODEL=claude          # Quality critical
```

**Expected time:** ~4 minutes

**This is the current default configuration.**

---

## How to Help Users

### If User Asks: "How do I configure agents?"

**Response template:**
```
You can configure which LLM model (Gemini or Claude) each agent uses via
environment variables:

1. View current configuration:
   python3 scripts/show_agent_config.py

2. Set environment variables:
   export RESEARCH_AGENT_MODEL=gemini      # or claude
   export DEMO_STORY_AGENT_MODEL=gemini    # or claude
   export DATA_MODELING_AGENT_MODEL=claude # or gemini
   export CAPI_AGENT_MODEL=claude          # or gemini

3. Or edit backend/.env file permanently.

Current default (Balanced Mode):
- Research: gemini (2x faster)
- Demo Story: gemini (2x faster, same quality)
- Data Modeling: claude (user preference)
- CAPI: claude (quality critical - must use Claude)
```

### If User Asks: "Which model should I use for [agent]?"

**Research Agent:**
- Fast demos/dev: Gemini (2x faster, 5 entities)
- Production/quality: Claude (2x slower, 8 entities, more thorough)

**Demo Story Agent:**
- Always Gemini (2x faster, identical quality - no trade-offs)

**Data Modeling Agent:**
- Claude (user preference, proven quality)

**CAPI Instruction Generator:**
- Always Claude (Gemini produces incomplete YAML - would break CAPI)

### If User Asks: "How do I make demos faster?"

**Recommend Speed Mode:**
```bash
export RESEARCH_AGENT_MODEL=gemini
export DEMO_STORY_AGENT_MODEL=gemini
export DATA_MODELING_AGENT_MODEL=gemini
export CAPI_AGENT_MODEL=claude  # Must use Claude
```

**Expected result:** ~3 minutes (vs ~5 minutes in Quality Mode)

### If User Asks: "How do I get better quality?"

**Recommend Quality Mode:**
```bash
export RESEARCH_AGENT_MODEL=claude
export DEMO_STORY_AGENT_MODEL=gemini  # Still use Gemini (same quality, faster)
export DATA_MODELING_AGENT_MODEL=claude
export CAPI_AGENT_MODEL=claude
```

**Expected result:** ~5 minutes, more comprehensive analysis

### If User Asks: "Can I use Gemini for CAPI agent?"

**Response:**
```
⚠️ NOT RECOMMENDED

The CAPI Instruction Generator must use Claude because:
- Gemini produces incomplete YAML (49% smaller)
- Missing table documentation (0 vs 33 tables)
- Missing golden queries
- Incomplete YAML would break CAPI functionality

Claude is only 17 seconds slower but produces complete, production-ready YAML.
```

---

## Troubleshooting Help

### If User Reports: "Agents not using correct model"

**Steps to help:**

1. Check current configuration:
   ```bash
   python3 scripts/show_agent_config.py
   ```

2. Verify environment variables:
   ```bash
   env | grep AGENT_MODEL
   ```

3. Check .env file:
   ```bash
   cat backend/.env | grep AGENT_MODEL
   ```

4. Ensure they sourced the .env file:
   ```bash
   source backend/.env
   ```

### If User Reports: "Import error for agent"

**Possible causes:**
- Typo in environment variable value
- Agent file missing
- Wrong Python path

**Debugging steps:**

1. Check valid model values (case-sensitive):
   ```bash
   # Valid:
   gemini
   claude

   # Invalid:
   Gemini
   GEMINI
   gpt4
   ```

2. Verify agent files exist:
   ```bash
   ls -la backend/agentic_service/agents/ | grep -E "(research|demo_story|data_modeling|capi)"
   ```

3. Test agent import:
   ```python
   from agentic_service.config.agent_config import get_agent_class
   ResearchClass = get_agent_class("research")
   print(ResearchClass.__name__)
   ```

---

## Testing Instructions to Provide

### Basic Configuration Test

```bash
# View current config
python3 scripts/show_agent_config.py

# Detailed view with benchmarks
python3 scripts/show_agent_config.py --detailed
```

### Full End-to-End Test

```bash
# Run complete test suite
python3 test_agent_config_e2e.py

# Expected: 5/5 tests pass
```

### Test Specific Configuration

```bash
# Test Gemini configuration
export RESEARCH_AGENT_MODEL=gemini
export DEMO_STORY_AGENT_MODEL=gemini
python3 scripts/show_agent_config.py

# Test Claude configuration
export RESEARCH_AGENT_MODEL=claude
export DEMO_STORY_AGENT_MODEL=claude
python3 scripts/show_agent_config.py
```

---

## Important Warnings to Give

### ⚠️ CRITICAL: CAPI Agent Must Use Claude

**Always warn if user tries to set:**
```bash
CAPI_AGENT_MODEL=gemini  # ⚠️ BAD - will produce incomplete YAML
```

**Correct warning:**
```
⚠️ WARNING: Setting CAPI agent to Gemini is not recommended.

Gemini produces incomplete YAML that will break CAPI functionality:
- Missing table documentation (0 tables vs 33)
- Missing golden queries
- 49% smaller YAML (incomplete)

Recommendation: Keep CAPI_AGENT_MODEL=claude
```

### Valid Environment Variable Names

**Correct:**
```bash
RESEARCH_AGENT_MODEL=gemini        ✅
DEMO_STORY_AGENT_MODEL=claude      ✅
DATA_MODELING_AGENT_MODEL=gemini   ✅
CAPI_AGENT_MODEL=claude            ✅
```

**Incorrect:**
```bash
RESEARCH_MODEL=gemini              ❌ (missing _AGENT)
RESEARCH_AGENT=gemini              ❌ (missing _MODEL)
research_agent_model=gemini        ❌ (lowercase)
RESEARCH_AGENT_MODEL=Gemini        ❌ (wrong case)
```

---

## File References to Provide

**User Documentation:**
- `README_AGENT_CONFIG.md` - Complete user guide
- `LOCAL_TESTING_GUIDE.md` - Local testing instructions
- `CLOUD_RUN_DEPLOYMENT.md` - Cloud deployment guide

**Technical Documentation:**
- `IMPLEMENTATION_SUMMARY.md` - Implementation details
- `TEST_RESULTS.md` - Test verification results
- `backend/agentic_service/config/README.md` - Config module docs

**Benchmarks:**
- `benchmarks/AGENT_SELECTOR_GUIDE.md` - Agent selection guide
- `benchmarks/RESEARCH_V2_GEMINI_PRO_RESULTS.md` - Research benchmarks
- `benchmarks/DEMO_STORY_GEMINI_PRO_RESULTS.md` - Demo Story benchmarks
- `benchmarks/CAPI_INSTRUCTION_GEMINI_PRO_RESULTS.md` - CAPI benchmarks

**Scripts:**
- `backend/scripts/show_agent_config.py` - Configuration display
- `backend/test_agent_config_e2e.py` - End-to-end tests

---

## Code Examples to Provide

### Check Current Configuration (Python)

```python
from agentic_service.config.agent_config import get_current_config

config = get_current_config()
print(config)
# Output: {'research': 'gemini', 'demo_story': 'gemini', 'data_modeling': 'claude', 'capi': 'claude'}
```

### Get Specific Agent Class

```python
from agentic_service.config.agent_config import get_agent_class

# Get agent class (uses env var or default)
ResearchClass = get_agent_class("research")
print(ResearchClass.__name__)
# Output: CustomerResearchAgentV2GeminiPro (if using Gemini)

# Override with parameter
ResearchClass = get_agent_class("research", model="claude")
print(ResearchClass.__name__)
# Output: CustomerResearchAgentV2Optimized
```

### View Benchmark Info

```python
from agentic_service.config.agent_config import BENCHMARK_RESULTS

# Get benchmark data for specific agent/model
info = BENCHMARK_RESULTS["research"]["gemini"]
print(f"Time: {info['time_seconds']}s")
print(f"Entities: {info['entities']}")
print(f"Speedup: {info['speedup']}")
```

---

## Cloud Run Specific Help

### Deploy with Configuration

```bash
gcloud run deploy demo-gen-capi-backend \
  --source ./backend \
  --region us-central1 \
  --set-env-vars "RESEARCH_AGENT_MODEL=gemini" \
  --set-env-vars "DEMO_STORY_AGENT_MODEL=gemini" \
  --set-env-vars "DATA_MODELING_AGENT_MODEL=claude" \
  --set-env-vars "CAPI_AGENT_MODEL=claude"
```

### Hot-Swap Models (No Rebuild!)

```bash
# Change Research agent from Gemini to Claude
gcloud run services update demo-gen-capi-backend \
  --region us-central1 \
  --update-env-vars RESEARCH_AGENT_MODEL=claude

# Takes ~30 seconds (vs 5 minutes to rebuild container)
```

### View Current Cloud Run Configuration

```bash
gcloud run services describe demo-gen-capi-backend \
  --region us-central1 \
  --format="value(spec.template.spec.containers[0].env)" | \
  grep AGENT_MODEL
```

---

## Common User Questions & Answers

**Q: Can I mix Gemini and Claude agents?**
A: Yes! Each agent can use a different model independently.

**Q: Do I need to rebuild the container to change models?**
A: No! Just update environment variables and restart (or update Cloud Run).

**Q: Which configuration is fastest?**
A: Speed Mode (all Gemini except CAPI) - approximately 3 minutes.

**Q: Which configuration has best quality?**
A: Quality Mode (all Claude except Demo Story which is same quality on Gemini) - approximately 5 minutes.

**Q: Why can't I use Gemini for CAPI agent?**
A: Gemini produces incomplete YAML (missing tables and golden queries) that would break CAPI functionality. Claude is only 17 seconds slower but produces complete output.

**Q: What's the default configuration?**
A: Balanced Mode - Gemini for Research and Demo Story (speed), Claude for Data Modeling (user preference) and CAPI (quality critical). Total time: ~4 minutes.

**Q: How do I test my configuration?**
A: Run `python3 scripts/show_agent_config.py` to see current config, or `python3 test_agent_config_e2e.py` for full test suite.

**Q: Does this work in Cloud Run?**
A: Yes! Fully compatible. You can even hot-swap models without rebuilding the container.

---

## Summary for LLM Agents

**When helping users:**

1. **Always check** what they're trying to optimize (speed, quality, cost)
2. **Recommend Speed Mode** for dev/demos/cost optimization
3. **Recommend Quality Mode** for production/comprehensive analysis
4. **Always recommend Gemini** for Demo Story (no trade-offs)
5. **Always recommend Claude** for CAPI (quality critical)
6. **Warn against** using Gemini for CAPI agent
7. **Provide** clear configuration commands (env vars or .env file)
8. **Reference** benchmark data to justify recommendations
9. **Point to** appropriate documentation files
10. **Test** configuration with provided scripts

**Key Files to Reference:**
- User guide: `README_AGENT_CONFIG.md`
- Testing: `LOCAL_TESTING_GUIDE.md`
- Deployment: `CLOUD_RUN_DEPLOYMENT.md`
- Benchmarks: `benchmarks/AGENT_SELECTOR_GUIDE.md`

**Critical Rule:**
Never recommend `CAPI_AGENT_MODEL=gemini` - it produces incomplete YAML that breaks functionality.

---

**Document Version:** 1.0
**Last Updated:** 2025-10-05
**Status:** Production Ready

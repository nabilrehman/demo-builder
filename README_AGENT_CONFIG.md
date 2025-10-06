# Agent Configuration System - Complete Guide

## 🎉 Implementation Complete & Tested!

A centralized configuration system for selecting LLM models (Gemini vs Claude) for each agent in the demo generation pipeline.

## ✅ What Was Built

### 1. Configuration Module
**Location:** `backend/agentic_service/config/`

- `agent_config.py` - Core configuration with agent registry
- `__init__.py` - Package exports
- `README.md` - Detailed documentation

### 2. Orchestrator Integration
**Modified:** `backend/agentic_service/demo_orchestrator.py`

- Removed hardcoded agent imports
- Added dynamic agent selection via config
- Fully backward compatible

### 3. Environment Configuration
**Updated:** `backend/.env` and `backend/local.env`

Added 4 new environment variables:
- `RESEARCH_AGENT_MODEL` - gemini or claude
- `DEMO_STORY_AGENT_MODEL` - gemini or claude
- `DATA_MODELING_AGENT_MODEL` - gemini or claude
- `CAPI_AGENT_MODEL` - gemini or claude

### 4. Helper Tools
- `backend/scripts/show_agent_config.py` - Configuration display tool
- `backend/test_agent_config_e2e.py` - End-to-end test suite

### 5. Documentation
- `LOCAL_TESTING_GUIDE.md` - Complete local testing instructions
- `CLOUD_RUN_DEPLOYMENT.md` - Cloud Run deployment guide
- `IMPLEMENTATION_SUMMARY.md` - Implementation details
- `TEST_RESULTS.md` - Test results and verification
- `README_AGENT_CONFIG.md` - This file

## 🚀 Quick Start

### View Current Configuration

```bash
cd /home/admin_/final_demo/capi/demo-gen-capi/backend

# Simple view
python3 scripts/show_agent_config.py

# Detailed view with benchmarks
python3 scripts/show_agent_config.py --detailed
```

### Change Agent Models

```bash
# Option 1: Environment variables (temporary)
export RESEARCH_AGENT_MODEL=claude
export DEMO_STORY_AGENT_MODEL=gemini
export DATA_MODELING_AGENT_MODEL=claude
export CAPI_AGENT_MODEL=claude

# Option 2: Edit .env file (permanent)
# Edit backend/.env or backend/local.env
```

### Run Tests

```bash
# Run full end-to-end test suite
python3 test_agent_config_e2e.py

# Expected: 5/5 tests pass
```

## 📊 Agent Variants

### Research Agent
| Model | Class | Time | Quality | Use Case |
|-------|-------|------|---------|----------|
| **Gemini** | `CustomerResearchAgentV2GeminiPro` | 131s | 5 entities | Speed (2x faster) |
| **Claude** | `CustomerResearchAgentV2Optimized` | 263s | 8 entities | Quality (more thorough) |

**Default:** `gemini` (speed priority)

### Demo Story Agent
| Model | Class | Time | Quality | Use Case |
|-------|-------|------|---------|----------|
| **Gemini** | `DemoStoryAgentGeminiPro` | 43s | Identical | **Clear winner** |
| **Claude** | `DemoStoryAgent` | 92s | Same | No advantage |

**Default:** `gemini` (2x faster, same quality)

### Data Modeling Agent
| Model | Class | Time | Quality | Use Case |
|-------|-------|------|---------|----------|
| **Gemini** | `DataModelingAgentGeminiPro` | ~40s | Untested | Alternative |
| **Claude** | `DataModelingAgent` | ~40s | Proven | User preference |

**Default:** `claude` (user explicitly requested)

### CAPI Instruction Generator
| Model | Class | Time | Quality | Use Case |
|-------|-------|------|---------|----------|
| **Gemini** | `CAPIInstructionGeneratorGeminiPro` | 67s | **Incomplete** | ❌ Not recommended |
| **Claude** | `CAPIInstructionGeneratorOptimized` | 84s | Complete | **Required** |

**Default:** `claude` (QUALITY CRITICAL - Gemini produces incomplete YAML)

## 🎯 Configuration Modes

### Speed Mode (~3 minutes)
Best for: Demos, development, cost optimization

```bash
export RESEARCH_AGENT_MODEL=gemini
export DEMO_STORY_AGENT_MODEL=gemini
export DATA_MODELING_AGENT_MODEL=gemini
export CAPI_AGENT_MODEL=claude  # Quality critical
```

### Quality Mode (~5 minutes)
Best for: Production, comprehensive analysis

```bash
export RESEARCH_AGENT_MODEL=claude
export DEMO_STORY_AGENT_MODEL=gemini
export DATA_MODELING_AGENT_MODEL=claude
export CAPI_AGENT_MODEL=claude
```

### Balanced Mode (~4 minutes) - **DEFAULT**
Best for: General use, good trade-off

```bash
export RESEARCH_AGENT_MODEL=gemini
export DEMO_STORY_AGENT_MODEL=gemini
export DATA_MODELING_AGENT_MODEL=claude
export CAPI_AGENT_MODEL=claude
```

## ✅ Test Results

### All Tests Passed! (5/5)

- ✅ **TEST 1:** Configuration display works correctly
- ✅ **TEST 2:** All agents imported successfully
- ✅ **TEST 3:** Environment variable override works
- ✅ **TEST 4:** All agents instantiated successfully
- ✅ **TEST 5:** Mini pipeline executed successfully

**Both Gemini and Claude configurations tested and verified.**

## 📁 Files Created/Modified

### Created:
```
backend/agentic_service/config/
├── __init__.py
├── agent_config.py
└── README.md

backend/scripts/
└── show_agent_config.py

backend/
└── test_agent_config_e2e.py

Documentation/
├── LOCAL_TESTING_GUIDE.md
├── CLOUD_RUN_DEPLOYMENT.md
├── IMPLEMENTATION_SUMMARY.md
├── TEST_RESULTS.md
└── README_AGENT_CONFIG.md
```

### Modified:
```
backend/agentic_service/demo_orchestrator.py
backend/.env
backend/local.env
```

## 🔧 Usage Examples

### In Code

```python
from agentic_service.config.agent_config import get_agent_class

# Get agent class (checks env var, then default)
ResearchAgentClass = get_agent_class("research")
agent = ResearchAgentClass(max_pages=30, max_depth=2)

# Override with parameter
ResearchAgentClass = get_agent_class("research", model="claude")
agent = ResearchAgentClass(max_pages=30, max_depth=2)
```

### Environment Variables

```bash
# Set for current session
export RESEARCH_AGENT_MODEL=claude

# Verify
python3 scripts/show_agent_config.py

# Reset
unset RESEARCH_AGENT_MODEL
```

### Cloud Run Deployment

```bash
# Deploy with configuration
gcloud run deploy demo-gen-capi-backend \
  --source ./backend \
  --region us-central1 \
  --set-env-vars "RESEARCH_AGENT_MODEL=gemini" \
  --set-env-vars "DEMO_STORY_AGENT_MODEL=gemini" \
  --set-env-vars "DATA_MODELING_AGENT_MODEL=claude" \
  --set-env-vars "CAPI_AGENT_MODEL=claude"

# Hot-swap models (no rebuild!)
gcloud run services update demo-gen-capi-backend \
  --region us-central1 \
  --update-env-vars RESEARCH_AGENT_MODEL=claude
```

## 🎓 Key Benefits

1. **Simple Configuration**
   - Just set environment variables
   - No code changes needed

2. **Benchmark-Driven Defaults**
   - Based on real performance data
   - Clear speed vs quality trade-offs

3. **Cloud Run Ready**
   - Hot-swap models without rebuilding
   - A/B testing support
   - Multi-environment configs

4. **Developer Friendly**
   - Configuration helper script
   - Detailed documentation
   - Comprehensive test suite

5. **Production Ready**
   - All tests passing
   - No breaking changes
   - Backward compatible

## 📖 Documentation Links

- **Local Testing:** `LOCAL_TESTING_GUIDE.md`
- **Cloud Run Deployment:** `CLOUD_RUN_DEPLOYMENT.md`
- **Implementation Details:** `IMPLEMENTATION_SUMMARY.md`
- **Test Results:** `TEST_RESULTS.md`
- **Config Module Docs:** `backend/agentic_service/config/README.md`
- **Benchmarks:** `benchmarks/AGENT_SELECTOR_GUIDE.md`

## 🚀 Next Steps

### Immediate
1. ✅ All implementation complete
2. ✅ All tests passing
3. ✅ Documentation complete

### When Ready to Deploy
1. Commit changes to git
2. Deploy to Cloud Run (see `CLOUD_RUN_DEPLOYMENT.md`)
3. Test with sample customer URL
4. Monitor performance
5. Optimize based on usage

## 💡 Common Scenarios

### Scenario 1: Fastest Possible Demo
```bash
export RESEARCH_AGENT_MODEL=gemini
export DEMO_STORY_AGENT_MODEL=gemini
export DATA_MODELING_AGENT_MODEL=gemini
export CAPI_AGENT_MODEL=claude
# Result: ~3 minutes
```

### Scenario 2: Highest Quality Analysis
```bash
export RESEARCH_AGENT_MODEL=claude
export DEMO_STORY_AGENT_MODEL=gemini  # Gemini is same quality, faster
export DATA_MODELING_AGENT_MODEL=claude
export CAPI_AGENT_MODEL=claude
# Result: ~5 minutes
```

### Scenario 3: Cost Optimization
```bash
# Use Gemini where possible (faster = cheaper)
export RESEARCH_AGENT_MODEL=gemini
export DEMO_STORY_AGENT_MODEL=gemini
export DATA_MODELING_AGENT_MODEL=gemini
export CAPI_AGENT_MODEL=claude  # Must use Claude
# Result: Lowest cost, ~3 minutes
```

## ❓ FAQ

### Q: Can I mix Gemini and Claude?
**A:** Yes! You can use different models for different agents.

### Q: Do I need to rebuild the container to change models?
**A:** No! Just update environment variables and restart.

### Q: Which configuration is fastest?
**A:** Speed Mode (all Gemini except CAPI) - ~3 minutes

### Q: Which configuration is best quality?
**A:** Quality Mode (all Claude except Demo Story) - ~5 minutes

### Q: Why must CAPI use Claude?
**A:** Gemini produces incomplete YAML (missing tables/queries) that would break CAPI functionality.

### Q: Does this work in Cloud Run?
**A:** Yes! Fully compatible with Cloud Run. See `CLOUD_RUN_DEPLOYMENT.md`.

## 📞 Support

**Configuration Issues:**
```bash
python3 scripts/show_agent_config.py --detailed
```

**Test Issues:**
```bash
python3 test_agent_config_e2e.py
```

**Check Logs:**
```bash
# Look for agent selection logs
# Format: ✅ AGENT_NAME Agent: ClassName (MODEL) [source: ...]
```

## Summary

**Status:** ✅ Production Ready

**What You Can Do:**
- Configure which model each agent uses
- Switch models via environment variables
- Works locally and in Cloud Run
- No code changes needed
- Hot-swap models in production
- A/B test different configurations

**Simple Example:**
```bash
# Want faster demos?
export RESEARCH_AGENT_MODEL=gemini

# Want better quality?
export RESEARCH_AGENT_MODEL=claude

# That's it! 🎉
```

---

**Last Updated:** 2025-10-05
**Test Status:** ✅ All tests passed (5/5)
**Production Ready:** ✅ Yes

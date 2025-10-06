# Quick Reference: Optimized vs Original Agents

## 🚀 Use Optimized Versions (Recommended)

| Agent | Import Statement | Speedup |
|-------|-----------------|---------|
| **Research Agent V2** | `from backend.agentic_service.agents.research_agent_v2_optimized import ResearchAgentV2Optimized` | **12x faster** |
| **Synthetic Data Generator** | `from backend.agentic_service.agents.synthetic_data_generator_optimized import SyntheticDataGeneratorOptimized` | **3x faster** |
| **Infrastructure Agent** | `from backend.agentic_service.agents.infrastructure_agent_optimized import InfrastructureAgentOptimized` | **4-5x faster** |
| **Demo Validator** | `from backend.agentic_service.agents.demo_validator_optimized import DemoValidatorOptimized` | **3-4x faster** |
| **CAPI Instructions** | `from backend.agentic_service.agents.capi_instruction_generator_optimized import CAPIInstructionGeneratorOptimized` | Minor |

---

## ⏸️ Keep Original Versions

| Agent | Import Statement | Reason |
|-------|-----------------|--------|
| **Data Modeling Agent** | `from backend.agentic_service.agents.data_modeling_agent import DataModelingAgent` | User prefers Claude Sonnet 4.5 |
| **Demo Story Agent** | `from backend.agentic_service.agents.demo_story_agent import DemoStoryAgent` | Already optimized |

---

## 📊 Overall Impact

- **Total Time Saved:** ~4 minutes
- **Research Phase:** 160s → 13s
- **Data Generation:** 24s → 8s
- **Infrastructure:** 90s → 20s
- **Validation:** 15s → 5s

---

## ⚡ Key Pattern: asyncio.gather()

```python
# ❌ SLOW (Sequential)
for task in tasks:
    result = await task

# ✅ FAST (Parallel)
results = await asyncio.gather(*tasks)
```

---

See `OPTIMIZATION_SUMMARY.md` for full details.

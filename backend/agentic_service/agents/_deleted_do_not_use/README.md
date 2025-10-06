# ⛔ DELETED / DEPRECATED FILES - DO NOT USE

This folder contains old/broken versions of agents that should **NOT** be used.

---

## `synthetic_data_generator_optimized.py.DEPRECATED`

**Status:** ❌ BROKEN - DO NOT USE

**Why deprecated:**
- Has keyword filtering (line 275-281) that prevents LLM generation for most tables
- Only generates LLM data for tables matching: `product`, `customer`, `category`, `merchant`, `subscription`, `plan`, `service`, `feature`, `region`, `channel`, `segment`
- **Misses critical tables:** `users`, `listings`, `transactions`, `messages`, `search_events`, `orders`, `payments`, `reviews`, etc.
- Falls back to Faker for 70% of tables → generates unrealistic data
- Caused all provisioning demos to use Faker instead of LLM

**✅ Use instead:** `synthetic_data_generator_markdown.py`
- ALWAYS uses LLM for ALL tables
- No keyword filtering
- No Faker fallback
- Located: `backend/agentic_service/agents/synthetic_data_generator_markdown.py`

**Date deprecated:** 2025-10-06
**Last working date:** Never worked correctly

---

## How This Happened

The orchestrator (`demo_orchestrator.py`) was accidentally switched to use the "optimized" version which had the keyword filtering bug.

**Fixed by:**
- Switching orchestrator back to markdown version
- Moving optimized version here with warnings

**Lesson learned:**
- Always use LLM for ALL tables
- No conditional generation based on table names
- Test with real data generation, not just schema validation

---

**If you found this file in your imports, you have a bug! Fix it by:**
```python
# ❌ WRONG:
from agentic_service.agents.synthetic_data_generator_optimized import SyntheticDataGeneratorOptimized

# ✅ CORRECT:
from agentic_service.agents.synthetic_data_generator_markdown import SyntheticDataGeneratorMarkdown
```

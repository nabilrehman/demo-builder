# Research Agent V2: Gemini 2.5 Pro vs Claude Sonnet 4.5 Benchmark

**Test Date:** 2025-10-05
**Test URL:** https://www.offerup.com

---

## 🏆 Winner: Gemini 2.5 Pro (2x Faster)

**Key Finding:** Gemini 2.5 Pro delivers **2x speedup** over Claude Sonnet 4.5 for the Research Agent V2 phase.

---

## 📊 Performance Comparison

### Overall Results

| Model | Total Time | Company | Industry | Key Entities | Data Entities |
|-------|-----------|---------|----------|--------------|---------------|
| **Gemini 2.5 Pro** | **131.72s** | OfferUp | Online Marketplace | 5 | 5 |
| **Claude Sonnet 4.5** | **262.82s** | OfferUp | Online Classifieds & Marketplace | 8 | 12 |

**Speedup:** 2.0x faster ⚡
**Time Saved:** 131.11 seconds (~2.2 minutes)

---

## 🔍 Phase-by-Phase Breakdown

### Gemini 2.5 Pro Performance

| Phase | Time | Details |
|-------|------|---------|
| **Phase 1: Intelligence Gathering** | 12.79s | 6 parallel scrapers (homepage, crawl, blog, linkedin, youtube, jobs) |
| **Phase 2: Business Analysis** | 30.72s | Gemini 2.5 Pro analyzes business model |
| **Phase 3: Data Architecture** | 88.20s | Gemini 2.5 Pro infers data architecture |
| **TOTAL** | **131.72s** | |

### Claude Sonnet 4.5 Performance

| Phase | Time | Details |
|-------|------|---------|
| **Phase 1: Intelligence Gathering** | 13.04s | 6 parallel scrapers (homepage, crawl, blog, linkedin, youtube, jobs) |
| **Phase 2: Business Analysis** | 36.29s | Claude Sonnet 4.5 analyzes business model |
| **Phase 3: Data Architecture** | 213.49s | Claude Sonnet 4.5 infers data architecture |
| **TOTAL** | **262.82s** | |

---

## 💡 Key Insights

### Speed vs Quality Trade-off

**Gemini 2.5 Pro Advantages:**
- ✅ **2x faster** overall execution
- ✅ **2.9x faster** in Phase 3 (Architecture Inference): 88s vs 213s
- ✅ **1.2x faster** in Phase 2 (Business Analysis): 30.7s vs 36.3s
- ✅ Excellent for rapid prototyping and demos

**Claude Sonnet 4.5 Advantages:**
- ✅ **More thorough entity detection**: 8 entities vs 5 entities
- ✅ **Deeper architecture analysis**: 12 data entities vs 5 data entities
- ✅ Better for production use cases requiring comprehensive analysis

---

## 🎯 Recommendation

### Use Gemini 2.5 Pro When:
- Speed is critical (demos, rapid prototyping)
- You need results in ~2 minutes instead of ~4 minutes
- Basic entity extraction is sufficient
- Cost optimization is important

### Use Claude Sonnet 4.5 When:
- Comprehensive analysis is required
- You need detailed data architecture insights
- Quality > Speed for production use
- Thorough entity detection is critical

---

## 📈 Architecture Inference Analysis

The biggest performance difference is in **Phase 3 (Data Architecture Inference)**:

- **Gemini 2.5 Pro:** 88.20s
- **Claude Sonnet 4.5:** 213.49s
- **Difference:** 2.42x slower for Claude

This phase is where Claude excels at finding more data entities (12 vs 5), suggesting deeper architectural analysis.

---

## 🔧 Implementation Details

### Gemini 2.5 Pro Version

**File:** `backend/agentic_service/agents/research_agent_v2_gemini_pro.py`

**Key Changes:**
```python
# Uses Gemini 2.5 Pro instead of Claude
from ..utils.vertex_llm_client import get_gemini_pro_vertex_client

self.client = get_gemini_pro_vertex_client()
```

**Import Statement:**
```python
from backend.agentic_service.agents.research_agent_v2_gemini_pro import CustomerResearchAgentV2GeminiPro
agent = CustomerResearchAgentV2GeminiPro()
```

---

## 📁 Benchmark Files

- **JSON Results:** `benchmarks/benchmark_research_v2_gemini_pro_vs_claude.json`
- **Test Output:** `benchmarks/test_output_research_v2_gemini_pro.log`
- **Test Script:** `test_research_agent_v2_gemini_pro.py`

---

## 🚀 How to Use Gemini Pro Version

### Option 1: Direct Import
```python
from backend.agentic_service.agents.research_agent_v2_gemini_pro import CustomerResearchAgentV2GeminiPro

agent = CustomerResearchAgentV2GeminiPro()
state = {"customer_url": "https://www.example.com"}
result = await agent.execute(state)
```

### Option 2: Update Orchestrator
Replace the research agent import in your orchestrator:

**Before:**
```python
from backend.agentic_service.agents.research_agent_v2_optimized import CustomerResearchAgentV2Optimized
```

**After (for 2x speedup):**
```python
from backend.agentic_service.agents.research_agent_v2_gemini_pro import CustomerResearchAgentV2GeminiPro
```

---

## ⚠️ Important Notes

1. **Both versions use the same optimized parallel execution** for Phase 1 (intelligence gathering)
2. **Speed difference is in LLM inference** (Phases 2 & 3), not in web scraping
3. **Claude finds more entities**, suggesting more thorough analysis
4. **Gemini is faster but may miss some edge cases** in complex architectures
5. **Cost considerations:** Gemini 2.5 Pro may be more cost-effective for high-volume usage

---

## 🧪 Test Environment

- **Platform:** Google Cloud Shell
- **Project:** bq-demos-469816
- **Region:** us-central1 (Gemini), global (Claude)
- **Test URL:** https://www.offerup.com
- **Parallel Scrapers:** 6 (homepage, crawl, blog, linkedin, youtube, jobs)
- **Concurrent Requests:** 15

---

## 📝 Conclusion

**For the orchestrator, consider:**

- **Development/Demos:** Use Gemini 2.5 Pro (2x faster, ~2 minutes total)
- **Production:** Use Claude Sonnet 4.5 (more thorough, ~4 minutes total)
- **Hybrid Approach:** Use Gemini for initial research, Claude for final validation

**Winner for Speed:** Gemini 2.5 Pro ⚡
**Winner for Quality:** Claude Sonnet 4.5 🎯

---

**Last Updated:** 2025-10-05
**Benchmark Version:** research_agent_v2_gemini_pro vs research_agent_v2_optimized

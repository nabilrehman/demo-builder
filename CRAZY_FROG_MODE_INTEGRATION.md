# Crazy Frog Mode - Integration Guide

## Overview

**Crazy Frog Mode** is an advanced customization feature that allows Customer Engineers to provide rich context for highly tailored demo generation. Unlike the default mode (which only takes a customer URL), Crazy Frog Mode accepts detailed business context, target personas, complexity preferences, and specific focus areas to create perfectly customized demos.

## 🎯 Key Value Proposition

### Default Mode vs Crazy Frog Mode

| Aspect | Default Mode | Crazy Frog Mode 🐸 |
|--------|-------------|-------------------|
| **Input** | Customer URL only | URL + detailed use case context |
| **Demo Narrative** | Generic industry patterns | Specific business pain points addressed |
| **Target Audience** | Generic business user | Tailored to specific persona (CFO/CMO/CTO) |
| **Query Complexity** | Mixed (simple to medium) | Matches CE's requirements (simple/medium/advanced) |
| **Data Model** | Standard industry schema | Designed for exact scenarios CE wants |
| **Golden Queries** | Generic analytical questions | Persona-specific, business-relevant questions |

## 🏗️ Architecture

### Backend Components

#### 1. **Data Model** - `crazy_frog_request.py`
```python
class CrazyFrogProvisioningRequest(BaseModel):
    customer_url: str  # Required
    use_case_context: str  # Min 50 chars, recommended 300+

    # Optional customization hints
    industry_hint: Optional[str]
    target_persona: Optional[str]
    demo_complexity: Optional[str]
    special_focus: Optional[str]
    integrations: Optional[str]
    avoid_topics: Optional[str]
```

#### 2. **Prompt Enhancement Utility** - `prompt_enhancer.py`
- `build_crazy_frog_context_block()` - Constructs formatted context from request
- `enhance_research_prompt()` - Injects context into Research Agent
- `enhance_demo_story_prompt()` - Injects context into Demo Story Agent
- `enhance_data_modeling_prompt()` - Injects context into Data Modeling Agent
- `enhance_all_prompts_with_crazy_frog_context()` - Batch enhancement

#### 3. **Updated Prompt Templates** - `prompt_templates.py`
All 7 agent prompts now include `{crazy_frog_context}` placeholder:
- Research Agent
- Demo Story Agent
- Data Modeling Agent
- Synthetic Data Generator
- Demo Validator
- CAPI Instruction Generator
- Infrastructure Agent

#### 4. **API Endpoint** - `api.py`
```python
@app.post("/api/provision/crazy-frog")
async def start_crazy_frog_provision(request: CrazyFrogProvisioningRequest)
```

### Frontend Components

#### **CrazyFrogModeForm.tsx**
Advanced form with:
- Customer URL input
- Large textarea for use case context (500+ chars)
- Character counter with visual feedback
- Expandable accordion for optional hints:
  - Industry vertical dropdown
  - Target persona selector
  - Demo complexity level
  - Special focus area
  - Integrations to highlight
  - Topics to avoid
- Frog-themed UI with emerald green accents (#10b981)
- "🐸 Unleash the Frog" submit button

## 📋 Example Usage

### Example 1: Retail CMO Demo

**Input:**
```json
{
  "customer_url": "https://acme-retail.com",
  "use_case_context": "Leading e-commerce retailer with $500M+ annual revenue. Current pain: Marketing team uses static dashboards that require SQL expertise. They want to analyze: 1) Customer cohort behavior, 2) Product affinity analysis, 3) Marketing attribution across channels, 4) Seasonal trends. Key stakeholders: CMO (needs strategic insights), Marketing Analysts (need self-service). Success: Enable non-technical users to ask complex analytical questions.",
  "industry_hint": "Retail & E-commerce",
  "target_persona": "CMO",
  "demo_complexity": "Advanced",
  "special_focus": "Marketing Attribution",
  "integrations": "Google Analytics, Salesforce Commerce Cloud",
  "avoid_topics": "competitor comparisons, pricing strategies"
}
```

**Output:**
- **Demo Title:** "Transforming Retail Analytics: From Static Dashboards to Conversational Insights"
- **Golden Queries:** 15+ CMO-focused questions including:
  - "Show me customer acquisition by marketing channel this quarter"
  - "Which products are frequently bought together but have declining cross-sell rates?"
  - "What's the lifetime value trend for customers acquired through paid search?"
- **Schema:** Customers, Orders, Products, Marketing_Touchpoints, Cohorts tables
- **Complexity:** Advanced SQL (CTEs, window functions, multi-table JOINs)

### Example 2: Healthcare Operations Demo

**Input:**
```json
{
  "customer_url": "https://regional-health.com",
  "use_case_context": "Regional healthcare network with 15 hospitals. Need to analyze patient flow, appointment scheduling efficiency, resource utilization. Target: COO and Operations Directors (not SQL-savvy). Pain points: Can't answer 'which facilities have capacity for elective procedures?' without data team.",
  "industry_hint": "Healthcare",
  "target_persona": "COO",
  "demo_complexity": "Medium",
  "special_focus": "Operational Efficiency"
}
```

**Output:**
- **Demo Title:** "Healthcare Operations Command Center: Real-Time Resource Intelligence"
- **Golden Queries:** Operations-focused questions
- **Schema:** Facilities, Appointments, Staff, Patients, Equipment, Procedures
- **Complexity:** Medium SQL (JOINs, GROUP BY, time-series)

## 🔄 How Context Flows Through the Pipeline

```
1. CE fills out Crazy Frog form
   ↓
2. Frontend sends CrazyFrogProvisioningRequest to /api/provision/crazy-frog
   ↓
3. Backend builds context block from request
   ↓
4. Orchestrator injects context into initial state
   ↓
5. Each agent receives enhanced prompt with context:

   Research Agent:
   - Looks for aspects aligned with use case context
   - Prioritizes entities that support CE scenarios

   Demo Story Agent:
   - Designs narrative addressing specific business challenges
   - Creates golden queries for target persona
   - Matches complexity level requested

   Data Modeling Agent:
   - Includes entities from mentioned integrations
   - Structures schema to support special focus area

   Synthetic Data Generator:
   - Embeds patterns that illustrate use case scenarios
   - Creates distributions compelling for target persona

   Validator & CAPI Instruction Generator:
   - Ensures queries address use case scenarios
   - Tailors system instructions to persona
   ↓
6. Return customized demo artifacts
```

## 🧪 Testing

### Run Test Suite
```bash
cd /home/admin_/final_demo/capi/demo-gen-capi/backend
python test_crazy_frog_mode.py
```

**Test Coverage:**
1. ✅ Context block building
2. ✅ Prompt enhancement with context injection
3. ✅ Mock enhanced demo story output
4. ✅ Comparison: Default vs Crazy Frog mode

## 🎨 Design Notes

### Color Scheme
- **Crazy Frog Mode:** Emerald green (#10b981, #22c55e)
- **Default Mode:** Purple/pink gradient (#8b5cf6, #ec4899)

### UX Principles
- **Progressive Disclosure:** Optional fields hidden in accordion
- **Guided Input:** Character counter shows progress (50 min, 300+ recommended)
- **Clear Value Prop:** Tooltip explains "more context = better demo"
- **Fun but Professional:** Frog branding adds personality without compromising credibility

## 📊 Example Enhanced Prompt

**Before (Default Mode):**
```
You are a business analyst researching a company...
TASK: Analyze the provided website content...
```

**After (Crazy Frog Mode):**
```
=== CUSTOMER ENGINEER CONTEXT ===

**USE CASE DETAILS:**
Regional healthcare network with 15 hospitals...
Target: COO and Operations Directors (not SQL-savvy)

**INDUSTRY:** Healthcare
**TARGET AUDIENCE:** COO
IMPORTANT: Tailor the demo narrative, terminology, and metrics to resonate with a COO.

**COMPLEXITY LEVEL:** Medium
Balance simple and complex queries. Include JOINs, GROUP BY, basic time-series.

**SPECIAL FOCUS:** Operational Efficiency
Ensure golden queries and data model emphasize Operational Efficiency scenarios.

=== END CUSTOMER ENGINEER CONTEXT ===

You are a business analyst researching a company...
TASK: Analyze the provided website content...

**IMPORTANT:** Use the above CE context to guide your research...
```

## 🚀 Integration Checklist

### Backend ✅
- [x] CrazyFrogProvisioningRequest model created
- [x] prompt_enhancer.py utility created
- [x] prompt_templates.py updated with `{crazy_frog_context}` placeholders
- [x] /api/provision/crazy-frog endpoint added to api.py
- [x] Test suite created and passing

### Frontend ✅
- [x] CrazyFrogModeForm.tsx component created
- [ ] Add route to App.tsx (e.g., `/crazy-frog`)
- [ ] Integrate with CE dashboard or provisioning flow
- [ ] Add progress tracking for long-running provisioning

### Orchestrator Integration 🔄
- [ ] Update agents to use `state["crazy_frog_context"]` when formatting prompts
- [ ] Add logic to check if `crazy_frog_request` exists in state
- [ ] Format prompts with `.format(crazy_frog_context=context or "")` fallback

## 💡 Best Practices for CEs

### Writing Effective Use Case Context

**Good Example:**
```
Leading fintech startup ($50M ARR) needs to demo real-time fraud detection
analytics. Current pain: Security team gets alerts but can't ask "show me
transaction patterns for flagged users in last 24h across all accounts".
Target: CISO and Security Ops team. Success: Enable security analysts to
investigate anomalies through natural language without waiting for data team.
```

**Better Example:**
```
Enterprise SaaS company (5000+ customers) struggling with churn prediction.
Pain points:
1. Customer Success team can't identify at-risk accounts without data analyst
2. No way to ask "which high-value customers reduced usage 30%+ this month?"
3. Insights lag by 1+ weeks, too late to intervene

Desired capabilities:
- Real-time customer health scoring
- Usage trend analysis across product features
- Predictive cohort analysis (likelihood to churn)

Stakeholders:
- VP Customer Success: Needs proactive churn signals
- CS Managers: Need account-level drill-down
- Ops Team: Needs aggregate trends

Success: CS team can identify and act on churn risks within 24 hours,
reducing churn by 15% ($2M+ annual impact).
```

### Selecting Complexity Level

- **Simple:** Demo to executives or non-technical stakeholders (basic aggregations)
- **Medium:** Demo to business analysts (JOINs, GROUP BY, time-series)
- **Advanced:** Demo to data teams or technical buyers (CTEs, window functions, statistical analysis)

## 🔗 Files Created

### Backend
- `/backend/agentic_service/models/crazy_frog_request.py`
- `/backend/agentic_service/utils/prompt_enhancer.py`
- `/backend/agentic_service/utils/prompt_templates.py` (updated)
- `/backend/api.py` (updated with endpoint)
- `/backend/test_crazy_frog_mode.py`

### Frontend
- `/newfrontend/conversational-api-demo-frontend/src/components/CrazyFrogModeForm.tsx`

### Documentation
- `/CRAZY_FROG_MODE_INTEGRATION.md` (this file)

## 🎯 Success Metrics

The feature is working correctly when:
1. ✅ Test suite passes all 4 tests
2. ✅ Context block includes all provided hints
3. ✅ Enhanced prompts contain CE context before base prompt
4. ✅ API endpoint returns success with demo artifacts
5. ✅ Frontend form validates input and submits to backend
6. ✅ Generated demos align with CE's specified persona, complexity, and focus

---

**Built with 🐸 for Customer Engineers who want maximum demo customization!**

# Agent Configuration System

Centralized configuration for selecting which LLM model (Gemini vs Claude) to use for each agent in the pipeline.

## Quick Start

### View Current Configuration

```bash
# Simple view
python3 scripts/show_agent_config.py

# Detailed view with benchmarks
python3 scripts/show_agent_config.py --detailed
```

### Change Model for an Agent

```bash
# Option 1: Environment variable (temporary)
export RESEARCH_AGENT_MODEL=claude
export DEMO_STORY_AGENT_MODEL=gemini

# Option 2: Update .env file (permanent)
# Edit backend/.env or backend/local.env
RESEARCH_AGENT_MODEL=claude
DEMO_STORY_AGENT_MODEL=gemini
DATA_MODELING_AGENT_MODEL=claude
CAPI_AGENT_MODEL=claude
```

## Available Agents

| Agent | Options | Default | Recommendation |
|-------|---------|---------|----------------|
| **Research** | `gemini`, `claude` | `gemini` | Gemini for speed (2x faster), Claude for quality (more entities) |
| **Demo Story** | `gemini`, `claude` | `gemini` | Gemini (2x faster, same quality) |
| **Data Modeling** | `gemini`, `claude` | `claude` | Claude (user preference) |
| **CAPI Instructions** | `gemini`, `claude` | `claude` | Claude (quality critical - Gemini incomplete) |

## Benchmark-Based Recommendations

### Speed Mode (Fastest - ~3 minutes)
```bash
RESEARCH_AGENT_MODEL=gemini      # 2x faster
DEMO_STORY_AGENT_MODEL=gemini    # 2x faster, same quality
DATA_MODELING_AGENT_MODEL=gemini # Untested but likely fast
CAPI_AGENT_MODEL=claude          # Quality critical - don't change
```

### Quality Mode (Most Thorough - ~5 minutes)
```bash
RESEARCH_AGENT_MODEL=claude      # More entities (8 vs 5)
DEMO_STORY_AGENT_MODEL=gemini    # Same quality, 2x faster
DATA_MODELING_AGENT_MODEL=claude # User preference
CAPI_AGENT_MODEL=claude          # Quality critical
```

### Balanced Mode (Recommended - ~4 minutes)
```bash
RESEARCH_AGENT_MODEL=gemini      # 2x faster
DEMO_STORY_AGENT_MODEL=gemini    # 2x faster, same quality
DATA_MODELING_AGENT_MODEL=claude # User preference
CAPI_AGENT_MODEL=claude          # Quality critical
```

## Benchmark Results

Detailed benchmarks available in:
- `benchmarks/RESEARCH_V2_GEMINI_PRO_RESULTS.md`
- `benchmarks/DEMO_STORY_GEMINI_PRO_RESULTS.md`
- `benchmarks/CAPI_INSTRUCTION_GEMINI_PRO_RESULTS.md`
- `benchmarks/AGENT_SELECTOR_GUIDE.md`

## Usage in Code

```python
from agentic_service.config.agent_config import get_agent_class

# Get agent class (checks env var, then default)
ResearchAgentClass = get_agent_class("research")
agent = ResearchAgentClass(max_pages=30, max_depth=2)

# Override with parameter
ResearchAgentClass = get_agent_class("research", model="claude")
agent = ResearchAgentClass(max_pages=30, max_depth=2)
```

## Cloud Run Deployment

In Cloud Run, set environment variables:

```bash
# Using gcloud CLI
gcloud run services update demo-gen-capi-backend \
  --region us-central1 \
  --update-env-vars RESEARCH_AGENT_MODEL=gemini,DEMO_STORY_AGENT_MODEL=gemini,DATA_MODELING_AGENT_MODEL=claude,CAPI_AGENT_MODEL=claude

# Or use service.yaml
env:
  - name: RESEARCH_AGENT_MODEL
    value: gemini
  - name: DEMO_STORY_AGENT_MODEL
    value: gemini
  - name: DATA_MODELING_AGENT_MODEL
    value: claude
  - name: CAPI_AGENT_MODEL
    value: claude
```

## Files

- `agent_config.py` - Main configuration module
- `__init__.py` - Package exports
- `README.md` - This file

## Important Notes

1. **CAPI Agent**: Must use Claude - Gemini produces incomplete YAML (missing tables/queries)
2. **Demo Story Agent**: Gemini is clear winner (2x faster, identical quality)
3. **Research Agent**: Gemini for speed, Claude for thoroughness
4. **Data Modeling**: Claude by user preference

## Troubleshooting

### Check current configuration
```bash
python3 scripts/show_agent_config.py --detailed
```

### Verify environment variables
```bash
env | grep AGENT_MODEL
```

### Test configuration
```python
from agentic_service.config.agent_config import get_current_config
print(get_current_config())
# Output: {'research': 'gemini', 'demo_story': 'gemini', 'data_modeling': 'claude', 'capi': 'claude'}
```

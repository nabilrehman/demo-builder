# Testing Framework for CAPI Demo Generator

## Overview

This testing framework enables **fast, isolated testing** of the 7-agent pipeline without running the entire system every time.

### Key Benefits
- **Speed**: Test in 30 seconds instead of 8-12 minutes
- **Isolation**: Test individual agents without running predecessors
- **Reproducibility**: Use saved snapshots for consistent test conditions
- **Debugging**: Quickly iterate on bug fixes without full pipeline runs

---

## Directory Structure

```
tests/
├── README.md                              # This file
├── fixtures/
│   ├── snapshots/                         # Captured from real job runs
│   │   ├── nike_20251006/
│   │   │   ├── 01_research_output.json
│   │   │   ├── 02_demo_story_output.json
│   │   │   ├── 03_data_modeling_output.json
│   │   │   ├── 04_synthetic_data_output.json
│   │   │   ├── 05_infrastructure_output.json
│   │   │   ├── 06_capi_instructions_output.json
│   │   │   ├── 07_validation_output.json
│   │   │   ├── complete_job_state.json
│   │   │   └── metadata.json
│   │   └── shopify_20251006/...
│   └── templates/                         # Hand-curated minimal states
│       └── minimal_state.json
├── utils/
│   ├── snapshot_capture.py                # Capture job outputs as fixtures
│   ├── fixture_loader.py                  # Load fixtures for testing
│   └── mock_services.py                   # Mock BigQuery, Gemini (future)
├── test_infrastructure_agent_with_fixtures.py  # Example test
└── conftest.py                            # Pytest fixtures (future)
```

---

## Quick Start

### 1. Capture a Snapshot from a Successful Job

After a job completes successfully, capture its state:

```bash
cd /home/admin_/final_demo/capi/demo-gen-capi/backend

# Capture snapshot (replace JOB_ID with actual ID)
python -m tests.utils.snapshot_capture <JOB_ID> --name nike_20251006 --create-template
```

This creates:
- `tests/fixtures/snapshots/nike_20251006/` with all agent outputs
- `tests/fixtures/templates/minimal_state.json` (if --create-template used)

### 2. Run Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_infrastructure_agent_with_fixtures.py

# Run specific test
pytest tests/test_infrastructure_agent_with_fixtures.py::TestInfrastructureAgentWithFixtures::test_infrastructure_with_synthetic_data_snapshot

# Run tests with verbose output
pytest -v tests/

# Run tests excluding slow ones
pytest -m "not slow" tests/
```

### 3. Example: Test Infrastructure Agent

```python
from tests.utils.fixture_loader import FixtureLoader
from agentic_service.agents.infrastructure_agent_optimized import InfrastructureAgentOptimized

# Load state after Synthetic Data Generator (agent 4)
loader = FixtureLoader()
state = loader.load_snapshot("nike_20251006", "04_synthetic_data")

# Test Infrastructure Agent (agent 5)
agent = InfrastructureAgentOptimized()
result = await agent.execute(state)

# Verify CAPI agent was created
assert result["capi_agent_created"] == True
assert result.get("capi_agent_id"), "CAPI agent ID should not be empty"
```

---

## Use Cases

### Use Case 1: Test CAPI Agent Creation Fix

**Problem**: Infrastructure Agent fails to create CAPI Data Agent

**Traditional Approach**: Run full pipeline (8-12 min) → Wait for Infrastructure Agent → See failure → Fix code → Repeat

**With Testing Framework**:
1. Capture snapshot from last successful run (before bug)
2. Load `04_synthetic_data_output.json` (input to Infrastructure Agent)
3. Test Infrastructure Agent in isolation (~30s)
4. Iterate on fix quickly

**Example**:
```bash
# Capture snapshot once
python -m tests.utils.snapshot_capture abc123 --name before_capi_bug

# Test Infrastructure Agent repeatedly (30s each)
pytest tests/test_infrastructure_agent_with_fixtures.py -v
```

### Use Case 2: Regression Testing

**Goal**: Ensure bug fixes don't break in future

**Approach**:
1. Capture snapshot when bug was discovered
2. Write test that reproduces the bug
3. Fix bug, verify test passes
4. Keep test to prevent regression

**Example**:
```python
@pytest.mark.regression
async def test_capi_agent_creation_not_empty(self, fixture_loader):
    """Regression test for CAPI agent creation bug."""
    state = fixture_loader.load_snapshot("nike_20251006", "04_synthetic_data")
    agent = InfrastructureAgentOptimized()
    result = await agent.execute(state)

    # This used to fail before the fix
    assert result.get("capi_agent_id"), "CAPI agent ID must not be empty"
```

### Use Case 3: Test Data Modeling Changes

**Goal**: Test Data Modeling Agent with different customer types

**Approach**:
1. Capture snapshots from different industries (Nike, Shopify, Stripe)
2. Load `01_research_output.json` (input to Data Modeling Agent)
3. Test schema generation for each industry

**Example**:
```python
@pytest.mark.parametrize("snapshot_name", ["nike_20251006", "shopify_20251006", "stripe_20251006"])
async def test_schema_generation(self, snapshot_name, fixture_loader):
    state = fixture_loader.load_snapshot(snapshot_name, "01_research")
    agent = DataModelingAgentGeminiPro()
    result = await agent.execute(state)

    assert len(result["schema"]["tables"]) >= 5, "Should generate at least 5 tables"
```

---

## Snapshot Capture Tool

### Usage

```bash
python -m tests.utils.snapshot_capture <JOB_ID> [OPTIONS]
```

### Options
- `--name SNAPSHOT_NAME`: Custom snapshot name (default: auto-generated from company)
- `--create-template`: Also create minimal template for fast testing

### What Gets Captured

For each agent, the snapshot captures:
- **Input state**: What the agent received
- **Output state**: What the agent produced
- **Metadata**: Job info, timestamps, dataset IDs

### Example

```bash
# Capture Nike job
python -m tests.utils.snapshot_capture abc-123-def --name nike_20251006

# Output:
✅ Snapshot captured: nike_20251006
   Location: tests/fixtures/snapshots/nike_20251006
   Agents: 7
   Dataset: nike_capi_demo_20251006
   CAPI Agent: nike_demo_20251006_1234
```

---

## Fixture Loader Tool

### Basic Usage

```python
from tests.utils.fixture_loader import FixtureLoader

loader = FixtureLoader()

# Load specific agent output
state = loader.load_snapshot("nike_20251006", "04_synthetic_data")

# Load minimal template (fast testing)
state = loader.load_template("minimal_state")

# List available fixtures
snapshots = loader.list_snapshots()
templates = loader.list_templates()

# Print summary
loader.print_summary()
```

### Convenience Function

```python
from tests.utils.fixture_loader import load_fixture

# Load snapshot
state = load_fixture("nike_20251006", "04_synthetic_data")

# Load template
state = load_fixture("minimal_state")
```

---

## Writing Tests

### Test Structure

```python
import pytest
from tests.utils.fixture_loader import FixtureLoader
from agentic_service.agents.YOUR_AGENT import YourAgent

class TestYourAgent:
    @pytest.fixture
    def fixture_loader(self):
        return FixtureLoader()

    @pytest.mark.asyncio
    async def test_your_agent_with_fixture(self, fixture_loader):
        # Load input state
        state = fixture_loader.load_snapshot("nike_20251006", "03_data_modeling")

        # Execute agent
        agent = YourAgent()
        result = await agent.execute(state)

        # Assertions
        assert result["expected_field"] == "expected_value"
```

### Markers

```python
@pytest.mark.slow           # Slow test (excluded by default)
@pytest.mark.integration    # Integration test
@pytest.mark.unit           # Unit test
@pytest.mark.requires_bq    # Requires BigQuery access
@pytest.mark.requires_gemini # Requires Gemini API access
```

---

## Best Practices

### 1. Capture Multiple Snapshots
- Different industries (ecommerce, fintech, sports)
- Different data sizes (small, medium, large)
- Edge cases (circular dependencies, REPEATED fields)

### 2. Use Descriptive Snapshot Names
- ✅ `nike_ecommerce_20251006`
- ✅ `stripe_fintech_large_20251006`
- ❌ `snapshot1`
- ❌ `test_data`

### 3. Keep Snapshots Small
- Don't capture full CSV files (too large)
- Capture state metadata only
- Use templates for minimal tests

### 4. Document Test Purpose
```python
async def test_infrastructure_capi_creation(self):
    """
    Test Infrastructure Agent CAPI creation fix.

    Bug: agent_id was empty, causing chat to fallback to .env agent
    Fix: Generate data_agent_id upfront, include in CreateDataAgentRequest
    Regression test: Ensure CAPI agent ID is never empty
    """
```

---

## Next Steps

### Immediate (Done ✅)
- [x] Create snapshot capture tool
- [x] Create fixture loader
- [x] Create example test
- [x] Create pytest config
- [x] Create this README

### Short Term (TODO)
- [ ] Capture first successful Nike job as snapshot
- [ ] Run example test to verify framework works
- [ ] Create mock services for BigQuery and Gemini
- [ ] Add conftest.py with reusable fixtures

### Long Term (TODO)
- [ ] Capture 3-5 diverse snapshots (different industries)
- [ ] Write comprehensive test suite for all agents
- [ ] Add CI/CD integration (run tests on every commit)
- [ ] Performance benchmarking tests

---

## FAQ

**Q: Why not just run the full pipeline?**
A: Full pipeline takes 8-12 minutes. With fixtures, you can test a specific agent in 30 seconds.

**Q: How do I test agents that depend on external APIs (BigQuery, Gemini)?**
A: Use mocks (coming soon in `tests/utils/mock_services.py`). For now, tests hit real APIs.

**Q: Can I modify a snapshot before testing?**
A: Yes! Load it, modify the state dict, then pass to agent. Useful for testing edge cases.

**Q: How often should I capture new snapshots?**
A: After major changes, or when you encounter a new bug/edge case worth preserving.

**Q: Do snapshots contain sensitive data?**
A: No. They contain synthetic data and metadata only. Safe to commit to git.

---

## Contributing

When adding new tests:
1. Use descriptive test names
2. Add docstrings explaining what's being tested
3. Use appropriate markers (@pytest.mark.slow, etc.)
4. Update this README if adding new patterns

---

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Testing Best Practices](https://docs.python.org/3/library/unittest.html)

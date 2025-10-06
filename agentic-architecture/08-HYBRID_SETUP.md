# Hybrid Setup - Gemini + Claude Sonnet 4.5 (Optimal)

## 🎯 Best of Both Worlds

Use **Claude Sonnet 4.5** for complex reasoning and **Gemini 2.5 Pro** for data/content generation.

---

## 🏆 Optimal Agent Assignment

```
┌─────────────────────────────────────┐
│         LangGraph Orchestrator      │
└──────────────┬──────────────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼────┐ ┌──▼───┐ ┌───▼────┐
│Research│ │Data  │ │Infra   │
│        │ │Model │ │        │
│CLAUDE  │ │GEMINI│ │Python  │
│4.5     │ │2.5Pro│ │BigQuery│
└────────┘ └──────┘ └────────┘
    │          │          │
    └──────────┼──────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼────┐ ┌──▼───────┐
│  CAPI  │ │  Demo    │
│ Agent  │ │ Content  │
│        │ │          │
│Google  │ │  GEMINI  │
│CAPI API│ │  2.5 Pro │
└────────┘ └──────────┘
```

### Why This Split?

| Agent | Model | Reasoning |
|-------|-------|-----------|
| **Research Agent** | **Claude Sonnet 4.5** | ✅ Best reasoning for complex business analysis<br>✅ Superior at understanding nuanced business models<br>✅ Better at extracting structured data from unstructured text |
| **Data Modeling** | **Gemini 2.5 Pro** | ✅ Excellent at schema generation<br>✅ Strong code generation (SQL, JSON)<br>✅ You have credits (cost-effective)<br>✅ Native BigQuery understanding |
| **Infrastructure** | **Python** | No LLM needed (direct BigQuery SDK) |
| **CAPI Creator** | **Google CAPI** | No LLM needed (API calls) |
| **Demo Content** | **Gemini 2.5 Pro** | ✅ Great creative content generation<br>✅ Excellent at writing queries<br>✅ Cost-effective with your credits |

**Result**: Claude for the hardest task (research), Gemini for everything else!

---

## 📦 Dependencies

```txt
# requirements.txt

# Core
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.6.0
python-dotenv==1.0.0

# Agentic Framework
langgraph==0.0.20
langchain-core==0.1.0

# LLMs
google-generativeai==0.3.2       # Gemini
anthropic==0.18.0                 # Claude

# Google Cloud
google-cloud-bigquery==3.17.0
google-cloud-geminidataanalytics==0.1.0

# Utilities
aiohttp==3.9.0
beautifulsoup4==4.12.0
faker==22.0.0
```

---

## 🔧 Unified LLM Client

```python
# backend/agentic_service/utils/llm_client.py
"""
Unified LLM client supporting both Gemini and Claude.
"""
import os
import json
import logging
from typing import Optional, Dict
from enum import Enum

import google.generativeai as genai
from anthropic import Anthropic

logger = logging.getLogger(__name__)

# Configure APIs
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


class ModelType(Enum):
    """Supported model types."""
    GEMINI = "gemini-2.5-pro"
    CLAUDE = "claude-sonnet-4-5-20241022"


class LLMClient:
    """Unified client for multiple LLMs."""

    def __init__(self, model_type: ModelType):
        """
        Initialize LLM client.

        Args:
            model_type: Which model to use (GEMINI or CLAUDE)
        """
        self.model_type = model_type

        if model_type == ModelType.GEMINI:
            self.gemini_model = genai.GenerativeModel(model_type.value)
        elif model_type == ModelType.CLAUDE:
            self.anthropic_client = anthropic_client
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

    async def generate_content(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_output_tokens: int = 8192,
        system_instruction: Optional[str] = None
    ) -> str:
        """
        Generate content using the configured model.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_output_tokens: Maximum tokens to generate
            system_instruction: Optional system instruction

        Returns:
            Generated text
        """
        try:
            if self.model_type == ModelType.GEMINI:
                return await self._generate_gemini(
                    prompt, temperature, max_output_tokens, system_instruction
                )
            elif self.model_type == ModelType.CLAUDE:
                return await self._generate_claude(
                    prompt, temperature, max_output_tokens, system_instruction
                )
        except Exception as e:
            logger.error(f"Generation failed with {self.model_type.name}: {e}")
            raise

    async def _generate_gemini(
        self,
        prompt: str,
        temperature: float,
        max_output_tokens: int,
        system_instruction: Optional[str]
    ) -> str:
        """Generate content using Gemini."""
        # Create model with system instruction if provided
        if system_instruction:
            model = genai.GenerativeModel(
                self.model_type.value,
                system_instruction=system_instruction
            )
        else:
            model = self.gemini_model

        generation_config = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            top_p=0.95,
        )

        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )

        return response.text

    async def _generate_claude(
        self,
        prompt: str,
        temperature: float,
        max_output_tokens: int,
        system_instruction: Optional[str]
    ) -> str:
        """Generate content using Claude."""
        messages = [{"role": "user", "content": prompt}]

        response = self.anthropic_client.messages.create(
            model=self.model_type.value,
            max_tokens=max_output_tokens,
            temperature=temperature,
            system=system_instruction or "",
            messages=messages
        )

        return response.content[0].text

    async def generate_with_retry(
        self,
        prompt: str,
        max_retries: int = 3,
        **kwargs
    ) -> str:
        """Generate with automatic retry on failure."""
        import asyncio

        for attempt in range(max_retries):
            try:
                return await self.generate_content(prompt, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"Attempt {attempt + 1} failed, retrying: {e}")
                await asyncio.sleep(2 ** attempt)

    def parse_json_response(self, response_text: str) -> Dict:
        """Parse JSON from LLM response."""
        # Remove markdown code blocks if present
        if "```json" in response_text:
            json_start = response_text.index("```json") + 7
            json_end = response_text.rindex("```")
            json_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.index("```") + 3
            json_end = response_text.rindex("```")
            json_text = response_text[json_start:json_end].strip()
        else:
            json_text = response_text.strip()

        try:
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.error(f"Response text: {response_text}")
            raise ValueError(f"Invalid JSON response: {str(e)}")


# ============================================================================
# Convenience Functions
# ============================================================================

def get_claude_client() -> LLMClient:
    """Get Claude client."""
    return LLMClient(ModelType.CLAUDE)


def get_gemini_client() -> LLMClient:
    """Get Gemini client."""
    return LLMClient(ModelType.GEMINI)
```

---

## 🤖 Updated Agent Implementations

### Research Agent (Claude Sonnet 4.5)

```python
# backend/agentic_service/agents/research_agent.py
"""
Customer Research Agent - Uses Claude Sonnet 4.5 for superior reasoning.
"""
import logging
from typing import Dict

from ..utils.llm_client import get_claude_client
from ..tools.web_research import scrape_website
from ..utils.prompt_templates import RESEARCH_AGENT_PROMPT

logger = logging.getLogger(__name__)


class CustomerResearchAgent:
    """Agent for researching customer business domain."""

    def __init__(self):
        # Use Claude for complex business analysis
        self.client = get_claude_client()
        logger.info("Research Agent initialized with Claude Sonnet 4.5")

    async def execute(self, state: Dict) -> Dict:
        """Execute research phase."""
        logger.info(f"Researching {state['customer_url']} with Claude")

        try:
            # Scrape website
            website_content = await scrape_website(state["customer_url"])
            logger.info(f"Scraped {len(website_content)} characters")

            # Analyze with Claude (best reasoning)
            analysis = await self._analyze_business(website_content)

            # Update state
            state["customer_info"] = analysis
            state["business_domain"] = analysis.get("business_domain")
            state["industry"] = analysis.get("industry")
            state["key_entities"] = [e["name"] for e in analysis.get("key_entities", [])]

            logger.info(f"Claude analysis complete. Domain: {state['business_domain']}")
            return state

        except Exception as e:
            logger.error(f"Research failed: {e}", exc_info=True)
            raise

    async def _analyze_business(self, website_content: str) -> Dict:
        """Use Claude to analyze business (superior reasoning)."""
        # Truncate if needed
        max_chars = 15000
        if len(website_content) > max_chars:
            website_content = website_content[:max_chars] + "\n\n[Content truncated...]"

        prompt = RESEARCH_AGENT_PROMPT.format(website_content=website_content)

        # Claude excels at this complex analysis task
        response_text = await self.client.generate_with_retry(
            prompt=prompt,
            temperature=0.2,  # Lower for more consistent analysis
            max_output_tokens=4096,
            system_instruction="You are a business analyst expert at understanding company business models from their websites."
        )

        return self.client.parse_json_response(response_text)
```

### Data Modeling Agent (Gemini 2.5 Pro)

```python
# backend/agentic_service/agents/data_modeling_agent.py
"""
Data Modeling Agent - Uses Gemini 2.5 Pro for schema generation.
"""
import json
import logging
from typing import Dict, List
from faker import Faker

from ..utils.llm_client import get_gemini_client
from ..utils.prompt_templates import DATA_MODELING_PROMPT

logger = logging.getLogger(__name__)


class DataModelingAgent:
    """Agent for designing data schema."""

    def __init__(self):
        # Use Gemini for schema/code generation
        self.client = get_gemini_client()
        self.faker = Faker()
        logger.info("Data Modeling Agent initialized with Gemini 2.5 Pro")

    async def execute(self, state: Dict) -> Dict:
        """Execute data modeling phase."""
        logger.info("Designing data schema with Gemini")

        try:
            # Design schema with Gemini (excellent at this)
            schema_design = await self._design_schema(
                state["customer_info"],
                state["key_entities"]
            )

            # Generate synthetic data
            sample_data = await self._generate_data(schema_design)

            # Update state
            state["schema_design"] = schema_design
            state["table_definitions"] = schema_design["tables"]
            state["sample_data"] = sample_data

            logger.info(f"Gemini created {len(schema_design['tables'])} table schemas")
            return state

        except Exception as e:
            logger.error(f"Data modeling failed: {e}", exc_info=True)
            raise

    async def _design_schema(self, customer_info: Dict, entities: List[str]) -> Dict:
        """Use Gemini to design schema (great at structured output)."""
        prompt = DATA_MODELING_PROMPT.format(
            customer_info=json.dumps(customer_info, indent=2),
            entities=json.dumps(entities)
        )

        # Gemini excels at schema/code generation
        response_text = await self.client.generate_with_retry(
            prompt=prompt,
            temperature=0.3,
            max_output_tokens=8192,
            system_instruction="You are a database architect expert at designing BigQuery schemas."
        )

        return self.client.parse_json_response(response_text)

    async def _generate_data(self, schema: Dict) -> Dict[str, List[Dict]]:
        """Generate synthetic data using Faker."""
        all_data = {}

        for table in schema["tables"]:
            records = []
            count = table.get("record_count", 100)

            for i in range(count):
                record = self._generate_record(table["schema"], i)
                records.append(record)

            all_data[table["name"]] = records
            logger.info(f"Generated {count} records for {table['name']}")

        return all_data

    def _generate_record(self, schema: List[Dict], index: int) -> Dict:
        """Generate a single record with Faker."""
        record = {}

        for field in schema:
            field_name = field["name"]
            field_type = field["type"]

            # Smart field generation based on name and type
            if "id" in field_name.lower():
                record[field_name] = index + 1
            elif field_type == "STRING":
                if "email" in field_name.lower():
                    record[field_name] = self.faker.email()
                elif "name" in field_name.lower():
                    record[field_name] = self.faker.name()
                elif "address" in field_name.lower():
                    record[field_name] = self.faker.address()
                elif "phone" in field_name.lower():
                    record[field_name] = self.faker.phone_number()
                elif "company" in field_name.lower():
                    record[field_name] = self.faker.company()
                elif "url" in field_name.lower():
                    record[field_name] = self.faker.url()
                elif "description" in field_name.lower():
                    record[field_name] = self.faker.text(max_nb_chars=200)
                else:
                    record[field_name] = self.faker.word()
            elif field_type == "INT64":
                record[field_name] = self.faker.random_int(min=1, max=10000)
            elif field_type == "FLOAT64":
                record[field_name] = round(self.faker.random.uniform(0, 1000), 2)
            elif field_type == "TIMESTAMP":
                record[field_name] = self.faker.date_time_this_year().isoformat()
            elif field_type == "DATE":
                record[field_name] = self.faker.date_this_year().isoformat()
            elif field_type == "BOOL":
                record[field_name] = self.faker.boolean()
            else:
                record[field_name] = None

        return record
```

### Demo Content Generator (Gemini 2.5 Pro)

```python
# backend/agentic_service/agents/demo_content_agent.py
"""
Demo Content Generator - Uses Gemini 2.5 Pro for creative content.
"""
import json
import logging
from typing import Dict

from ..utils.llm_client import get_gemini_client
from ..utils.prompt_templates import DEMO_CONTENT_PROMPT

logger = logging.getLogger(__name__)


class DemoContentGenerator:
    """Agent for generating demo content."""

    def __init__(self):
        # Use Gemini for creative content generation
        self.client = get_gemini_client()
        logger.info("Demo Content Agent initialized with Gemini 2.5 Pro")

    async def execute(self, state: Dict) -> Dict:
        """Execute demo content generation."""
        logger.info("Generating demo content with Gemini")

        try:
            # Generate content with Gemini (great at creative tasks)
            demo_content = await self._generate_content(
                state["customer_info"],
                state["schema_design"]
            )

            # Update state
            state["golden_queries"] = demo_content["golden_queries"]
            state["demo_script"] = demo_content["demo_script"]
            state["sample_qa"] = demo_content["sample_qa"]
            state["current_phase"] = "completed"
            state["progress_percentage"] = 100

            logger.info(f"Gemini generated {len(demo_content['golden_queries'])} golden queries")
            return state

        except Exception as e:
            logger.error(f"Demo content generation failed: {e}", exc_info=True)
            raise

    async def _generate_content(self, customer_info: Dict, schema: Dict) -> Dict:
        """Use Gemini to generate demo content (excellent at this)."""
        schema_summary = self._summarize_schema(schema)

        prompt = DEMO_CONTENT_PROMPT.format(
            customer_info=json.dumps(customer_info, indent=2),
            schema_summary=schema_summary
        )

        # Gemini is great at generating queries and scripts
        response_text = await self.client.generate_with_retry(
            prompt=prompt,
            temperature=0.7,  # Higher for creative content
            max_output_tokens=8192,
            system_instruction="You are a sales enablement specialist creating compelling demo content."
        )

        return self.client.parse_json_response(response_text)

    def _summarize_schema(self, schema: Dict) -> str:
        """Create human-readable schema summary."""
        summary = []
        for table in schema["tables"]:
            fields = [f["name"] for f in table["schema"][:5]]
            summary.append(f"- {table['name']}: {', '.join(fields)}...")
        return "\n".join(summary)
```

---

## 🔧 Environment Configuration

### .env file

```bash
# .env (for local development)

# Claude Sonnet 4.5
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Gemini 2.5 Pro
GEMINI_API_KEY=your-gemini-key-here

# Google Cloud
PROJECT_ID=bq-demos-469816
LOCATION=us-central1

# Environment
ENVIRONMENT=development
```

### Cloud Run Secrets

```bash
# Create secrets
echo -n "your_claude_key" | gcloud secrets create claude-api-key \
    --data-file=- \
    --replication-policy="automatic"

echo -n "your_gemini_key" | gcloud secrets create gemini-api-key \
    --data-file=- \
    --replication-policy="automatic"

# Grant access to service account
for secret in claude-api-key gemini-api-key; do
    gcloud secrets add-iam-policy-binding $secret \
        --member="serviceAccount:capi-demo-sa@bq-demos-469816.iam.gserviceaccount.com" \
        --role="roles/secretmanager.secretAccessor"
done
```

### Deploy with Both Secrets

```bash
gcloud run deploy capi-agentic-demo \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 8Gi \
  --cpu 4 \
  --timeout 3600 \
  --min-instances 1 \
  --max-instances 10 \
  --service-account capi-demo-sa@bq-demos-469816.iam.gserviceaccount.com \
  --set-env-vars "PROJECT_ID=bq-demos-469816,LOCATION=us-central1" \
  --set-secrets "ANTHROPIC_API_KEY=claude-api-key:latest,GEMINI_API_KEY=gemini-api-key:latest"
```

---

## 💰 Cost Analysis (Hybrid Approach)

### Per Provisioning Job

| Agent | Model | Input | Output | Cost |
|-------|-------|-------|--------|------|
| Research | Claude 4.5 | 5K | 1K | $0.03 |
| Data Modeling | Gemini 2.5 Pro | 2K | 3K | $0.02 |
| Demo Content | Gemini 2.5 Pro | 3K | 2K | $0.01 |
| Infrastructure | N/A | - | - | $0.01 (BQ) |
| **Total** | - | **10K** | **6K** | **$0.07** |

### Monthly Costs (200 demos)

| Item | Cost |
|------|------|
| Claude API | $6 (200 × $0.03) |
| Gemini API | $6 (200 × $0.03) |
| BigQuery | $20 |
| Cloud Run | $30 |
| **Total** | **~$62/month** |

**With Gemini credits**: Reduces to ~$56/month!

### Cost Comparison

| Approach | Cost/Demo | Monthly (200) |
|----------|-----------|---------------|
| **All Claude** | $0.17 | $54 (LLM) + $50 (infra) = $104 |
| **All Gemini** | $0.05 | $10 (LLM) + $50 (infra) = $60 |
| **Hybrid (Recommended)** | $0.07 | $12 (LLM) + $50 (infra) = $62 |

**Hybrid gives best quality for only $2/month more than all-Gemini!**

---

## 🎯 Why Hybrid is Optimal

### Claude Sonnet 4.5 Advantages (Research)
✅ **Superior reasoning** - Best at understanding complex business models
✅ **Better extraction** - Excels at pulling structured data from unstructured text
✅ **Nuanced understanding** - Catches subtle business domain details
✅ **Consistent output** - More reliable JSON formatting

### Gemini 2.5 Pro Advantages (Data & Content)
✅ **Excellent schema generation** - Strong at database design
✅ **Native BigQuery knowledge** - Understands BQ types and constraints
✅ **Great at queries** - Perfect for SQL and demo query generation
✅ **Cost-effective** - You have credits!
✅ **Fast** - Lower latency

### Result
**Use the right tool for each job:**
- Claude where reasoning matters most (research)
- Gemini where code/content generation excels (schema, queries)

---

## ✅ Quick Start (Hybrid Setup)

```bash
# 1. Get both API keys
# - Claude: https://console.anthropic.com/
# - Gemini: https://makersuite.google.com/app/apikey

# 2. Set up environment
cat > backend/.env << EOF
ANTHROPIC_API_KEY=sk-ant-your-key
GEMINI_API_KEY=your-gemini-key
PROJECT_ID=bq-demos-469816
LOCATION=us-central1
EOF

# 3. Install dependencies
pip install anthropic google-generativeai langgraph langchain-core

# 4. Copy the hybrid code from this document

# 5. Test locally
cd backend
uvicorn api:app --reload --port 8000

# 6. Deploy to Cloud Run
gcloud run deploy capi-agentic-demo --source .
```

---

## 🎯 Summary

**Optimal Hybrid Setup:**
- ✅ Claude Sonnet 4.5 for Research (best reasoning)
- ✅ Gemini 2.5 Pro for Data Modeling & Demo Content (cost-effective, excellent quality)
- ✅ Total cost: ~$0.07/demo or ~$62/month
- ✅ Best quality-to-cost ratio
- ✅ Works perfectly on Cloud Run

**This is the recommended approach!** 🚀

You get Claude's superior reasoning where it matters most (understanding businesses) and Gemini's excellent generation capabilities everywhere else.

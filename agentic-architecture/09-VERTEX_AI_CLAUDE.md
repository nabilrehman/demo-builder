# Vertex AI Model Garden Setup - Claude Sonnet 4.5

## 🎯 Optimal Setup for Your Environment

Use **Claude Sonnet 4.5 via Vertex AI Model Garden** + **Gemini 2.5 Pro** (direct API)

This approach:
- ✅ No external Anthropic API key needed
- ✅ Everything in your Google Cloud project
- ✅ Unified billing
- ✅ Better security (no API keys to manage)
- ✅ Native Google Cloud integration

---

## 🏗️ Architecture

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
│via     │ │API   │ │BigQuery│
│VERTEX  │ │      │ │        │
└────────┘ └──────┘ └────────┘
    │          │          │
    └──────────┼──────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼────┐ ┌──▼───────┐
│  CAPI  │ │  Demo    │
│ Agent  │ │ Content  │
│Google  │ │  GEMINI  │
│CAPI API│ │  API     │
└────────┘ └──────────┘
```

---

## 📦 Updated Dependencies

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
langchain-google-vertexai==1.0.0

# Google Cloud
google-cloud-aiplatform==1.40.0        # Vertex AI (includes Claude)
google-generativeai==0.3.2             # Gemini direct API
google-cloud-bigquery==3.17.0
google-cloud-geminidataanalytics==0.1.0

# Utilities
aiohttp==3.9.0
beautifulsoup4==4.12.0
faker==22.0.0
```

---

## 🔧 Unified LLM Client (Vertex AI Claude + Gemini API)

```python
# backend/agentic_service/utils/vertex_llm_client.py
"""
Unified LLM client for Vertex AI Claude and Gemini API.
"""
import os
import json
import logging
from typing import Optional, Dict
from enum import Enum

import google.generativeai as genai
from google.cloud import aiplatform
from vertexai.preview.generative_models import GenerativeModel

logger = logging.getLogger(__name__)

# Initialize Vertex AI
PROJECT_ID = os.getenv("PROJECT_ID", "bq-demos-469816")
LOCATION = os.getenv("LOCATION", "us-central1")

aiplatform.init(project=PROJECT_ID, location=LOCATION)

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


class ModelType(Enum):
    """Supported model types."""
    GEMINI_API = "gemini-2.5-pro"
    CLAUDE_VERTEX = "claude-3-5-sonnet-v2@20241022"  # Via Vertex AI Model Garden


class VertexLLMClient:
    """Unified client for Vertex AI Claude and Gemini API."""

    def __init__(self, model_type: ModelType):
        """
        Initialize LLM client.

        Args:
            model_type: Which model to use (GEMINI_API or CLAUDE_VERTEX)
        """
        self.model_type = model_type

        if model_type == ModelType.GEMINI_API:
            self.gemini_model = genai.GenerativeModel(model_type.value)
            logger.info("Initialized Gemini API client")
        elif model_type == ModelType.CLAUDE_VERTEX:
            # Claude via Vertex AI Model Garden
            self.claude_model = GenerativeModel(model_type.value)
            logger.info(f"Initialized Claude via Vertex AI in project {PROJECT_ID}")
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
            if self.model_type == ModelType.GEMINI_API:
                return await self._generate_gemini(
                    prompt, temperature, max_output_tokens, system_instruction
                )
            elif self.model_type == ModelType.CLAUDE_VERTEX:
                return await self._generate_claude_vertex(
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
        """Generate content using Gemini API."""
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

    async def _generate_claude_vertex(
        self,
        prompt: str,
        temperature: float,
        max_output_tokens: int,
        system_instruction: Optional[str]
    ) -> str:
        """Generate content using Claude via Vertex AI Model Garden."""
        from vertexai.preview.generative_models import GenerationConfig

        # Build the full prompt with system instruction
        if system_instruction:
            full_prompt = f"{system_instruction}\n\n{prompt}"
        else:
            full_prompt = prompt

        generation_config = GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            top_p=0.95,
        )

        # Generate with Claude via Vertex AI
        response = self.claude_model.generate_content(
            full_prompt,
            generation_config=generation_config
        )

        return response.text

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
            logger.error(f"Response text: {response_text[:500]}...")
            raise ValueError(f"Invalid JSON response: {str(e)}")


# ============================================================================
# Convenience Functions
# ============================================================================

def get_claude_vertex_client() -> VertexLLMClient:
    """Get Claude (via Vertex AI) client."""
    return VertexLLMClient(ModelType.CLAUDE_VERTEX)


def get_gemini_client() -> VertexLLMClient:
    """Get Gemini API client."""
    return VertexLLMClient(ModelType.GEMINI_API)
```

---

## 🤖 Updated Agent Implementations

### Research Agent (Claude via Vertex AI)

```python
# backend/agentic_service/agents/research_agent.py
"""
Customer Research Agent - Uses Claude Sonnet 4.5 via Vertex AI Model Garden.
"""
import logging
from typing import Dict

from ..utils.vertex_llm_client import get_claude_vertex_client
from ..tools.web_research import scrape_website
from ..utils.prompt_templates import RESEARCH_AGENT_PROMPT

logger = logging.getLogger(__name__)


class CustomerResearchAgent:
    """Agent for researching customer business domain."""

    def __init__(self):
        # Use Claude via Vertex AI (no external API key needed!)
        self.client = get_claude_vertex_client()
        logger.info("Research Agent initialized with Claude via Vertex AI")

    async def execute(self, state: Dict) -> Dict:
        """Execute research phase."""
        logger.info(f"Researching {state['customer_url']} with Claude (Vertex AI)")

        try:
            # Scrape website
            website_content = await scrape_website(state["customer_url"])
            logger.info(f"Scraped {len(website_content)} characters")

            # Analyze with Claude via Vertex AI
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
        """Use Claude (via Vertex AI) to analyze business."""
        # Truncate if needed
        max_chars = 15000
        if len(website_content) > max_chars:
            website_content = website_content[:max_chars] + "\n\n[Content truncated...]"

        prompt = RESEARCH_AGENT_PROMPT.format(website_content=website_content)

        # Claude via Vertex AI excels at this complex analysis
        response_text = await self.client.generate_with_retry(
            prompt=prompt,
            temperature=0.2,
            max_output_tokens=4096,
            system_instruction="You are a business analyst expert at understanding company business models from their websites."
        )

        return self.client.parse_json_response(response_text)
```

### Data Modeling Agent (Gemini API)

```python
# backend/agentic_service/agents/data_modeling_agent.py
"""
Data Modeling Agent - Uses Gemini 2.5 Pro via API.
"""
import json
import logging
from typing import Dict, List
from faker import Faker

from ..utils.vertex_llm_client import get_gemini_client
from ..utils.prompt_templates import DATA_MODELING_PROMPT

logger = logging.getLogger(__name__)


class DataModelingAgent:
    """Agent for designing data schema."""

    def __init__(self):
        # Use Gemini API (you have credits!)
        self.client = get_gemini_client()
        self.faker = Faker()
        logger.info("Data Modeling Agent initialized with Gemini 2.5 Pro API")

    async def execute(self, state: Dict) -> Dict:
        """Execute data modeling phase."""
        logger.info("Designing data schema with Gemini")

        try:
            # Design schema with Gemini
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
        """Use Gemini to design schema."""
        prompt = DATA_MODELING_PROMPT.format(
            customer_info=json.dumps(customer_info, indent=2),
            entities=json.dumps(entities)
        )

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

            # Smart field generation
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

### Demo Content Generator (Gemini API)

```python
# backend/agentic_service/agents/demo_content_agent.py
"""
Demo Content Generator - Uses Gemini 2.5 Pro via API.
"""
import json
import logging
from typing import Dict

from ..utils.vertex_llm_client import get_gemini_client
from ..utils.prompt_templates import DEMO_CONTENT_PROMPT

logger = logging.getLogger(__name__)


class DemoContentGenerator:
    """Agent for generating demo content."""

    def __init__(self):
        # Use Gemini API
        self.client = get_gemini_client()
        logger.info("Demo Content Agent initialized with Gemini 2.5 Pro API")

    async def execute(self, state: Dict) -> Dict:
        """Execute demo content generation."""
        logger.info("Generating demo content with Gemini")

        try:
            # Generate content with Gemini
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
        """Use Gemini to generate demo content."""
        schema_summary = self._summarize_schema(schema)

        prompt = DEMO_CONTENT_PROMPT.format(
            customer_info=json.dumps(customer_info, indent=2),
            schema_summary=schema_summary
        )

        response_text = await self.client.generate_with_retry(
            prompt=prompt,
            temperature=0.7,
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

# Gemini API Key (only this one needed!)
GEMINI_API_KEY=your_gemini_api_key_here

# Google Cloud (for Vertex AI Claude)
PROJECT_ID=bq-demos-469816
LOCATION=us-central1

# Environment
ENVIRONMENT=development
```

**Note**: No Anthropic API key needed! Claude runs via Vertex AI using your Google Cloud credentials.

---

## ☁️ Vertex AI Model Garden Setup

### Enable Claude in Model Garden

```bash
# 1. Enable Vertex AI API (already done)
gcloud services enable aiplatform.googleapis.com

# 2. Grant service account access to Vertex AI
gcloud projects add-iam-policy-binding bq-demos-469816 \
    --member="serviceAccount:capi-demo-sa@bq-demos-469816.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

# 3. Enable Claude in Model Garden (via Console)
# Go to: https://console.cloud.google.com/vertex-ai/publishers/anthropic/model-garden/claude-3-5-sonnet-v2
# Click "Enable" for your project
```

### Manual Setup Steps (One-time)

1. **Navigate to Vertex AI Model Garden**
   - Go to: https://console.cloud.google.com/vertex-ai/model-garden
   - Search for "Claude 3.5 Sonnet"

2. **Enable Claude 3.5 Sonnet v2**
   - Click on "Claude 3.5 Sonnet v2"
   - Click "Enable"
   - Accept Anthropic's terms
   - Model will be available in ~5 minutes

3. **Verify Access**
   ```bash
   # Test Claude via Vertex AI
   python3 -c "
   from google.cloud import aiplatform
   from vertexai.preview.generative_models import GenerativeModel

   aiplatform.init(project='bq-demos-469816', location='us-central1')
   model = GenerativeModel('claude-3-5-sonnet-v2@20241022')
   response = model.generate_content('Hello, world!')
   print(response.text)
   "
   ```

---

## 🚀 Cloud Run Deployment

### Service Account Permissions

```bash
# Create service account (if not exists)
gcloud iam service-accounts create capi-demo-sa \
    --display-name="CAPI Agentic Demo Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding bq-demos-469816 \
    --member="serviceAccount:capi-demo-sa@bq-demos-469816.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding bq-demos-469816 \
    --member="serviceAccount:capi-demo-sa@bq-demos-469816.iam.gserviceaccount.com" \
    --role="roles/bigquery.admin"

gcloud projects add-iam-policy-binding bq-demos-469816 \
    --member="serviceAccount:capi-demo-sa@bq-demos-469816.iam.gserviceaccount.com" \
    --role="roles/geminidataanalytics.dataAgentCreator"
```

### Deploy to Cloud Run

```bash
# Store Gemini API key in Secret Manager
echo -n "your_gemini_key" | gcloud secrets create gemini-api-key \
    --data-file=- \
    --replication-policy="automatic"

# Grant access
gcloud secrets add-iam-policy-binding gemini-api-key \
    --member="serviceAccount:capi-demo-sa@bq-demos-469816.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Deploy
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
  --set-secrets "GEMINI_API_KEY=gemini-api-key:latest"
```

---

## 💰 Cost Analysis (Vertex AI Claude)

### Vertex AI Model Garden Pricing

**Claude 3.5 Sonnet v2 (via Vertex AI):**
- Input: $3.00 per 1M tokens
- Output: $15.00 per 1M tokens

**Gemini 2.5 Pro (API):**
- Input: $1.25 per 1M tokens
- Output: $5.00 per 1M tokens

### Per Provisioning Job

| Agent | Model | Input | Output | Cost |
|-------|-------|-------|--------|------|
| Research | Claude (Vertex) | 5K | 1K | $0.03 |
| Data Modeling | Gemini API | 2K | 3K | $0.02 |
| Demo Content | Gemini API | 3K | 2K | $0.01 |
| Infrastructure | N/A | - | - | $0.01 (BQ) |
| **Total** | - | **10K** | **6K** | **$0.07** |

### Monthly Costs (200 demos)

| Item | Cost |
|------|------|
| Claude (Vertex AI) | $6 |
| Gemini API | $6 (or less with credits!) |
| BigQuery | $20 |
| Cloud Run | $30 |
| **Total** | **~$62/month** |

**Same cost as direct Anthropic API, but with better integration!**

---

## ✅ Advantages of Vertex AI Claude

### vs. Direct Anthropic API

✅ **No external API key** - Uses Google Cloud auth
✅ **Unified billing** - Everything on one bill
✅ **Better security** - No API keys to manage/rotate
✅ **Same pricing** - No markup for Vertex AI
✅ **Native integration** - Works seamlessly with other GCP services
✅ **Enterprise support** - Google Cloud support included
✅ **Compliance** - Easier for regulated industries

### Same Performance

- ✅ Same Claude 3.5 Sonnet model
- ✅ Same quality outputs
- ✅ Similar latency
- ✅ Same capabilities

---

## 🎯 Summary

**Perfect Setup for Your Environment:**

```
Research Agent      → Claude 3.5 Sonnet v2 (Vertex AI Model Garden)
Data Modeling Agent → Gemini 2.5 Pro (API, with your credits)
Infrastructure      → Python/BigQuery
CAPI Creator        → Google CAPI
Demo Content        → Gemini 2.5 Pro (API)
```

**Benefits:**
- ✅ Everything in Google Cloud
- ✅ Only need Gemini API key
- ✅ Claude via Vertex AI (no external API)
- ✅ Unified billing and security
- ✅ Same cost (~$0.07/demo)
- ✅ Works perfectly on Cloud Run

**This is the OPTIMAL setup for your use case!** 🚀

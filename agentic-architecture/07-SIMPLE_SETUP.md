# Simple Setup - Gemini API Key Approach

## 🎯 Simplified Architecture

You're right - let's keep it simple! Use **Gemini 2.5 Pro** with your API key directly.

---

## 🏗️ Simplified Stack

```
LangGraph Orchestrator
    ↓
All Agents Use Gemini 2.5 Pro
    ↓
(No Vertex AI complexity)
```

### Benefits of This Approach

✅ **Simple**: Just one API key
✅ **Fast**: Direct API calls
✅ **Cost-effective**: You have Gemini credits
✅ **Easy to deploy**: No Vertex AI setup
✅ **Works on Cloud Run**: No special configuration needed

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

# Google Gemini (Simple API)
google-generativeai==0.3.2

# Google Cloud (for BigQuery and CAPI)
google-cloud-bigquery==3.17.0
google-cloud-geminidataanalytics==0.1.0

# Utilities
aiohttp==3.9.0
beautifulsoup4==4.12.0
faker==22.0.0
```

---

## 🔧 Simple Gemini Client

```python
# backend/agentic_service/utils/gemini_client.py
"""
Simple Gemini client using API key.
"""
import os
import json
import logging
from typing import Optional, List, Dict
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Configure Gemini with your API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


class GeminiClient:
    """Simple client for Gemini 2.5 Pro."""

    def __init__(self, model_name: str = "gemini-2.5-pro"):
        """
        Initialize Gemini client.

        Args:
            model_name: Model to use (default: gemini-2.5-pro)
        """
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)

    async def generate_content(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_output_tokens: int = 8192,
        system_instruction: Optional[str] = None
    ) -> str:
        """
        Generate content using Gemini.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0.0-1.0)
            max_output_tokens: Maximum tokens to generate
            system_instruction: Optional system instruction

        Returns:
            Generated text
        """
        try:
            # Create model with system instruction if provided
            if system_instruction:
                model = genai.GenerativeModel(
                    self.model_name,
                    system_instruction=system_instruction
                )
            else:
                model = self.model

            # Configure generation
            generation_config = genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                top_p=0.95,
            )

            # Generate content
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )

            return response.text

        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise

    async def generate_with_retry(
        self,
        prompt: str,
        max_retries: int = 3,
        **kwargs
    ) -> str:
        """
        Generate content with automatic retry on failure.

        Args:
            prompt: Input prompt
            max_retries: Maximum retry attempts
            **kwargs: Additional arguments for generate_content

        Returns:
            Generated text
        """
        import asyncio

        for attempt in range(max_retries):
            try:
                return await self.generate_content(prompt, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"Attempt {attempt + 1} failed, retrying: {e}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

    def parse_json_response(self, response_text: str) -> Dict:
        """
        Parse JSON from Gemini response (handles markdown code blocks).

        Args:
            response_text: Raw response from Gemini

        Returns:
            Parsed JSON dictionary
        """
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


# Singleton instance
_gemini_client = None

def get_gemini_client() -> GeminiClient:
    """Get or create Gemini client singleton."""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client
```

---

## 🤖 Updated Agent Implementations

### Research Agent (Gemini)

```python
# backend/agentic_service/agents/research_agent.py
"""
Customer Research Agent - Uses Gemini 2.5 Pro.
"""
import logging
from typing import Dict

from ..utils.gemini_client import get_gemini_client
from ..tools.web_research import scrape_website
from ..utils.prompt_templates import RESEARCH_AGENT_PROMPT

logger = logging.getLogger(__name__)


class CustomerResearchAgent:
    """Agent for researching customer business domain."""

    def __init__(self):
        self.client = get_gemini_client()

    async def execute(self, state: Dict) -> Dict:
        """Execute research phase."""
        logger.info(f"Researching {state['customer_url']}")

        try:
            # Scrape website
            website_content = await scrape_website(state["customer_url"])
            logger.info(f"Scraped {len(website_content)} characters")

            # Analyze with Gemini
            analysis = await self._analyze_business(website_content)

            # Update state
            state["customer_info"] = analysis
            state["business_domain"] = analysis.get("business_domain")
            state["industry"] = analysis.get("industry")
            state["key_entities"] = [e["name"] for e in analysis.get("key_entities", [])]

            logger.info(f"Research complete. Domain: {state['business_domain']}")
            return state

        except Exception as e:
            logger.error(f"Research failed: {e}", exc_info=True)
            raise

    async def _analyze_business(self, website_content: str) -> Dict:
        """Use Gemini to analyze business."""
        # Truncate if too long
        max_chars = 15000
        if len(website_content) > max_chars:
            website_content = website_content[:max_chars] + "\n\n[Content truncated...]"

        # Generate with Gemini
        prompt = RESEARCH_AGENT_PROMPT.format(website_content=website_content)

        response_text = await self.client.generate_with_retry(
            prompt=prompt,
            temperature=0.2,  # Lower for more consistent analysis
            max_output_tokens=4096
        )

        # Parse JSON
        return self.client.parse_json_response(response_text)
```

### Data Modeling Agent (Gemini)

```python
# backend/agentic_service/agents/data_modeling_agent.py
"""
Data Modeling Agent - Uses Gemini 2.5 Pro.
"""
import json
import logging
from typing import Dict, List
from faker import Faker

from ..utils.gemini_client import get_gemini_client
from ..utils.prompt_templates import DATA_MODELING_PROMPT

logger = logging.getLogger(__name__)


class DataModelingAgent:
    """Agent for designing data schema and generating synthetic data."""

    def __init__(self):
        self.client = get_gemini_client()
        self.faker = Faker()

    async def execute(self, state: Dict) -> Dict:
        """Execute data modeling phase."""
        logger.info("Designing data schema")

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

            logger.info(f"Created {len(schema_design['tables'])} table schemas")
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
            max_output_tokens=8192
        )

        return self.client.parse_json_response(response_text)

    async def _generate_data(self, schema: Dict) -> Dict[str, List[Dict]]:
        """Generate synthetic data for each table."""
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
        """Generate a single synthetic record using Faker."""
        record = {}

        for field in schema:
            field_name = field["name"]
            field_type = field["type"]

            # Generate based on field type and name
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

### Demo Content Generator (Gemini)

```python
# backend/agentic_service/agents/demo_content_agent.py
"""
Demo Content Generator - Uses Gemini 2.5 Pro.
"""
import json
import logging
from typing import Dict

from ..utils.gemini_client import get_gemini_client
from ..utils.prompt_templates import DEMO_CONTENT_PROMPT

logger = logging.getLogger(__name__)


class DemoContentGenerator:
    """Agent for generating demo content."""

    def __init__(self):
        self.client = get_gemini_client()

    async def execute(self, state: Dict) -> Dict:
        """Execute demo content generation."""
        logger.info("Generating demo content")

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

            logger.info(f"Generated {len(demo_content['golden_queries'])} golden queries")
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
            temperature=0.7,  # Higher for creative content
            max_output_tokens=8192
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

# Gemini API Key (get from https://makersuite.google.com/app/apikey)
GEMINI_API_KEY=your_gemini_api_key_here

# Google Cloud
PROJECT_ID=bq-demos-469816
LOCATION=us-central1

# Environment
ENVIRONMENT=development
```

### Cloud Run Environment Variables

```bash
# Set secret in Google Secret Manager
echo -n "your_gemini_api_key" | gcloud secrets create gemini-api-key \
    --data-file=- \
    --replication-policy="automatic"

# Grant service account access to secret
gcloud secrets add-iam-policy-binding gemini-api-key \
    --member="serviceAccount:capi-demo-sa@bq-demos-469816.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### Updated Cloud Run Deployment

```bash
# Deploy with secret
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

## 📝 Updated Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY newfrontend/conversational-api-demo-frontend/dist/ ./backend/newfrontend/conversational-api-demo-frontend/dist/

# Environment
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Expose port
EXPOSE 8080

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health', timeout=5)"

# Run
CMD exec uvicorn backend.api:app --host 0.0.0.0 --port ${PORT}
```

---

## 💰 Cost with Gemini 2.5 Pro

### Pricing (as of 2025)
- Input: $1.25 per 1M tokens
- Output: $5.00 per 1M tokens

### Per Provisioning Job

| Agent | Input Tokens | Output Tokens | Cost |
|-------|--------------|---------------|------|
| Research | 5,000 | 1,000 | $0.01 |
| Data Modeling | 2,000 | 3,000 | $0.02 |
| Demo Content | 3,000 | 2,000 | $0.01 |
| **Total** | **10,000** | **6,000** | **~$0.04** |

**Plus Infrastructure**: $0.01 (BigQuery)

### **Total per demo: ~$0.05** 🎉

**With your Gemini credits**: Even cheaper or FREE!

---

## ✅ Simple Deployment Checklist

- [ ] Get Gemini API key from https://makersuite.google.com/app/apikey
- [ ] Add key to Secret Manager
- [ ] Update requirements.txt (no Vertex AI dependencies)
- [ ] Copy Gemini client code
- [ ] Update all agents to use Gemini client
- [ ] Test locally with `.env` file
- [ ] Build Docker image
- [ ] Deploy to Cloud Run
- [ ] Test provisioning flow

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r backend/requirements.txt

# 2. Set up environment
cat > backend/.env << EOF
GEMINI_API_KEY=your_key_here
PROJECT_ID=bq-demos-469816
LOCATION=us-central1
EOF

# 3. Run locally
cd backend
uvicorn api:app --reload --port 8000

# 4. Test
curl -X POST http://localhost:8000/api/provision/start \
  -H "Content-Type: application/json" \
  -d '{"customer_url": "https://example-company.com"}'
```

---

## 🎯 Summary

**Simplest approach**:
- ✅ Just Gemini 2.5 Pro with API key
- ✅ No Vertex AI complexity
- ✅ No Claude needed (Gemini 2.5 Pro is excellent!)
- ✅ Works perfectly on Cloud Run
- ✅ Only $0.05 per demo
- ✅ Your credits make it FREE

**This is the recommended approach** - simple, effective, and uses your existing Gemini credits! 🚀

# Agent Specifications

This document provides detailed specifications for each agent in the agentic provisioning system.

---

## Agent 1: Customer Research Agent

### Purpose
Analyze customer's website and business to understand their domain, industry, and data requirements.

### Inputs
- `customer_url`: URL of customer's website
- `project_id`: Google Cloud project ID

### Outputs
- `customer_info`: Comprehensive business analysis
- `business_domain`: Identified business domain
- `industry`: Industry classification
- `key_entities`: List of key business entities

### Tools Required

```python
tools = [
    {
        "name": "fetch_webpage",
        "description": "Fetches and extracts content from a webpage",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to fetch"},
                "extract_links": {"type": "boolean", "description": "Whether to extract all links"}
            },
            "required": ["url"]
        }
    },
    {
        "name": "search_company_info",
        "description": "Searches for additional company information online",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string"},
                "search_terms": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["company_name"]
        }
    },
    {
        "name": "classify_business_domain",
        "description": "Classifies business into predefined domains",
        "input_schema": {
            "type": "object",
            "properties": {
                "description": {"type": "string"},
                "products": {"type": "array", "items": {"type": "string"}},
                "services": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["description"]
        }
    }
]
```

### Prompt Template

```python
RESEARCH_AGENT_PROMPT = """You are a business analyst researching a company for a data analytics demo.

TASK: Analyze the provided website content and determine:
1. The company's primary business domain (e.g., e-commerce, SaaS, healthcare, manufacturing)
2. The industry they operate in
3. Key business entities they likely track (e.g., customers, orders, products, appointments)
4. Their main products or services
5. Potential data relationships between entities

WEBSITE CONTENT:
{website_content}

INSTRUCTIONS:
- Be thorough but concise
- Focus on data-relevant aspects
- Identify 5-10 key entities
- Suggest entity relationships
- Return structured JSON

OUTPUT FORMAT:
{{
    "company_name": "...",
    "business_domain": "...",
    "industry": "...",
    "description": "...",
    "products_services": [...],
    "key_entities": [
        {{
            "name": "entity_name",
            "description": "what it represents",
            "relationships": ["related_entity_1", "related_entity_2"]
        }}
    ],
    "data_characteristics": {{
        "estimated_volume": "low|medium|high",
        "update_frequency": "real-time|daily|weekly",
        "complexity": "simple|moderate|complex"
    }}
}}
"""
```

### Implementation Details

```python
class CustomerResearchAgent:
    """Agent for researching customer business domain."""

    def __init__(self, anthropic_client: Anthropic):
        self.client = anthropic_client
        self.model = "claude-3-5-sonnet-20241022"

    async def execute(self, state: ProvisioningState) -> ProvisioningState:
        """Execute research phase."""
        # Scrape website
        content = await self.scrape_website(state["customer_url"])

        # Analyze with Claude
        analysis = await self.analyze_business(content)

        # Update state
        state["customer_info"] = analysis
        state["business_domain"] = analysis["business_domain"]
        state["industry"] = analysis["industry"]
        state["key_entities"] = [e["name"] for e in analysis["key_entities"]]

        return state

    async def scrape_website(self, url: str) -> str:
        """Scrape website content."""
        # Use BeautifulSoup, Playwright, or Firecrawl
        # Extract main content, remove scripts/styles
        # Return clean text
        pass

    async def analyze_business(self, content: str) -> Dict:
        """Use Claude to analyze business."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            temperature=0.2,
            messages=[{
                "role": "user",
                "content": RESEARCH_AGENT_PROMPT.format(
                    website_content=content[:15000]
                )
            }]
        )

        # Parse JSON response
        return json.loads(response.content[0].text)
```

### Success Criteria
- ✅ Correctly identifies business domain (90% accuracy target)
- ✅ Extracts 5+ relevant entities
- ✅ Provides entity relationships
- ✅ Completes within 30 seconds

---

## Agent 2: Data Modeling Agent

### Purpose
Design database schema and generate synthetic data based on identified business domain.

### Inputs
- `customer_info`: From Research Agent
- `business_domain`: Identified domain
- `key_entities`: List of entities

### Outputs
- `schema_design`: Complete database schema
- `table_definitions`: BigQuery table schemas
- `sample_data`: Generated synthetic data

### Tools Required

```python
tools = [
    {
        "name": "generate_table_schema",
        "description": "Generates BigQuery table schema for an entity",
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_name": {"type": "string"},
                "attributes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"type": "string"},
                            "description": {"type": "string"}
                        }
                    }
                },
                "relationships": {"type": "array"}
            },
            "required": ["entity_name", "attributes"]
        }
    },
    {
        "name": "generate_synthetic_records",
        "description": "Generates realistic synthetic data records",
        "input_schema": {
            "type": "object",
            "properties": {
                "table_name": {"type": "string"},
                "schema": {"type": "object"},
                "count": {"type": "integer"},
                "business_context": {"type": "string"}
            },
            "required": ["table_name", "schema", "count"]
        }
    },
    {
        "name": "validate_schema",
        "description": "Validates schema for BigQuery compatibility",
        "input_schema": {
            "type": "object",
            "properties": {
                "schema": {"type": "object"}
            },
            "required": ["schema"]
        }
    }
]
```

### Prompt Template

```python
DATA_MODELING_PROMPT = """You are a data architect designing a database schema for a demo.

COMPANY INFORMATION:
{customer_info}

TASK: Design a comprehensive BigQuery database schema that includes:
1. Tables for each key entity
2. Appropriate fields with correct data types
3. Relationships between tables (foreign keys)
4. Realistic field names and structures

REQUIREMENTS:
- Use BigQuery-compatible data types (STRING, INT64, FLOAT64, BOOL, DATE, TIMESTAMP, etc.)
- Include timestamps (created_at, updated_at) where appropriate
- Add status/state fields for lifecycle tracking
- Consider transactional vs. dimensional data
- Design for typical analytical queries

ENTITIES TO MODEL:
{entities}

OUTPUT FORMAT:
{{
    "tables": [
        {{
            "name": "table_name",
            "description": "...",
            "schema": [
                {{
                    "name": "field_name",
                    "type": "BIGQUERY_TYPE",
                    "mode": "REQUIRED|NULLABLE|REPEATED",
                    "description": "..."
                }}
            ],
            "relationships": [
                {{
                    "type": "foreign_key",
                    "references": "other_table.field"
                }}
            ],
            "record_count": 100
        }}
    ],
    "sample_data_specs": {{
        "table_name": {{
            "generation_strategy": "...",
            "constraints": [...],
            "distributions": {{...}}
        }}
    }}
}}
"""
```

### Implementation Details

```python
class DataModelingAgent:
    """Agent for designing data schema and generating synthetic data."""

    def __init__(self, anthropic_client: Anthropic):
        self.client = anthropic_client
        self.model = "claude-3-5-sonnet-20241022"

    async def execute(self, state: ProvisioningState) -> ProvisioningState:
        """Execute data modeling phase."""

        # Design schema
        schema_design = await self.design_schema(
            state["customer_info"],
            state["key_entities"]
        )

        # Generate synthetic data
        sample_data = await self.generate_data(schema_design)

        # Update state
        state["schema_design"] = schema_design
        state["table_definitions"] = schema_design["tables"]
        state["sample_data"] = sample_data

        return state

    async def design_schema(self, customer_info: Dict, entities: List[str]) -> Dict:
        """Use Claude to design schema."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=8192,
            temperature=0.3,
            messages=[{
                "role": "user",
                "content": DATA_MODELING_PROMPT.format(
                    customer_info=json.dumps(customer_info, indent=2),
                    entities=json.dumps(entities)
                )
            }]
        )

        return json.loads(response.content[0].text)

    async def generate_data(self, schema: Dict) -> Dict[str, List[Dict]]:
        """Generate synthetic data for each table."""
        from faker import Faker
        fake = Faker()

        all_data = {}

        for table in schema["tables"]:
            records = []
            count = table.get("record_count", 100)

            for i in range(count):
                record = await self.generate_record(
                    table["schema"],
                    table.get("sample_data_specs", {}),
                    i,
                    fake
                )
                records.append(record)

            all_data[table["name"]] = records

        return all_data

    async def generate_record(
        self, schema: List[Dict], specs: Dict, index: int, faker: Faker
    ) -> Dict:
        """Generate a single synthetic record."""
        record = {}

        for field in schema:
            field_name = field["name"]
            field_type = field["type"]

            # Generate realistic data based on type and name
            if field_name in ["id", f"{field_name}_id"]:
                record[field_name] = index + 1
            elif field_type == "STRING":
                record[field_name] = self.generate_string_field(field_name, faker)
            elif field_type == "INT64":
                record[field_name] = self.generate_int_field(field_name, faker)
            elif field_type == "FLOAT64":
                record[field_name] = self.generate_float_field(field_name, faker)
            elif field_type == "TIMESTAMP":
                record[field_name] = faker.date_time_this_year().isoformat()
            elif field_type == "DATE":
                record[field_name] = faker.date_this_year().isoformat()
            elif field_type == "BOOL":
                record[field_name] = faker.boolean()

        return record
```

### Success Criteria
- ✅ Generates valid BigQuery schemas
- ✅ Creates realistic synthetic data
- ✅ Maintains referential integrity
- ✅ Produces 100-1000 records per table
- ✅ Completes within 60 seconds

---

## Agent 3: Infrastructure Provisioning Agent

### Purpose
Create BigQuery datasets, tables, and load data.

### Inputs
- `schema_design`: Database schema
- `sample_data`: Synthetic data
- `project_id`: Google Cloud project ID

### Outputs
- `dataset_id`: Created BigQuery dataset ID
- `tables_created`: List of created tables
- `data_loaded`: Boolean success flag

### Tools Required

```python
tools = [
    {
        "name": "create_bigquery_dataset",
        "description": "Creates a new BigQuery dataset",
        "input_schema": {
            "type": "object",
            "properties": {
                "project_id": {"type": "string"},
                "dataset_id": {"type": "string"},
                "location": {"type": "string", "default": "US"}
            },
            "required": ["project_id", "dataset_id"]
        }
    },
    {
        "name": "create_bigquery_table",
        "description": "Creates a table in BigQuery",
        "input_schema": {
            "type": "object",
            "properties": {
                "dataset_id": {"type": "string"},
                "table_id": {"type": "string"},
                "schema": {"type": "array"}
            },
            "required": ["dataset_id", "table_id", "schema"]
        }
    },
    {
        "name": "load_data_to_table",
        "description": "Loads data into a BigQuery table",
        "input_schema": {
            "type": "object",
            "properties": {
                "table_id": {"type": "string"},
                "data": {"type": "array"},
                "write_disposition": {"type": "string"}
            },
            "required": ["table_id", "data"]
        }
    }
]
```

### Implementation Details

```python
class InfrastructureAgent:
    """Agent for provisioning BigQuery infrastructure."""

    def __init__(self, project_id: str):
        from google.cloud import bigquery
        self.client = bigquery.Client(project=project_id)
        self.project_id = project_id

    async def execute(self, state: ProvisioningState) -> ProvisioningState:
        """Execute infrastructure provisioning."""

        # Generate unique dataset ID
        dataset_id = f"demo_{state['job_id'][:8]}"

        # Create dataset
        await self.create_dataset(dataset_id)

        # Create tables
        tables_created = []
        for table_def in state["table_definitions"]:
            table_id = await self.create_table(dataset_id, table_def)
            tables_created.append(table_id)

        # Load data
        for table_name, records in state["sample_data"].items():
            await self.load_data(dataset_id, table_name, records)

        # Update state
        state["dataset_id"] = dataset_id
        state["tables_created"] = tables_created
        state["data_loaded"] = True

        return state

    async def create_dataset(self, dataset_id: str):
        """Create BigQuery dataset."""
        from google.cloud import bigquery

        dataset_ref = f"{self.project_id}.{dataset_id}"
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"

        self.client.create_dataset(dataset, exists_ok=True)
        logging.info(f"Created dataset: {dataset_id}")

    async def create_table(self, dataset_id: str, table_def: Dict) -> str:
        """Create BigQuery table."""
        from google.cloud import bigquery

        table_id = f"{self.project_id}.{dataset_id}.{table_def['name']}"

        # Convert schema to BigQuery format
        schema = [
            bigquery.SchemaField(
                field["name"],
                field["type"],
                mode=field.get("mode", "NULLABLE"),
                description=field.get("description")
            )
            for field in table_def["schema"]
        ]

        table = bigquery.Table(table_id, schema=schema)
        self.client.create_table(table, exists_ok=True)
        logging.info(f"Created table: {table_id}")

        return table_id

    async def load_data(self, dataset_id: str, table_name: str, records: List[Dict]):
        """Load data into table."""
        from google.cloud import bigquery

        table_id = f"{self.project_id}.{dataset_id}.{table_name}"

        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_TRUNCATE",
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
        )

        load_job = self.client.load_table_from_json(
            records,
            table_id,
            job_config=job_config
        )

        load_job.result()  # Wait for completion
        logging.info(f"Loaded {len(records)} records to {table_id}")
```

### Success Criteria
- ✅ Successfully creates dataset
- ✅ Creates all tables without errors
- ✅ Loads data with 100% success rate
- ✅ Validates data integrity
- ✅ Completes within 90 seconds

---

## Agent 4: Conversational Analytics API Agent Creator

### Purpose
Create and configure a Conversational Analytics API data agent.

### Inputs
- `dataset_id`: BigQuery dataset ID
- `tables_created`: List of tables
- `customer_info`: Business context
- `project_id`: Google Cloud project

### Outputs
- `data_agent_id`: Created agent ID
- `agent_config`: Agent configuration
- `agent_tested`: Test success flag

### Implementation Details

```python
class CAPIAgentCreator:
    """Agent for creating Conversational Analytics API agent."""

    def __init__(self, project_id: str):
        from google.cloud import geminidataanalytics
        self.client = geminidataanalytics.DataAgentServiceClient()
        self.project_id = project_id

    async def execute(self, state: ProvisioningState) -> ProvisioningState:
        """Execute CAPI agent creation."""

        # Generate agent ID
        agent_id = f"agent_{state['job_id'][:8]}"

        # Create system instruction
        system_instruction = self.generate_system_instruction(
            state["customer_info"]
        )

        # Create agent
        await self.create_agent(
            agent_id,
            system_instruction,
            state["dataset_id"],
            state["tables_created"]
        )

        # Test agent
        test_success = await self.test_agent(agent_id)

        # Update state
        state["data_agent_id"] = agent_id
        state["agent_config"] = {
            "system_instruction": system_instruction,
            "dataset": state["dataset_id"],
            "tables": state["tables_created"]
        }
        state["agent_tested"] = test_success

        return state

    def generate_system_instruction(self, customer_info: Dict) -> str:
        """Generate contextual system instruction."""
        return f"""You are a helpful data assistant for {customer_info['company_name']},
a company in the {customer_info['industry']} industry.

Your role is to help users analyze data about {', '.join(customer_info['key_entities'])}.

When answering questions:
- Be concise and business-focused
- Provide relevant metrics and insights
- Suggest follow-up questions
- Use appropriate visualizations

Available data includes: {', '.join(customer_info['key_entities'])}."""

    async def create_agent(
        self,
        agent_id: str,
        system_instruction: str,
        dataset_id: str,
        tables: List[str]
    ):
        """Create data agent via API."""
        # Implementation similar to existing create_data_agent() function
        pass

    async def test_agent(self, agent_id: str) -> bool:
        """Test agent with a simple query."""
        # Send test query and verify response
        pass
```

### Success Criteria
- ✅ Successfully creates data agent
- ✅ Configures correct datasources
- ✅ Passes basic functionality test
- ✅ Completes within 45 seconds

---

## Agent 5: Demo Content Generator

### Purpose
Generate golden queries, demo scripts, and sample Q&A for CE demos.

### Inputs
- `customer_info`: Business context
- `schema_design`: Database schema
- `data_agent_id`: Created agent ID

### Outputs
- `golden_queries`: List of demo queries
- `demo_script`: Narrative demo script
- `sample_qa`: Sample Q&A pairs

### Prompt Template

```python
DEMO_CONTENT_PROMPT = """You are a sales enablement specialist creating demo content.

COMPANY INFORMATION:
{customer_info}

DATABASE SCHEMA:
{schema_summary}

TASK: Generate compelling demo content including:
1. 10-15 "golden queries" - questions that showcase the agent's capabilities
2. A demo script with introduction, key talking points, and conclusion
3. 5-7 sample Q&A pairs with expected insights

GOLDEN QUERIES SHOULD:
- Progress from simple to complex
- Cover different query types (aggregation, filtering, trending, comparison)
- Highlight business value
- Be realistic for the industry
- Showcase chart/visualization capabilities

OUTPUT FORMAT:
{{
    "golden_queries": [
        {{
            "query": "...",
            "purpose": "...",
            "expected_insight": "...",
            "visualization_type": "bar|line|pie|table"
        }}
    ],
    "demo_script": {{
        "introduction": "...",
        "key_points": [...],
        "golden_query_flow": [...],
        "conclusion": "..."
    }},
    "sample_qa": [
        {{
            "question": "...",
            "answer": "...",
            "follow_up": "..."
        }}
    ]
}}
"""
```

### Implementation Details

```python
class DemoContentGenerator:
    """Agent for generating demo content."""

    def __init__(self, anthropic_client: Anthropic):
        self.client = anthropic_client
        self.model = "claude-3-5-sonnet-20241022"

    async def execute(self, state: ProvisioningState) -> ProvisioningState:
        """Execute demo content generation."""

        # Generate content
        demo_content = await self.generate_content(
            state["customer_info"],
            state["schema_design"]
        )

        # Update state
        state["golden_queries"] = demo_content["golden_queries"]
        state["demo_script"] = demo_content["demo_script"]
        state["sample_qa"] = demo_content["sample_qa"]
        state["current_phase"] = "completed"
        state["progress_percentage"] = 100

        return state

    async def generate_content(
        self, customer_info: Dict, schema: Dict
    ) -> Dict:
        """Use Claude to generate demo content."""

        schema_summary = self.summarize_schema(schema)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=8192,
            temperature=0.7,
            messages=[{
                "role": "user",
                "content": DEMO_CONTENT_PROMPT.format(
                    customer_info=json.dumps(customer_info, indent=2),
                    schema_summary=schema_summary
                )
            }]
        )

        return json.loads(response.content[0].text)

    def summarize_schema(self, schema: Dict) -> str:
        """Create a human-readable schema summary."""
        summary = []
        for table in schema["tables"]:
            fields = [f["name"] for f in table["schema"]]
            summary.append(f"- {table['name']}: {', '.join(fields[:5])}...")
        return "\n".join(summary)
```

### Success Criteria
- ✅ Generates 10+ relevant queries
- ✅ Creates comprehensive demo script
- ✅ Provides actionable Q&A pairs
- ✅ Content is industry-appropriate
- ✅ Completes within 45 seconds

---

## Cross-Agent Communication

### Shared State
All agents read from and write to the shared `ProvisioningState` object managed by LangGraph.

### Error Propagation
If any agent fails:
1. Error is logged to `state["errors"]`
2. `state["current_phase"]` set to "failed"
3. Workflow routes to error handler
4. CE is notified via frontend

### Progress Tracking
Each agent updates:
- `state["progress_percentage"]`
- `state["logs"]`
- `state["current_phase"]`

Frontend polls these updates for real-time display.

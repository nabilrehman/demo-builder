# CAPI Demo Generator - Complete Video Walkthrough Transcript

## 🎯 Project Overview

### What is CAPI Demo Generator?

The CAPI Demo Generator is an **AI-powered automated demo provisioning platform** that transforms any company website into a fully functional conversational AI analytics demo in minutes. It's designed for Customer Engineers (CEs) at Google Cloud to quickly create impressive, data-driven demos for potential customers using Google's Conversational Analytics API (CAPI) powered by Gemini.

### Core Value Proposition

Instead of spending hours manually:
- Researching a customer's business
- Designing database schemas
- Creating synthetic data
- Writing SQL queries
- Configuring analytics agents

...a CE simply **enters a customer's website URL** and the system autonomously generates everything needed for a production-ready conversational analytics demo.

---

## 🏠 Act 1: Homepage - Landing Experience

### Scene: User Arrives at Homepage (/)

**Visual**: Beautiful gradient background (light blue to indigo), modern glassmorphic design

**Header Section** (Top of page):
- **Logo**: Sparkles icon in a gradient button background (left)
- **Title**: "CAPI Demo Generator" with gradient text effect
- **Subtitle**: "AI-Powered Demo Provisioning"
- **Authentication UI** (right side):
  - If Firebase authentication is enabled:
    - Shows "Loading..." during initialization
    - **Not signed in**: "Sign In" button with Google icon
    - **Signed in**: User email display + "Sign Out" button
  - "Go to Dashboard" button (primary CTA)

**Hero Section** (Center):
- **Badge**: "Automated Demo Provisioning Platform" with sparkles icon
- **Main Headline**: "Generate Production-Ready Demos in Minutes" (large, gradient text)
- **Subheading**: "Transform any website into a fully functional conversational AI demo with automatic data modeling, BigQuery provisioning, and intelligent query generation."
- **Two CTA Buttons**:
  - Primary: "Start Provisioning" (purple gradient, with lightning bolt icon)
  - Secondary: "View Analytics" (outline style, with bar chart icon)

**"How It Works" Section**:
6 feature cards arranged in a grid:

1. **AI Research Agent** (Sparkles icon)
   - Automatically crawls and analyzes target website
   - Understands business context, products, use cases

2. **Smart Data Modeling** (Database icon)
   - Generates realistic data schemas
   - Populates BigQuery with synthetic data

3. **Conversational AI** (Message icon)
   - Creates Gemini-powered analytics agent
   - Golden queries with natural language understanding

4. **Instant Deployment** (Lightning icon)
   - One-click provisioning to BigQuery
   - Automatic dataset creation and agent configuration

5. **Demo Assets** (Bar chart icon)
   - Executive summaries and talking tracks
   - Golden queries and schema documentation

6. **Secure & Scalable** (Shield icon)
   - Firebase authentication
   - User-scoped data isolation
   - Enterprise-grade security

**Footer**:
- "CAPI Demo Generator - Powered by Gemini & Claude"
- Quick links to Dashboard and Analytics

---

## 🎛️ Act 2: CE Dashboard - Starting a Demo Provision

### Scene: CE Clicks "Start Provisioning" → Navigates to /ce-dashboard

**Header**:
- **Title**: "CE Dashboard" with gradient text
- **Subtitle**: "Provision and manage conversational AI chatbots"
- **Right side**:
  - Authentication status (if enabled)
  - Settings button

### Main Dashboard Content:

#### Section 1: "Provision New Chatbot"

Two side-by-side cards offering different provisioning modes:

**DEFAULT MODE Card** (Left):
- **Icon**: Link/Chain icon (large)
- **Title**: "DEFAULT MODE"
- **Description**: "Quick setup with automatic configuration"
- **Input Field**:
  - Label: "Website URL"
  - Placeholder: "https://example.com"
  - Accepts any customer website URL
- **Button**: "Start Provision" (gradient background, disabled while provisioning)
  - Changes to "Provisioning..." when clicked
  - Button is primary call-to-action

**CRAZY FROG MODE Card** (Right):
- **Icon**: Lightning/Zap icon (large)
- **Title**: "CRAZY FROG MODE"
- **Description**: "Advanced setup with full customization"
- **Features Listed**:
  - Custom branding and styling
  - Advanced AI configuration
  - Integration options
- **Button**: "Advanced Setup" (outline style)
- **Status**: Shows "Coming Soon - Available in Phase 2D" toast when clicked

#### Section 2: "Recent Provisions"

**Job History Table** displaying past provisioning jobs:
- Columns:
  - Job ID
  - Customer URL
  - Status (badge: complete/failed/running)
  - Duration (e.g., "2m 34s")
  - Date/Time
  - Mode (default/advanced)
- Each row is clickable to view details
- Status indicators:
  - **Complete**: Green badge with checkmark
  - **Failed**: Red badge with X
  - **Running**: Blue badge with animated spinner

### User Action: CE Enters URL

**Example**: CE types "https://www.nike.com" into the DEFAULT MODE input field

**What Happens**:
1. CE clicks "Start Provision" button
2. Frontend sends POST request to `/api/provision/start` with customer URL
3. Backend creates unique job ID (UUID)
4. Backend initializes job in Job State Manager
5. Backend starts 7-agent provisioning pipeline in background
6. **CE is immediately redirected** to `/provision-progress?jobId={job_id}`

---

## ⚙️ Act 3: Provision Progress - Real-Time Pipeline Execution

### Scene: Progress Page (/provision-progress?jobId=xyz)

**Visual**: Full-screen dashboard with live updates, glassmorphic cards

### Header Card (Top):

**Status Banner**:
- **Title**: "Provisioning Pipeline"
- **Customer URL**: Displayed with external link icon (clickable)
- **Status Badge**:
  - **Running**: Blue badge with pulsing dot + "Running"
  - **Complete**: Green badge + "Complete"
  - **Failed**: Red badge with pulsing dot + "Failed"
- **Timer**: Shows elapsed time in MM:SS format (updates every second)
  - Example: "2:34"
- **Start Time**: "Started 2:45:32 PM"

**Overall Progress Bar**:
- Percentage display (0-100%)
- Animated gradient progress bar
- Updates in real-time as agents complete

**Current Status Message Box**:
- Large bordered card with dynamic border color:
  - Blue border when running
  - Green border when complete
  - Red border when failed
- **While Running**: Shows witty loading messages that rotate every few seconds:
  - "Teaching robots to understand your business... 🤖"
  - "Generating data faster than a caffeinated data scientist... ☕"
  - "Making BigQuery tables prettier than a spreadsheet... 📊"
  - "Convincing Gemini to write good queries... 💎"
- **When Complete/Failed**: Shows final status message

### Pipeline Stages Visualization

**7-Stage Grid** (responsive grid layout):

Each stage is a small card showing:
- **Stage Number**: 1-7
- **Stage Name**:
  1. Research Agent
  2. Demo Story Agent
  3. Data Modeling Agent
  4. Synthetic Data Generator
  5. Infrastructure Agent
  6. CAPI Instruction Generator
  7. Demo Validator
- **Status Icon**:
  - ⏳ Pending (gray, clock icon)
  - 🔄 Running (blue, spinning icon)
  - ✅ Complete (green, checkmark)
  - ❌ Failed (red, X icon)
- **Duration**: Shows time elapsed for running/completed stages

**Visual Flow**: Stages light up sequentially as they execute, creating a visual "progress wave" effect

### Live Logs Panel

**Scrollable log viewer** with:
- **Auto-scroll**: Automatically scrolls to bottom as new logs arrive
- **Log entries** showing:
  - **Timestamp**: HH:MM:SS
  - **Phase**: Which agent is logging (colored badge)
  - **Message**: Log content
  - **Level**: INFO (blue), WARNING (yellow), ERROR (red)

**Example Log Sequence**:
```
[14:30:15] [system] Starting 7-agent pipeline...
[14:30:16] [research] Starting Research Agent...
[14:30:18] [research] Crawling https://www.nike.com...
[14:30:25] [research] Found 15 pages to analyze
[14:30:42] [research] Extracted company info: Nike, Inc.
[14:31:05] [research] ✅ Research Agent completed successfully
[14:31:06] [demo_story] Starting Demo Story Agent...
[14:31:08] [demo_story] Generating demo narrative...
[14:31:35] [demo_story] Created 8 golden queries
[14:31:40] [demo_story] ✅ Demo Story Agent completed successfully
[14:31:41] [data_modeling] Starting Data Modeling Agent...
```

### Real-Time Updates (SSE Streaming)

**How it works behind the scenes**:
- Frontend opens Server-Sent Events (SSE) connection to `/api/provision/stream/{job_id}`
- Backend streams updates every time agent status changes
- Frontend receives JSON payloads and updates UI instantly
- Connection stays open until job completes or fails
- Heartbeat messages every 30 seconds keep connection alive

---

## 🤖 Act 4: The 7 Agents - What Each One Does

### Agent 1: Research Agent (V2 with Intelligent Crawler)

**Purpose**: Deeply understand the customer's business, products, and use cases

**What it does**:
1. **Crawls customer website** using intelligent breadth-first search
   - Starts at homepage
   - Follows internal links up to max depth (default: 2 levels)
   - Respects robots.txt
   - Maximum pages: 30 (configurable via env var)
2. **Analyzes page content**:
   - Extracts text, headings, meta descriptions
   - Identifies products, services, features
   - Understands business model
3. **Optional external sources** (disabled by default):
   - LinkedIn company page scraping
   - Blog post analysis
   - YouTube channel content
4. **Uses Gemini 1.5 Flash** to synthesize findings

**Output** (customer_info):
```json
{
  "company_name": "Nike, Inc.",
  "industry": "Athletic Footwear & Apparel",
  "business_model": "B2C E-commerce + Retail",
  "key_products": ["Running Shoes", "Basketball Shoes", "Apparel", "Fitness Gear"],
  "target_audience": "Athletes and sports enthusiasts",
  "key_features": ["Nike Membership", "SNKRS App", "Customization", "Sustainability"],
  "business_domain": "retail_ecommerce"
}
```

**Logs shown**:
- "Starting Research Agent..."
- "Crawling https://www.nike.com..."
- "Analyzed 25 pages"
- "✅ Research Agent completed successfully"

---

### Agent 2: Demo Story Agent

**Purpose**: Create a compelling demo narrative with golden queries

**What it does**:
1. **Receives research data** from Agent 1
2. **Generates demo story** including:
   - **Demo Title**: Catchy, business-focused title
   - **Executive Summary**: 2-3 sentence overview of the demo
   - **Business Challenges**: 3-5 key challenges this demo addresses
   - **Talking Track**: Narrative for presenting the demo
3. **Creates 6-10 Golden Queries**:
   - Mix of complexity levels (SIMPLE, MEDIUM, COMPLEX)
   - Business-relevant questions a customer would ask
   - Each query includes:
     - Natural language question
     - Expected SQL query
     - Business value explanation
     - Complexity rating

**Uses Gemini 1.5 Pro** for creative, contextual output

**Example Output**:
```json
{
  "demo_title": "Nike Digital Commerce Intelligence Platform",
  "executive_summary": "This demo showcases how Nike can leverage conversational analytics to gain real-time insights into customer behavior, product performance, and sales trends across their digital ecosystem.",
  "business_challenges": [
    "Understanding customer purchase patterns across multiple channels",
    "Identifying top-performing products by region and season",
    "Optimizing inventory based on demand forecasts"
  ],
  "golden_queries": [
    {
      "sequence": 1,
      "complexity": "SIMPLE",
      "question": "What are the total sales for the last quarter?",
      "expected_sql": "SELECT SUM(total_amount) FROM orders WHERE order_date >= '2024-10-01'",
      "business_value": "Quick revenue snapshot for executive reporting"
    },
    {
      "sequence": 2,
      "complexity": "MEDIUM",
      "question": "Which products are most popular in the Pacific Northwest?",
      "expected_sql": "SELECT p.product_name, COUNT(*) as order_count FROM orders o JOIN products p ON o.product_id = p.id WHERE o.region = 'Pacific Northwest' GROUP BY p.product_name ORDER BY order_count DESC LIMIT 10",
      "business_value": "Regional product optimization and marketing insights"
    }
  ]
}
```

**Logs shown**:
- "Starting Demo Story Agent..."
- "Generating demo narrative for Nike, Inc."
- "Created demo title: Nike Digital Commerce Intelligence Platform"
- "Generated 8 golden queries"
- "✅ Demo Story Agent completed successfully"

---

### Agent 3: Data Modeling Agent

**Purpose**: Design realistic BigQuery schema based on business domain

**What it does**:
1. **Analyzes business domain** (e.g., "retail_ecommerce")
2. **Designs 5-12 related tables**:
   - Core entities (customers, products, orders)
   - Relationship tables (order_items, reviews)
   - Supporting data (categories, regions, payments)
3. **For each table**:
   - Table name (snake_case)
   - Description of what it stores
   - 5-15 fields with:
     - Name, Type (STRING, INTEGER, FLOAT, TIMESTAMP, etc.)
     - Mode (NULLABLE, REQUIRED, REPEATED)
     - Description
   - Relationships to other tables
4. **Ensures referential integrity**:
   - Foreign keys properly defined
   - Realistic cardinalities (1:M, M:M)

**Uses Gemini 1.5 Pro** for intelligent schema design

**Example Output Schema** (Nike demo):
```json
{
  "tables": [
    {
      "name": "customers",
      "description": "Nike membership and customer profiles",
      "schema": [
        {"name": "customer_id", "type": "STRING", "mode": "REQUIRED", "description": "Unique customer identifier"},
        {"name": "email", "type": "STRING", "mode": "REQUIRED", "description": "Customer email address"},
        {"name": "first_name", "type": "STRING", "mode": "NULLABLE"},
        {"name": "last_name", "type": "STRING", "mode": "NULLABLE"},
        {"name": "membership_tier", "type": "STRING", "mode": "NULLABLE", "description": "Nike Member tier level"},
        {"name": "registration_date", "type": "TIMESTAMP", "mode": "NULLABLE"},
        {"name": "location_city", "type": "STRING", "mode": "NULLABLE"},
        {"name": "location_state", "type": "STRING", "mode": "NULLABLE"}
      ]
    },
    {
      "name": "products",
      "description": "Nike product catalog",
      "schema": [
        {"name": "product_id", "type": "STRING", "mode": "REQUIRED"},
        {"name": "product_name", "type": "STRING", "mode": "REQUIRED"},
        {"name": "category", "type": "STRING", "mode": "NULLABLE", "description": "Running, Basketball, Training, etc."},
        {"name": "price", "type": "FLOAT", "mode": "REQUIRED"},
        {"name": "color", "type": "STRING", "mode": "NULLABLE"},
        {"name": "size", "type": "STRING", "mode": "NULLABLE"}
      ]
    },
    {
      "name": "orders",
      "description": "Customer purchase transactions",
      "schema": [
        {"name": "order_id", "type": "STRING", "mode": "REQUIRED"},
        {"name": "customer_id", "type": "STRING", "mode": "REQUIRED", "description": "Foreign key to customers"},
        {"name": "order_date", "type": "TIMESTAMP", "mode": "REQUIRED"},
        {"name": "total_amount", "type": "FLOAT", "mode": "REQUIRED"},
        {"name": "order_status", "type": "STRING", "mode": "NULLABLE"},
        {"name": "shipping_method", "type": "STRING", "mode": "NULLABLE"}
      ]
    }
  ]
}
```

**Logs shown**:
- "Starting Data Modeling Agent..."
- "Designing schema for retail_ecommerce domain"
- "Created 10 tables with 87 total fields"
- "✅ Data Modeling Agent completed successfully"

---

### Agent 4: Synthetic Data Generator (Markdown LLM Version)

**Purpose**: Generate realistic, contextually accurate synthetic data for all tables

**What it does**:
1. **Analyzes schema and business context** from previous agents
2. **For each table**, generates realistic data:
   - **ALWAYS uses LLM** (Gemini 1.5 Flash) - no Faker fallback
   - Generates data in **Markdown table format** for efficient parsing
   - Maintains referential integrity across tables
   - Creates realistic distributions and patterns
3. **Generates 50-500 rows per table** (configurable)
4. **Ensures data quality**:
   - Foreign keys match parent records
   - Dates are realistic and sequential
   - Numeric values are in sensible ranges
   - Text data is contextually appropriate
5. **Writes JSONL files** (one per table) to `/tmp/synthetic_data/`

**Why Markdown format?**
- 10x faster than JSON parsing
- More token-efficient for LLM
- Easier for LLM to generate correctly formatted data

**Example Prompt** to Gemini:
```
Generate 200 rows for the 'customers' table.

Table: customers
Description: Nike membership and customer profiles
Schema:
- customer_id (STRING, REQUIRED): Unique customer identifier
- email (STRING, REQUIRED): Customer email address
- first_name (STRING, NULLABLE)
- last_name (STRING, NULLABLE)
- membership_tier (STRING, NULLABLE): Nike Member tier level (Free, Plus, Premium)

Business Context: Nike is a global athletic brand. Customers span all age ranges and locations.

Format your response ONLY as a Markdown table with NO additional text:

| customer_id | email | first_name | last_name | membership_tier |
|---|---|---|---|---|
| CUST001 | john.smith@email.com | John | Smith | Plus |
```

**Example Generated Data**:
```
| customer_id | email | first_name | last_name | membership_tier | location_city | location_state |
|---|---|---|---|---|---|---|
| CUST001 | sarah.johnson@email.com | Sarah | Johnson | Premium | Portland | Oregon |
| CUST002 | mike.williams@email.com | Mike | Williams | Free | Seattle | Washington |
| CUST003 | emily.davis@email.com | Emily | Davis | Plus | San Francisco | California |
...
```

**Output Files**:
```
/tmp/synthetic_data/nike_demo_20251007/
├── customers.jsonl (200 rows)
├── products.jsonl (150 rows)
├── orders.jsonl (800 rows)
├── order_items.jsonl (1500 rows)
└── reviews.jsonl (300 rows)
```

**Logs shown**:
- "Starting Synthetic Data Generator..."
- "Generating data for customers table (200 rows)..."
- "Generating data for products table (150 rows)..."
- "Generated 2950 total rows across 10 tables"
- "✅ Synthetic Data Generator completed successfully"

---

### Agent 5: Infrastructure Agent (Optimized with Parallel Loading)

**Purpose**: Provision BigQuery infrastructure and load all data

**What it does**:
1. **Creates BigQuery dataset**:
   - Dataset ID: `{company_name}_demo_{timestamp}` (e.g., `nike_demo_20251007_1430`)
   - Location: US (multi-region)
   - Description: Auto-generated demo dataset
2. **Creates all tables in parallel**:
   - Reads schema from Agent 3
   - Creates empty tables with proper schema
   - Sets clustering/partitioning if appropriate
3. **Loads data in parallel** (10x faster):
   - Reads JSONL files from Agent 4
   - Uses BigQuery load jobs with `autodetect=False`
   - Batches multiple load jobs concurrently
   - Monitors progress for each table
4. **Gathers statistics**:
   - Row counts per table
   - Storage size (MB) per table
   - Total dataset size
5. **Creates CAPI Data Agent**:
   - Agent ID: `{dataset_id}_agent`
   - Connects agent to all tables in dataset
   - Configures with basic system instructions
6. **Generates demo documentation** (Markdown report)

**Uses Google Cloud BigQuery Python SDK**

**Example Actions**:
```python
# Create dataset
dataset_id = "nike_demo_20251007_1430"
dataset = bigquery.Dataset(f"{project_id}.{dataset_id}")
dataset.location = "US"
client.create_dataset(dataset)

# Create tables in parallel
async def create_table(table_info):
    schema = [bigquery.SchemaField(f['name'], f['type'], mode=f['mode'])
              for f in table_info['schema']]
    table_ref = f"{project_id}.{dataset_id}.{table_info['name']}"
    table = bigquery.Table(table_ref, schema=schema)
    client.create_table(table)

await asyncio.gather(*[create_table(t) for t in schema['tables']])

# Load data in parallel
async def load_data(table_name, jsonl_file):
    job_config = bigquery.LoadJobConfig(source_format='NEWLINE_DELIMITED_JSON')
    with open(jsonl_file, 'rb') as f:
        job = client.load_table_from_file(f, table_ref, job_config=job_config)
    job.result()  # Wait for completion

await asyncio.gather(*[load_data(t, f) for t, f in data_files.items()])
```

**Output**:
```json
{
  "dataset_id": "nike_demo_20251007_1430",
  "dataset_full_name": "bq-demos-469816.nike_demo_20251007_1430",
  "capi_agent_id": "nike_demo_20251007_1430_agent",
  "table_stats": {
    "customers": {"row_count": 200, "size_mb": 0.05},
    "products": {"row_count": 150, "size_mb": 0.03},
    "orders": {"row_count": 800, "size_mb": 0.12},
    "order_items": {"row_count": 1500, "size_mb": 0.22},
    "reviews": {"row_count": 300, "size_mb": 0.08}
  }
}
```

**Logs shown**:
- "Starting Infrastructure Agent..."
- "Creating BigQuery dataset: nike_demo_20251007_1430"
- "Creating 10 tables in parallel..."
- "Loading data for customers (200 rows)..."
- "Loading data for products (150 rows)..."
- "All tables loaded successfully"
- "Creating CAPI Data Agent: nike_demo_20251007_1430_agent"
- "✅ Infrastructure Agent completed successfully"

---

### Agent 6: CAPI Instruction Generator

**Purpose**: Create optimized system instructions (YAML) for the CAPI agent

**What it does**:
1. **Analyzes demo story and schema**
2. **Generates comprehensive system instructions**:
   - Agent personality and tone
   - Business context understanding
   - Query interpretation guidelines
   - Table relationship explanations
   - Common query patterns
3. **Creates example queries** from golden queries
4. **Writes YAML file** in CAPI format

**Uses Gemini 1.5 Pro** for instruction generation

**Example YAML Output**:
```yaml
system_instruction: |
  You are a conversational analytics assistant for Nike's Digital Commerce Intelligence Platform.

  Your role is to help business users query and analyze Nike's sales, customer, and product data
  using natural language. You have access to a BigQuery dataset containing:

  - Customer profiles and membership data
  - Product catalog with categories and pricing
  - Order transactions and purchase history
  - Customer reviews and ratings

  When answering questions:
  1. Generate clear, optimized SQL queries
  2. Provide business context in your responses
  3. Highlight insights and trends
  4. Suggest follow-up questions

  Key Tables:
  - customers: Nike member profiles
  - products: Product catalog (shoes, apparel, gear)
  - orders: Purchase transactions
  - order_items: Individual items in each order
  - reviews: Customer product reviews

  Example Queries:

  Q: "What are our total sales this quarter?"
  A: SELECT SUM(total_amount) FROM orders WHERE order_date >= '2024-10-01'

  Q: "Which products are most popular?"
  A: SELECT p.product_name, COUNT(*) as purchases
     FROM order_items oi
     JOIN products p ON oi.product_id = p.product_id
     GROUP BY p.product_name
     ORDER BY purchases DESC
     LIMIT 10

datasource_references:
  bq:
    table_references:
      - project_id: bq-demos-469816
        dataset_id: nike_demo_20251007_1430
        table_id: customers
      - project_id: bq-demos-469816
        dataset_id: nike_demo_20251007_1430
        table_id: products
      # ... etc
```

**Saves file to**: `/tmp/capi_instructions/nike_demo_20251007_1430.yaml`

**Logs shown**:
- "Starting CAPI Instruction Generator..."
- "Generating system instructions for Nike demo"
- "Created YAML file: /tmp/capi_instructions/nike_demo_20251007_1430.yaml"
- "✅ CAPI Instruction Generator completed successfully"

---

### Agent 7: Demo Validator (Optimized with Parallel Validation)

**Purpose**: Test all golden queries using CAPI to ensure they work

**What it does**:
1. **Receives golden queries** from Agent 2
2. **Tests each query through CAPI**:
   - Creates conversation with CAPI Data Agent
   - Sends natural language question
   - Receives response + generated SQL
   - Validates response is not an error
3. **Runs validations in parallel** (much faster than sequential)
4. **Records results**:
   - Which queries passed
   - Which queries failed (with error messages)
   - CAPI response preview (first 200 chars)

**Uses Google Cloud Gemini Data Analytics SDK**

**Example Validation**:
```python
async def validate_query(query):
    # Create CAPI conversation
    conversation = data_chat_client.create_conversation(
        parent=f"projects/{project_id}/locations/global",
        conversation=Conversation(
            agents=[f"projects/{project_id}/locations/global/dataAgents/{agent_id}"]
        )
    )

    # Send query
    response = data_chat_client.chat(
        messages=[Message(user_message=UserMessage(text=query['question']))],
        conversation_reference=conversation
    )

    # Check for success
    success = not any('error' in msg.lower() for msg in response.messages)

    return {
        "sequence": query['sequence'],
        "question": query['question'],
        "capi_success": success,
        "capi_response": response.messages[0].text[:200],
        "capi_error": None if success else "Query failed"
    }

# Run all validations in parallel
results = await asyncio.gather(*[validate_query(q) for q in golden_queries])
```

**Output**:
```json
{
  "validation_results": {
    "total_queries": 8,
    "sql_results": [
      {
        "sequence": 1,
        "question": "What are total sales for Q4?",
        "capi_success": true,
        "capi_response": "Total sales for Q4 2024 are $2.4M. Here's the breakdown by month...",
        "capi_error": null
      },
      {
        "sequence": 2,
        "question": "Top 10 products by revenue?",
        "capi_success": true,
        "capi_response": "Here are the top 10 products: 1. Air Max 90 ($450K), 2. Jordan 1 ($380K)...",
        "capi_error": null
      }
    ]
  }
}
```

**Logs shown**:
- "Starting Demo Validator..."
- "Validating 8 golden queries via CAPI"
- "Testing query 1/8: What are total sales for Q4?"
- "✅ Query 1 passed"
- "Testing query 2/8: Top 10 products by revenue?"
- "✅ Query 2 passed"
- "Validation complete: 8/8 queries passed"
- "✅ Demo Validator completed successfully"

---

## 🎉 Act 5: Completion - Demo Assets Ready

### Scene: All 7 Agents Complete Successfully

**Progress Page Updates**:
- Overall progress bar: **100%**
- Status badge: Changes to **Green "Complete"**
- All 7 stage cards: Show **green checkmarks ✅**
- Current message box:
  - Border turns **green**
  - Message: "🎉 Provisioning Complete! Your demo environment is ready"

**Final Log Entries**:
```
[14:35:42] [validation] ✅ Demo Validator completed successfully
[14:35:43] [system] Provisioning completed successfully! Dataset: nike_demo_20251007_1430
[14:35:43] [system] 🎉 All stages complete - Demo ready to use!
```

### Success Banner Appears

**Green card** at bottom of page with:
- **Title**: "🎉 Provisioning Complete!"
- **Subtitle**: "Your demo environment is ready"
- **Three Action Buttons**:

1. **"Open BigQuery Console"** (external link)
   - Opens: `https://console.cloud.google.com/bigquery?project=bq-demos-469816&dataset=nike_demo_20251007_1430`
   - Shows dataset in BigQuery UI

2. **"View Demo Assets"** (internal navigation)
   - Navigates to: `/demo-assets?jobId={job_id}`
   - Shows demo story, golden queries, schema viewer

3. **"Launch Chat Interface"** (internal navigation)
   - Navigates to: `/?website={url}&agent_id={agent_id}&dataset_id={dataset_id}`
   - Opens conversational chat interface with pre-loaded agent

---

## 📋 Act 6: Demo Assets Viewer - Reviewing Generated Materials

### Scene: CE Clicks "View Demo Assets" → Navigates to /demo-assets?jobId=xyz

**Success Banner** (top):
- **Green background** with checkmark icon
- **Title**: "🎉 Provision Complete!"
- **Subtitle**: "Demo ready at: {customer_url}"
- **Duration**: Shows total time (e.g., "5m 17s")

**Launch Chat Button** (prominent card):
- **Purple gradient background**
- **Left side**:
  - Rocket icon
  - "Ready to Launch"
  - "Your demo is provisioned and ready. Click to open the chat interface with pre-loaded data."
- **Right side**:
  - Large "Launch Chat Interface" button (white text on gradient)

**Action Buttons Row** (4 quick actions):

1. **Download YAML**
   - Downloads: `capi_instructions_nike_demo_20251007_1430.yaml`
   - Use case: Manual CAPI agent creation or customization

2. **Copy Dataset ID**
   - Copies to clipboard: `nike_demo_20251007_1430`
   - Shows toast notification

3. **View in BigQuery**
   - Opens BigQuery console in new tab
   - Navigates to dataset

4. **Re-run Provision**
   - Triggers new provisioning job with same URL
   - Use case: Refresh data or update demo

### Tabbed Content Area

**4 tabs** for different aspects of the demo:

#### Tab 1: "Demo Title"

Displays the **demo story** created by Agent 2:

**Demo Title Card**:
- **Large heading**: "Nike Digital Commerce Intelligence Platform"
- **Subheading**: Demo category/type

**Executive Summary**:
- 2-3 paragraph overview
- Business value proposition
- Target use cases

**Business Challenges** (numbered list):
1. Understanding customer purchase patterns across multiple channels
2. Identifying top-performing products by region and season
3. Optimizing inventory based on demand forecasts
4. Personalizing marketing campaigns using behavioral data
5. Tracking Nike membership engagement and retention

**Talking Track** (collapsible sections):
- **Opening**: How to introduce the demo
- **Key Features**: What to highlight
- **Demo Flow**: Suggested query sequence
- **Closing**: How to wrap up and next steps

#### Tab 2: "Golden Queries"

**8-10 query cards** arranged vertically:

Each card shows:
- **Complexity badge** (top-right corner)
  - SIMPLE (green)
  - MEDIUM (yellow)
  - COMPLEX (orange)
- **Question** (large, bold text)
  - Example: "What are our total sales for Q4 2024?"
- **Business Value** (italic subtitle)
  - Example: "Quick revenue snapshot for executive reporting"
- **CAPI Validation Status**:
  - ✅ "Tested via CAPI - Passed"
  - ❌ "CAPI test failed: {error message}"
- **"Try in Chat" button**
  - Copies question to clipboard
  - Opens chat interface with pre-filled question

**Example Golden Query Card**:
```
┌─────────────────────────────────────────────┐
│  MEDIUM                                     │
│                                             │
│  Which products are most popular in the    │
│  Pacific Northwest region?                 │
│                                             │
│  📊 Regional product optimization and       │
│     marketing insights                     │
│                                             │
│  ✅ Tested via CAPI - Passed               │
│  Response preview: "Here are the top 10... │
│                                             │
│  [Try in Chat]                              │
└─────────────────────────────────────────────┘
```

**Sort/Filter Options**:
- Sort by: Complexity, Sequence, Validation Status
- Filter: Show only failed queries

#### Tab 3: "Schema"

**Table list** (left sidebar):
- Shows all 10 tables
- Each table shows row count
- Clickable to view details

**Selected Table Details** (main area):

When CE clicks a table (e.g., "customers"):

**Table Card**:
- **Table Name**: `customers`
- **Description**: "Nike membership and customer profiles"
- **Row Count**: 200 rows
- **Storage Size**: 0.05 MB
- **Field Count**: 8 fields

**Fields Table**:
```
┌─────────────────┬─────────┬──────────┬────────────────────────────────┐
│ Field Name      │ Type    │ Mode     │ Description                    │
├─────────────────┼─────────┼──────────┼────────────────────────────────┤
│ customer_id     │ STRING  │ REQUIRED │ Unique customer identifier     │
│ email           │ STRING  │ REQUIRED │ Customer email address         │
│ first_name      │ STRING  │ NULLABLE │ Customer first name            │
│ last_name       │ STRING  │ NULLABLE │ Customer last name             │
│ membership_tier │ STRING  │ NULLABLE │ Nike Member tier (Free/Plus/   │
│                 │         │          │ Premium)                       │
│ location_city   │ STRING  │ NULLABLE │ Customer city                  │
│ location_state  │ STRING  │ NULLABLE │ Customer state                 │
└─────────────────┴─────────┴──────────┴────────────────────────────────┘
```

**Relationships**:
- "Referenced by: orders.customer_id"
- Visual indicator of table connections

**Sample Data Preview** (optional):
- Shows first 5 rows from table
- Fetched on demand from BigQuery

#### Tab 4: "Metadata"

**Technical details** about the provisioned demo:

**Provisioning Info**:
- Job ID: `e3db8d72-6b98-4f17-999e-c5575b151744`
- Customer URL: `https://www.nike.com`
- Created: `2024-10-07 14:30:15`
- Duration: `5m 17s`
- Mode: `DEFAULT`

**BigQuery Details**:
- Project ID: `bq-demos-469816`
- Dataset ID: `nike_demo_20251007_1430`
- Dataset Full Name: `bq-demos-469816.nike_demo_20251007_1430`
- Location: `US`
- Total Tables: `10`
- Total Rows: `2,950`
- Total Storage: `0.5 MB`

**CAPI Agent Info**:
- Agent ID: `nike_demo_20251007_1430_agent`
- Agent Name: `Nike Digital Commerce Intelligence Platform Agent`
- Status: ✅ Active
- Connected Tables: `10`

**Files Generated**:
- YAML Instructions: `/tmp/capi_instructions/nike_demo_20251007_1430.yaml`
- Demo Report: `/tmp/demo_reports/nike_demo_20251007_1430.md`
- Data Files: `/tmp/synthetic_data/nike_demo_20251007_1430/*.jsonl`

---

## 💬 Act 7: Chat Interface - Conversational Analytics in Action

### Scene: CE Clicks "Launch Chat Interface" → Navigates to /chat

**OR** CE can navigate to the **polished chat interface** at `/` with URL params:
- `/?website=https://www.nike.com&agent_id=nike_demo_20251007_1430_agent&dataset_id=nike_demo_20251007_1430`

### Chat Header

**Top Bar**:
- **Logo**: Nike logo (automatically extracted via `/api/extract-branding`)
- **Title**: "Nike Digital Commerce Intelligence Platform"
- **Dataset Badge**: Shows dataset ID in monospace font
- **Database icon**: Visual indicator this is a data chat

### Chat Interface Layout

**Main Chat Area** (scrollable):

**Empty State** (before first message):
- **Greeting**: "👋 Start asking questions about your data..."
- **Suggested Questions Section**:
  - Title: "✨ Suggested Questions" (with sparkles icon)
  - Shows 6-8 golden queries as **clickable cards**

**Golden Query Card** (clickable):
```
┌──────────────────────────────────────────────────┐
│ ✨ Which products are most popular in the       │
│    Pacific Northwest region?                    │
│                                                  │
│    📊 Regional product optimization and         │
│       marketing insights                        │
│                                        [MEDIUM]  │
└──────────────────────────────────────────────────┘
```

- **Hover effect**: Border changes to blue, shadow increases
- **Click action**: Fills query into input box

**Message Display** (after first query):

**User Message** (right-aligned):
- Blue/purple gradient background
- White text
- Shows user's question
- Example: "Which products are most popular in the Pacific Northwest region?"

**Assistant Message** (left-aligned):
- White background with border
- Black text
- Contains:
  1. **Natural language response**
  2. **Generated SQL** (expandable code block with syntax highlighting)
  3. **Chart visualization** (if applicable)

**Example Assistant Response**:
```
┌─────────────────────────────────────────────────────────────┐
│ Based on the data, the most popular products in the        │
│ Pacific Northwest are:                                     │
│                                                             │
│ 1. Air Max 90 - 347 purchases                             │
│ 2. Pegasus Trail 4 - 289 purchases                        │
│ 3. Jordan 1 Mid - 256 purchases                           │
│ 4. React Infinity Run - 198 purchases                     │
│ 5. Air Force 1 - 176 purchases                            │
│                                                             │
│ Running shoes dominate the Pacific Northwest market,      │
│ likely due to the region's active outdoor culture and     │
│ rainy climate which favors trail running shoes.           │
│                                                             │
│ ┌─ Generated SQL ────────────────────────────────────┐    │
│ │ SELECT p.product_name,                              │    │
│ │        COUNT(*) as purchase_count                   │    │
│ │ FROM order_items oi                                 │    │
│ │ JOIN products p ON oi.product_id = p.product_id     │    │
│ │ JOIN orders o ON oi.order_id = o.order_id           │    │
│ │ WHERE o.region = 'Pacific Northwest'                │    │
│ │ GROUP BY p.product_name                             │    │
│ │ ORDER BY purchase_count DESC                        │    │
│ │ LIMIT 5                                             │    │
│ └─────────────────────────────────────────────────────┘    │
│                                                             │
│ [Bar Chart Visualization]                                  │
│ ┌─────────────────────────────────────────────────┐       │
│ │                                                 │       │
│ │  Air Max 90          ████████████████████████  │       │
│ │  Pegasus Trail 4     ███████████████████       │       │
│ │  Jordan 1 Mid        ████████████████          │       │
│ │  React Infinity Run  ████████████              │       │
│ │  Air Force 1         ██████████                │       │
│ │                                                 │       │
│ └─────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

**Chart Types** (automatically generated):
- **Bar Chart**: For category comparisons
- **Line Chart**: For time-series trends
- **Pie Chart**: For distribution/proportions

Charts are rendered using **Recharts** library with:
- Responsive sizing
- Hover tooltips
- Color-coded bars
- Axis labels
- Legend

### Input Area (Bottom)

**Message Input Box**:
- Placeholder: "Ask a question about your data..."
- Multi-line support (Shift+Enter for new line)
- Enter key sends message

**Send Button**:
- **Idle**: Paper airplane icon
- **Loading**: Spinning loader icon
- Disabled when: Input is empty or query is processing

**Warning Message** (if dataset ID missing):
- "⚠️ No dataset ID provided. Chat may not work correctly."

### Developer Mode Toggle (Optional)

**Bottom-left corner**: "Developer Mode" checkbox

**When enabled, shows**:
- Raw API response JSON
- Request/response timings
- Token usage
- Model version used

### How Chat Works (Behind the Scenes)

**User sends message**:
```typescript
1. User types: "What are total sales for Q4?"
2. Frontend calls: POST /api/chat
   Body: {
     message: "What are total sales for Q4?",
     dataset_id: "nike_demo_20251007_1430",
     agent_id: "nike_demo_20251007_1430_agent"
   }
3. Backend creates CAPI conversation
4. Backend sends message to Gemini Data Analytics API
5. Gemini:
   - Interprets natural language
   - Generates SQL query
   - Executes against BigQuery
   - Generates response with results
6. Backend processes CAPI stream:
   - Extracts text response
   - Extracts generated SQL
   - Converts Vega-Lite chart spec to frontend format
7. Backend returns:
   {
     response: "Total sales for Q4 2024...",
     sqlQuery: "SELECT SUM(total_amount)...",
     chartData: { type: "bar", data: [...], xKey: "month", yKey: "sales" }
   }
8. Frontend displays all three components
```

**Error Handling**:
- If agent_id is missing/empty: Shows error
- If query fails: Shows friendly error message
- If response times out: Shows retry button

### Example Conversation Flow

**Query 1** (SIMPLE):
```
User: "What are total sales for Q4 2024?"
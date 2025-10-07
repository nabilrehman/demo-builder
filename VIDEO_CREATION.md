# CAPI Demo Generator - Video Walkthrough Script

## 📝 Video Production Guide
**Purpose:** Comprehensive walkthrough of the CAPI Demo Generator application
**Target Audience:** Customer Engineers, Sales Engineers, Developers
**Duration:** 8-10 minutes
**Format:** Screen recording with voiceover

---

## 🎬 Scene 1: Landing Page Introduction (30 seconds)

### Visual
- Open browser to: `https://demo-gen-capi-prod-549403515075.us-central1.run.app/`
- Show the **professional landing page** with hero section

### Narration Script
> "Welcome to the CAPI Demo Generator - an AI-powered platform that transforms any website into a fully functional conversational analytics demo in minutes. This tool automatically analyzes target websites, generates realistic data models, provisions BigQuery datasets, and creates intelligent chatbots - all without manual configuration."

### Key UI Elements to Highlight
- **Header**: CAPI Demo Generator branding with Sparkles icon
- **Hero Section**: "Generate Production-Ready Demos in Minutes" headline
- **Feature Cards**: 6 cards showing AI Research, Data Modeling, Conversational AI, Instant Deployment, Demo Assets, Security
- **CTA Buttons**: "Start Provisioning" and "View Analytics"
- **Sign In Button** (top-right) - mention Firebase authentication

---

## 🎬 Scene 2: Authentication & Sign In (20 seconds)

### Visual
- Click **"Sign In"** button in top-right
- Show Google Sign-In popup
- Select `@google.com` account
- Show successful sign-in with email displayed

### Narration Script
> "The platform uses Firebase authentication with Google Sign-In, restricted to authorized Google accounts only. This ensures secure, user-scoped access to all provisioning jobs and demo assets."

### Key UI Elements to Highlight
- Google OAuth popup
- Email restriction (only `@google.com` allowed)
- User email displayed in header after sign-in
- "Sign Out" button appears

---

## 🎬 Scene 3: CE Dashboard Overview (30 seconds)

### Visual
- Click "Go to Dashboard" or "Start Provisioning" button
- Navigate to CE Dashboard at `/ce-dashboard`
- Show the full dashboard interface

### Narration Script
> "The CE Dashboard is your command center for provisioning conversational AI demos. From here, you can create new demos using either Default Mode for quick setup, or Crazy Frog Mode for advanced customization. The dashboard also tracks all your recent provisions with real-time status updates."

### Key UI Elements to Highlight
- **Header**: "CE Dashboard" title with "Provision and manage conversational AI chatbots" subtitle
- **Sign In Status**: User email and Sign Out button
- **Settings Icon**
- **Provision Cards**:
  - **DEFAULT MODE** card: Quick setup with automatic configuration
  - **CRAZY FROG MODE** card: Advanced setup with full customization
- **Website URL Input Field**: Shows placeholder `https://example.com`
- **Start Provision Button**: Primary CTA
- **Recent Provisions Table**: Shows job history with columns:
  - URL
  - Status (Complete/Running/Failed)
  - Mode (default/advanced)
  - Duration
  - Date
  - Actions menu

---

## 🎬 Scene 4: Starting a New Provision - Input Phase (45 seconds)

### Visual
- Focus on **DEFAULT MODE** card
- Click on the **Website URL** input field
- Type a real customer URL: `https://www.nike.com`
- Hover over the **"Start Provision"** button

### Narration Script
> "Let's create a demo for Nike's website. In Default Mode, all you need is the target website URL. The system will automatically handle everything else - from research to data generation to chatbot provisioning. Let's click Start Provision to begin the automated workflow."

### Key UI Elements to Highlight
- Website URL input field (actively typing)
- Placeholder text changing
- "Start Provision" button state (enabled when URL is valid)

---

## 🎬 Scene 5: Provision Progress - Phase Monitoring (2-3 minutes)

### Visual
- Click **"Start Provision"** button
- Redirect to `/provision-progress?jobId={job-id}` page
- Show the **progress tracking interface**

### Narration Script - Part 1: Overview
> "After clicking Start Provision, we're taken to the Provision Progress page where we can monitor the entire orchestration in real-time. The system runs 7 specialized AI agents in sequence, each handling a specific part of the demo generation process. Let's watch as the platform builds a complete conversational analytics demo from scratch."

### Key UI Elements to Highlight
- **Page Header**:
  - "Provision Progress" title
  - Customer URL displayed: `https://www.nike.com/`
  - Overall Progress Bar: Shows percentage (0% → 100%)
  - Current Status: "Running" with animated spinner

- **Progress Phases Section**:
  - 7 phase indicators shown vertically
  - Each phase has: Icon, Name, Status (Pending/Running/Complete)

---

### PHASE 1: RESEARCH AGENT (30 seconds)

### Visual
- Show Research Agent phase transitioning from "Pending" to "Running"
- Display real-time logs scrolling

### Narration Script
> "**Phase 1: Research Agent** - This is where the magic begins. The Research Agent uses advanced web crawling to analyze Nike's website. It explores the homepage, product pages, about pages, and more - gathering information about Nike's business model, product categories, customer demographics, and use cases. The agent extracts key entities like products, locations, customer segments, and business metrics that will inform our data model."

### Agent Actions (Show in Logs)
```
Starting research for Nike...
Crawling homepage: https://www.nike.com/
Found sections: Men's, Women's, Kids', Sale, SNKRS
Analyzing product categories: Running Shoes, Basketball Shoes, Sportswear, Jordan
Discovered entities: Products, Customers, Orders, Locations, Reviews
Extracting business context: Athletic footwear and apparel retailer
Completed research phase - 45 entities discovered
```

### Key UI Elements to Highlight
- Phase status: "Research" badge changes from gray → blue (running) → green (complete)
- Real-time log output in scrollable area
- Checkmark appears when phase completes
- Automatic scroll to next phase

---

### PHASE 2: DEMO STORY AGENT (25 seconds)

### Visual
- Research Agent completes (green checkmark)
- Demo Story Agent starts (blue running indicator)
- Show log output for storytelling

### Narration Script
> "**Phase 2: Demo Story Agent** - With research complete, the Demo Story Agent creates a compelling narrative for the demo. It generates an executive summary, identifies business challenges that Nike faces, creates a talking track for presentations, and defines specific demo scenarios that showcase the power of conversational analytics in the athletic retail industry."

### Agent Actions (Show in Logs)
```
Generating demo story for Nike...
Business Challenge 1: Understanding customer purchase patterns across channels
Business Challenge 2: Optimizing inventory for seasonal product launches
Business Challenge 3: Analyzing geographic demand for limited edition releases
Creating executive summary...
Developing talking track: "Nike Analytics Demo - Real-time insights into customer behavior"
Generated 4 demo scenarios focused on: Sales Analytics, Customer Insights, Inventory Intelligence
Demo story complete
```

### Key UI Elements to Highlight
- Demo Story phase indicator turns blue → green
- Executive summary preview in logs
- Business challenges listed (3-4 items)

---

### PHASE 3: DATA MODELING AGENT (35 seconds)

### Visual
- Data Modeling Agent activates (blue indicator)
- Show complex schema generation in logs
- Display entity relationships

### Narration Script
> "**Phase 3: Data Modeling Agent** - This is one of the most sophisticated phases. The Data Modeling Agent takes all the research findings and creates a complete BigQuery schema. For Nike, it generates realistic tables for Customers, Products, Orders, OrderLineItems, Reviews, Stores, and Inventory. Each table is designed with proper relationships, data types, and constraints that mirror a real e-commerce data warehouse."

### Agent Actions (Show in Logs)
```
Designing data model for Nike...

Creating table: customers
  - customer_id (STRING)
  - name (STRING)
  - email (STRING)
  - location (GEOGRAPHY)
  - membership_tier (STRING: Bronze, Silver, Gold, Platinum)
  - lifetime_value (FLOAT64)
  - signup_date (DATE)

Creating table: products
  - product_id (STRING)
  - product_name (STRING)
  - category (STRING: Running, Basketball, Sportswear, Jordan)
  - subcategory (STRING)
  - price (FLOAT64)
  - color (STRING)
  - size (STRING)

Creating table: orders
  - order_id (STRING)
  - customer_id (STRING) -- FK to customers
  - order_date (TIMESTAMP)
  - total_amount (FLOAT64)
  - channel (STRING: Online, Retail, Mobile App)
  - status (STRING)

Creating table: order_line_items
  - line_item_id (STRING)
  - order_id (STRING) -- FK to orders
  - product_id (STRING) -- FK to products
  - quantity (INT64)
  - unit_price (FLOAT64)

Schema validation: PASSED
Total tables: 8 | Total fields: 67
Data model generation complete
```

### Key UI Elements to Highlight
- Schema visualization preview
- Table count increasing
- Field definitions scrolling
- Validation checkmarks

---

### PHASE 4: SYNTHETIC DATA GENERATION (30 seconds)

### Visual
- Data Generation phase activates
- Show row count increasing in logs
- Display sample data snippets

### Narration Script
> "**Phase 4: Synthetic Data Generation** - With the schema defined, the platform generates realistic synthetic data. Using the Gretel SDK and the research insights, it creates thousands of rows of contextual, realistic data. For Nike, this means generating customer profiles with appropriate names, locations near Nike stores, product data with real Nike product categories and price ranges, and order transactions that reflect actual shopping patterns."

### Agent Actions (Show in Logs)
```
Generating synthetic data for Nike...

Table: customers
  Generating 5,000 customer records...
  Sample: {customer_id: "CUST_001", name: "Michael Jordan", email: "mj@nike.com",
           location: "Portland, OR", membership_tier: "Platinum", lifetime_value: 8450.50}
  Progress: 1000/5000 rows... 2000/5000... Complete ✓

Table: products
  Generating 2,500 product records...
  Sample: {product_id: "NK_AIR_001", product_name: "Air Max 90", category: "Running",
           price: 129.99, color: "White/Black", size: "US 10"}
  Progress: Complete ✓

Table: orders
  Generating 15,000 order records...
  Date range: 2024-01-01 to 2025-10-07
  Progress: 5000/15000... 10000/15000... Complete ✓

Table: order_line_items
  Generating 45,000 line item records...
  Average items per order: 3
  Progress: Complete ✓

Total rows generated: 67,500
Data generation complete - Ready for BigQuery upload
```

### Key UI Elements to Highlight
- Row counters incrementing
- Progress bars for each table
- Sample data snippets showing realistic values
- Total row count summary

---

### PHASE 5: BIGQUERY PROVISIONING (40 seconds)

### Visual
- BigQuery phase activates
- Show GCP project connection
- Display dataset creation and table uploads

### Narration Script
> "**Phase 5: BigQuery Provisioning** - Now the platform connects to Google BigQuery and provisions everything automatically. It creates a dedicated dataset with a unique name, uploads all the generated tables with their data, and configures appropriate permissions. For Nike, this creates a fully functional data warehouse in BigQuery that's immediately queryable."

### Agent Actions (Show in Logs)
```
Connecting to BigQuery project: bq-demos-469816...
Connection established ✓

Creating dataset: nike_demo_gen_abc123...
Dataset created: bq-demos-469816.nike_demo_gen_abc123 ✓

Uploading tables to BigQuery:

  Uploading customers (5,000 rows)...
    Schema: 7 fields
    Upload: Complete ✓
    Query validation: SELECT COUNT(*) FROM customers → 5,000 rows

  Uploading products (2,500 rows)...
    Schema: 8 fields
    Upload: Complete ✓

  Uploading orders (15,000 rows)...
    Schema: 6 fields
    Upload: Complete ✓

  Uploading order_line_items (45,000 rows)...
    Schema: 5 fields
    Upload: Complete ✓

Total tables uploaded: 8
Total rows in dataset: 67,500
Dataset URL: https://console.cloud.google.com/bigquery?project=bq-demos-469816&d=nike_demo_gen_abc123

BigQuery provisioning complete ✓
```

### Key UI Elements to Highlight
- GCP project ID displayed
- Dataset name (unique identifier)
- Table upload progress bars
- Row counts verified
- BigQuery console link appears

---

### PHASE 6: CONVERSATIONAL AGENT CREATION (35 seconds)

### Visual
- CAPI Agent phase activates
- Show Gemini agent configuration
- Display golden queries generation

### Narration Script
> "**Phase 6: Conversational Agent Creation** - This is where the conversational AI comes to life. The platform uses Google's Conversational Analytics API (CAPI) powered by Gemini to create an intelligent agent. The agent is connected to our Nike BigQuery dataset and pre-configured with golden queries - high-value questions that showcase the data insights. These queries are designed to demonstrate powerful analytics capabilities in natural language."

### Agent Actions (Show in Logs)
```
Creating Conversational AI Agent for Nike...

Initializing Gemini agent...
  Model: gemini-1.5-flash
  Agent type: Data Analyst
  Context: Nike athletic retail analytics

Connecting to BigQuery dataset: nike_demo_gen_abc123...
  Tables linked: customers, products, orders, order_line_items, reviews, stores, inventory
  Agent has access to 67,500 rows across 8 tables ✓

Generating golden queries...

  Query 1: "What are our top 5 best-selling products this month?"
    → SQL: SELECT product_name, SUM(quantity) FROM order_line_items
           JOIN products ON... GROUP BY product_name ORDER BY... LIMIT 5
    ✓ Validated

  Query 2: "Show me customer purchase patterns by membership tier"
    → SQL: SELECT membership_tier, AVG(total_amount)...
    ✓ Validated

  Query 3: "What's the geographic distribution of our highest-value customers?"
    → SQL: SELECT location, COUNT(*), AVG(lifetime_value)...
    ✓ Validated

  Query 4: "Compare sales performance across online vs retail channels"
    ✓ Validated

  Query 5: "Which product categories have the highest return rates?"
    ✓ Validated

  Query 6: "Show me inventory levels for limited edition Jordan releases"
    ✓ Validated

Total golden queries: 6
Agent ID: projects/bq-demos-469816/locations/us-central1/agents/nike_agent_xyz789

Agent creation complete ✓
Agent is ready for conversational queries
```

### Key UI Elements to Highlight
- Agent ID displayed
- Golden queries list (6 items)
- Each query shows natural language + SQL preview
- Validation checkmarks
- Agent status: "Active"

---

### PHASE 7: DEMO ASSETS FINALIZATION (25 seconds)

### Visual
- Final phase activates
- Show asset compilation
- Display completion summary

### Narration Script
> "**Phase 7: Demo Assets Finalization** - In the final phase, the platform compiles all the demo materials into a comprehensive assets package. This includes the executive summary, talking track, golden queries, schema documentation, and direct links to the chatbot interface. Everything a Customer Engineer needs to deliver a compelling Nike analytics demo is packaged and ready to present."

### Agent Actions (Show in Logs)
```
Finalizing demo assets for Nike...

Compiling materials:
  ✓ Executive Summary (450 words)
  ✓ Business Challenges (4 items)
  ✓ Talking Track (8 sections)
  ✓ Golden Queries (6 queries with SQL)
  ✓ Schema Documentation (8 tables, 67 fields)
  ✓ Dataset Information (BigQuery links)
  ✓ Agent Configuration (Gemini CAPI settings)

Generating chatbot link:
  URL: https://demo-gen-capi-prod.../chat?agent_id=nike_agent_xyz789&dataset_id=nike_demo_gen_abc123
  Status: Ready ✓

Demo assets complete ✓
Ready for presentation

Total provisioning time: 2m 34s
```

### Key UI Elements to Highlight
- Asset checklist with green checkmarks
- Chatbot URL generated
- Total time displayed
- "View Demo Assets" button appears

---

## 🎬 Scene 6: Demo Assets Page (1.5 minutes)

### Visual
- Provisioning complete (100% progress bar)
- Click **"View Demo Assets"** button
- Navigate to `/demo-assets?jobId={job-id}` page
- Show the complete assets interface

### Narration Script - Overview
> "Now that provisioning is complete, let's explore the Demo Assets page. This is your presentation toolkit - everything you need to deliver an impactful Nike analytics demo is organized here."

### Key UI Elements to Highlight - Header Section
- **Page Title**: "Nike Demo Assets"
- **Status Badge**: "Complete" (green)
- **Metadata Bar**:
  - Customer URL: https://www.nike.com/
  - Dataset ID: `nike_demo_gen_abc123`
  - Agent ID: `nike_agent_xyz789`
  - Completion Time: "2m 34s"
  - Date: "2025-10-07 16:45"

---

### Section 1: Executive Summary

### Visual
- Scroll to Executive Summary card
- Show full text content

### Narration Script
> "The Executive Summary provides a high-level overview of the Nike analytics demo. It explains the business context, the data model, and the value proposition of conversational analytics for athletic retail. This is perfect for opening a presentation or sending to stakeholders before a demo."

### Example Content to Show
```
Nike Analytics Demo - Conversational Insights for Athletic Retail

This demo showcases how Nike can leverage Google's Conversational Analytics API
powered by Gemini to unlock real-time insights from their e-commerce and retail data.

The demo includes:
- Comprehensive data model covering customers, products, orders, inventory, and reviews
- 67,500 rows of realistic synthetic data spanning 2 years of operations
- Natural language query interface for business users
- Pre-configured golden queries demonstrating key analytics use cases

Business Value:
- Enable business users to query data without SQL knowledge
- Reduce time-to-insight from days to seconds
- Uncover hidden patterns in customer behavior and product performance
- Support data-driven decision making across the organization
```

### Key UI Elements to Highlight
- Executive Summary card with scroll
- Word count displayed
- Copy to clipboard button

---

### Section 2: Business Challenges

### Visual
- Scroll to Business Challenges section
- Show 4 challenge cards

### Narration Script
> "The Business Challenges section identifies specific problems that Nike faces - problems that this analytics solution can solve. These are talking points that resonate with business stakeholders."

### Example Challenges to Show
```
1. Understanding Customer Purchase Patterns Across Channels
   How do customers shop differently on mobile vs desktop vs retail stores?
   Which channels drive the highest lifetime value?

2. Optimizing Inventory for Seasonal Product Launches
   How much inventory should we stock for new Jordan releases?
   Which sizes and colors have the highest demand by region?

3. Analyzing Geographic Demand for Limited Edition Releases
   Where should we allocate limited edition products?
   Which markets show the strongest brand loyalty?

4. Improving Product Recommendation Accuracy
   What products do customers buy together?
   How can we personalize recommendations based on purchase history?
```

### Key UI Elements to Highlight
- Challenge cards in grid layout
- Icons for each challenge
- Numbered list format

---

### Section 3: Talking Track

### Visual
- Scroll to Talking Track section
- Show structured presentation flow

### Narration Script
> "The Talking Track provides a complete presentation script. It's structured as a step-by-step walkthrough that guides you through the demo from introduction to closing."

### Example Talking Track to Show
```
NIKE ANALYTICS DEMO - TALKING TRACK

1. INTRODUCTION (30 seconds)
   "Today I'll show you how Nike can empower business users to query data
   using natural language, powered by Google's Conversational Analytics API..."

2. DATA OVERVIEW (45 seconds)
   "We've created a realistic Nike data warehouse with 8 tables covering
   customers, products, orders, and more. Let me show you the schema..."
   [SCREEN: Show BigQuery dataset]

3. CONVERSATIONAL INTERFACE (1 minute)
   "Instead of writing SQL, business users can ask questions in plain English.
   Let's try some examples..."
   [SCREEN: Navigate to chatbot]

4. GOLDEN QUERY DEMO 1: Sales Performance (1 minute)
   "Let's start with a common question: 'What are our top 5 best-selling
   products this month?'"
   [ACTION: Type query, show results with chart]

5. GOLDEN QUERY DEMO 2: Customer Insights (1 minute)
   "Now let's analyze customer behavior: 'Show me purchase patterns by
   membership tier'"
   [ACTION: Type query, show results]

... [Additional sections]

8. CLOSING (30 seconds)
   "As you can see, Nike can democratize data access, reduce time-to-insight,
   and enable data-driven decisions across the organization..."
```

### Key UI Elements to Highlight
- Talking track sections (numbered 1-8)
- Time estimates for each section
- Action items highlighted
- Screen direction notes

---

### Section 4: Golden Queries

### Visual
- Scroll to Golden Queries section
- Show all 6 queries in expandable cards

### Narration Script
> "The Golden Queries are your demo script. These are pre-tested, high-impact questions that showcase the power of conversational analytics. Each query includes the natural language question, the generated SQL, and sample results."

### Example Golden Queries to Show (Expand 2-3)

**Query 1:**
```
Natural Language:
"What are our top 5 best-selling products this month?"

Generated SQL:
SELECT
  p.product_name,
  SUM(oli.quantity) as total_sold,
  SUM(oli.quantity * oli.unit_price) as revenue
FROM order_line_items oli
JOIN products p ON oli.product_id = p.product_id
JOIN orders o ON oli.order_id = o.order_id
WHERE DATE(o.order_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH)
GROUP BY p.product_name
ORDER BY total_sold DESC
LIMIT 5

Sample Results:
| Product Name           | Total Sold | Revenue    |
|------------------------|------------|------------|
| Air Max 90             | 1,245      | $161,850   |
| Jordan 1 Retro High    | 1,103      | $198,540   |
| Air Force 1 '07        | 987        | $98,700    |
| Dunk Low              | 876        | $122,640   |
| Blazer Mid '77        | 834        | $91,740    |
```

**Query 2:**
```
Natural Language:
"Show me customer purchase patterns by membership tier"

Generated SQL:
SELECT
  c.membership_tier,
  COUNT(DISTINCT c.customer_id) as customer_count,
  AVG(c.lifetime_value) as avg_lifetime_value,
  COUNT(o.order_id) as total_orders,
  AVG(o.total_amount) as avg_order_value
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.membership_tier
ORDER BY avg_lifetime_value DESC

Sample Results:
| Membership Tier | Customers | Avg LTV    | Total Orders | Avg Order |
|-----------------|-----------|------------|--------------|-----------|
| Platinum        | 234       | $8,450.50  | 2,340        | $215.30   |
| Gold            | 892       | $4,230.20  | 6,250        | $178.90   |
| Silver          | 1,456     | $2,100.80  | 8,920        | $142.50   |
| Bronze          | 2,418     | $890.40    | 12,100       | $95.20    |
```

### Key UI Elements to Highlight
- 6 golden query cards
- Expand/collapse functionality
- Copy SQL button
- "Try in Chatbot" button for each query
- Syntax highlighting for SQL
- Sample results table

---

### Section 5: Schema Documentation

### Visual
- Scroll to Schema section
- Expand table details (show 2-3 tables)

### Narration Script
> "The Schema Documentation provides complete technical details about the BigQuery data model. Each table shows its fields, data types, relationships, and row counts. This is essential for technical audiences and for understanding what data is available."

### Example Tables to Show

**Table 1: customers**
```
Table: customers
Rows: 5,000
Description: Customer profiles with demographics and lifetime value

Fields:
  customer_id          STRING       Primary Key
  name                 STRING       Customer full name
  email                STRING       Contact email
  location             GEOGRAPHY    Customer location
  membership_tier      STRING       Bronze|Silver|Gold|Platinum
  lifetime_value       FLOAT64      Total revenue from customer
  signup_date          DATE         Account creation date

Relationships:
  → orders.customer_id (One-to-Many)
```

**Table 2: orders**
```
Table: orders
Rows: 15,000
Description: Order transactions across all channels

Fields:
  order_id            STRING       Primary Key
  customer_id         STRING       Foreign Key → customers
  order_date          TIMESTAMP    When order was placed
  total_amount        FLOAT64      Order total value
  channel             STRING       Online|Retail|Mobile
  status              STRING       Pending|Completed|Cancelled

Relationships:
  ← customers.customer_id (Many-to-One)
  → order_line_items.order_id (One-to-Many)
```

### Key UI Elements to Highlight
- 8 table cards in grid
- Expand/collapse table details
- Field list with data types
- Row counts
- Relationship diagrams
- "View in BigQuery" link

---

### Section 6: Action Buttons

### Visual
- Scroll to bottom action bar
- Hover over buttons to show tooltips

### Narration Script
> "At the bottom of the Demo Assets page, we have quick action buttons to access the chatbot interface, view the BigQuery dataset, check the agent configuration, and download all assets for offline use."

### Key UI Elements to Highlight
- **"Open Chatbot Interface"** button (primary CTA)
- **"View in BigQuery"** button (opens BigQuery console)
- **"Agent Configuration"** button (shows CAPI settings)
- **"Download Assets"** button (exports PDF/JSON)
- **"Back to Dashboard"** link

---

## 🎬 Scene 7: Chatbot Interface - Live Demo (2 minutes)

### Visual
- Click **"Open Chatbot Interface"** button
- Navigate to `/chat?agent_id=nike_agent_xyz789&dataset_id=nike_demo_gen_abc123`
- Show the chat interface

### Narration Script - Interface Overview
> "Now for the most exciting part - the live chatbot interface. This is where business users interact with the data using natural language. The interface is clean, intuitive, and requires zero SQL knowledge. Let's demonstrate some queries."

### Key UI Elements to Highlight - Chat Interface
- **Header**:
  - Nike branding (logo extracted from website)
  - "Nike AI Assistant" title
  - Developer Mode toggle (shows SQL)
  - Reconfigure button
  - Sign Out button

- **Chat Area**:
  - Welcome message
  - Empty state with suggestions
  - Message bubbles (user vs assistant)
  - Chart visualizations (Vega-Lite)
  - SQL query display (in dev mode)

- **Input Area**:
  - Text input field with placeholder "Ask a question about Nike data..."
  - Send button
  - Suggested queries chips (golden queries)

---

### Demo Query 1: Top Products

### Visual
- Type or click suggested query: "What are our top 5 best-selling products this month?"
- Show loading state
- Display results with bar chart

### Narration Script
> "Let's ask our first question: 'What are our top 5 best-selling products this month?' Watch as the AI agent processes this natural language query, generates the appropriate SQL, queries BigQuery, and returns results with a visualization."

### Expected Response
```
USER: What are our top 5 best-selling products this month?

ASSISTANT (with loading animation...):
Based on the data, here are Nike's top 5 best-selling products this month:

1. Air Max 90 - 1,245 units sold ($161,850 revenue)
2. Jordan 1 Retro High - 1,103 units sold ($198,540 revenue)
3. Air Force 1 '07 - 987 units sold ($98,700 revenue)
4. Dunk Low - 876 units sold ($122,640 revenue)
5. Blazer Mid '77 - 834 units sold ($91,740 revenue)

The Jordan 1 Retro High generated the highest revenue despite not having
the highest unit sales, indicating a premium price point.

[BAR CHART VISUALIZATION showing products on X-axis, units sold on Y-axis]
```

### Key UI Elements to Highlight
- User message bubble (right-aligned, blue)
- Loading indicator (animated dots)
- Assistant response (left-aligned, gray)
- Bar chart appears (interactive, can hover)
- Developer Mode shows SQL query
- Copy button for response

---

### Demo Query 2: Customer Segmentation

### Visual
- Type: "Show me customer purchase patterns by membership tier"
- Show loading
- Display results with pie chart or grouped bar chart

### Narration Script
> "Let's try a more analytical question: 'Show me customer purchase patterns by membership tier.' This demonstrates how the AI can join multiple tables and provide business insights."

### Expected Response
```
USER: Show me customer purchase patterns by membership tier

ASSISTANT:
Here's a breakdown of Nike customer purchase behavior across membership tiers:

📊 Customer Distribution:
- Platinum (234 customers): Average Lifetime Value $8,450.50
  • Avg Order Value: $215.30
  • Total Orders: 2,340 (10 orders per customer)

- Gold (892 customers): Average Lifetime Value $4,230.20
  • Avg Order Value: $178.90
  • Total Orders: 6,250 (7 orders per customer)

- Silver (1,456 customers): Average Lifetime Value $2,100.80
  • Avg Order Value: $142.50
  • Total Orders: 8,920 (6 orders per customer)

- Bronze (2,418 customers): Average Lifetime Value $890.40
  • Avg Order Value: $95.20
  • Total Orders: 12,100 (5 orders per customer)

Key Insight: Platinum members represent only 5% of customers but generate
35% of total revenue. Consider exclusive offers to convert Gold members.

[GROUPED BAR CHART showing membership tiers vs avg LTV]
```

### Key UI Elements to Highlight
- Formatted response with emojis and bullet points
- Grouped bar chart visualization
- Key insight highlighted
- Developer Mode shows complex JOIN SQL

---

### Demo Query 3: Geographic Analysis

### Visual
- Type: "What's the geographic distribution of our highest-value customers?"
- Show loading
- Display results with map or geographic chart

### Narration Script
> "For our third demo, let's ask a geographic question: 'What's the geographic distribution of our highest-value customers?' This shows how the AI can work with BigQuery's GEOGRAPHY data types."

### Expected Response
```
USER: What's the geographic distribution of our highest-value customers?

ASSISTANT:
Here are the top 10 locations with the highest concentration of valuable
Nike customers (top 25% by lifetime value):

1. 🌎 Portland, OR - 156 customers (Avg LTV: $9,240)
2. 🌎 Los Angeles, CA - 142 customers (Avg LTV: $8,890)
3. 🌎 New York, NY - 134 customers (Avg LTV: $8,650)
4. 🌎 Chicago, IL - 98 customers (Avg LTV: $8,420)
5. 🌎 Seattle, WA - 87 customers (Avg LTV: $8,320)
6. 🌎 Miami, FL - 76 customers (Avg LTV: $7,980)
7. 🌎 Boston, MA - 72 customers (Avg LTV: $7,850)
8. 🌎 Atlanta, GA - 68 customers (Avg LTV: $7,720)
9. 🌎 San Francisco, CA - 65 customers (Avg LTV: $7,690)
10. 🌎 Denver, CO - 61 customers (Avg LTV: $7,580)

Recommendation: Portland and West Coast markets show the strongest
customer loyalty. Consider exclusive product launches in these regions.

[MAP VISUALIZATION showing customer concentration by location]
```

### Key UI Elements to Highlight
- Geographic visualization (if available)
- Location-based insights
- Emoji usage for visual appeal

---

### Demo Query 4: Open-Ended Question

### Visual
- Type a custom question not in golden queries:
  "Which products have the best reviews but low sales?"
- Show AI processing
- Display creative response

### Narration Script
> "Here's where it gets really powerful. Let's ask a question that's NOT in the golden queries - something completely open-ended: 'Which products have the best reviews but low sales?' Watch as the AI figures out how to answer this on its own."

### Expected Response
```
USER: Which products have the best reviews but low sales?

ASSISTANT:
Great question! I found several highly-rated Nike products that are
underperforming in sales - these could be hidden gems worth promoting:

🌟 High Rating + Low Sales:
1. Nike Zoom Pegasus Trail 4 GORE-TEX
   • Average Rating: 4.8/5 (156 reviews)
   • Units Sold: 234 (Bottom 10%)
   • Price: $159.99
   • Category: Trail Running

2. Nike ACG Mountain Fly Low
   • Average Rating: 4.7/5 (89 reviews)
   • Units Sold: 198 (Bottom 15%)
   • Price: $139.99
   • Category: ACG Lifestyle

3. Nike Air Zoom Alphafly NEXT%
   • Average Rating: 4.9/5 (203 reviews)
   • Units Sold: 312 (Bottom 20%)
   • Price: $275.99
   • Category: Performance Running

Analysis: These specialized products have exceptional customer satisfaction
but low awareness. Consider:
- Featured placement on homepage
- Influencer partnerships with trail runners
- Educational content about technical features

[TABLE showing Product | Rating | Sales Rank | Potential]
```

### Key UI Elements to Highlight
- AI handles non-golden query successfully
- Creative problem-solving (joins reviews + sales data)
- Actionable recommendations
- Demonstrates true conversational intelligence

---

### Developer Mode View

### Visual
- Toggle **Developer Mode** switch ON
- Re-run one of the previous queries
- Show SQL query alongside results

### Narration Script
> "For technical audiences, we can enable Developer Mode to see exactly what SQL the AI is generating. This transparency helps data engineers understand and trust the system."

### Developer Mode Display
```
🔧 DEVELOPER MODE ACTIVE

Query: "What are our top 5 best-selling products this month?"

Generated SQL:
------------------------------------------------------
SELECT
  p.product_name,
  SUM(oli.quantity) AS total_sold,
  SUM(oli.quantity * oli.unit_price) AS revenue,
  COUNT(DISTINCT o.order_id) AS num_orders
FROM
  `bq-demos-469816.nike_demo_gen_abc123.order_line_items` oli
INNER JOIN
  `bq-demos-469816.nike_demo_gen_abc123.products` p
  ON oli.product_id = p.product_id
INNER JOIN
  `bq-demos-469816.nike_demo_gen_abc123.orders` o
  ON oli.order_id = o.order_id
WHERE
  DATE(o.order_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH)
GROUP BY
  p.product_name
ORDER BY
  total_sold DESC
LIMIT 5;
------------------------------------------------------

Execution Time: 1.24s
Rows Scanned: 45,000
Bytes Processed: 2.3 MB

[RESULTS DISPLAY with chart]
```

### Key UI Elements to Highlight
- SQL syntax highlighting
- Fully qualified table names
- Execution statistics
- Copy SQL button
- "Run in BigQuery" button

---

## 🎬 Scene 8: Analytics Dashboard (45 seconds)

### Visual
- Navigate to `/analytics-dashboard`
- Show aggregate analytics

### Narration Script
> "Finally, the Analytics Dashboard provides a bird's-eye view of all your provisioning activity. See success rates, track performance metrics, and monitor system health across all your demos."

### Key UI Elements to Highlight
- Total jobs provisioned
- Success rate percentage
- Average provisioning time
- Most popular customer URLs
- Phase performance breakdown
- Agent model usage stats
- Time-series charts

---

## 🎬 Scene 9: Closing & Summary (30 seconds)

### Visual
- Return to CE Dashboard
- Show list of completed provisions
- Highlight Nike demo in the list

### Narration Script
> "And that's the complete CAPI Demo Generator workflow. In just 2-3 minutes, we transformed Nike.com into a fully functional conversational analytics demo with realistic data, intelligent querying, and presentation-ready assets. Customer Engineers can now provision demos for any customer in minutes instead of days, with AI handling all the complex work automatically. The platform supports both quick default setups and advanced customization through Crazy Frog Mode, making it perfect for demos ranging from quick proofs-of-concept to comprehensive enterprise showcases."

### Key UI Elements to Highlight
- Dashboard showing multiple completed demos
- Status indicators (Complete, Running, Failed)
- Quick actions menu on each row
- Ability to restart or duplicate demos
- User-scoped data (only shows your demos when signed in)

---

## 📊 Technical Architecture Summary (for advanced viewers)

### System Components
```
Frontend Stack:
- React + TypeScript + Vite
- TailwindCSS + shadcn/ui components
- Firebase Authentication (Google OAuth)
- React Router for navigation

Backend Stack:
- FastAPI (Python)
- Firebase Admin SDK for auth verification
- Firestore for user-scoped job persistence
- Pydantic for data validation

AI/ML Stack:
- Research Agent: Crawls websites with BeautifulSoup/Playwright
- Demo Story Agent: Gemini 1.5 Flash for narrative generation
- Data Modeling Agent: Claude 3.5 Sonnet for schema design
- Synthetic Data: Gretel SDK for realistic data generation
- CAPI Agent: Gemini + Conversational Analytics API

Infrastructure:
- Google Cloud Run (containerized deployment)
- BigQuery (data warehouse)
- Cloud Build (CI/CD)
- Firebase (auth + Firestore)
```

### Data Flow
```
1. User enters URL → Frontend sends POST /api/provision/start
2. Backend creates job ID → Firestore saves job metadata (if authenticated)
3. Orchestrator launches 7 agents sequentially
4. Each agent updates job state → Real-time logs to frontend via SSE
5. Final agent returns demo assets → Saved to Firestore
6. User accesses chatbot → CAPI agent queries BigQuery
7. Results + visualizations → Rendered in frontend
```

---

## 🎥 Video Production Notes

### Recommended Camera Angles
- **Full screen captures** for dashboard and interface views
- **Close-up zooms** for specific UI elements when highlighting features
- **Smooth transitions** between pages (use fade or slide effects)
- **Mouse cursor highlighting** for important clicks and interactions

### Voiceover Tips
- Speak at moderate pace (conversational, not rushed)
- Pause for 2-3 seconds when showing complex visualizations
- Use enthusiastic but professional tone
- Emphasize key numbers (e.g., "in just 2 minutes", "67,500 rows")

### Visual Effects
- **Progress indicators**: Show animated progress bars clearly
- **Highlighting**: Use yellow highlights or arrows for important UI elements
- **Code snippets**: Zoom in slightly when showing SQL
- **Charts**: Allow 3-5 seconds for viewers to absorb data visualizations

### Background Music (Optional)
- Soft, upbeat, tech-focused instrumental
- Keep volume low (20-30%) so it doesn't overpower narration
- Fade out during critical explanation moments

### Annotations/Callouts
- Add text overlays for key technical terms on first mention
- Use arrows or circles to highlight specific buttons/fields
- Display tooltips or info boxes for advanced concepts
- Include timestamp markers for different sections

---

## 📋 Pre-Production Checklist

### Before Recording
- [ ] Clear browser cache and cookies
- [ ] Sign in to `@google.com` account
- [ ] Prepare 2-3 test customer URLs (Nike, Stripe, Airbnb)
- [ ] Set screen resolution to 1920x1080
- [ ] Close unnecessary browser tabs and applications
- [ ] Test microphone audio levels
- [ ] Disable system notifications
- [ ] Have script open on second monitor

### Test Run
- [ ] Complete one full provision flow before recording
- [ ] Verify all golden queries work in chatbot
- [ ] Check that charts render correctly
- [ ] Confirm BigQuery links open properly
- [ ] Test Developer Mode toggle
- [ ] Ensure sign in/out works smoothly

### Recording Setup
- [ ] Use screen recording software (OBS, Camtasia, Loom)
- [ ] Record at 60fps for smooth transitions
- [ ] Enable system audio for any UI sounds
- [ ] Use high-quality microphone
- [ ] Record narration separately or live (your choice)
- [ ] Have water nearby for voiceover hydration

---

## 🎬 Post-Production Steps

### Editing
1. Trim dead air and long pauses
2. Add transitions between scenes (fade/slide)
3. Insert text overlays for section titles
4. Add arrows/highlights to emphasize UI elements
5. Adjust audio levels for consistency
6. Add background music (if desired)
7. Include intro/outro screens with branding

### Quality Check
- [ ] Review entire video for audio/video sync
- [ ] Check that all text is readable
- [ ] Verify chart visualizations are clear
- [ ] Confirm no sensitive data is visible
- [ ] Test playback at different speeds
- [ ] Get peer review feedback

### Export Settings
- **Resolution**: 1920x1080 (1080p)
- **Frame Rate**: 60fps or 30fps
- **Format**: MP4 (H.264 codec)
- **Bitrate**: 8-12 Mbps for high quality
- **Audio**: AAC 256kbps

### Distribution
- Upload to YouTube (unlisted or public)
- Share with internal team for feedback
- Add to product documentation
- Include in customer presentations
- Post on social media (if approved)

---

## 📝 Supplementary Materials

### Create These Additional Assets
1. **One-Page Overview PDF**: Quick reference showing the 7 phases
2. **FAQ Document**: Common questions about provisioning
3. **Troubleshooting Guide**: What to do if a provision fails
4. **API Documentation**: For developers who want to integrate
5. **Best Practices Guide**: Tips for choosing good customer URLs
6. **Demo Script Template**: Reusable template for presentations

---

## 🎯 Success Metrics

After creating the video, track:
- View count and watch time
- Drop-off points (where people stop watching)
- User feedback and questions
- Internal adoption rate (CEs using the platform)
- Demo conversion rates (demos leading to sales)

---

## 🚀 Next Steps

1. Record pilot video with one complete demo flow (Nike)
2. Get feedback from 3-5 Customer Engineers
3. Iterate on script and visual style
4. Create full production video
5. Develop supplementary training materials
6. Launch internal training program
7. Measure adoption and impact

---

**Document Version**: 1.0
**Last Updated**: 2025-10-07
**Author**: CAPI Demo Generator Team
**Contact**: For questions or feedback on this guide, contact the development team

---

## Appendix A: Keyboard Shortcuts Reference

For smoother screen recording, use these shortcuts:

| Action | Shortcut |
|--------|----------|
| Start/Stop Recording | Varies by software |
| Toggle Developer Mode | Click switch |
| Copy SQL | Click copy button |
| Navigate to Dashboard | Alt + D |
| Open Chat | Click "Open Chatbot" |
| Sign Out | Top-right dropdown |

---

## Appendix B: Sample Customer URLs for Demos

Use these URLs for different demo scenarios:

1. **Retail/E-commerce**: Nike.com, Zappos.com, REI.com
2. **SaaS/Technology**: Stripe.com, Shopify.com, Slack.com
3. **Travel/Hospitality**: Airbnb.com, Marriott.com
4. **Financial Services**: Robinhood.com, Chime.com
5. **Healthcare**: Teladoc.com, Oscar.com
6. **B2B**: Salesforce.com, HubSpot.com

Choose URLs based on your target audience's industry.

---

**End of Video Creation Guide**

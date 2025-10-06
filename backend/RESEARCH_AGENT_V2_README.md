# Research Agent V2 - Enhanced Intelligence Gathering

## 🎯 Overview

**Research Agent V2** is an advanced, AI-powered business intelligence agent that acts as a **Data Architect Detective**. It deeply analyzes companies by:

- 🕸️ **Intelligent Website Crawling** - Explores entire website structure
- 📰 **Blog/News Analysis** - Discovers technology stack and projects
- 🔗 **LinkedIn Integration** - Analyzes company posts and announcements
- 📺 **YouTube Channel Research** - Extracts insights from video content
- 🏗️ **Data Architecture Inference** - Uses AI to infer complete data ecosystems

## 🆕 What's New in V2?

| Feature | V1 | V2 |
|---------|----|----|
| Website Analysis | Single page scrape | Full site crawl (sitemap + navigation) |
| Content Depth | Homepage only | 50+ pages across categories |
| Blog Intelligence | ❌ | ✅ Tech stack, projects, use cases |
| Social Media | ❌ | ✅ LinkedIn + YouTube |
| Data Architecture | Basic entities | Complete warehouse design, tech stack, scale estimates |
| Analysis Engine | Claude 4.5 | Claude 4.5 with multi-source synthesis |

## 📁 Architecture

```
backend/
├── agentic_service/
│   ├── agents/
│   │   ├── research_agent.py         # V1 (unchanged)
│   │   └── research_agent_v2.py      # V2 (new) ⭐
│   │
│   ├── tools/
│   │   ├── web_research.py           # Shared by both
│   │   ├── v2_intelligent_crawler.py # V2 crawler
│   │   ├── v2_multi_source.py        # Blog/LinkedIn/YouTube
│   │   └── v2_data_architect.py      # AI inference engine
│   │
│   └── utils/
│       ├── vertex_llm_client.py      # Shared (Claude via Vertex)
│       └── prompt_templates.py       # Extended with V2 prompts
│
├── test_research_agent.py            # V1 test (unchanged)
└── test_research_agent_v2.py         # V2 test (isolated) ⭐
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Note**: Only `lxml` was added. All other dependencies already exist!

### 2. Set Environment Variables

```bash
# Required (already set in your project)
export PROJECT_ID="bq-demos-469816"
export DEVSHELL_PROJECT_ID="bq-demos-469816"

# Optional: For YouTube video analysis
export YOUTUBE_API_KEY="your-youtube-api-key"
```

### 3. Run Isolated Test

```bash
# Basic test with Nike
python test_research_agent_v2.py --url https://www.nike.com

# Custom configuration
python test_research_agent_v2.py \
  --url https://www.shopify.com \
  --max-pages 100 \
  --max-depth 4 \
  --output shopify_analysis.json

# Disable specific features
python test_research_agent_v2.py \
  --url https://www.airbnb.com \
  --no-blog \
  --no-linkedin
```

### 4. View Results

Results are automatically saved to:
```
research_v2_results_{domain}_{timestamp}.json
```

## 📊 Output Format

```json
{
  "metadata": {
    "test_url": "https://www.nike.com",
    "timestamp": "2025-10-05T14:30:00",
    "duration_seconds": 45.2,
    "configuration": {...}
  },

  "business_analysis": {
    "company_name": "Nike",
    "industry": "Retail & E-commerce",
    "business_domain": "Athletic footwear and apparel",
    "key_entities": [
      {
        "name": "customers",
        "description": "Nike members and shoppers",
        "importance": "high",
        "relationships": ["orders", "memberships", "workouts"]
      }
    ],
    "technologies_detected": [
      "BigQuery", "Google Analytics", "React", "AWS"
    ],
    "primary_use_cases": [
      "Customer segmentation and personalization",
      "Inventory optimization across retail locations",
      "Member engagement analytics"
    ]
  },

  "v2_intelligence": {
    "website_crawl": {
      "pages_crawled": 47,
      "categories": {
        "product": 15,
        "blog": 8,
        "about": 3
      }
    },

    "blog_data": {
      "found": true,
      "articles_count": 18,
      "technologies_mentioned": ["React", "Node.js", "BigQuery"],
      "topics": ["sustainability", "innovation", "athlete-stories"]
    },

    "data_architecture": {
      "core_entities": [
        {
          "table_name": "customers",
          "entity_type": "dimension",
          "estimated_rows": "50M+",
          "key_fields": [
            {"name": "customer_id", "type": "INT64"},
            {"name": "email", "type": "STRING"},
            {"name": "member_tier", "type": "STRING"}
          ]
        }
      ],

      "warehouse_design": {
        "architecture_pattern": "star",
        "fact_tables": [
          {
            "name": "fact_orders",
            "grain": "One row per order line item",
            "measures": ["quantity", "revenue", "discount"],
            "estimated_rows": "500M+"
          }
        ],
        "dimension_tables": [
          {
            "name": "dim_customer",
            "type": "SCD Type 2"
          },
          {
            "name": "dim_product",
            "type": "SCD Type 1"
          }
        ]
      },

      "tech_stack": {
        "data_warehouse": {
          "platform": "BigQuery",
          "rationale": "Google Cloud ecosystem, scale for retail analytics"
        },
        "cloud_provider": {
          "primary": "GCP",
          "rationale": "Based on BigQuery and Google Analytics usage"
        }
      },

      "scale_estimates": {
        "daily_data_volume_gb": 500,
        "total_warehouse_size_tb": 20,
        "concurrent_users": 200
      }
    }
  }
}
```

## 🔧 Configuration Options

### Agent Initialization

```python
from agentic_service.agents.research_agent_v2 import CustomerResearchAgentV2

agent = CustomerResearchAgentV2(
    max_pages=50,          # Maximum pages to crawl (default: 50)
    max_depth=3,           # Maximum crawl depth (default: 3)
    enable_blog=True,      # Scrape blog/news section
    enable_linkedin=True,  # Find LinkedIn company page
    enable_youtube=True    # Find YouTube channel
)
```

### Command-Line Options

```bash
python test_research_agent_v2.py --help

Options:
  --url URL              Website URL to analyze (required)
  --max-pages N          Maximum pages to crawl (default: 50)
  --max-depth N          Maximum crawl depth (default: 3)
  --no-blog              Disable blog scraping
  --no-linkedin          Disable LinkedIn scraping
  --no-youtube           Disable YouTube scraping
  --output FILE          Output JSON file path
```

## 🧪 Testing Examples

### Example 1: E-commerce Platform
```bash
python test_research_agent_v2.py --url https://www.shopify.com
```

**Expected Output:**
- Core entities: merchants, stores, products, orders, customers
- Warehouse: Multi-tenant architecture, SaaS metrics
- Tech stack: Ruby, PostgreSQL, MySQL, Kafka, BigQuery
- Use cases: Merchant analytics, revenue reporting, fraud detection

### Example 2: SaaS Company
```bash
python test_research_agent_v2.py --url https://www.salesforce.com
```

**Expected Output:**
- Core entities: accounts, contacts, opportunities, leads
- Warehouse: CRM analytics, sales forecasting
- Tech stack: Multi-cloud, custom data platform
- Use cases: Sales pipeline analysis, customer 360

### Example 3: Marketplace
```bash
python test_research_agent_v2.py --url https://www.airbnb.com
```

**Expected Output:**
- Core entities: hosts, guests, listings, bookings, reviews
- Warehouse: Two-sided marketplace metrics
- Tech stack: AWS, Airflow, Presto/Druid
- Use cases: Host performance, dynamic pricing, trust & safety

## 📈 Performance Benchmarks

| Metric | Typical Value |
|--------|---------------|
| Execution Time | 30-60 seconds |
| Pages Crawled | 30-50 pages |
| Content Analyzed | 50,000-100,000 words |
| Entities Identified | 15-30 core entities |
| Fact Tables Designed | 5-15 tables |
| Dimension Tables | 8-20 tables |

## 🔄 Integration with Existing Pipeline

### Option 1: Swap in demo_orchestrator.py

```python
# In demo_orchestrator.py
from agentic_service.agents.research_agent_v2 import CustomerResearchAgentV2

# Replace this:
# from agentic_service.agents.research_agent import CustomerResearchAgent
# research_agent = CustomerResearchAgent()

# With this:
research_agent = CustomerResearchAgentV2(
    max_pages=50,
    max_depth=3,
    enable_blog=True,
    enable_linkedin=True,
    enable_youtube=True
)
```

### Option 2: Use Both (A/B Testing)

```python
# Use V1 for fast iteration
if os.getenv('USE_V2_RESEARCH') == 'true':
    research_agent = CustomerResearchAgentV2()
else:
    research_agent = CustomerResearchAgent()  # V1
```

## 🛠️ Advanced Features

### Custom Crawler Priorities

```python
# In v2_intelligent_crawler.py, customize:
self.priority_keywords = [
    'product', 'api', 'documentation',
    'pricing', 'enterprise', 'platform'
]

self.skip_patterns = [
    'login', 'terms', 'privacy'
]
```

### Enable JavaScript Rendering (Optional)

For JavaScript-heavy sites, uncomment in `requirements.txt`:
```txt
playwright==1.40.0
```

Then install Playwright browsers:
```bash
playwright install chromium
```

## 🐛 Troubleshooting

### Issue: "No blog section found"
**Solution**: Some sites use non-standard URLs. Manually check:
- Check `/resources`, `/insights`, `/learning-center`
- Update `blog_patterns` in `v2_multi_source.py`

### Issue: "LinkedIn scraping requires authentication"
**Solution**: LinkedIn's public API is restricted. For full access:
- Use LinkedIn's official API with authentication
- Or rely on finding the LinkedIn URL only (current behavior)

### Issue: "YouTube API quota exceeded"
**Solution**:
- YouTube API has daily quotas
- Set `enable_youtube=False` or get API key from Google Cloud Console

### Issue: Crawling takes too long
**Solution**:
- Reduce `max_pages` (try 20-30)
- Reduce `max_depth` (try 2)
- Disable social media scrapers

## 📝 What V2 Does NOT Change

✅ **V1 Agent** - Completely untouched, still works
✅ **V1 Tests** - `test_research_agent.py` unchanged
✅ **Orchestrator** - Uses V1 by default
✅ **Other Agents** - No impact on data modeling, infrastructure, etc.
✅ **Frontend** - No changes
✅ **API** - No changes

## 🎓 Key Differences: V1 vs V2

| Aspect | V1 | V2 |
|--------|----|----|
| **Speed** | ~5-10 seconds | ~30-60 seconds |
| **Depth** | Surface-level | Comprehensive |
| **Entities** | 5-10 | 15-30 |
| **Architecture** | Basic schema | Full warehouse design + tech stack |
| **Use Case** | Quick demos | Enterprise demos, sales engineering |
| **Best For** | Rapid prototyping | Customer presentations |

## 🚦 When to Use Which?

### Use V1 When:
- Quick iteration and testing
- Simple demo scenarios
- Time-constrained environments
- Basic entity identification is enough

### Use V2 When:
- Customer-facing demos
- Complex business models
- Need detailed architecture insights
- Showcasing AI-powered analysis
- Sales engineering presentations

## 📞 Support

For questions or issues:
1. Check this README
2. Review test output logs
3. Examine generated JSON files
4. Check individual tool modules for debugging

## 🎉 Success Metrics

After running V2, you should see:

✅ **Business Analysis**: Accurate company profile
✅ **Website Crawl**: 30-50 pages across categories
✅ **Blog Intelligence**: Technologies and projects identified
✅ **Data Architecture**: 15-30 entities with relationships
✅ **Warehouse Design**: Star/snowflake schema with fact + dim tables
✅ **Tech Stack**: Inferred cloud provider, databases, tools
✅ **Scale Estimates**: Realistic data volumes and growth

---

**Built with ❤️ using Claude 4.5 Sonnet via Vertex AI**

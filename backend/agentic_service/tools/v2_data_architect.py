"""
Data Architecture Inference Engine for Research Agent V2.
Analyzes business intelligence and infers complete data ecosystem.
"""
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class DataArchitectureAnalyzer:
    """
    AI-powered analyzer that infers data architecture from business intelligence.
    Acts as a Data Architect examining a company's data ecosystem.
    """

    def __init__(self, llm_client):
        """
        Initialize analyzer.

        Args:
            llm_client: VertexLLMClient instance (Claude or Gemini)
        """
        self.llm_client = llm_client

    async def infer_architecture(self, research_data: Dict) -> Dict:
        """
        Infer complete data architecture from research data.

        Args:
            research_data: Combined research data from all sources

        Returns:
            Dict with inferred data architecture
        """
        logger.info("Starting data architecture inference...")

        # Build comprehensive analysis prompt
        prompt = self._build_inference_prompt(research_data)

        # Use Claude to perform deep analysis
        try:
            response = await self.llm_client.generate_with_retry(
                prompt=prompt,
                temperature=0.3,  # Lower for more consistent analysis
                max_output_tokens=16384,  # Increased from 8192 to allow comprehensive analysis
                system_instruction=(
                    "You are a Principal Data Architect and Solutions Architect with 15+ years of experience "
                    "designing enterprise data platforms. You excel at reverse-engineering data architectures "
                    "by analyzing business models, inferring database schemas, and identifying data flows. "
                    "You understand both structured and unstructured data, and how to leverage modern data warehouses "
                    "like BigQuery for ML/AI on unstructured data (images, text, videos). "
                    "You think like both a data engineer and business analyst. "
                    "Always return valid JSON only, with comprehensive technical detail."
                )
            )

            architecture = self.llm_client.parse_json_response(response)
            logger.info("Data architecture inference complete")

            return architecture

        except Exception as e:
            logger.error(f"Architecture inference failed: {e}", exc_info=True)
            # Return basic structure on failure
            return {
                'error': str(e),
                'entities': [],
                'warehouse_design': {},
                'tech_stack': {}
            }

    def _build_inference_prompt(self, research_data: Dict) -> str:
        """Build comprehensive prompt for architecture inference."""

        # Extract key information
        business_info = research_data.get('business_analysis', {})
        crawl_data = research_data.get('website_crawl', {})
        blog_data = research_data.get('blog_data', {})
        jobs_data = research_data.get('jobs_data', {})

        # Build prompt sections
        prompt = f"""# DATA ARCHITECTURE INFERENCE TASK

You are analyzing a company to infer their complete data ecosystem as a Data Architect would.

## COMPANY INTELLIGENCE GATHERED

### Business Overview
- **Company**: {business_info.get('company_name', 'Unknown')}
- **Industry**: {business_info.get('industry', 'Unknown')}
- **Business Model**: {business_info.get('business_domain', 'Unknown')}
- **Company Type**: {business_info.get('company_type', 'Unknown')}

### Website Analysis
- **Pages Crawled**: {crawl_data.get('pages_crawled', 0)}
- **Categories Found**: {', '.join(crawl_data.get('categories', {}).keys())}

### Key Business Entities Identified
{self._format_entities(business_info.get('key_entities', []))}

### Primary Use Cases
{self._format_list(business_info.get('primary_use_cases', []))}

### Technologies Detected (from Blog/Content)
{self._format_list(blog_data.get('technologies_mentioned', []))}

### Products/Services Offered
{self._format_list(business_info.get('key_products_services', []))}

### ⭐ ACTUAL TECH STACK (from Job Postings)
{self._format_job_tech_stack(jobs_data)}

## YOUR TASK

As a Principal Data Architect, infer and design this company's complete data ecosystem:

### 1. DATABASE ENTITIES & SCHEMA
For each major entity, provide:
- Table name (database naming convention)
- Estimated row count/scale
- Key fields with data types
- Relationships to other tables
- Data update frequency

### 2. DATA WAREHOUSE ARCHITECTURE
Design a modern data warehouse following Kimball or Inmon methodology:
- **Fact Tables**: Transactional/event data with measures
- **Dimension Tables**: Descriptive attributes (SCD Type 1/2 where appropriate)
- **Star/Snowflake Schema**: How tables relate
- **Data Mart Layers**: Organized by business domain

### 3. TECHNOLOGY STACK INFERENCE
Infer likely technologies for:
- **Operational Databases**: OLTP systems (PostgreSQL, MySQL, MongoDB, etc.)
- **Data Warehouse**: OLAP system (BigQuery, Snowflake, Redshift, etc.)
- **Streaming/Real-time**: Kafka, Pub/Sub, Kinesis
- **ETL/ELT**: Airflow, dbt, Fivetran, Talend
- **Analytics Tools**: Looker, Tableau, Power BI, custom
- **Cloud Provider**: AWS, GCP, Azure (with rationale)
- **Data Lake**: S3, GCS, ADLS (if applicable)

### 4. DATA FLOWS & PIPELINES
Map the data journey:
- **Data Sources**: Where data originates (apps, APIs, third-party)
- **Ingestion Methods**: Batch, streaming, CDC, API polling
- **Transformation Layers**: Raw → Staged → Curated → Analytics
- **Consumption Patterns**: How data is used (BI, ML, APIs)

### 5. ANALYTICS USE CASES
Specific analytics this company likely needs:
- Customer analytics (segmentation, churn, LTV)
- Product analytics (usage, adoption, performance)
- Operational analytics (efficiency, monitoring)
- Financial analytics (revenue, forecasting)
- Predictive analytics (ML use cases)

### 6. DATA GOVERNANCE & QUALITY
- PII/sensitive data considerations
- Data retention policies
- Data quality checks
- Compliance requirements (GDPR, CCPA, etc.)

### 7. SCALE ESTIMATES
- Daily data volume (GB/TB)
- Total data warehouse size
- Query patterns and concurrency
- Growth projections

### 8. UNSTRUCTURED DATA ANALYSIS ⭐ NEW
Analyze unstructured data opportunities:
- **Types of Unstructured Data**: Images, videos, text (messages, reviews, descriptions), documents, audio
- **Current Storage**: Where is it likely stored today (S3, GCS, cloud storage)
- **Business Value**: What insights can be extracted (image classification, sentiment, content moderation, search)
- **BigQuery Integration**: How to leverage BigQuery ML, Vector Search, Vertex AI integration
- **ML/AI Use Cases**: Computer vision, NLP, recommendation engines
- **Data Lake Architecture**: Raw unstructured → Processed/enriched → Feature store
- **Metadata Extraction**: How to make unstructured data queryable
- **Cost Optimization**: Storage tiers, lifecycle policies

## OUTPUT FORMAT (MUST BE VALID JSON)

```json
{{
  "company_profile": {{
    "name": "...",
    "industry": "...",
    "data_maturity_level": "beginner|intermediate|advanced|expert"
  }},

  "core_entities": [
    {{
      "table_name": "customers",
      "entity_type": "dimension|fact",
      "description": "Customer master data",
      "estimated_rows": "1M-10M",
      "update_frequency": "real-time|hourly|daily|weekly",
      "key_fields": [
        {{"name": "customer_id", "type": "INT64", "description": "Primary key"}},
        {{"name": "email", "type": "STRING", "description": "Customer email"}},
        {{"name": "created_at", "type": "TIMESTAMP", "description": "Account creation date"}}
      ],
      "relationships": [
        {{"related_table": "orders", "relationship_type": "one-to-many", "join_key": "customer_id"}}
      ],
      "data_sensitivity": "PII|confidential|public"
    }}
  ],

  "warehouse_design": {{
    "architecture_pattern": "star|snowflake|data_vault|hybrid",
    "fact_tables": [
      {{
        "name": "fact_orders",
        "grain": "One row per order line item",
        "measures": ["quantity", "unit_price", "total_amount", "discount"],
        "dimensions": ["customer_key", "product_key", "date_key", "store_key"],
        "estimated_rows": "10M+",
        "partitioning": "PARTITION BY DATE(order_date)"
      }}
    ],
    "dimension_tables": [
      {{
        "name": "dim_customer",
        "type": "SCD Type 2",
        "attributes": ["customer_id", "name", "segment", "tier"],
        "estimated_rows": "1M"
      }}
    ],
    "data_marts": [
      {{
        "name": "customer_analytics_mart",
        "purpose": "Customer behavior and segmentation",
        "source_tables": ["fact_orders", "dim_customer", "fact_web_events"]
      }}
    ]
  }},

  "tech_stack": {{
    "operational_databases": [
      {{
        "type": "PostgreSQL|MySQL|MongoDB|etc",
        "purpose": "Transactional system for...",
        "rationale": "Why this technology fits",
        "estimated_size_gb": 500
      }}
    ],
    "data_warehouse": {{
      "platform": "BigQuery|Snowflake|Redshift",
      "rationale": "Why chosen (scale, cost, features)",
      "estimated_size_tb": 5,
      "query_concurrency": "low|medium|high"
    }},
    "streaming": {{
      "platform": "Kafka|Pub/Sub|Kinesis|None",
      "use_cases": ["real-time event tracking", "CDC"],
      "estimated_throughput": "1000 events/sec"
    }},
    "etl_orchestration": {{
      "tools": ["Airflow", "dbt", "Fivetran"],
      "pipeline_count_estimate": 50,
      "schedule_frequency": "hourly|daily|real-time"
    }},
    "analytics_tools": ["Looker", "Tableau", "Custom dashboards"],
    "cloud_provider": {{
      "primary": "AWS|GCP|Azure",
      "rationale": "Based on technologies detected and industry patterns"
    }},
    "data_lake": {{
      "present": true,
      "storage": "S3|GCS|ADLS",
      "layers": ["raw", "staged", "curated", "analytics"]
    }}
  }},

  "data_flows": [
    {{
      "flow_name": "Customer order processing",
      "source": "E-commerce application database",
      "ingestion_method": "CDC|batch|API",
      "frequency": "real-time|hourly|daily",
      "transformations": ["Data quality checks", "PII masking", "Aggregations"],
      "destination": "Data warehouse fact_orders table",
      "latency_requirement": "< 5 minutes|< 1 hour|daily"
    }}
  ],

  "analytics_use_cases": [
    {{
      "use_case": "Customer segmentation analysis",
      "business_question": "Which customer segments drive most revenue?",
      "data_sources": ["customers", "orders", "web_events"],
      "complexity": "basic|intermediate|advanced",
      "techniques": ["RFM analysis", "clustering", "cohort analysis"],
      "stakeholders": ["Marketing team", "Product managers"]
    }}
  ],

  "data_governance": {{
    "pii_fields": ["email", "phone", "address", "payment_info"],
    "retention_policies": [
      {{"data_type": "user_events", "retention_days": 730}},
      {{"data_type": "transactional", "retention_days": 2555}}
    ],
    "compliance_requirements": ["GDPR", "CCPA", "PCI-DSS"],
    "data_quality_checks": [
      "Null checks on required fields",
      "Referential integrity",
      "Duplicate detection"
    ]
  }},

  "scale_estimates": {{
    "daily_data_volume_gb": 100,
    "total_warehouse_size_tb": 5,
    "monthly_query_count": 50000,
    "concurrent_users": 50,
    "annual_growth_rate_percent": 30
  }},

  "data_products": [
    {{
      "name": "Customer 360 View",
      "description": "Unified customer profile with all interactions",
      "consumers": ["Sales", "Marketing", "Support"],
      "update_frequency": "daily"
    }}
  ],

  "unstructured_data": {{
    "types_present": [
      {{
        "data_type": "images|videos|text|documents|audio",
        "description": "Product photos, user profile images, etc.",
        "estimated_volume_tb": 10,
        "business_criticality": "high|medium|low"
      }}
    ],
    "current_storage": {{
      "primary_location": "Cloud Storage (GCS/S3/Azure Blob)",
      "storage_classes": ["Standard", "Nearline", "Coldline"],
      "total_size_tb": 50,
      "growth_rate_tb_per_month": 2
    }},
    "business_value_opportunities": [
      {{
        "use_case": "Image classification for product categorization",
        "value": "Improve search relevance and reduce manual tagging",
        "implementation": "Vertex AI Vision API + BigQuery ML",
        "estimated_impact": "20% improvement in search accuracy"
      }}
    ],
    "bigquery_integration_strategy": {{
      "object_tables": "Create BigQuery object tables pointing to GCS buckets",
      "metadata_extraction": "Extract EXIF, file attributes to structured columns",
      "ml_models": [
        "Image classification models in Vertex AI",
        "Text sentiment analysis with BigQuery ML",
        "Vector embeddings for similarity search"
      ],
      "query_patterns": [
        "Join image metadata with transactional data",
        "Run ML.PREDICT on images for classification",
        "Vector search for similar products/content"
      ]
    }},
    "ml_ai_use_cases": [
      {{
        "use_case": "Visual search and product recommendations",
        "data_sources": ["product_images", "user_browsing_history"],
        "approach": "Computer vision + collaborative filtering",
        "bigquery_feature": "Vector Search + ML.RECOMMEND"
      }},
      {{
        "use_case": "Content moderation and trust & safety",
        "data_sources": ["user_uploaded_images", "listing_descriptions"],
        "approach": "Image classification + NLP sentiment",
        "bigquery_feature": "ML.PREDICT with Vertex AI models"
      }},
      {{
        "use_case": "Automated product tagging and categorization",
        "data_sources": ["product_images", "product_descriptions"],
        "approach": "Multi-modal learning (vision + text)",
        "bigquery_feature": "Remote models + feature engineering"
      }}
    ],
    "data_lake_architecture": {{
      "raw_layer": "GCS buckets with original files (images, videos, docs)",
      "processed_layer": "Extracted features, thumbnails, transcriptions",
      "feature_store": "Vertex AI Feature Store for ML features",
      "metadata_catalog": "BigQuery tables with pointers to objects + metadata",
      "integration_pattern": "Object tables + remote functions for ML inference"
    }},
    "cost_optimization": {{
      "storage_lifecycle": "Hot → Nearline (30 days) → Coldline (365 days)",
      "compression": "Image optimization, video transcoding",
      "deduplication": "Hash-based duplicate detection",
      "estimated_monthly_cost_usd": 5000,
      "optimization_potential_percent": 30
    }},
    "technical_requirements": [
      "BigQuery object tables for querying file metadata",
      "Vertex AI integration for ML model inference",
      "Cloud Functions for preprocessing pipelines",
      "Pub/Sub for event-driven processing",
      "Cloud Vision API, Natural Language API, Speech-to-Text"
    ]
  }},

  "recommendations": [
    "Start with core transactional entities (customers, orders)",
    "Implement CDC for real-time data synchronization",
    "Build customer analytics data mart first for quick wins",
    "Consider implementing dbt for transformation layer",
    "Leverage BigQuery object tables for unstructured data analytics",
    "Implement ML models for automated categorization and moderation",
    "Use Vertex AI Feature Store for ML feature management"
  ]
}}
```

IMPORTANT:
- Be SPECIFIC with table names, field names, and technical choices
- Base inferences on the actual business model discovered
- Estimate realistic scale based on company size and industry
- Think about the complete data journey from source to insight
- Consider both current state and what they SHOULD have for best practices
"""

        return prompt

    def _format_entities(self, entities: List) -> str:
        """Format entities list for prompt."""
        if not entities:
            return "None identified"

        formatted = []
        for entity in entities[:15]:  # Limit to top 15
            if isinstance(entity, dict):
                name = entity.get('name', str(entity))
                desc = entity.get('description', '')
                formatted.append(f"- **{name}**: {desc}" if desc else f"- {name}")
            else:
                formatted.append(f"- {entity}")

        return '\n'.join(formatted)

    def _format_list(self, items: List) -> str:
        """Format list for prompt."""
        if not items:
            return "None identified"
        return '\n'.join([f"- {item}" for item in items[:20]])

    def _format_job_tech_stack(self, jobs_data: Dict) -> str:
        """Format job posting tech stack data."""
        if not jobs_data or not jobs_data.get('found'):
            return "No job postings data available"

        tech_stack = jobs_data.get('tech_stack_detected', {})
        if not tech_stack:
            return "No technologies detected from job postings"

        formatted = []
        formatted.append(f"**Data Jobs Found**: {jobs_data.get('data_jobs_count', 0)} out of {jobs_data.get('total_jobs_found', 0)} total jobs")
        formatted.append(f"**Careers Page**: {jobs_data.get('careers_url', 'N/A')}")
        formatted.append("")
        formatted.append("**Technologies mentioned in job requirements:**")

        for category, techs in tech_stack.items():
            category_name = category.replace('_', ' ').title()
            formatted.append(f"- **{category_name}**: {', '.join(techs)}")

        # Add sample job titles
        job_titles = jobs_data.get('job_titles', [])
        if job_titles:
            formatted.append("")
            formatted.append("**Sample Data Job Titles:**")
            for title in job_titles[:5]:
                formatted.append(f"- {title}")

        return '\n'.join(formatted)

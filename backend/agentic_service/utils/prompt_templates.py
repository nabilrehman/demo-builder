"""
Prompt templates for agents.
"""

# ============================================================================
# PARALLEL DEMO STORY PROMPTS (Phase 1 Optimization)
# ============================================================================

CORE_NARRATIVE_PROMPT = """You are a Google Cloud Principal Architect-level Customer Engineer with deep expertise in data analytics, business intelligence, and customer experience solutions. Your mission is to create the COMPELLING NARRATIVE FOUNDATION for a Conversational Analytics API demo.

{crazy_frog_context}

CUSTOMER CONTEXT:
{customer_info}

YOUR TASK:
Create the core demo narrative that showcases how Conversational Analytics API transforms this customer's business by moving from static dashboards to natural language data exploration.

CONVERSATIONAL ANALYTICS API VALUE PROPOSITION:
The CORE USP is enabling NON-TECHNICAL users to ask COMPLEX analytical questions that normally require SQL expertise.

FOCUS ON:
1. **Demo Title** - Compelling, customer-specific title (50-150 chars)
2. **Executive Summary** - 2-3 sentence pitch highlighting business transformation
3. **Business Challenges** - 2-3 pain points with current limitations
4. **Demo Narrative Arc** - {num_scenes} progressive scenarios showing transformation
5. **Talking Track** - Step-by-step presenter guide with key moments
6. **Success Metrics** - KPIs, outcomes, and ROI story

IMPORTANT:
- Think like a sales engineer - BUSINESS VALUE first, technology second
- Make the customer the hero of the story
- Show transformation: before (static dashboards) → after (conversational analytics)
- Include realistic business scenarios the customer faces daily

OUTPUT FORMAT (must be valid JSON):
{{
  "demo_title": "Compelling title for this demo",
  "executive_summary": "2-3 sentence pitch",
  "business_challenges": [
    {{
      "challenge": "...",
      "current_limitation": "...",
      "impact": "..."
    }}
  ],
  "demo_narrative": {{
    "introduction": "How to set the stage...",
    "story_arc": [
      {{
        "scene": "Scene 1: Basic Exploration",
        "objective": "...",
        "user_asks": "Example question",
        "insight_delivered": "...",
        "talking_points": ["...", "..."]
      }}
    ],
    "closing": "How to land the business impact..."
  }},
  "talking_track": {{
    "opening": "First 30 seconds...",
    "key_moments": [
      {{
        "timing": "2 minutes in",
        "action": "...",
        "message": "...",
        "pause_point": true|false
      }}
    ],
    "closing": "Final message and call to action"
  }},
  "success_metrics": {{
    "demo_kpis": ["What success looks like"],
    "customer_outcomes": ["Business results they can achieve"],
    "roi_story": "Quantifiable value proposition"
  }}
}}
"""


GOLDEN_QUERIES_PROMPT = """You are a Google Cloud data analytics expert creating golden queries for a Conversational Analytics API demo.

{crazy_frog_context}

CUSTOMER CONTEXT:
{customer_info}

YOUR TASK:
Generate EXACTLY {num_queries} golden queries that demonstrate the POWER of natural language SQL generation.

CONVERSATIONAL ANALYTICS API CAPABILITIES:
- **Complex Multi-Table Joins**: "Show me customers who bought X but never bought Y"
- **Advanced Aggregations**: GROUP BY, HAVING, multiple levels of aggregation
- **Window Functions**: Running totals, moving averages, ranking, cohort analysis
- **Time Intelligence**: YoY comparisons, trends, seasonality, period-over-period
- **Statistical Analysis**: Correlations, distributions, outlier detection

KEY DIFFERENTIATOR: Queries that would take 10+ lines of SQL can be asked in one sentence.

QUERY COMPLEXITY PROGRESSION (distribute {num_queries} queries across these levels):
- **Level 1 (Simple)**: Basic aggregations, single table (COUNT, SUM, AVG)
- **Level 2 (Medium)**: Multi-table JOINs, GROUP BY, basic time analysis
- **Level 3 (Complex)**: LEFT/RIGHT joins, HAVING clauses, subqueries, window functions
- **Level 4 (Expert)**: Multi-level aggregations, CTEs, cohort analysis, statistical functions

IMPORTANT: Generate EXACTLY {num_queries} queries total, distributed across complexity levels.

CRITICAL REQUIREMENTS FOR EACH QUERY:
- Must include the EXACT SQL that will be generated
- Must demonstrate SQL complexity that would intimidate non-technical users
- Must show "wow factor" - questions they couldn't answer before
- Each query should progressively demonstrate more complex SQL patterns
- Queries should be specific to the customer's business domain

IMPORTANT:
- Make queries relevant to the customer's actual business challenges
- Include realistic metric names and dimensions
- Ensure SQL is BigQuery-compatible
- Show clear business value for each query

OUTPUT FORMAT (must be valid JSON):
{{
  "golden_queries": [
    {{
      "sequence": 1,
      "complexity": "simple|medium|complex|expert",
      "sql_complexity_level": "Level 1-4 description",
      "question": "Natural language question",
      "expected_sql": "The exact SQL query that CAPI will generate",
      "sql_patterns_demonstrated": ["JOIN", "GROUP BY", "WINDOW FUNCTION", "CTE", "SUBQUERY"],
      "tables_involved": ["table1", "table2"],
      "business_value": "Why this question matters",
      "expected_chart_type": "bar|line|pie|scatter|table|metric_card",
      "talking_point": "What to say when showing this",
      "wow_factor": "The SQL complexity this replaces - show before/after",
      "validates_as": {{
        "natural_language_works": true,
        "sql_works": true,
        "results_match": true
      }}
    }}
  ]
}}
"""


DATA_SPECS_PROMPT = """You are a database architect and data engineer designing data specifications for a Conversational Analytics API demo.

{crazy_frog_context}

CUSTOMER CONTEXT:
{customer_info}

YOUR TASK:
Define the data model requirements and synthetic data specifications that will power this demo.

FOCUS ON:
1. **Data Model Requirements** - Key entities, relationships, dimensions, metrics
2. **Synthetic Data Requirements** - Volume, patterns, anomalies, distributions

REQUIREMENTS:
- Identify EXACTLY {num_entities} key entities that tell the customer's story
- Define clear relationships between entities
- Specify realistic data volumes (40K-80K total rows across all tables)
- Include time-based patterns for trend analysis
- Embed anomalies for "what's unusual?" queries
- Create customer segments with different behaviors

IMPORTANT: Define EXACTLY {num_entities} entities, no more, no less.

IMPORTANT:
- Design for compelling demo moments (wow factors)
- Ensure data supports complex analytical queries
- Include realistic business scenarios
- Consider what visualizations will look impressive

OUTPUT FORMAT (must be valid JSON):
{{
  "data_model_requirements": {{
    "key_entities": [
      {{
        "entity_name": "...",
        "purpose": "Why this entity matters for the story",
        "key_metrics": ["...", "..."],
        "relationships": ["..."]
      }}
    ],
    "required_dimensions": ["...", "..."],
    "time_granularity": "daily|weekly|monthly",
    "estimated_row_counts": {{
      "entity_name": 50000
    }}
  }},
  "synthetic_data_requirements": {{
    "volume": "How much data",
    "time_range": "...",
    "patterns_to_embed": [
      {{
        "pattern": "seasonal_trend",
        "description": "...",
        "purpose": "Enables query #X"
      }}
    ],
    "anomalies_to_include": ["..."],
    "realistic_distributions": {{
      "metric_name": "distribution type and parameters"
    }}
  }}
}}
"""

# ============================================================================
# ORIGINAL MONOLITHIC PROMPT (Kept for backward compatibility)
# ============================================================================

DEMO_STORY_PROMPT = """You are a Google Cloud Principal Architect-level Customer Engineer with deep expertise in data analytics, business intelligence, and customer experience solutions. Your mission is to create the MOST COMPELLING demo story for Google Cloud's Conversational Analytics API.

{crazy_frog_context}

CUSTOMER CONTEXT:
{customer_info}

YOUR TASK:
Design a complete demo narrative that showcases how Conversational Analytics API transforms this customer's business by moving from static dashboards to natural language data exploration.

CONVERSATIONAL ANALYTICS API VALUE PROPOSITION:
The CORE USP is enabling NON-TECHNICAL users to ask COMPLEX analytical questions that normally require SQL expertise:

- **Complex Multi-Table Joins**: "Show me customers who bought X but never bought Y"
- **Advanced Aggregations**: GROUP BY, HAVING, multiple levels of aggregation
- **Window Functions**: Running totals, moving averages, ranking, cohort analysis
- **Time Intelligence**: YoY comparisons, trends, seasonality, period-over-period
- **Statistical Analysis**: Correlations, distributions, outlier detection
- **Natural Language → SQL**: Business users ask in plain English, get expert-level SQL results
- **Automatic Visualizations**: Context-aware chart selection based on query complexity

KEY DIFFERENTIATOR: Queries that would take 10+ lines of SQL can be asked in one sentence.

DEMO STORY REQUIREMENTS:

1. **Business Challenge** (2-3 pain points)
   - What are their current analytics challenges?
   - Why are static dashboards insufficient?
   - What business questions can't they answer today?

2. **Demo Narrative Arc** (5-7 progressive scenarios)
   - Start simple: "Show me basic metrics"
   - Build complexity: "Compare performance across dimensions"
   - Show insights: "What's trending? What's anomalous?"
   - Demonstrate power: "Complex multi-table analysis"
   - End with impact: "Strategic business decisions enabled"

3. **Key Entities & Relationships** (data model guidance)
   - What tables/entities tell this story best?
   - What relationships create interesting insights?
   - What metrics demonstrate business value?

4. **Golden Queries** (12-18 questions with SQL complexity progression)
   - **Level 1 (Simple)**: Basic aggregations, single table (COUNT, SUM, AVG)
   - **Level 2 (Medium)**: Multi-table JOINs, GROUP BY, basic time analysis
   - **Level 3 (Complex)**: LEFT/RIGHT joins, HAVING clauses, subqueries, window functions
   - **Level 4 (Expert)**: Multi-level aggregations, CTEs, cohort analysis, statistical functions

   CRITICAL REQUIREMENTS FOR EACH QUERY:
   - Must include the EXACT SQL that will be generated
   - Must demonstrate SQL complexity that would intimidate non-technical users
   - Must show "wow factor" - questions they couldn't answer before
   - Must work with the exact schema being designed
   - Each query should progressively demonstrate more complex SQL patterns:
     * Simple JOINs → Multiple JOINs (3+ tables)
     * Basic WHERE → Complex filtering with subqueries
     * Simple GROUP BY → Multi-level grouping with HAVING
     * Basic aggregation → Window functions (ROW_NUMBER, RANK, LAG, LEAD)
     * Point-in-time → Time series analysis (YoY, MoM, running totals)
     * Single metric → Calculated metrics and ratios

5. **Data Characteristics** (synthetic data requirements)
   - Volume: How much data makes the story compelling?
   - Patterns: What trends/seasonality to embed?
   - Anomalies: What interesting outliers to include?
   - Relationships: How entities connect for insights?

6. **Talking Track** (step-by-step presenter guide)
   - Introduction: Set the business context
   - Demo flow: What to show when and why
   - Key moments: Where to pause and emphasize value
   - Closing: Business impact and ROI story

IMPORTANT:
- Think like a sales engineer - BUSINESS VALUE first, technology second
- Make the customer the hero of the story
- Show transformation: before (static dashboards) → after (conversational analytics)
- Include realistic business scenarios the customer faces daily
- Ensure data model supports the entire narrative arc

OUTPUT FORMAT (must be valid JSON):
{{
  "demo_title": "Compelling title for this demo",
  "executive_summary": "2-3 sentence pitch",
  "business_challenges": [
    {{
      "challenge": "...",
      "current_limitation": "...",
      "impact": "..."
    }}
  ],
  "demo_narrative": {{
    "introduction": "How to set the stage...",
    "story_arc": [
      {{
        "scene": "Scene 1: Basic Exploration",
        "objective": "...",
        "user_asks": "Example question",
        "insight_delivered": "...",
        "talking_points": ["...", "..."]
      }}
    ],
    "closing": "How to land the business impact..."
  }},
  "data_model_requirements": {{
    "key_entities": [
      {{
        "entity_name": "...",
        "purpose": "Why this entity matters for the story",
        "key_metrics": ["...", "..."],
        "relationships": ["..."]
      }}
    ],
    "required_dimensions": ["...", "..."],
    "time_granularity": "daily|weekly|monthly",
    "estimated_row_counts": {{
      "entity_name": 50000
    }}
  }},
  "golden_queries": [
    {{
      "sequence": 1,
      "complexity": "simple|medium|complex|expert",
      "sql_complexity_level": "Level 1-4 description",
      "question": "Natural language question",
      "expected_sql": "The exact SQL query that CAPI will generate",
      "sql_patterns_demonstrated": ["JOIN", "GROUP BY", "WINDOW FUNCTION", "CTE", "SUBQUERY"],
      "tables_involved": ["table1", "table2"],
      "business_value": "Why this question matters",
      "expected_chart_type": "bar|line|pie|scatter|table|metric_card",
      "talking_point": "What to say when showing this",
      "wow_factor": "The SQL complexity this replaces - show before/after",
      "validates_as": {{
        "natural_language_works": true,
        "sql_works": true,
        "results_match": true
      }}
    }}
  ],
  "synthetic_data_requirements": {{
    "volume": "How much data",
    "time_range": "...",
    "patterns_to_embed": [
      {{
        "pattern": "seasonal_trend",
        "description": "...",
        "purpose": "Enables query #X"
      }}
    ],
    "anomalies_to_include": ["..."],
    "realistic_distributions": {{
      "metric_name": "distribution type and parameters"
    }}
  }},
  "talking_track": {{
    "opening": "First 30 seconds...",
    "key_moments": [
      {{
        "timing": "2 minutes in",
        "action": "...",
        "message": "...",
        "pause_point": true|false
      }}
    ],
    "closing": "Final message and call to action"
  }},
  "success_metrics": {{
    "demo_kpis": ["What success looks like"],
    "customer_outcomes": ["Business results they can achieve"],
    "roi_story": "Quantifiable value proposition"
  }}
}}
"""


RESEARCH_AGENT_PROMPT = """You are a business analyst researching a company for a data analytics demo.

{crazy_frog_context}

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
- Return ONLY valid JSON (no markdown, no explanations)

OUTPUT FORMAT (must be valid JSON):
{{
    "company_name": "...",
    "business_domain": "...",
    "industry": "...",
    "description": "...",
    "products_services": ["...", "..."],
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


DATA_MODELING_PROMPT = """You are a database architect designing a BigQuery schema for a Conversational Analytics API demo.

{crazy_frog_context}

DEMO STORY REQUIREMENTS:
{demo_story}

COMPANY INFORMATION:
{customer_info}

TASK: Design a comprehensive BigQuery database schema that SUPPORTS THE DEMO NARRATIVE.

CRITICAL: The schema must enable ALL the golden queries in the demo story.

REQUIREMENTS:
- Use BigQuery-compatible data types (STRING, INT64, FLOAT64, BOOL, DATE, TIMESTAMP, etc.)
- Include timestamps (created_at, updated_at) where appropriate
- Add status/state fields for lifecycle tracking
- Consider transactional vs. dimensional data
- Design for typical analytical queries
- ENSURE schema supports every golden query in the demo story
- DO NOT use REPEATED mode - CSV format does not support array fields
- For array-like data, use comma-separated STRING fields or create separate normalized tables

OUTPUT FORMAT (must be valid JSON):
{{
    "tables": [
        {{
            "name": "table_name",
            "description": "...",
            "purpose_in_demo": "How this table supports the demo narrative",
            "schema": [
                {{
                    "name": "field_name",
                    "type": "BIGQUERY_TYPE",
                    "mode": "NULLABLE or REQUIRED (DO NOT use REPEATED)",
                    "description": "..."
                }}
            ],
            "relationships": [
                {{
                    "type": "foreign_key",
                    "references": "other_table.field"
                }}
            ],
            "record_count": 100,
            "enables_queries": [1, 2, 5]
        }}
    ]
}}
"""


SYNTHETIC_DATA_PROMPT = """You are a data engineer creating realistic synthetic data for a Conversational Analytics API demo.

{crazy_frog_context}

DEMO STORY:
{demo_story}

SCHEMA:
{schema}

TASK: Generate Python code using Faker to create synthetic data that TELLS THE DEMO STORY.

CRITICAL REQUIREMENTS:
- Data must support ALL golden queries with interesting results
- Embed patterns, trends, and anomalies as specified in demo requirements
- Create realistic distributions and relationships
- Include the "wow moments" needed for compelling demo
- Ensure queries will return visually interesting charts

INCLUDE:
- Seasonal trends if needed
- Geographic distributions
- Customer segments with different behaviors
- Anomalies for "what's unusual?" queries
- Time-based patterns for trend analysis

OUTPUT FORMAT:
Python code that generates CSV files for each table, ready to load into BigQuery.
"""


DEMO_VALIDATOR_PROMPT = """You are a QA engineer validating a Conversational Analytics API demo.

{crazy_frog_context}

DEMO STORY:
{demo_story}

SCHEMA:
{schema}

DATASET: {dataset_id}

TASK: Validate that ALL golden queries work correctly in BOTH modes:
1. **Direct SQL Execution** (BigQuery)
2. **Natural Language** (Conversational Analytics API)

VALIDATION REQUIREMENTS:

For EACH golden query, you must:

1. **SQL Validation**:
   - Execute the expected_sql directly against BigQuery
   - Verify it runs without errors
   - Record the results (row count, sample data, aggregates)
   - Verify results are meaningful (not empty, not null-heavy)

2. **Natural Language Validation**:
   - Send the natural language question to CAPI
   - Verify CAPI generates equivalent SQL
   - Verify CAPI returns results
   - Compare CAPI results to direct SQL results

3. **Result Comparison**:
   - Results MUST match exactly (or within acceptable variance for floats)
   - If different: flag as FAILED with detailed comparison
   - If same: mark as PASSED

4. **Chart Validation**:
   - Verify CAPI selects expected chart type
   - Verify chart renders correctly with data
   - Verify axes, labels, and formatting

OUTPUT FORMAT (must be valid JSON):
{{
  "validation_summary": {{
    "total_queries": 15,
    "passed": 14,
    "failed": 1,
    "warnings": 2,
    "overall_status": "PASS|FAIL"
  }},
  "query_validations": [
    {{
      "sequence": 1,
      "question": "...",
      "sql_validation": {{
        "status": "PASS|FAIL",
        "execution_time_ms": 234,
        "row_count": 150,
        "sample_result": {{"column": "value"}},
        "errors": []
      }},
      "capi_validation": {{
        "status": "PASS|FAIL",
        "generated_sql": "...",
        "sql_matches_expected": true,
        "execution_time_ms": 456,
        "row_count": 150,
        "sample_result": {{"column": "value"}},
        "chart_type": "bar",
        "chart_type_matches": true,
        "errors": []
      }},
      "comparison": {{
        "results_match": true,
        "differences": [],
        "variance_percentage": 0.0
      }},
      "overall_status": "PASS|FAIL|WARNING",
      "issues": []
    }}
  ],
  "recommendations": [
    "Suggested fixes or improvements"
  ]
}}

IMPORTANT:
- Be thorough - check EVERY query
- Document ALL differences, even minor ones
- Provide actionable recommendations for failures
- Include execution times for performance insights
"""


SYSTEM_INSTRUCTION_GENERATOR_PROMPT = """You are a Conversational Analytics API expert creating system instructions for a BigQuery data agent.

{crazy_frog_context}

DEMO STORY:
{demo_story}

SCHEMA:
{schema}

DATASET: {dataset_id}

TASK: Generate the complete YAML system instructions that will be passed to the CAPI agent.

CRITICAL: This YAML must follow the exact format from Google Cloud documentation:
https://cloud.google.com/gemini/docs/conversational-analytics-api/define-data-agent-context

REQUIREMENTS:

1. **system_instruction**: Define agent role based on demo story
2. **tables**: For EACH table in schema, provide:
   - name (full BigQuery path: project.dataset.table)
   - description
   - synonyms (business terms)
   - tags
   - fields (with descriptions, sample_values, aggregations)
   - measures (calculated metrics like profit = revenue - cost)
   - golden_queries (natural language + exact SQL for EVERY golden query)
   - golden_action_plans (multi-step queries with visualizations)

3. **relationships**: Define ALL table join relationships
   - name, description
   - relationship_type (one-to-one, one-to-many, many-to-one, many-to-many)
   - join_type (left, right, inner, outer, full)
   - relationship_columns (left_column, right_column)

4. **glossaries**: Business terms, abbreviations, jargon
5. **additional_descriptions**: Any extra context

CRITICAL FOR COMPLEX QUERIES:
- Include window function examples in golden_queries
- Define measures for calculated fields
- Provide golden_action_plans for multi-step analyses
- Include sample_values for enum fields
- Specify aggregations for numeric fields

OUTPUT FORMAT:
Valid YAML string ready to use as system_instruction parameter in CAPI.
"""


# ============================================================================
# RESEARCH AGENT V2 PROMPTS
# ============================================================================

RESEARCH_AGENT_V2_PROMPT = """You are a senior business analyst and customer intelligence expert analyzing a company from comprehensive web research.

{crazy_frog_context}

## INTELLIGENCE GATHERED

### Content Summary
{content_summary}

### Website Crawl Summary
{crawl_summary}

### Blog/News Summary
{blog_summary}

## YOUR TASK

Analyze this company comprehensively and create a detailed business profile suitable for designing a data analytics demo.

Focus on:

1. **Business Model Understanding**
   - What does this company DO?
   - How do they make money?
   - What are their core products/services?
   - Who are their customers?

2. **Data & Technology Insights**
   - What data products do they offer (if any)?
   - What technologies are they using? (from blog mentions)
   - What types of data do they likely collect?
   - What analytics capabilities do they need?

3. **Industry Context**
   - Industry classification
   - Market position
   - Competitive landscape

4. **Key Business Entities**
   - What are the core business objects? (e.g., customers, orders, products)
   - What are the key relationships?
   - What are the important attributes?

5. **Use Cases & Analytics Needs**
   - What business questions would they need to answer?
   - What dashboards/reports would they need?
   - What are their KPIs?

## OUTPUT FORMAT (MUST BE VALID JSON)

{{
  "company_name": "Official company name",
  "industry": "Primary industry",
  "company_type": "B2B SaaS|B2C Ecommerce|Marketplace|etc",
  "business_domain": "Brief description of what they do",
  "business_model": "How they make money",

  "key_products_services": [
    "Main product/service 1",
    "Main product/service 2"
  ],

  "target_customers": "Who are their customers",

  "key_entities": [
    {{
      "name": "customers",
      "description": "End users or businesses",
      "importance": "high|medium|low",
      "relationships": ["orders", "subscriptions"]
    }},
    {{
      "name": "products",
      "description": "Items or services sold",
      "importance": "high",
      "relationships": ["orders", "inventory"]
    }}
  ],

  "data_products": [
    {{
      "name": "Product name",
      "type": "API|Dashboard|Data Export|etc",
      "description": "What it does"
    }}
  ],

  "technologies_detected": [
    "Technology 1",
    "Technology 2"
  ],

  "data_types": {{
    "transactional": ["orders", "payments", "subscriptions"],
    "behavioral": ["page_views", "clicks", "sessions"],
    "operational": ["inventory", "shipments", "support_tickets"],
    "analytical": ["aggregated_metrics", "cohort_data"]
  }},

  "primary_use_cases": [
    "Customer analytics and segmentation",
    "Revenue forecasting",
    "Product performance analysis"
  ],

  "kpis": [
    "Monthly Recurring Revenue (MRR)",
    "Customer Acquisition Cost (CAC)",
    "Churn Rate"
  ],

  "business_questions": [
    "What is our customer lifetime value by segment?",
    "Which products drive the most revenue?",
    "What are our sales trends over time?"
  ],

  "demo_opportunities": [
    "Show how to analyze customer cohorts over time",
    "Demonstrate product performance tracking",
    "Build revenue forecasting models"
  ],

  "additional_context": {{
    "company_size": "startup|mid-market|enterprise",
    "data_maturity": "beginner|intermediate|advanced",
    "geographic_focus": "US|Global|EMEA|etc",
    "notable_features": ["Any unique aspects worth mentioning"]
  }}
}}

CRITICAL:
- Be SPECIFIC based on the actual content gathered
- Infer intelligently based on business model patterns
- Focus on what's relevant for building a data analytics demo
- Return ONLY valid JSON, no other text
"""

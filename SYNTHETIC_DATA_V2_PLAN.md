# 🎯 SYNTHETIC DATA GENERATION V2 - COMPREHENSIVE PLAN

**Goal:** Generate story-driven, query-validated, BigQuery-compliant synthetic data that guarantees meaningful demo insights.

**Status:** PLANNING PHASE
**Created:** 2025-10-06
**Complexity:** High (Est. 3-5 days implementation)

---

## 📊 CURRENT STATE ANALYSIS

### What We Have:
```
Research Agent → customer_info (company, products, industry)
       ↓
Demo Story Agent → demo_story:
   ├── demo_title
   ├── executive_summary
   ├── business_challenges [list]
   ├── demo_narrative
   │   ├── introduction
   │   ├── story_arc [scenes]
   │   └── closing
   ├── talking_track
   │   ├── opening
   │   ├── key_moments [list]
   │   └── closing
   ├── success_metrics
   └── golden_queries [6-10 queries]
       ├── sequence
       ├── complexity (simple/medium/complex/expert)
       ├── question (natural language)
       ├── expected_sql ⭐ THE CRITICAL FIELD
       ├── tables_involved
       ├── business_value
       ├── talking_point
       └── wow_factor
       ↓
Data Modeling Agent → schema (tables, fields, types)
       ↓
❌ Synthetic Data Generator → Random data (BROKEN - doesn't use demo_story!)
       ↓
Infrastructure Agent → Load to BigQuery (FAILS for users, transactions, search_queries)
```

### What's Broken:
1. ❌ Synthetic Data Generator **ignores demo_story**
2. ❌ Data doesn't match **temporal requirements** (queries search 2025, data is 2023)
3. ❌ Data doesn't create **meaningful patterns** (queries return empty or 0.0)
4. ❌ No **hero entities** (top products, key customers, important segments)
5. ❌ LLM generates **malformed timestamps** (BigQuery rejects them)
6. ❌ No **cross-table coordination** (product in one table, missing in another)
7. ❌ No **audience awareness** (same data for internal vs external demo)

---

## 🎯 V2 OBJECTIVES

### Primary Goals:
1. ✅ **Query-Driven:** Every golden query returns meaningful, insightful results
2. ✅ **Story-Aligned:** Data supports business narrative and scenes
3. ✅ **BigQuery-Safe:** 100% compatible formatting (no load failures)
4. ✅ **Coordinated:** Hero entities appear consistently across tables
5. ✅ **Audience-Aware:** Different patterns for internal vs external demos

### Success Criteria:
- [ ] All golden queries return non-empty results
- [ ] Top result for each query is business-meaningful (>1000 transactions, >$100K revenue, etc.)
- [ ] All tables load to BigQuery without errors
- [ ] Data tells a coherent story across scenes
- [ ] Temporal patterns match query requirements

---

## 🏗️ ARCHITECTURE: Hybrid Approach

### Why Hybrid?

| Data Type | Tool | Reason |
|-----------|------|--------|
| **Structural** (dates, IDs, numbers) | Faker | 100% BigQuery safe, fast, reliable |
| **Content** (names, descriptions) | LLM | Domain-specific, realistic, engaging |
| **Patterns** (distributions, correlations) | Blueprint | Story-driven, query-validated |

### Key Insight:
- LLM is **great at text**, **terrible at structure**
- Faker is **great at structure**, **generic at text**
- Blueprint is **great at coordination**

**Solution:** Use each tool for what it's best at!

---

## 📋 IMPLEMENTATION PLAN

### PHASE 1: Query Analyzer (NEW COMPONENT)
**Purpose:** Extract data requirements from golden queries

**Input:**
- `demo_story` (with golden_queries)
- `schema` (table definitions)

**Output:** `data_requirements` dictionary

```python
{
  "temporal_requirements": {
    "date_range": "2024-01-01 to 2024-10-06",
    "current_year": 2024,
    "last_quarter": "Q3 2024 (Jul-Sep)",
    "this_month": "October 2024",
    "coverage_needed": ["2024-Q1", "2024-Q2", "2024-Q3", "2024-10"]
  },

  "hero_entities": {
    "products": [
      {
        "name": "Nike Air Jordan XXXVIII",
        "category": "Basketball Shoes",
        "target_sales_q3": 1247,
        "target_revenue": 156000,
        "price_point": 125
      }
    ],
    "customer_segments": [
      {
        "segment": "Premium Collectors",
        "percentage": 15,
        "avg_spend": 350
      }
    ]
  },

  "query_patterns": [
    {
      "query_id": "q1",
      "question": "Which product sold most last quarter?",
      "tables": ["transactions", "products", "categories"],
      "temporal_filter": "Q3 2024",
      "expected_pattern": "One product with >1000 sales",
      "aggregation": "SUM(sales) GROUP BY product",
      "meaningful_threshold": {
        "min_sales": 1000,
        "min_revenue": 100000
      }
    }
  ],

  "cross_table_relationships": {
    "hero_products_must_appear_in": [
      "products", "transactions", "inventory", "reviews"
    ],
    "foreign_key_integrity": "strict"
  }
}
```

#### Subtasks:

##### 1.1 SQL Parser
**File:** `backend/agentic_service/agents/query_analyzer/sql_parser.py`

**Purpose:** Parse `expected_sql` from golden queries to extract requirements

```python
class SQLRequirementExtractor:
    """Extracts data requirements from SQL queries."""

    def extract_temporal_filters(self, sql: str) -> dict:
        """
        Finds date filters in WHERE clauses.

        Examples:
          - "WHERE DATE_TRUNC(transaction_date, MONTH) = DATE '2025-10-01'"
            → {"field": "transaction_date", "filter": "october 2024"}

          - "WHERE EXTRACT(YEAR FROM date) = 2025"
            → {"field": "date", "filter": "year 2025"}

          - "WHERE date BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)"
            → {"field": "date", "filter": "last 90 days"}
        """
        pass

    def extract_aggregation_requirements(self, sql: str) -> dict:
        """
        Finds GROUP BY, aggregations, and expected result patterns.

        Example:
          - "SELECT product, SUM(sales) ... GROUP BY product ORDER BY 2 DESC LIMIT 1"
            → {"needs_top_product": true, "min_count": 1000}
        """
        pass

    def extract_table_dependencies(self, sql: str) -> list:
        """Extract all tables and their join relationships."""
        pass
```

**Complexity:** Medium (regex + SQL parsing)
**Dependencies:** None
**Estimated Time:** 1 day

---

##### 1.2 Temporal Strategy Builder
**File:** `backend/agentic_service/agents/query_analyzer/temporal_strategy.py`

**Purpose:** Calculate exact date ranges needed

```python
class TemporalStrategyBuilder:
    """Builds temporal distribution strategy from query requirements."""

    def build_strategy(self, golden_queries: list) -> dict:
        """
        Analyzes all queries and creates unified temporal strategy.

        Steps:
        1. Extract all temporal references ("last quarter", "this month")
        2. Map to absolute dates (Q3 2024 = Jul-Sep 2024)
        3. Identify current date anchor (today = 2024-10-06)
        4. Calculate distribution percentages
        """

        return {
            "base_date": "2024-10-06",  # Today
            "min_date": "2024-01-01",   # Start of current year
            "max_date": "2024-10-06",   # Today

            "distributions": {
                "Q1_2024": 0.20,  # 20% of data
                "Q2_2024": 0.25,  # 25% of data
                "Q3_2024": 0.35,  # 35% of data (CRITICAL - queries focus here)
                "Q4_2024": 0.20   # 20% of data (current month)
            },

            "seasonal_patterns": {
                "july_spike": 1.4,     # Summer/holiday boost
                "december_spike": 1.8,  # Christmas
                "january_drop": 0.7    # Post-holiday slowdown
            }
        }
```

**Complexity:** Medium
**Dependencies:** 1.1
**Estimated Time:** 0.5 day

---

##### 1.3 Hero Entity Extractor (LLM-POWERED)
**File:** `backend/agentic_service/agents/query_analyzer/hero_entity_extractor.py`

**Purpose:** Use LLM to identify key entities that should dominate the data

```python
class HeroEntityExtractor:
    """Uses LLM to identify hero entities from demo narrative."""

    async def extract_heroes(
        self,
        customer_info: dict,
        demo_story: dict,
        query_patterns: list
    ) -> dict:
        """
        Analyzes:
        - business_challenges (what problems exist?)
        - story_arc scenes (what products/segments are highlighted?)
        - golden queries (what needs to be "top" result?)
        - talking_track (what presenter will emphasize?)

        Returns hero entities with target metrics.
        """

        prompt = f"""
        Analyze this demo story and identify 3-5 HERO ENTITIES that should
        dominate the data to make golden queries return insightful results.

        Demo Story:
        {demo_story}

        Golden Queries:
        {[q['question'] for q in golden_queries]}

        For each hero entity, specify:
        1. Entity type (product, customer_segment, category, etc.)
        2. Name (specific, realistic for {customer_info['company_name']})
        3. Target metrics (how many sales, revenue, rating, etc.)
        4. Which queries need this entity to be "top result"

        Example:
        {{
          "hero_products": [
            {{
              "name": "iPhone 13 Pro 256GB",
              "category": "Electronics > Smartphones",
              "needed_for_queries": ["q1", "q3"],
              "target_metrics": {{
                "q3_sales_count": 1247,
                "q3_revenue": 156000,
                "avg_rating": 4.8,
                "listing_count": 850
              }}
            }}
          ]
        }}
        """

        # Call LLM
        # Parse response
        # Validate against query requirements

        return hero_entities
```

**Complexity:** Medium-High (LLM + validation)
**Dependencies:** 1.1, 1.2
**Estimated Time:** 1 day

---

##### 1.4 Query Requirement Validator
**File:** `backend/agentic_service/agents/query_analyzer/requirement_validator.py`

**Purpose:** Combine all analyzers and validate completeness

```python
class QueryRequirementValidator:
    """Validates that data requirements cover all queries."""

    def validate(self, data_requirements: dict, golden_queries: list) -> dict:
        """
        Checks:
        1. Every query has temporal coverage
        2. Every query has hero entities (if needed)
        3. Every table in query has generation plan
        4. Meaningful thresholds are set

        Returns validation report + warnings.
        """
        pass
```

**Complexity:** Low
**Dependencies:** 1.1, 1.2, 1.3
**Estimated Time:** 0.5 day

---

### PHASE 2: Blueprint-Driven Data Generator (ENHANCED)
**Purpose:** Generate data following the blueprint with hybrid approach

#### 2.1 Master Data Generator (Faker + LLM Hybrid)
**File:** `backend/agentic_service/agents/synthetic_data_generator_v2/master_data_generator.py`

**Strategy:**
```python
# STEP 1: Generate structural data with Faker (100% BigQuery safe)
df = pd.DataFrame()
df['product_id'] = range(1, row_count + 1)
df['created_at'] = faker_generate_timestamps(blueprint.temporal_strategy)
df['price'] = faker_generate_prices(blueprint.price_ranges)

# STEP 2: Generate content with LLM (domain-specific)
product_names = llm_generate_product_names(
    company=customer_info,
    hero_products=blueprint.hero_products,
    count=row_count
)
df['product_name'] = product_names

# STEP 3: Inject hero entities
df = inject_hero_products(df, blueprint.hero_products)

# STEP 4: Validate BigQuery compatibility
df = validate_and_coerce_types(df, schema)
```

**Subtasks:**

##### 2.1.1 Temporal Data Generator
```python
def generate_timestamps_with_pattern(
    count: int,
    temporal_strategy: dict,
    field_name: str
) -> List[datetime]:
    """
    Generates timestamps following blueprint distribution.

    Features:
    - Respects quarter distributions (35% in Q3, etc.)
    - Applies seasonal spikes (July +40%, December +80%)
    - Ensures recent data for "this month" queries
    - 100% BigQuery-compliant format
    """
```

##### 2.1.2 Hero Entity Injector
```python
def inject_hero_entities(
    df: pd.DataFrame,
    hero_entities: dict,
    concentration_rate: float = 0.4
) -> pd.DataFrame:
    """
    Ensures hero products/customers appear with high frequency.

    Example:
      - Hero product "Jordan Airmax" should be 40% of Q3 sales
      - Premium customer segment should be 15% of customers
      - Top category should be 35% of listings
    """
```

##### 2.1.3 Cross-Table Coordinator
```python
class CrossTableCoordinator:
    """Ensures hero entities appear consistently across tables."""

    def coordinate_hero_presence(
        self,
        tables: dict,  # All generated DataFrames
        hero_entities: dict
    ) -> dict:
        """
        Ensures:
        - Hero product appears in products, transactions, reviews, inventory
        - Hero customer appears in customers, transactions, messages
        - Foreign key relationships are valid
        """
```

**Complexity:** High
**Dependencies:** Phase 1
**Estimated Time:** 2 days

---

#### 2.2 LLM Content Generator (IMPROVED)
**File:** `backend/agentic_service/agents/synthetic_data_generator_v2/llm_content_generator.py`

**Changes from current:**

1. **Request ONLY text fields** (no timestamps!)
```python
prompt = f"""
Generate ONLY product names and descriptions for {company_name}.

CRITICAL: Return ONLY these fields:
- product_name (string)
- description (string)
- category (string)

DO NOT include:
- IDs (we'll generate)
- Dates (we'll generate)
- Prices (we'll generate)
- Any other fields

HERO PRODUCTS (MUST include these first):
{blueprint.hero_products}

Then generate {row_count - len(heroes)} supporting products.
"""
```

2. **Post-process and validate**
```python
# LLM returns content
llm_data = await llm.generate(prompt)

# Merge with Faker-generated structure
final_df = pd.DataFrame({
    'product_id': faker_ids,
    'product_name': llm_data['names'],
    'description': llm_data['descriptions'],
    'category': llm_data['categories'],
    'price': faker_prices,
    'created_at': faker_dates,  # ← Faker ensures correct format
    'updated_at': faker_dates
})

# Validate BigQuery types
final_df = coerce_to_bigquery_types(final_df, schema)
```

**Complexity:** Medium
**Dependencies:** 2.1
**Estimated Time:** 1 day

---

#### 2.3 BigQuery Type Validator (NEW)
**File:** `backend/agentic_service/agents/synthetic_data_generator_v2/bigquery_validator.py`

**Purpose:** Ensure 100% BigQuery compatibility BEFORE CSV write

```python
class BigQueryTypeValidator:
    """Validates and coerces data to BigQuery-compatible formats."""

    BIGQUERY_FORMATS = {
        'TIMESTAMP': '%Y-%m-%d %H:%M:%S',  # No 'T', no 'UTC'
        'DATE': '%Y-%m-%d',
        'DATETIME': '%Y-%m-%d %H:%M:%S'
    }

    def validate_and_fix(self, df: pd.DataFrame, schema: dict) -> pd.DataFrame:
        """
        For each field:
        1. Check type matches schema
        2. Validate format (timestamps, dates)
        3. Fix common issues (space before T, UTC suffix)
        4. Coerce to correct type
        5. Validate no nulls in REQUIRED fields
        """

        for field in schema['fields']:
            if field['type'] == 'TIMESTAMP':
                # Fix timestamps
                df[field['name']] = pd.to_datetime(df[field['name']])
                df[field['name']] = df[field['name']].dt.strftime(
                    self.BIGQUERY_FORMATS['TIMESTAMP']
                )

            elif field['type'] in ['INT64', 'INTEGER']:
                df[field['name']] = df[field['name']].astype(int)

            # etc.

        return df

    def pre_load_test(self, csv_file: str, schema: dict) -> dict:
        """
        Simulates BigQuery load to catch errors BEFORE actual load.

        Uses pandas to read CSV and validates:
        - All columns present
        - All types parseable
        - No format issues

        Returns: {"valid": true/false, "errors": [...]}
        """
```

**Complexity:** Medium
**Dependencies:** None
**Estimated Time:** 1 day

---

### PHASE 3: Query Validator (NEW COMPONENT)
**Purpose:** Verify queries return meaningful results BEFORE BigQuery load

**File:** `backend/agentic_service/agents/query_validator_v2.py`

```python
class QueryResultValidator:
    """Simulates golden queries on generated data before BigQuery load."""

    def __init__(self):
        # Use DuckDB for in-memory SQL simulation
        import duckdb
        self.db = duckdb.connect(':memory:')

    async def validate_all_queries(
        self,
        csv_files: dict,  # {table_name: csv_path}
        golden_queries: list,
        data_requirements: dict
    ) -> dict:
        """
        For each golden query:
        1. Load CSVs into DuckDB
        2. Run the expected_sql
        3. Check if results are meaningful
        4. Flag issues for regeneration
        """

        validation_results = {}

        for query in golden_queries:
            # Load relevant tables
            for table in query['tables_involved']:
                self.db.execute(
                    f"CREATE TABLE {table} AS SELECT * FROM '{csv_files[table]}'"
                )

            # Run query
            result = self.db.execute(query['expected_sql']).fetchall()

            # Validate result
            is_valid = self._check_meaningful(result, query, data_requirements)

            validation_results[query['sequence']] = {
                "valid": is_valid,
                "result_preview": result[:5],
                "issues": []
            }

        return validation_results

    def _check_meaningful(
        self,
        result: list,
        query: dict,
        requirements: dict
    ) -> bool:
        """
        Checks if result meets "meaningful" threshold.

        Examples:
        - "Top product" query: Top result should have >1000 sales
        - "Revenue by category": Each category should have >$10K
        - "Growth trend": Should show actual trend, not flat line
        """

        if not result or len(result) == 0:
            return False

        # Get threshold from requirements
        threshold = requirements['query_patterns'][query['sequence']].get(
            'meaningful_threshold', {}
        )

        # Apply threshold checks
        # ...

        return all_checks_passed
```

**Complexity:** High (SQL simulation)
**Dependencies:** Phase 2
**Estimated Time:** 1.5 days

---

### PHASE 4: Orchestration Updates

#### 4.1 Update Pipeline
**File:** `backend/agentic_service/demo_orchestrator.py`

**New Flow:**
```
Research Agent
    ↓
Demo Story Agent
    ↓
Data Modeling Agent
    ↓
[NEW] Query Analyzer ← Analyze golden queries
    ↓
Synthetic Data Generator V2 ← Use blueprint
    ↓
[NEW] Query Validator ← Verify results
    ↓    ↓
    ↓    └─ If INVALID → Regenerate with fixes
    ↓
Infrastructure Agent (only if validated!)
    ↓
CAPI Instructions
    ↓
Demo Validator
```

**Complexity:** Medium
**Dependencies:** All previous phases
**Estimated Time:** 1 day

---

## 🎯 AUDIENCE-AWARE DATA GENERATION

### Concept:
Different demos need different data characteristics

**Internal Demo (for company's own employees):**
- Real employee names (if available)
- Actual department structures
- Real product SKUs
- Recent dates (last 30 days)
- Sensitive metrics visible

**External Demo (for prospects/customers):**
- Generic but realistic names
- Industry-standard categories
- Broader date ranges
- Sanitized/anonymized data
- Focus on insights, not specifics

### Implementation:
```python
# In Demo Story Agent output
demo_story['target_audience'] = 'internal|external|partner'
demo_story['data_sensitivity'] = 'high|medium|low'

# In Query Analyzer
if demo_story['target_audience'] == 'internal':
    data_requirements['name_strategy'] = 'realistic_internal'
    data_requirements['date_recency'] = 'last_30_days'
else:
    data_requirements['name_strategy'] = 'generic_realistic'
    data_requirements['date_recency'] = 'last_12_months'
```

**Complexity:** Low (conditional logic)
**Dependencies:** Phase 1, Phase 2
**Estimated Time:** 0.5 day

---

## 📊 TESTING STRATEGY

### Unit Tests:
- [ ] SQL parser correctly extracts temporal filters
- [ ] Temporal strategy generates correct date ranges
- [ ] Hero entity injection reaches target percentages
- [ ] BigQuery type validator catches malformed timestamps
- [ ] Query validator correctly identifies empty results

### Integration Tests:
- [ ] Full pipeline: OfferUp → demo_story → data generation → query validation
- [ ] All golden queries return non-empty results
- [ ] Top results meet meaningful thresholds
- [ ] All CSVs load to BigQuery without errors

### Regression Tests:
- [ ] Compare V2 vs V1 data quality
- [ ] Verify no performance degradation
- [ ] Check all existing demos still work

---

## 🚀 ROLLOUT PLAN

### Week 1: Core Infrastructure
- [ ] Day 1-2: SQL Parser + Temporal Strategy (Phase 1.1, 1.2)
- [ ] Day 3-4: Hero Entity Extractor (Phase 1.3)
- [ ] Day 5: Validation framework (Phase 1.4)

### Week 2: Data Generation
- [ ] Day 1-2: Master Data Generator (Phase 2.1)
- [ ] Day 3: LLM Content Generator improvements (Phase 2.2)
- [ ] Day 4-5: BigQuery Validator + Query Validator (Phase 2.3, 3)

### Week 3: Integration & Testing
- [ ] Day 1-2: Orchestration updates (Phase 4)
- [ ] Day 3: Audience-aware generation
- [ ] Day 4-5: End-to-end testing

---

## ⚠️ RISKS & MITIGATIONS

| Risk | Impact | Mitigation |
|------|--------|-----------|
| SQL parsing fails for complex queries | High | Fallback to LLM-based requirement extraction |
| Hero entities don't appear as expected | High | Post-generation validation + regeneration loop |
| Query validator too slow | Medium | Cache DuckDB tables, parallel validation |
| LLM still generates bad timestamps | High | Use Faker for ALL temporal fields |
| Data doesn't tell coherent story | High | Stronger cross-table coordination |

---

## 🎯 SUCCESS METRICS

### V2 vs V1 Comparison:
| Metric | V1 (Current) | V2 (Target) |
|--------|--------------|-------------|
| Golden queries with results | 0% | 100% |
| BigQuery load failures | 3/8 tables | 0/8 tables |
| Meaningful top results | 0% | 90%+ |
| Data story coherence | Low | High |
| Timestamp format errors | 100+ | 0 |

---

## 💡 FUTURE ENHANCEMENTS (V3+)

1. **Machine Learning Patterns:** Use actual patterns from customer's data (if available)
2. **Anomaly Injection:** Add realistic data quality issues for "data cleaning" demos
3. **Multi-Scenario Support:** Generate different datasets for different demo scenes
4. **Real-Time Adjustment:** Regenerate specific tables if query fails during demo

---

## 📝 NEXT STEPS

**IMMEDIATE ACTION:**
1. Review this plan with team
2. Approve architecture (Hybrid Approach)
3. Prioritize phases (can we skip any?)
4. Assign ownership for each component
5. Set up tracking (GitHub project board?)

**DECISION NEEDED:**
- [ ] Go with full 3-phase approach?
- [ ] Start with simpler version (Faker only, manual hero injection)?
- [ ] Timeline acceptable (3 weeks)?

---

**END OF PLAN**

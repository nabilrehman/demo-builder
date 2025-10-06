"""
Synthetic Data Generator - MARKDOWN VERSION.
Creates realistic demo data using MARKDOWN TABLE format (more reliable than JSON).

KEY FEATURES:
- LLM generates markdown tables (more reliable than JSON)
- Detailed logging of prompts and responses for debugging
- Parallel table generation (3-5x speedup)
- Dependency-aware batching (dimension tables → fact tables)
- Async file I/O

WHY MARKDOWN:
- LLMs excel at markdown tables
- More forgiving than JSON (extra text doesn't break parsing)
- Easy to verify visually
- Simple parsing logic
"""
import logging
import os
import random
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Set, Tuple, Optional
import pandas as pd
from faker import Faker
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Initialize Faker
fake = Faker()
Faker.seed(42)  # Reproducible data
random.seed(42)


class SyntheticDataGeneratorMarkdown:
    """MARKDOWN VERSION: Generates realistic synthetic data using markdown tables (more reliable than JSON)."""

    def __init__(self):
        self.output_dir = "/tmp/synthetic_data"
        os.makedirs(self.output_dir, exist_ok=True)

        # Configure Gemini for data generation (Vertex AI)
        import vertexai
        from vertexai.generative_models import GenerativeModel

        project_id = os.environ.get("DEVSHELL_PROJECT_ID", "bq-demos-469816")
        vertexai.init(project=project_id, location="us-central1")

        # Use Gemini 2.5 Pro for highest quality data generation
        self.llm_model = GenerativeModel("gemini-2.5-pro")
        self.generation_config = {
            "temperature": 0.7,
        }
        logger.info("🤖 Using Gemini 2.5 Pro for data generation (highest quality)")

        logger.info(f"Synthetic Data Generator OPTIMIZED initialized with LLM. Output: {self.output_dir}")

    async def execute(self, state: Dict) -> Dict:
        """Execute synthetic data generation phase with parallel processing."""
        import time

        # 🔍 CRITICAL DEBUG: Log what state we receive
        logger.info("🚀 Generating synthetic data with PARALLEL processing")
        logger.info(f"🔍 DEBUG: State keys received: {list(state.keys())}")
        customer_info = state.get("customer_info", {})
        logger.info(f"🔍 DEBUG: customer_info type: {type(customer_info)}, len: {len(customer_info) if isinstance(customer_info, dict) else 'N/A'}")
        if customer_info:
            logger.info(f"🔍 DEBUG: customer_info keys: {list(customer_info.keys()) if isinstance(customer_info, dict) else 'not a dict'}")
            logger.info(f"🔍 DEBUG: Company name: {customer_info.get('company_name', 'MISSING')}")
        else:
            logger.error(f"❌ CRITICAL: customer_info is EMPTY or falsy! Value: {customer_info}")

        # ⚠️ CRITICAL: FAIL THE PIPELINE if customer_info is missing
        # User requirement: "if synthetic data doesn't work, quit at that part and shouldn't continue"
        if not customer_info or not isinstance(customer_info, dict) or len(customer_info) == 0:
            error_msg = (
                "❌ CRITICAL FAILURE: customer_info is missing or empty! "
                "Cannot generate realistic synthetic data without company context. "
                "Pipeline aborted to prevent garbage data generation."
            )
            logger.error(error_msg)
            if "job_manager" in state and "job_id" in state:
                state["job_manager"].add_log(
                    state["job_id"],
                    "synthetic data generator optimized",
                    error_msg,
                    "ERROR"
                )
            raise ValueError(error_msg)

        # Log to job manager at START
        if "job_manager" in state and "job_id" in state:
            state["job_manager"].add_log(
                state["job_id"],
                "synthetic data generator optimized",
                f"🔍 customer_info check: {bool(customer_info)} (len={len(customer_info) if isinstance(customer_info, dict) else 0})",
                "WARNING" if not customer_info else "INFO"
            )
            state["job_manager"].add_log(
                state["job_id"],
                "synthetic data generator optimized",
                "🚀 Starting LLM-based synthetic data generation...",
                "INFO"
            )

        start_time = time.time()

        try:
            schema = state.get("schema", {})
            demo_story = state.get("demo_story", {})

            if not schema:
                raise ValueError("No schema found in state. Run Data Modeling Agent first.")

            # Generate data for all tables IN PARALLEL
            generated_files = await self._generate_all_tables_parallel(schema, demo_story, state)

            elapsed = time.time() - start_time

            # Update state
            state["synthetic_data_files"] = generated_files
            state["data_generation_complete"] = True

            logger.info(f"✅ Data generation complete in {elapsed:.2f}s. {len(generated_files)} CSV files created")

            # Log to CE Dashboard - summary
            if "job_manager" in state and "job_id" in state:
                job_manager = state["job_manager"]
                job_id = state["job_id"]

                total_rows = sum(f.get("row_count", 0) for f in state.get("table_file_metadata", []))
                job_manager.add_log(
                    job_id,
                    "synthetic data generator optimized",
                    f"✅ Data Generation Complete (OPTIMIZED): {total_rows:,} rows across {len(generated_files)} tables in {elapsed:.2f}s",
                    "INFO"
                )

            return state

        except Exception as e:
            logger.error(f"Data generation failed: {e}", exc_info=True)
            raise

    async def _generate_all_tables_parallel(
        self,
        schema: Dict,
        demo_story: Dict,
        state: Dict
    ) -> List[str]:
        """
        OPTIMIZED: Generate data for all tables with parallel processing.

        Strategy:
        1. Group tables by dependency level
        2. Generate each level in parallel
        3. Maintain foreign key integrity
        """
        tables = schema.get("tables", [])
        generated_files = []
        table_file_metadata = []

        # Optimal row counts by table type
        volume_strategy = {
            "dimension_small": 50,      # channels, categories, stores
            "dimension_medium": 800,    # products, inventory
            "entity_medium": 3000,      # customers
            "entity_large": 3500,       # customer_addresses
            "transaction_medium": 15000, # orders
            "transaction_large": 40000   # order_items
        }

        # Track generated IDs for foreign keys
        id_mappings = {}

        # Group tables by dependency level for parallel processing
        dependency_levels = self._group_by_dependency(tables)

        # Log start to CE Dashboard
        if "job_manager" in state and "job_id" in state:
            job_manager = state["job_manager"]
            job_id = state["job_id"]
            job_manager.add_log(
                job_id,
                "synthetic data generator optimized",
                f"🔄 Generating synthetic data for {len(tables)} tables in {len(dependency_levels)} parallel batches...",
                "INFO"
            )

        # Process each dependency level in parallel
        for level_idx, table_batch in enumerate(dependency_levels):
            logger.info(f"⚡ Processing level {level_idx + 1}/{len(dependency_levels)}: {len(table_batch)} tables in PARALLEL")

            # Generate all tables in this level concurrently
            tasks = []
            for table in table_batch:
                tasks.append(
                    self._generate_single_table(
                        table,
                        volume_strategy,
                        id_mappings,
                        demo_story,
                        state
                    )
                )

            # Execute in parallel
            results = await asyncio.gather(*tasks)

            # Process results
            for table, df, filename in results:
                table_name = table["name"]
                generated_files.append(filename)

                # Store metadata
                table_file_metadata.append({
                    "table_name": table_name,
                    "row_count": len(df),
                    "filename": filename
                })

                # Store IDs for foreign key relationships
                # Try multiple ID column name patterns
                id_col = None
                if "id" in df.columns:
                    id_col = "id"
                elif f"{table_name}_id" in df.columns:
                    id_col = f"{table_name}_id"
                else:
                    # Try singular form (e.g., "customer_id" for "customers" table)
                    singular_table = table_name.rstrip('s')  # Simple singular: remove trailing 's'
                    if f"{singular_table}_id" in df.columns:
                        id_col = f"{singular_table}_id"
                    else:
                        # Try to find any column ending with _id that might be the primary key
                        id_candidates = [col for col in df.columns if col.endswith('_id')]
                        if len(id_candidates) == 1:
                            id_col = id_candidates[0]
                        elif len(id_candidates) > 1:
                            # If multiple, prefer one that contains the table name
                            for candidate in id_candidates:
                                if table_name.lower() in candidate.lower() or singular_table.lower() in candidate.lower():
                                    id_col = candidate
                                    break
                            if not id_col:
                                id_col = id_candidates[0]  # Just use first one

                if id_col:
                    id_mappings[table_name] = df[id_col].tolist()
                    logger.info(f"  🔑 Stored {len(df)} IDs from '{id_col}' column for table '{table_name}'")

                logger.info(f"  ✓ {table_name}: {len(df):,} rows → {filename}")

                # Log each table to CE Dashboard
                if "job_manager" in state and "job_id" in state:
                    job_manager = state["job_manager"]
                    job_id = state["job_id"]
                    job_manager.add_log(
                        job_id,
                        "synthetic data generator optimized",
                        f"  ✅ {table_name}: {len(df):,} rows generated",
                        "INFO"
                    )

        # Store metadata in state for summary logging
        state["table_file_metadata"] = table_file_metadata

        return generated_files

    async def _generate_single_table(
        self,
        table: Dict,
        volume_strategy: Dict,
        id_mappings: Dict,
        demo_story: Dict,
        state: Dict
    ) -> Tuple[Dict, pd.DataFrame, str]:
        """
        Generate data for a single table (runs in parallel).
        Tries LLM-based generation first, falls back to Faker.

        Returns:
            Tuple of (table, dataframe, filename)
        """
        table_name = table["name"]

        # Determine row count
        row_count = self._determine_row_count(table, volume_strategy)

        # Try LLM generation first (for dimension/master data tables)
        df = None
        customer_info = state.get("customer_info", {})

        # DEBUGGING: Log what we received
        has_customer_info = bool(customer_info and len(customer_info) > 0)
        logger.info(f"📊 Table '{table_name}': customer_info available = {has_customer_info}")
        if has_customer_info:
            logger.info(f"   - Company: {customer_info.get('company_name', 'N/A')}")

        # 🎯 ALWAYS USE LLM - No Faker fallback, no keyword filtering
        logger.info(f"🤖 Generating realistic data for {table_name} with Gemini 2.5 Pro...")

        # Log to job manager
        if "job_manager" in state and "job_id" in state:
            state["job_manager"].add_log(
                state["job_id"],
                "synthetic data generator markdown",
                f"🤖 Using LLM (Gemini 2.5 Pro) to generate realistic data for table: {table_name}",
                "INFO"
            )

        # Generate with LLM - will raise exception if it fails
        df = await self._generate_table_data_with_llm(
            table, row_count, customer_info, demo_story, id_mappings, state
        )

        # If LLM returned None, fail the pipeline (no Faker fallback)
        if df is None:
            error_msg = f"❌ LLM generation failed for {table_name}. No fallback - aborting pipeline."
            logger.error(error_msg)
            if "job_manager" in state and "job_id" in state:
                state["job_manager"].add_log(
                    state["job_id"],
                    "synthetic data generator markdown",
                    error_msg,
                    "ERROR"
                )
            raise ValueError(error_msg)

        # Save to CSV (async I/O)
        filename = f"{self.output_dir}/{table_name}.csv"

        # Use asyncio.to_thread for non-blocking CSV write
        await asyncio.to_thread(df.to_csv, filename, index=False)

        return (table, df, filename)

    def _group_by_dependency(self, tables: List[Dict]) -> List[List[Dict]]:
        """
        Group tables into dependency levels for parallel processing.

        Level 0: Tables with no dependencies (can generate first)
        Level 1: Tables that depend on level 0
        Level 2: Tables that depend on level 1, etc.

        Returns:
            List of table batches, where each batch can be generated in parallel
        """
        # Build dependency graph
        table_deps = {}
        for table in tables:
            table_name = table["name"]
            deps = set()

            # Check for foreign key dependencies
            for field in table.get("schema", []):
                field_name = field["name"]
                # Foreign keys end with _id (except primary key 'id')
                if field_name.endswith('_id') and field_name != 'id':
                    # Extract referenced table (simple heuristic)
                    ref_table = field_name.replace('_id', '')
                    logger.info(f"🔍 FK Detection: {table_name}.{field_name} → looking for table '{ref_table}' or '{ref_table}s'")
                    # Try both singular and plural forms
                    if any(t["name"] == ref_table for t in tables):
                        deps.add(ref_table)
                        logger.info(f"  ✅ Found exact match: {ref_table}")
                    elif any(t["name"] == ref_table + 's' for t in tables):
                        deps.add(ref_table + 's')
                        logger.info(f"  ✅ Found plural match: {ref_table}s")
                    else:
                        logger.warning(f"  ❌ No matching table found for FK {field_name}")

            table_deps[table_name] = deps
            if deps:
                logger.info(f"📊 {table_name} depends on: {deps}")

        # Group into levels
        levels = []
        remaining = {t["name"]: t for t in tables}
        generated = set()

        while remaining:
            # Find tables with all dependencies satisfied
            current_level = []
            for table_name, table in list(remaining.items()):
                deps = table_deps[table_name]
                if deps.issubset(generated):
                    current_level.append(table)
                    del remaining[table_name]
                    generated.add(table_name)

            if not current_level:
                # Circular dependency or unresolved - add all remaining
                logger.warning(f"Circular dependency detected. Adding {len(remaining)} tables to final batch")
                current_level = list(remaining.values())
                remaining.clear()

            levels.append(current_level)

        logger.info(f"📊 Dependency analysis: {len(levels)} levels for parallel processing")
        for i, level in enumerate(levels):
            logger.info(f"   Level {i}: {len(level)} tables ({', '.join([t['name'] for t in level])})")

        return levels

    def _determine_row_count(self, table: Dict, strategy: Dict) -> int:
        """Determine optimal row count for table."""
        table_name = table["name"]
        suggested_count = table.get("record_count", 1000)

        # Apply smart volume strategy
        if suggested_count < 100:
            return strategy["dimension_small"]
        elif suggested_count < 1000:
            return strategy["dimension_medium"]
        elif suggested_count < 10000:
            return strategy["entity_medium"]
        elif suggested_count < 50000:
            return strategy["entity_large"]
        elif suggested_count < 100000:
            return strategy["transaction_medium"]
        else:
            return strategy["transaction_large"]

    async def _generate_table_data_with_llm(
        self,
        table: Dict,
        row_count: int,
        customer_info: Dict,
        demo_story: Dict,
        id_mappings: Dict,
        state: Dict
    ) -> Optional[pd.DataFrame]:
        """
        Generate realistic table data using LLM based on company context.

        Returns None if LLM generation fails (fallback to Faker).
        """
        table_name = table["name"]
        schema_fields = table.get("schema", [])

        try:
            # Build schema description and identify foreign keys
            schema_desc = []
            foreign_key_constraints = []

            for field in schema_fields:
                field_name = field['name']
                field_type = field['type']
                schema_desc.append(f"- {field_name} ({field_type})")

                # Detect foreign key fields (end with _id, not primary key 'id')
                if field_name.endswith('_id') and field_name != 'id':
                    # Extract referenced table name
                    ref_table = field_name.replace('_id', '')

                    # Try to find matching table in id_mappings (both singular and plural)
                    valid_ids = None
                    if ref_table in id_mappings:
                        valid_ids = id_mappings[ref_table]
                    elif ref_table + 's' in id_mappings:
                        valid_ids = id_mappings[ref_table + 's']
                        ref_table = ref_table + 's'

                    if valid_ids and len(valid_ids) > 0:
                        # Sample some IDs to show in prompt
                        sample_ids = valid_ids[:min(10, len(valid_ids))]
                        foreign_key_constraints.append({
                            'field': field_name,
                            'ref_table': ref_table,
                            'valid_ids': valid_ids,
                            'sample_ids': sample_ids
                        })

            # Extract comprehensive context from research and demo story
            company_name = customer_info.get("company_name", "Unknown Company")
            industry = customer_info.get("industry", "Unknown")
            products = customer_info.get("products", [])
            business_model = customer_info.get("business_model", "")
            business_description = customer_info.get("business_description", "")
            target_customers = customer_info.get("target_customers", [])
            key_features = customer_info.get("key_features", [])

            # Extract full demo story context
            executive_summary = demo_story.get("executive_summary", "")
            business_challenges = demo_story.get("business_challenges", [])
            demo_title = demo_story.get("demo_title", "")
            key_metrics = demo_story.get("key_metrics", [])
            scenes = demo_story.get("scenes", [])
            golden_queries = demo_story.get("golden_queries", [])
            talking_track = demo_story.get("talking_track", {})

            # Build comprehensive prompt
            prompt = f"""# ROLE: Expert Data Generation Specialist

You are an expert data generation specialist tasked with creating REALISTIC, DOMAIN-SPECIFIC synthetic data for a business analytics demo. Your data must be authentic and representative of the actual business, not generic placeholder data.

## COMPANY RESEARCH & CONTEXT

**Company:** {company_name}
**Industry:** {industry}
**Business Model:** {business_model}

**Business Description:**
{business_description}

**Key Products/Services:**
{chr(10).join(f"• {product}" for product in products[:10]) if products else "• Various products and services"}

**Target Customer Segments:**
{chr(10).join(f"• {customer}" for customer in target_customers[:5]) if target_customers else "• General market"}

**Key Features/Capabilities:**
{chr(10).join(f"• {feature}" for feature in key_features[:5]) if key_features else "• Standard business operations"}

## DEMO STORY & BUSINESS CONTEXT

**Demo Title:** {demo_title}

**Executive Summary:**
{executive_summary}

**Business Challenges Being Addressed:**
{chr(10).join(f"{i+1}. {challenge if isinstance(challenge, str) else challenge.get('challenge', str(challenge))}" for i, challenge in enumerate(business_challenges[:5]))}

**Key Metrics to Support:**
{chr(10).join(f"• {metric}" for metric in key_metrics[:5]) if key_metrics else "• Revenue, growth, customer satisfaction"}

## DEMO NARRATIVE - YOUR DATA MUST TELL THIS STORY

**Demo Scenes/Flow:**
{chr(10).join(f"Scene {i+1}: {scene.get('title', scene.get('scene_title', '')) if isinstance(scene, dict) else str(scene)}" for i, scene in enumerate(scenes[:5])) if scenes else "• Standard analytics workflow"}

**Golden Queries This Data Must Answer:**
{chr(10).join(f"{i+1}. {query.get('question', query.get('query', str(query))) if isinstance(query, dict) else str(query)}" for i, query in enumerate(golden_queries[:10])) if golden_queries else "• Standard business metrics"}

**Demo Talking Track/Introduction:**
{talking_track.get('introduction', talking_track.get('opening', '')) if isinstance(talking_track, dict) and talking_track else '(Standard business analytics demo)'}

## 🎯 CRITICAL - GOLDEN QUERY ANALYSIS & DATA BLUEPRINT

**THE GOLDEN QUERIES ABOVE ARE THE MOST IMPORTANT PART OF THIS DEMO.**

Your data will be queried using the golden queries listed above. Each query MUST return insightful, demo-worthy results.

**BEFORE generating data, analyze EACH golden query and determine:**

"""

            # Add query-specific analysis for each golden query
            if golden_queries and len(golden_queries) > 0:
                prompt += "\n"
                for idx, query in enumerate(golden_queries[:10], 1):
                    query_text = query.get('question', query.get('query', str(query))) if isinstance(query, dict) else str(query)

                    prompt += f"""**Golden Query #{idx}: "{query_text}"**

📋 **Analysis:**
   1. What table fields does this query need? (Think about JOINs, WHERE clauses, GROUP BY)
   2. What data patterns would create an interesting answer?
   3. What distributions/ranges would make this query reveal insights?

💡 **Data Pattern Blueprint for Query #{idx}:**
"""

                    # Smart query analysis based on keywords
                    query_lower = query_text.lower()

                    # Comparison/Ranking queries
                    if any(word in query_lower for word in ['top', 'best', 'highest', 'most', 'leading', 'largest']):
                        prompt += f"""   - Create CLEAR WINNERS: Top 3-5 items should dominate (40-60% of total)
   - Include meaningful spread: Winner has 2-3x more than 2nd place, 5-10x more than average
   - Long tail: Include 15-20 smaller performers to show contrast
   - If by category/segment: Each segment should have its own leader
"""

                    # Trend/Time-based queries
                    elif any(word in query_lower for word in ['over time', 'trend', 'growth', 'change', 'increase', 'decrease', 'month', 'year', 'quarter']):
                        prompt += f"""   - Create TEMPORAL PATTERNS: Data should show clear trend (growth, decline, or seasonal)
   - Spread dates across 6-12 months with realistic monthly/weekly distribution
   - Growth trend: Recent months should have 20-40% more activity than 6 months ago
   - Include variation: Not perfectly linear - add realistic noise
   - Month-over-month changes should be noticeable (not flat)
"""

                    # Segmentation queries
                    elif any(word in query_lower for word in ['by region', 'by category', 'by type', 'by segment', 'breakdown', 'distribution']):
                        prompt += f"""   - Create DISTINCT SEGMENTS: 4-7 segments with different characteristics
   - Each segment should have unique pattern (e.g., Region A: high volume/low value, Region B: low volume/high value)
   - Segments should NOT be equal - create interesting imbalances (60/25/10/5 split, not 25/25/25/25)
   - Use realistic segment names for this industry
"""

                    # Average/Statistical queries
                    elif any(word in query_lower for word in ['average', 'mean', 'median', 'typical']):
                        prompt += f"""   - Create REALISTIC DISTRIBUTION: Follow normal or skewed distribution (not all same value)
   - Include outliers: A few very high and very low values (5-10% of data)
   - Mean should differ from median if there are outliers (shows interesting distribution)
   - Standard deviation should be 20-40% of mean (shows natural variation)
"""

                    # Comparison between groups
                    elif any(word in query_lower for word in ['compare', 'versus', 'vs', 'difference between', 'compared to']):
                        prompt += f"""   - Create CLEAR CONTRAST: Groups being compared should have 30-80% difference (not 5%)
   - Each group should have distinct characteristics (price, volume, behavior)
   - Include enough data in EACH group (at least 20-30 items per group)
   - Make the difference meaningful and demo-worthy
"""

                    # Problem/Issue detection queries
                    elif any(word in query_lower for word in ['error', 'failure', 'issue', 'problem', 'alert', 'incident', 'outage']):
                        prompt += f"""   - Create REALISTIC PROBLEM DISTRIBUTION:
     * 2-3% critical issues (severe, needs immediate attention)
     * 8-12% important issues (needs attention soon)
     * 20-30% minor issues (low priority)
     * 60-70% no issues (normal operation)
   - Problems should CORRELATE with factors (e.g., older products more errors, peak times more incidents)
   - Include temporal clustering: Problems cluster on certain dates/times
"""

                    # Count/Volume queries
                    elif any(word in query_lower for word in ['how many', 'count', 'number of', 'total']):
                        prompt += f"""   - Create MEANINGFUL COUNTS: Not random - should tell a story
   - If counting by category: Follow power law (few categories dominate)
   - If counting by time: Show growth or seasonal patterns
   - Include enough entities for the count to be interesting (not just 3-5)
"""

                    # Revenue/Financial queries
                    elif any(word in query_lower for word in ['revenue', 'sales', 'profit', 'cost', 'price', 'value', 'spend']):
                        prompt += f"""   - Create REALISTIC FINANCIAL PATTERNS:
     * Premium tier: High price, low volume (10-15% of items, 40-50% of revenue)
     * Mid tier: Medium price, medium volume (50-60% of items, 35-45% of revenue)
     * Budget tier: Low price, high volume (25-35% of items, 10-20% of revenue)
   - Revenue should follow Pareto: Top 20% of products/customers drive 70-80% of revenue
   - Include price variation within tiers (not all exactly $100)
"""

                    # Percentage/Ratio queries
                    elif any(word in query_lower for word in ['percentage', 'percent', 'ratio', 'proportion', 'share']):
                        prompt += f"""   - Create INTERESTING PROPORTIONS: Not 50/50 splits - create imbalance
   - Use realistic industry ratios (e.g., enterprise vs SMB: 15/85, not 50/50)
   - Percentages should reveal insights ("Wow, only 15% of customers drive 65% of revenue!")
   - Make proportions align with business challenges mentioned in demo story
"""

                    # Customer/User behavior queries
                    elif any(word in query_lower for word in ['customer', 'user', 'client', 'buyer', 'subscriber']):
                        prompt += f"""   - Create DIVERSE CUSTOMER PROFILES:
     * Company sizes: Enterprise (15%), Mid-market (30%), SMB (40%), Startup (15%)
     * Industries: Spread across 6-8 industries (not 90% in one industry)
     * Geography: 12-20 different cities/regions
     * Activity levels: Very active (10%), Active (30%), Moderate (40%), Inactive (20%)
   - Customer behavior should correlate: Enterprise customers → higher spend, longer contracts
"""

                    # Product/Item queries
                    elif any(word in query_lower for word in ['product', 'item', 'listing', 'sku', 'catalog']):
                        prompt += f"""   - Create VARIED PRODUCT PORTFOLIO:
     * Price tiers: Budget (30%), Mid-range (45%), Premium (20%), Luxury (5%)
     * Categories: Spread across 6-8 categories (not clustered in 1-2)
     * Popularity: Bestsellers (15%), Popular (30%), Average (40%), Niche (15%)
     * At least 50-80 truly distinct product names (no "Product 1", "Product 2")
"""

                    # Generic fallback for other queries
                    else:
                        prompt += f"""   - Analyze this query carefully and create data that would make it return insightful results
   - Think about what fields are needed and what patterns would be interesting
   - Avoid flat/uniform data - create variation and clustering
   - Make the answer tell a compelling business story
"""

                    prompt += "\n"

                prompt += """
**🎯 SYNTHESIS - Combine All Query Requirements:**

Now that you've analyzed each golden query above, you must generate data that satisfies ALL of them simultaneously.

Key principles:
- If Query #1 needs price tiers and Query #5 needs category spread, include BOTH
- If Query #2 needs time trends and Query #4 needs geographic diversity, include BOTH
- Create data that is "multi-dimensional" - supports multiple types of analysis
- When in doubt, add MORE variety and MORE patterns (not less)

**🎯 CRITICAL - DATA STORYTELLING REQUIREMENT:**

Your generated data MUST support the demo narrative above. The golden queries listed above are THE MOST IMPORTANT PART of this demo."""

            else:
                prompt += """

**🎯 CRITICAL - DATA STORYTELLING REQUIREMENT:**

Your generated data MUST support the demo narrative above. The golden queries listed above are THE MOST IMPORTANT PART of this demo.

## 📊 CRITICAL: DASHBOARD VISUALIZATION CONTEXT

**This data is for VISUALIZATION DASHBOARDS and BUSINESS ANALYTICS.**

Your data will be displayed in charts, graphs, and dashboards. It must have:

1. **HIGH VARIETY**: Generate DISTINCT entities - no duplicate names/titles/items
   - Every row should be UNIQUE
   - Create diverse examples across different segments
   - Aim for 80-150 truly distinct entities in this batch

2. **REALISTIC DISTRIBUTIONS** (for dashboard visualization):
   - **Power Law Pattern**: 10-15% premium/very popular, 25-30% above-average, 40-45% average, 20-25% budget/niche
   - **Geographic Variety**: If location-based, include 8-12 different regions/cities
   - **Category Spread**: If categories exist, spread across 5-8 distinct categories
   - **Value Range**: Include budget ($), mid-tier ($$), and premium ($$$) options
   - **Time Patterns**: Vary dates realistically across weeks/months (not all on same day)

3. **BUSINESS STORYTELLING**:
   - Data should reveal interesting patterns when charted
   - Create natural clusters and trends that make sense for the business
   - Include some outliers for visual interest (but keep realistic)
   - Make data "demo-worthy" - should show surprising insights when analyzed

## YOUR TASK: Generate Data for Table "{table_name}"

**Table Schema:**
{chr(10).join(schema_desc)}

**Number of Records to Generate:** {min(row_count, 200)} realistic sample records
"""

            # Add foreign key constraints section if any exist
            if foreign_key_constraints:
                prompt += f"""
## 🔑 FOREIGN KEY CONSTRAINTS - CRITICAL FOR DATA INTEGRITY

**IMPORTANT:** This table has foreign key relationships with other tables. You MUST use the exact IDs provided below.

"""
                for fk in foreign_key_constraints:
                    prompt += f"""**{fk['field']}** references table `{fk['ref_table']}`
   - **VALID IDS (use ONLY these):** {', '.join(str(id) for id in fk['sample_ids'])}
   - Total available: {len(fk['valid_ids'])} IDs
   - **REQUIREMENT:** Every row MUST use one of the valid IDs listed above for {fk['field']}
   - **DO NOT** make up new IDs - only use the exact values provided

"""

            prompt += """
## CRITICAL REQUIREMENTS - READ CAREFULLY:

1. **DOMAIN AUTHENTICITY:**
   - Use REAL terminology from {company_name}'s business domain
   - For product/listing names: Use actual product categories they sell (e.g., for OfferUp: "iPhone 13 Pro 256GB", "Vintage Leather Sofa", not "receive" or "impact")
   - For descriptions: Write realistic business descriptions, not random words
   - For categories: Use industry-standard categories relevant to their business
   - For customer data: Use realistic demographics matching their target market

2. **BUSINESS REALISM:**
   - Values should reflect real-world business patterns (e.g., prices should be realistic for the product type)
   - Dates should follow logical sequences (created_at before updated_at)
   - Status fields should use industry-standard values (not random words)
   - Geographic data should be realistic (real cities, valid zip codes)
   - Quantities and counts should be business-realistic

3. **DATA COHERENCE:**
   - Data should support the business challenges mentioned above
   - Values should create meaningful patterns for analytics
   - Related fields should be logically consistent (e.g., luxury products have higher prices)
   - Support the key metrics that will be calculated from this data

4. **SPECIFICITY EXAMPLES:**

   ❌ BAD (Generic/Random - DO NOT DO THIS):
   - Using random words: "receive", "impact", "such", "carry", "she"
   - Using meaningless descriptions: "really", "let", "number", "gas"
   - Using nonsensical categories: "enough", "plant", "yes", "tonight"
   - Using unrelated categories: "Home & Garden" for electronics, "Apparel" for software

   ✅ GOOD (Domain-Specific - DO THIS):
   - Use actual product/service names relevant to {company_name}'s industry
   - Write realistic descriptions with proper grammar and business context
   - Use industry-standard terminology and categories
   - Match data to the business model described above

   **Example for E-commerce/Marketplace:**
   - Product: "Specific item name with brand/model", not random words
   - Description: "Detailed, realistic description of condition/features", not single words

   **Example for SaaS/Software:**
   - Product: "Software plan tier or feature name", not generic terms
   - Description: "What the plan includes, pricing model", not placeholder text

   **Example for Services:**
   - Service: "Specific service offering name", not random labels
   - Description: "What's included, duration, deliverables", not vague text

5. **VARIETY & DISTRIBUTION FOR DASHBOARDS:**

   **CRITICAL - DISTINCT ENTITIES:**
   - Generate AT LEAST 100-150 TRULY DISTINCT entities (products/customers/items/records)
   - NO DUPLICATES: Every name/title must be completely different
   - NO SIMILAR VARIATIONS: Don't generate "Product A", "Product B", "Product C" - make each unique and realistic

   **REALISTIC PATTERNS FOR VISUALIZATION:**
   - Follow power law distribution: Some items very popular/expensive, long tail of niche items
   - Geographic diversity: If location fields exist, use 10-15 different cities/regions
   - Category diversity: Spread evenly across all major business categories (5-8 categories)
   - Time diversity: Spread dates across weeks/months realistically (not clustered in one day)
   - Value diversity: Include full range from low to high (e.g., $10 budget to $10,000+ premium)

   **FOR VISUALIZATION QUALITY:**
   - When this data is charted, it should show interesting, realistic patterns
   - Bar charts should have varied heights (not all bars similar height)
   - Pie charts should have meaningful segments (not one slice dominating everything)
   - Time series should show realistic trends (growth patterns, seasonality if applicable)
   - Scatter plots should show natural clustering around business segments

   **SPECIFIC EXAMPLES BY TABLE TYPE:**

   📦 **Products/Items Tables:**
   - Include variety: Budget tier ($10-50), Mid-tier ($50-200), Premium ($200-500), Luxury ($500-2000+)
   - Categories: Spread across 6-8 product categories (not 90% in one category)
   - Popularity: 15% bestsellers (high demand), 30% popular, 40% average sellers, 15% niche/specialty
   - Ensure at least 50-80 distinct product names (not variations like "Nike Shoe 1", "Nike Shoe 2")

   👥 **Customers/Users Tables:**
   - Company sizes: 15% Enterprise (10,000+ employees), 30% Mid-market (500-10K), 40% SMB (50-500), 15% Startups (<50)
   - Industries: Include 6-8 different industries (Technology, Finance, Healthcare, Retail, Manufacturing, Education, etc.)
   - Geography: Use 12-20 different cities from varied regions (US, Europe, APAC, etc.)
   - Customer lifecycle: 20% new (0-3 months), 30% active (3-12 months), 35% established (1-3 years), 15% loyal (3+ years)
   - Ensure at least 50-100 distinct customer/company names (realistic business names, not "Customer 1")

   🛒 **Orders/Transactions Tables:**
   - Order values: Follow Pareto distribution (20% of orders account for 80% of revenue - include high-value orders)
   - Value ranges: 30% small ($10-100), 40% medium ($100-500), 20% large ($500-2000), 10% very large ($2000+)
   - Frequency patterns: 10% customers order weekly, 30% monthly, 40% quarterly, 20% rarely/once
   - Recency: Spread across last 6-12 months with growth trend (more recent orders should be slightly more common)
   - Status distribution: 75% completed, 15% processing, 7% pending, 3% cancelled/refunded

   📅 **Events/Activities/Sessions Tables:**
   - Time clustering: Events should cluster during business hours (9am-6pm if B2B), weekdays > weekends
   - User activity: Follow power law (10% very active users generate 60% of events, long tail of occasional users)
   - Event types: If event types exist, realistic distribution (70% normal actions, 20% important, 8% high-priority, 2% critical)
   - Temporal spread: Distribute events across days/weeks realistically (not 100 events all on same day)
   - Session duration: Most sessions 2-10 minutes, some quick (<2 min), few long sessions (>30 min)

## OUTPUT FORMAT - CRITICAL:

Return a MARKDOWN TABLE with ALL schema fields as columns. Generate {min(row_count, 200)} realistic rows.

**Format:**
| field1 | field2 | field3 |
|--------|--------|--------|
| realistic_value1 | 123 | 2024-10-06 |
| realistic_value2 | 456 | 2024-10-05 |
| realistic_value3 | 789 | 2024-10-04 |

**RULES:**
- Use standard markdown table format with pipes (|)
- First row is the header with field names matching schema EXACTLY
- Second row is separator with dashes
- Following rows are data
- You MAY include explanatory text before or after the table (it will be ignored)
- Field names must match the schema EXACTLY (case-sensitive)
- Use realistic values appropriate for {company_name}'s business

Generate the markdown table now based on {company_name}'s actual business domain:"""

            # 🔍 LOG: Save prompt to file for debugging
            prompt_file = f"/tmp/llm_prompts/{table_name}_prompt.txt"
            os.makedirs("/tmp/llm_prompts", exist_ok=True)
            with open(prompt_file, 'w') as f:
                f.write(prompt)
            logger.info(f"📝 LLM Prompt for {table_name} saved to: {prompt_file}")
            logger.debug(f"📝 LLM Prompt preview (first 300 chars): {prompt[:300]}...")

            # Call LLM
            logger.info(f"🤖 Calling Gemini 2.0 Flash for {table_name} data generation...")
            response = await asyncio.to_thread(
                self.llm_model.generate_content,
                prompt,
                generation_config=self.generation_config
            )

            # 🔍 LOG: Save raw response to file for debugging
            response_text = response.text.strip()
            response_file = f"/tmp/llm_prompts/{table_name}_response.txt"
            with open(response_file, 'w') as f:
                f.write(response_text)
            logger.info(f"📥 LLM Response for {table_name} saved to: {response_file}")
            logger.debug(f"📥 LLM Response preview (first 500 chars): {response_text[:500]}...")

            # 🔍 PARSE MARKDOWN TABLE
            logger.info(f"📊 Parsing markdown table for {table_name}...")

            # Extract table from response (handle code blocks)
            table_text = response_text
            if "```" in table_text:
                # Extract content from markdown code block
                parts = table_text.split("```")
                for part in parts:
                    if "|" in part:  # Find the part with the table
                        table_text = part.strip()
                        break

            # Split into lines
            lines = table_text.split('\n')

            # Find table lines (lines with pipes)
            table_lines = [line for line in lines if '|' in line and line.strip().startswith('|')]

            if len(table_lines) < 3:
                logger.warning(f"❌ No valid markdown table found for {table_name} (only {len(table_lines)} lines)")
                logger.debug(f"Response preview: {response_text[:300]}")
                return None

            # Parse header (first line)
            header_line = table_lines[0]
            headers = [col.strip() for col in header_line.split('|')[1:-1]]  # Skip first/last empty
            logger.info(f"  📋 Found {len(headers)} columns: {', '.join(headers[:5])}...")

            # Parse data rows (skip header and separator)
            data_rows = []
            for line in table_lines[2:]:  # Skip header and separator
                if '|' not in line:
                    continue
                values = [val.strip() for val in line.split('|')[1:-1]]
                if len(values) == len(headers):
                    row_dict = dict(zip(headers, values))
                    data_rows.append(row_dict)

            logger.info(f"  ✅ Parsed {len(data_rows)} rows from markdown table")

            if len(data_rows) == 0:
                logger.warning(f"❌ No data rows parsed from table for {table_name}")
                return None

            # Convert to DataFrame
            df = pd.DataFrame(data_rows)

            # Type conversion: Try to convert numeric strings to numbers
            for col in df.columns:
                # Try converting to numeric (handles integers and floats)
                try:
                    df[col] = pd.to_numeric(df[col])
                except (ValueError, TypeError):
                    # If that fails, keep as string
                    pass

            # 🔧 FIX: Replace "NULL" strings with empty values for nullable fields
            # BigQuery CSV loader can't handle "NULL" as a string
            df = df.replace(['NULL', 'null', 'None', 'nan'], '')
            logger.info(f"  🔧 Cleaned NULL strings from {table_name} data")

            # 🔑 FIX: Replace invalid foreign keys with valid IDs from parent tables
            if foreign_key_constraints:
                for fk in foreign_key_constraints:
                    field_name = fk['field']
                    valid_ids = fk['valid_ids']

                    if field_name in df.columns:
                        # Check if any values are invalid
                        invalid_count = 0
                        for idx, val in enumerate(df[field_name]):
                            if val not in valid_ids:
                                # Replace with random valid ID
                                df.at[idx, field_name] = random.choice(valid_ids)
                                invalid_count += 1

                        if invalid_count > 0:
                            logger.info(f"  🔑 Fixed {invalid_count} invalid foreign keys in {field_name} (replaced with valid IDs from {fk['ref_table']})")

            # If we got fewer rows than needed, replicate with variations
            while len(df) < row_count:
                # Add variations of existing data
                base_idx = random.randint(0, min(50, len(df)) - 1)
                varied_row = df.iloc[base_idx].copy()
                df = pd.concat([df, varied_row.to_frame().T], ignore_index=True)

            # Trim to exact row count
            df = df.head(row_count)

            # Ensure IDs are sequential
            if 'id' in df.columns:
                df['id'] = range(1, len(df) + 1)
            elif f'{table_name}_id' in df.columns:
                df[f'{table_name}_id'] = range(1, len(df) + 1)

            # Validate schema match
            expected_columns = set(f["name"] for f in schema_fields)
            actual_columns = set(df.columns)

            if expected_columns != actual_columns:
                logger.warning(f"LLM schema mismatch for {table_name}. Expected: {expected_columns}, Got: {actual_columns}")
                return None

            logger.info(f"✅ LLM generated {len(df)} realistic rows for {table_name}")
            return df

        except Exception as e:
            # FIX: Improved error logging to help diagnose LLM failures
            error_type = type(e).__name__
            error_msg = str(e)[:200]
            logger.warning(f"LLM generation failed for {table_name}: {error_type} - {error_msg}")

            # Log more details for specific error types
            if error_type == "JSONDecodeError":
                logger.info(f"  → JSON parsing failed for {table_name}. Check prompt output format.")
            elif "quota" in error_msg.lower() or "rate" in error_msg.lower():
                logger.info(f"  → API quota/rate limit hit for {table_name}")

            logger.debug(f"Full LLM error for {table_name}: {e}", exc_info=True)

            # Log to job manager with more detail
            if "job_manager" in state and "job_id" in state:
                state["job_manager"].add_log(
                    state["job_id"],
                    "synthetic data generator optimized",
                    f"⚠️ LLM generation failed for {table_name}: {error_type} (using Faker fallback)",
                    "WARNING"
                )
            return None

    def _generate_table_data(
        self,
        table: Dict,
        row_count: int,
        id_mappings: Dict,
        demo_story: Dict
    ) -> pd.DataFrame:
        """Generate data for a single table (Faker fallback)."""
        schema_fields = table.get("schema", [])
        table_name = table["name"]

        # Build data dictionary
        data = {}

        for field in schema_fields:
            field_name = field["name"]
            field_type = field["type"]

            data[field_name] = self._generate_field_data(
                field_name,
                field_type,
                row_count,
                table_name,
                id_mappings,
                demo_story
            )

        return pd.DataFrame(data)

    def _generate_field_data(
        self,
        field_name: str,
        field_type: str,
        row_count: int,
        table_name: str,
        id_mappings: Dict,
        demo_story: Dict
    ) -> List:
        """Generate data for a single field with realistic patterns."""

        # Primary keys
        if field_name in ['id', f'{table_name}_id', 'order_id', 'customer_id', 'product_id', 'store_id']:
            if field_name == 'id' or field_name == f'{table_name}_id':
                return list(range(1, row_count + 1))

        # Foreign keys
        if field_name.endswith('_id') and field_name != 'id':
            # Extract referenced table name
            ref_table = field_name.replace('_id', '')
            # Try plural form first
            if ref_table + 's' in id_mappings:
                return random.choices(id_mappings[ref_table + 's'], k=row_count)
            elif ref_table in id_mappings:
                return random.choices(id_mappings[ref_table], k=row_count)
            # Fallback
            return [random.randint(1, 1000) for _ in range(row_count)]

        # Timestamps
        if field_type == 'TIMESTAMP' or 'created_at' in field_name or 'updated_at' in field_name or '_at' in field_name:
            return self._generate_timestamps(row_count, field_name)

        # Dates
        if field_type == 'DATE' or '_date' in field_name:
            return [fake.date_between('-12m', 'today') for _ in range(row_count)]

        # Strings
        if field_type == 'STRING':
            return self._generate_string_data(field_name, row_count)

        # Numbers
        if field_type in ['INT64', 'INTEGER']:
            return self._generate_integer_data(field_name, row_count)

        if field_type in ['FLOAT64', 'NUMERIC', 'DECIMAL']:
            return self._generate_float_data(field_name, row_count)

        # Booleans
        if field_type in ['BOOL', 'BOOLEAN']:
            return [random.choice([True, False]) for _ in range(row_count)]

        # Default
        return [None] * row_count

    def _generate_timestamps(self, count: int, field_name: str) -> List[datetime]:
        """Generate timestamps with patterns."""
        base_date = datetime.now()

        if 'created' in field_name:
            # Spread over last 12 months with seasonal patterns
            timestamps = []
            for _ in range(count):
                days_ago = random.randint(0, 365)
                # More recent data is more common
                if random.random() < 0.3:
                    days_ago = random.randint(0, 90)  # 30% in last 90 days

                ts = base_date - timedelta(days=days_ago)
                timestamps.append(ts)
            return timestamps

        elif 'updated' in field_name:
            # Updated timestamps are more recent
            return [base_date - timedelta(days=random.randint(0, 60)) for _ in range(count)]

        else:
            return [base_date - timedelta(days=random.randint(0, 365)) for _ in range(count)]

    def _generate_string_data(self, field_name: str, count: int) -> List[str]:
        """Generate string data based on field name."""
        field_lower = field_name.lower()

        # Names
        if 'name' in field_lower and 'product' in field_lower:
            products = ["T-Shirt", "Jeans", "Dress", "Sneakers", "Jacket", "Hoodie",
                       "Shorts", "Skirt", "Boots", "Sandals", "Hat", "Scarf"]
            adjectives = ["Classic", "Premium", "Vintage", "Modern", "Casual", "Formal"]
            return [f"{random.choice(adjectives)} {random.choice(products)}" for _ in range(count)]

        if 'first_name' in field_lower or 'fname' in field_lower:
            return [fake.first_name() for _ in range(count)]

        if 'last_name' in field_lower or 'lname' in field_lower:
            return [fake.last_name() for _ in range(count)]

        if 'company' in field_lower or 'merchant' in field_lower:
            return [fake.company() for _ in range(count)]

        # Contact
        if 'email' in field_lower:
            return [fake.email() for _ in range(count)]

        if 'phone' in field_lower:
            return [fake.phone_number() for _ in range(count)]

        # Address
        if 'address' in field_lower or 'street' in field_lower:
            return [fake.street_address() for _ in range(count)]

        if 'city' in field_lower:
            return [fake.city() for _ in range(count)]

        if 'state' in field_lower or 'province' in field_lower:
            return [fake.state_abbr() for _ in range(count)]

        if 'country' in field_lower:
            return [fake.country_code() for _ in range(count)]

        if 'zip' in field_lower or 'postal' in field_lower:
            return [fake.zipcode() for _ in range(count)]

        # Status fields
        if 'status' in field_lower:
            statuses = ["pending", "processing", "completed", "shipped", "delivered", "cancelled", "returned"]
            # Realistic distribution (most orders are completed)
            weights = [0.05, 0.10, 0.50, 0.20, 0.10, 0.03, 0.02]
            return random.choices(statuses, weights=weights, k=count)

        # Channel
        if 'channel' in field_lower:
            channels = ["online_store", "pos", "instagram", "facebook", "mobile_app", "amazon", "tiktok"]
            return random.choices(channels, k=count)

        # Category
        if 'category' in field_lower:
            categories = ["Apparel", "Footwear", "Accessories", "Electronics", "Home & Garden",
                         "Beauty", "Sports", "Books", "Toys", "Food & Beverage"]
            return random.choices(categories, k=count)

        # Default
        return [fake.word() for _ in range(count)]

    def _generate_integer_data(self, field_name: str, count: int) -> List[int]:
        """Generate integer data based on field name."""
        field_lower = field_name.lower()

        if 'quantity' in field_lower or 'qty' in field_lower:
            return [random.randint(1, 10) for _ in range(count)]

        if 'count' in field_lower or 'num_of' in field_lower:
            return [random.randint(1, 5) for _ in range(count)]

        if 'age' in field_lower:
            return [random.randint(18, 75) for _ in range(count)]

        if 'stock' in field_lower or 'inventory' in field_lower:
            return [random.randint(0, 500) for _ in range(count)]

        # Default
        return [random.randint(1, 1000) for _ in range(count)]

    def _generate_float_data(self, field_name: str, count: int) -> List[float]:
        """Generate float data based on field name."""
        field_lower = field_name.lower()

        if 'price' in field_lower or 'cost' in field_lower:
            return [round(random.uniform(10.0, 500.0), 2) for _ in range(count)]

        if 'total' in field_lower or 'amount' in field_lower or 'revenue' in field_lower:
            return [round(random.uniform(20.0, 2000.0), 2) for _ in range(count)]

        if 'tax' in field_lower:
            return [round(random.uniform(0.0, 50.0), 2) for _ in range(count)]

        if 'discount' in field_lower:
            return [round(random.uniform(0.0, 100.0), 2) for _ in range(count)]

        if 'shipping' in field_lower:
            return [round(random.uniform(0.0, 50.0), 2) for _ in range(count)]

        if 'rate' in field_lower or 'percentage' in field_lower:
            return [round(random.uniform(0.0, 1.0), 4) for _ in range(count)]

        # Default
        return [round(random.uniform(0.0, 1000.0), 2) for _ in range(count)]

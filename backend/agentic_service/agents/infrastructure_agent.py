"""
Infrastructure Agent - Provisions BigQuery resources and loads data.

Creates:
- Dataset with smart naming (company_name_capi_demo_YYYYMMDD)
- Tables with proper schemas
- Loads synthetic data
- CAPI Data Agent with system instructions
- Generates demo documentation with statistics
"""
import logging
import os
from typing import Dict, List
from datetime import datetime
from google.cloud import bigquery
from google.cloud import geminidataanalytics
from google.api_core import exceptions

logger = logging.getLogger(__name__)


class InfrastructureAgent:
    """Agent for provisioning BigQuery infrastructure."""

    def __init__(self):
        self.project_id = os.getenv("PROJECT_ID", "bq-demos-469816")
        self.location = os.getenv("BQ_LOCATION", "US")  # BigQuery location
        self.client = bigquery.Client(project=self.project_id)
        logger.info(f"Infrastructure Agent initialized for project {self.project_id}")

    async def execute(self, state: Dict) -> Dict:
        """Execute infrastructure provisioning phase."""
        logger.info("Provisioning BigQuery infrastructure")

        try:
            schema = state.get("schema", {})
            demo_story = state.get("demo_story", {})
            customer_info = state.get("customer_info", {})
            data_files = state.get("synthetic_data_files", [])

            if not schema or not data_files:
                raise ValueError("Missing schema or synthetic data files")

            # Generate dataset name with prefix
            dataset_id = self._generate_dataset_name(customer_info)

            # Log to CE Dashboard - dataset creation
            if "job_manager" in state and "job_id" in state:
                job_manager = state["job_manager"]
                job_id = state["job_id"]
                job_manager.add_log(
                    job_id,
                    "infrastructure agent",
                    f"📊 Creating BigQuery Dataset: {dataset_id}",
                    "INFO"
                )

            # Create dataset
            dataset_ref = await self._create_dataset(dataset_id, customer_info, demo_story)

            # Log dataset created
            if "job_manager" in state and "job_id" in state:
                job_manager.add_log(
                    job_id,
                    "infrastructure agent",
                    f"✅ Dataset Created: {self.project_id}.{dataset_id}",
                    "INFO"
                )

                job_manager.add_log(
                    job_id,
                    "infrastructure agent",
                    f"📤 Loading data into {len(schema.get('tables', []))} tables...",
                    "INFO"
                )

            # Create tables and load data
            table_stats = await self._create_and_load_tables(
                dataset_ref,
                schema,
                data_files,
                state  # Pass state for logging
            )

            # Generate demo documentation
            demo_docs = await self._generate_demo_documentation(
                dataset_id,
                customer_info,
                demo_story,
                table_stats
            )

            # Create CAPI Data Agent
            capi_agent_id = await self._create_capi_agent(
                dataset_id,
                customer_info,
                demo_story,
                state
            )

            # Update state
            state["dataset_id"] = dataset_id
            state["dataset_full_name"] = f"{self.project_id}.{dataset_id}"
            state["table_stats"] = table_stats
            state["demo_documentation"] = demo_docs
            state["capi_agent_id"] = capi_agent_id
            state["capi_agent_created"] = True
            state["bigquery_provisioned"] = True

            logger.info(f"✅ Infrastructure provisioned: {dataset_id}")
            logger.info(f"   Dataset: {self.project_id}.{dataset_id}")
            logger.info(f"   Tables: {len(table_stats)}")
            logger.info(f"   Total rows: {sum(s['row_count'] for s in table_stats.values()):,}")
            logger.info(f"   CAPI Agent: {capi_agent_id}")

            return state

        except Exception as e:
            logger.error(f"Infrastructure provisioning failed: {e}", exc_info=True)
            raise

    def _generate_dataset_name(self, customer_info: Dict) -> str:
        """Generate dataset name: company_capi_demo_YYYYMMDD"""
        company_name = customer_info.get("company_name", "demo")

        # Clean company name (lowercase, replace spaces/special chars with underscores)
        clean_name = company_name.lower()
        clean_name = ''.join(c if c.isalnum() else '_' for c in clean_name)
        clean_name = '_'.join(filter(None, clean_name.split('_')))  # Remove duplicate underscores

        # Add prefix and timestamp
        timestamp = datetime.now().strftime("%Y%m%d")
        dataset_id = f"{clean_name}_capi_demo_{timestamp}"

        # BigQuery dataset names must be <= 1024 chars, alphanumeric + underscores
        if len(dataset_id) > 1024:
            dataset_id = dataset_id[:1024]

        return dataset_id

    async def _create_capi_agent(
        self,
        dataset_id: str,
        customer_info: Dict,
        demo_story: Dict,
        state: Dict
    ) -> str:
        """Create CAPI Data Agent programmatically."""
        logger.info("Creating CAPI Data Agent...")

        try:
            client = geminidataanalytics.DataAgentServiceClient()

            # Get YAML content from state (generated by CAPI Instructions Agent)
            yaml_content = state.get("capi_system_instructions", "")
            if not yaml_content:
                logger.warning("No YAML system instructions found, using basic config")
                yaml_content = f"You are a helpful assistant for {customer_info.get('company_name', 'Demo Company')}."

            # Generate unique agent display name AND agent_id
            company_name = customer_info.get("company_name", "Demo Company")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            display_name = f"{company_name} CAPI Demo Agent {timestamp}"

            # Generate unique agent ID (alphanumeric + underscores only, lowercase)
            clean_company = ''.join(c if c.isalnum() else '_' for c in company_name.lower())
            data_agent_id = f"{clean_company}_demo_{timestamp}"

            # Build agent configuration
            agent = geminidataanalytics.DataAgent()
            agent.display_name = display_name

            # Set system instruction from YAML
            published_context = geminidataanalytics.Context()
            published_context.system_instruction = yaml_content

            # FIX: Use datasource_references dict (like api.py) instead of Datasource object
            # Extract table names from schema (stored in state by Data Modeling Agent)
            schema = state.get("schema", {})
            table_names = [table["name"] for table in schema.get("tables", [])]

            # Build table references
            table_references = [
                {"project_id": self.project_id, "dataset_id": dataset_id, "table_id": table_name}
                for table_name in table_names
            ]

            # Create datasource_references dict
            datasource_references = {"bq": {"table_references": table_references}}

            # FIX: Use correct API structure - data_analytics_agent.published_context (not agent.published_context)
            # This matches api.py lines 84-96
            agent.data_analytics_agent.published_context = published_context
            agent.data_analytics_agent.published_context.datasource_references = datasource_references

            # Create the agent (with explicit ID like api.py does)
            request = geminidataanalytics.CreateDataAgentRequest(
                parent=f"projects/{self.project_id}/locations/global",
                data_agent_id=data_agent_id,  # Provide ID upfront
                data_agent=agent
            )

            # Create agent (returns Operation, but we don't need to wait since we have the ID)
            client.create_data_agent(request=request)

            logger.info(f"✅ Created CAPI Data Agent: {data_agent_id}")
            logger.info(f"   Display Name: {display_name}")
            logger.info(f"   Dataset: {self.project_id}.{dataset_id}")

            return data_agent_id

        except Exception as e:
            logger.error(f"Failed to create CAPI agent: {e}", exc_info=True)
            # Return empty string on failure - don't fail the whole pipeline
            logger.warning("Continuing without CAPI agent - must be created manually")
            return ""

    async def _create_dataset(
        self,
        dataset_id: str,
        customer_info: Dict,
        demo_story: Dict
    ) -> bigquery.DatasetReference:
        """Create BigQuery dataset with description."""
        dataset_ref = self.client.dataset(dataset_id)

        # Build comprehensive description
        company_name = customer_info.get("company_name", "Demo Company")
        industry = customer_info.get("industry", "Business")
        demo_title = demo_story.get("demo_title", "Conversational Analytics Demo")

        description = f"""
🎯 CONVERSATIONAL ANALYTICS API DEMO

Company: {company_name}
Industry: {industry}
Demo: {demo_title}

📊 DATASET PURPOSE:
This dataset contains synthetic data designed to demonstrate Google Cloud's
Conversational Analytics API capabilities for {company_name}.

The data enables natural language queries that showcase:
- Complex multi-table JOINs
- Advanced aggregations and window functions
- Time-series analysis and trends
- Customer segmentation and cohort analysis
- Geographic and channel performance insights

🤖 GENERATED BY:
Agentic CAPI Demo Generator
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}
Project: {self.project_id}

⚠️ NOTE: All data is synthetic and for demonstration purposes only.
""".strip()

        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = self.location
        dataset.description = description

        # Set labels for organization
        # BigQuery labels: only lowercase letters, numbers, underscores, hyphens
        clean_company_label = company_name.lower()
        clean_company_label = ''.join(c if c.isalnum() or c == '-' else '_' for c in clean_company_label)
        clean_company_label = '_'.join(filter(None, clean_company_label.split('_')))  # Remove duplicate underscores

        dataset.labels = {
            "purpose": "capi_demo",
            "company": clean_company_label[:63],  # Label max 63 chars
            "generated_by": "agentic_demo_generator",
            "environment": "demo"
        }

        try:
            dataset = self.client.create_dataset(dataset, exists_ok=False)
            logger.info(f"Created dataset: {dataset_id}")
        except exceptions.Conflict:
            logger.warning(f"Dataset {dataset_id} already exists, using existing")
            dataset = self.client.get_dataset(dataset_ref)

        return dataset_ref

    async def _create_and_load_tables(
        self,
        dataset_ref: bigquery.DatasetReference,
        schema: Dict,
        data_files: List[str],
        state: Dict = None
    ) -> Dict:
        """Create tables and load data from CSV files."""
        table_stats = {}

        for table_def in schema.get("tables", []):
            table_name = table_def["name"]

            # Find corresponding CSV file
            csv_file = None
            for filepath in data_files:
                if os.path.basename(filepath).replace('.csv', '') == table_name:
                    csv_file = filepath
                    break

            if not csv_file or not os.path.exists(csv_file):
                logger.warning(f"No data file found for {table_name}, skipping")
                continue

            # Create table
            table_ref = dataset_ref.table(table_name)
            bq_schema = self._convert_schema_to_bigquery(table_def["schema"])

            table = bigquery.Table(table_ref, schema=bq_schema)
            table.description = table_def.get("description", "")

            try:
                table = self.client.create_table(table, exists_ok=True)
                logger.info(f"Created table: {table_name}")
            except Exception as e:
                logger.error(f"Failed to create table {table_name}: {e}")
                continue

            # Load data from CSV
            # CSV doesn't support REPEATED fields, so we need to modify the schema for loading
            csv_schema = self._convert_schema_for_csv_load(bq_schema)

            job_config = bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.CSV,
                skip_leading_rows=1,  # Skip header
                autodetect=False,
                schema=csv_schema,
                write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
            )

            with open(csv_file, "rb") as source_file:
                load_job = self.client.load_table_from_file(
                    source_file,
                    table_ref,
                    job_config=job_config
                )

            # Wait for job to complete
            load_job.result()

            # Get table stats
            table = self.client.get_table(table_ref)
            table_stats[table_name] = {
                "row_count": table.num_rows,
                "size_mb": table.num_bytes / (1024 * 1024),
                "created": table.created.isoformat(),
                "full_name": f"{self.project_id}.{dataset_ref.dataset_id}.{table_name}"
            }

            logger.info(f"  ✓ Loaded {table.num_rows:,} rows into {table_name}")

            # Log to CE Dashboard
            if state and "job_manager" in state and "job_id" in state:
                job_manager = state["job_manager"]
                job_id = state["job_id"]
                job_manager.add_log(
                    job_id,
                    "infrastructure agent",
                    f"  ✅ {table_name}: {table.num_rows:,} rows ({table.num_bytes / (1024 * 1024):.2f} MB)",
                    "INFO"
                )

        return table_stats

    def _convert_schema_to_bigquery(self, schema_fields: List[Dict]) -> List[bigquery.SchemaField]:
        """Convert our schema format to BigQuery SchemaField objects."""
        bq_fields = []

        for field in schema_fields:
            field_name = field["name"]
            field_type = field["type"]
            field_mode = field.get("mode", "NULLABLE")
            field_desc = field.get("description", "")

            bq_fields.append(bigquery.SchemaField(
                name=field_name,
                field_type=field_type,
                mode=field_mode,
                description=field_desc
            ))

        return bq_fields

    def _convert_schema_for_csv_load(self, bq_schema: List[bigquery.SchemaField]) -> List[bigquery.SchemaField]:
        """Convert schema for CSV loading by changing REPEATED fields to STRING.

        CSV format doesn't support REPEATED (array) fields. This function converts
        REPEATED fields to STRING type so they can be loaded from CSV as comma-separated values.
        """
        csv_schema = []

        for field in bq_schema:
            if field.mode == "REPEATED":
                # Convert REPEATED fields to STRING for CSV loading
                csv_schema.append(bigquery.SchemaField(
                    name=field.name,
                    field_type="STRING",  # Store as comma-separated string
                    mode="NULLABLE",
                    description=field.description
                ))
            else:
                # Keep other fields as-is
                csv_schema.append(field)

        return csv_schema

    async def _generate_demo_documentation(
        self,
        dataset_id: str,
        customer_info: Dict,
        demo_story: Dict,
        table_stats: Dict
    ) -> Dict:
        """Generate comprehensive demo documentation with statistics."""
        company_name = customer_info.get("company_name", "Demo Company")
        industry = customer_info.get("industry", "Business")
        demo_title = demo_story.get("demo_title", "Conversational Analytics Demo")
        executive_summary = demo_story.get("executive_summary", "")

        total_rows = sum(s["row_count"] for s in table_stats.values())
        total_size_mb = sum(s["size_mb"] for s in table_stats.values())

        # Build documentation
        docs = {
            "demo_metadata": {
                "title": demo_title,
                "company": company_name,
                "industry": industry,
                "dataset": f"{self.project_id}.{dataset_id}",
                "generated_at": datetime.now().isoformat(),
                "location": self.location
            },
            "executive_summary": executive_summary,
            "dataset_statistics": {
                "total_tables": len(table_stats),
                "total_rows": total_rows,
                "total_size_mb": round(total_size_mb, 2),
                "tables": table_stats
            },
            "quick_start_guide": {
                "step_1": f"Open BigQuery Console: https://console.cloud.google.com/bigquery?project={self.project_id}&d={dataset_id}",
                "step_2": "Navigate to Conversational Analytics API",
                "step_3": "Create a data agent pointing to this dataset",
                "step_4": "Try the golden queries below",
                "step_5": "Watch complex SQL be generated from natural language!"
            },
            "golden_queries": demo_story.get("golden_queries", []),
            "table_descriptions": self._generate_table_descriptions(table_stats, demo_story),
            "demo_narrative": demo_story.get("demo_narrative", {}),
            "business_challenges": demo_story.get("business_challenges", [])
        }

        # Generate markdown report
        markdown_report = self._generate_markdown_report(docs)

        # Save report
        report_file = f"/tmp/DEMO_REPORT_{dataset_id}.md"
        with open(report_file, 'w') as f:
            f.write(markdown_report)

        docs["report_file"] = report_file
        logger.info(f"📄 Demo report generated: {report_file}")

        return docs

    def _generate_table_descriptions(self, table_stats: Dict, demo_story: Dict) -> Dict:
        """Generate human-readable table descriptions."""
        descriptions = {}

        for table_name, stats in table_stats.items():
            descriptions[table_name] = {
                "name": table_name,
                "rows": f"{stats['row_count']:,}",
                "size": f"{stats['size_mb']:.2f} MB",
                "full_name": stats["full_name"],
                "purpose": f"Contains {stats['row_count']:,} rows of {table_name} data"
            }

        return descriptions

    def _generate_markdown_report(self, docs: Dict) -> str:
        """Generate comprehensive markdown demo report."""
        metadata = docs["demo_metadata"]
        stats = docs["dataset_statistics"]

        report = f"""# 🎯 {metadata['title']}

## Demo Overview

**Company:** {metadata['company']}
**Industry:** {metadata['industry']}
**Dataset:** `{metadata['dataset']}`
**Location:** {metadata['location']}
**Generated:** {metadata['generated_at']}

---

## Executive Summary

{docs['executive_summary']}

---

## 📊 Dataset Statistics

| Metric | Value |
|--------|-------|
| **Total Tables** | {stats['total_tables']} |
| **Total Rows** | {stats['total_rows']:,} |
| **Total Size** | {stats['total_size_mb']} MB |

### Table Breakdown

| Table | Rows | Size | Full Name |
|-------|------|------|-----------|
"""

        for table_name, table_stats in stats["tables"].items():
            report += f"| `{table_name}` | {table_stats['row_count']:,} | {table_stats['size_mb']:.2f} MB | `{table_stats['full_name']}` |\n"

        report += f"""
---

## 🚀 Quick Start Guide

{self._format_quick_start(docs['quick_start_guide'])}

---

## 💡 Golden Queries

Try these questions to see Conversational Analytics API in action:

"""

        for i, query in enumerate(docs.get("golden_queries", [])[:10], 1):
            complexity = query.get("complexity", "medium")
            question = query.get("question", "")
            business_value = query.get("business_value", "")

            report += f"""### {i}. {question}

**Complexity:** {complexity.upper()}
**Business Value:** {business_value}

---

"""

        report += f"""
## 📖 Demo Narrative

{docs.get('demo_narrative', {}).get('introduction', '')}

---

## 🎬 Business Challenges Addressed

"""

        for i, challenge in enumerate(docs.get("business_challenges", []), 1):
            report += f"""### {i}. {challenge.get('challenge', '')}

**Current Limitation:** {challenge.get('current_limitation', '')}

**Impact:** {challenge.get('impact', '')}

---

"""

        report += """
## ⚠️ Important Notes

- All data is **synthetic** and for **demonstration purposes only**
- Generated by the Agentic CAPI Demo Generator
- Optimized for showcasing Conversational Analytics API capabilities
- Includes realistic patterns, trends, and anomalies for compelling demos

---

## 📞 Support

For questions about this demo:
1. Review the demo narrative above
2. Try the golden queries in sequence
3. Experiment with your own questions!

**Happy Demoing! 🎉**
"""

        return report

    def _format_quick_start(self, guide: Dict) -> str:
        """Format quick start guide as numbered list."""
        steps = []
        for key in sorted(guide.keys()):
            steps.append(f"{len(steps) + 1}. {guide[key]}")
        return "\n".join(steps)

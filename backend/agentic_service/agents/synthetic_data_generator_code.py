"""
Synthetic Data Generator - CODE EXECUTION VERSION.
Uses Claude to generate Python code that creates realistic demo data using Faker/numpy.

KEY FEATURES:
- Claude generates self-contained Python scripts based on schema
- Code uses Faker + numpy for realistic, business-appropriate data
- No LLM calls during data generation (faster, deterministic)
- Executes generated code in controlled environment
- Parallel table generation support

WHY CODE-BASED:
- Much faster than LLM-per-row generation
- More control over data distributions and relationships
- Deterministic and reproducible
- Better for large datasets (100K+ rows)
- Claude ensures code quality and business logic
"""
import logging
import os
import asyncio
import json
import tempfile
import subprocess
import sys
from typing import Dict, List, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class SyntheticDataGeneratorCode:
    """CODE VERSION: Generates realistic synthetic data by executing Claude-generated Python code."""

    def __init__(self):
        self.output_dir = "/tmp/synthetic_data"
        os.makedirs(self.output_dir, exist_ok=True)

        # Initialize Claude client (Anthropic Vertex AI)
        from anthropic import AnthropicVertex

        project_id = os.environ.get("DEVSHELL_PROJECT_ID", "bq-demos-469816")
        self.claude_client = AnthropicVertex(
            region="us-east5",
            project_id=project_id
        )

        logger.info("🤖 Using Claude Sonnet 4.5 for code generation (Vertex AI)")
        logger.info(f"Synthetic Data Generator CODE initialized. Output: {self.output_dir}")

    async def execute(self, state: Dict) -> Dict:
        """Execute synthetic data generation by generating and running Python code."""
        import time

        logger.info("🚀 Generating synthetic data using CODE EXECUTION approach")
        logger.info(f"🔍 State keys received: {list(state.keys())}")

        # Extract required data from state
        customer_info = state.get("customer_info", {})
        demo_story = state.get("demo_story", {})
        schema = state.get("schema", {})
        project_id = state.get("project_id")

        # Validate inputs
        if not customer_info or not isinstance(customer_info, dict):
            error_msg = "❌ CRITICAL: customer_info is missing! Cannot generate business-realistic code."
            logger.error(error_msg)
            raise ValueError(error_msg)

        if not schema or not schema.get("tables"):
            error_msg = "❌ CRITICAL: schema is missing or has no tables!"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Log to job manager
        if "job_manager" in state and "job_id" in state:
            job_manager = state["job_manager"]
            job_id = state["job_id"]
            job_manager.add_log(
                job_id,
                "synthetic data generator code",
                f"🔧 Generating Python code for {len(schema['tables'])} tables using Claude...",
                "INFO"
            )

        start_time = time.time()

        try:
            # Step 1: Generate Python code using Claude
            logger.info("📝 Step 1: Generating Python code with Claude...")
            python_code = await self._generate_data_creation_code(
                customer_info, demo_story, schema, project_id, state
            )

            # Step 2: Execute the generated code
            logger.info("⚙️  Step 2: Executing generated Python code...")
            generated_files = await self._execute_data_generation_code(
                python_code, schema, state
            )

            elapsed = time.time() - start_time

            # Calculate total rows
            total_rows = sum(
                metadata.get("row_count", 0)
                for metadata in state.get("table_file_metadata", [])
            )

            logger.info(f"✅ Synthetic data generation complete in {elapsed:.1f}s")
            logger.info(f"   Generated {total_rows:,} total rows across {len(generated_files)} tables")

            # Update state
            state["synthetic_data_files"] = generated_files
            state["data_generation_complete"] = True

            # Log to job manager
            if "job_manager" in state and "job_id" in state:
                job_manager.add_log(
                    job_id,
                    "synthetic data generator code",
                    f"✅ Code execution complete: {total_rows:,} rows in {elapsed:.1f}s",
                    "INFO"
                )

            return state

        except Exception as e:
            logger.error(f"Synthetic data generation failed: {e}", exc_info=True)
            if "job_manager" in state and "job_id" in state:
                job_manager.add_log(
                    job_id,
                    "synthetic data generator code",
                    f"❌ Code generation failed: {str(e)}",
                    "ERROR"
                )
            raise

    async def _generate_data_creation_code(
        self,
        customer_info: Dict,
        demo_story: Dict,
        schema: Dict,
        project_id: str,
        state: Dict
    ) -> str:
        """Use Claude to generate Python code that creates synthetic data."""

        # Build context for Claude
        company_name = customer_info.get("company_name", "Unknown Company")
        business_description = customer_info.get("business_description", "")
        demo_title = demo_story.get("demo_title", "")

        # Extract table schemas in a clear format
        tables_summary = []
        for table in schema.get("tables", []):
            table_info = {
                "name": table["name"],
                "description": table.get("description", ""),
                "fields": [
                    {
                        "name": f["name"],
                        "type": f["type"],
                        "mode": f.get("mode", "NULLABLE"),
                        "description": f.get("description", "")
                    }
                    for f in table.get("schema", [])
                ]
            }
            tables_summary.append(table_info)

        # Determine row counts based on DEMO_NUM_ENTITIES env var
        num_entities = int(os.environ.get("DEMO_NUM_ENTITIES", "8"))
        base_rows = num_entities * 1000  # Scale with complexity

        prompt = f"""You are a Python code generator expert. Generate a complete, self-contained Python script that creates realistic synthetic data for BigQuery tables.

BUSINESS CONTEXT:
- Company: {company_name}
- Description: {business_description}
- Demo Title: {demo_title}

DATASET SCHEMA:
{json.dumps(tables_summary, indent=2)}

TARGET ROW COUNTS:
- Dimension tables (users, products, etc.): {num_entities * 500} - {num_entities * 1000} rows
- Fact tables (transactions, events, etc.): {num_entities * 2000} - {num_entities * 5000} rows

REQUIREMENTS:
1. Generate a Python script that uses:
   - pandas for DataFrames
   - Faker for realistic fake data (names, addresses, dates, etc.)
   - numpy for distributions and random data
   - uuid for IDs
   - google.cloud.bigquery for uploading to BigQuery

2. The script should:
   - Define constants for row counts at the top
   - Create separate functions for each table (e.g., generate_user_profiles(), generate_transactions())
   - Handle foreign key relationships correctly (store IDs from dimension tables, reference them in fact tables)
   - Use realistic distributions (Zipf for popularity, normal for quantities, etc.)
   - Include proper data validation and type handling
   - Upload each DataFrame to BigQuery with error handling

3. Data should be business-realistic:
   - Use Faker to generate names, addresses, emails, phone numbers, etc.
   - Use industry-appropriate values (e.g., for {company_name}, generate data that makes sense for their business)
   - Ensure dates are in logical order (created_at before updated_at, etc.)
   - Use weighted distributions for realistic patterns

4. Code structure:
   ```python
   import pandas as pd
   import pyarrow  # Required for load_table_from_dataframe
   import uuid
   import random
   import numpy as np
   from faker import Faker
   from datetime import datetime, timedelta
   from google.cloud import bigquery

   # Configuration
   NUM_USERS = 5000
   NUM_TRANSACTIONS = 50000
   DATASET_NAME = "{schema.get('dataset_name', 'demo_dataset')}"
   PROJECT_ID = "{project_id}"

   fake = Faker()
   client = bigquery.Client(project=PROJECT_ID)

   # CRITICAL: Use system date for current time
   TODAY = datetime.now()
   # Generate data for the past (e.g., last 2 years for customers, last 6 months for transactions)
   # Always ensure start_date < end_date to avoid empty ranges

   def generate_table_1():
       ...
       return pd.DataFrame(data)

   def generate_table_2(table_1_df):
       ...
       return pd.DataFrame(data)

   def upload_to_bigquery(df, table_name, dataset_name, project_id):
       \"\"\"Upload DataFrame to BigQuery table.\"\"\"
       from google.cloud import bigquery
       from google.api_core import exceptions

       client = bigquery.Client(project=project_id)
       dataset_id = f"{{project_id}}.{{dataset_name}}"
       table_id = f"{{dataset_id}}.{{table_name}}"

       # Create dataset if it doesn't exist
       dataset = bigquery.Dataset(dataset_id)
       dataset.location = "US"
       try:
           dataset = client.create_dataset(dataset, exists_ok=True)
           print(f"Dataset {{dataset_id}} ready")
       except Exception as e:
           print(f"Dataset check: {{e}}")

       # Configure load job
       job_config = bigquery.LoadJobConfig(
           write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
       )

       # Upload DataFrame
       print(f"Uploading {{len(df)}} rows to {{table_id}}...")
       job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
       job.result()  # Wait for job to complete

       print(f"✅ Successfully uploaded {{len(df)}} rows to {{table_id}}")

   if __name__ == "__main__":
       # Generate tables in dependency order
       table_1_df = generate_table_1()
       table_2_df = generate_table_2(table_1_df)

       # Upload to BigQuery
       upload_to_bigquery(table_1_df, "table_1", DATASET_NAME, PROJECT_ID)
       upload_to_bigquery(table_2_df, "table_2", DATASET_NAME, PROJECT_ID)
   ```

5. IMPORTANT:
   - Do NOT use REPEATED fields - convert arrays to comma-separated strings
   - Ensure all timestamps are timezone-naive (use .dt.tz_localize(None))
   - Use WRITE_TRUNCATE to overwrite existing tables
   - Include try/except blocks for upload errors
   - Print progress messages
   - CRITICAL: Always use datetime objects (not date objects) to avoid type mixing errors
   - When creating helper functions for dates, ensure consistent types (datetime + timedelta, not date + timedelta)

6. CODE QUALITY AND DATE HANDLING:
   - Use datetime.now() to get TODAY, then generate all dates in the past
   - Example: customer created 2 years ago → TODAY - timedelta(days=730)
   - Example: orders in last 6 months → between (TODAY - timedelta(days=180)) and TODAY
   - ALWAYS ensure start_date < end_date before calling random helpers
   - In random_datetime_between() helper:
     ```python
     def random_datetime_between(start_date, end_date):
         if start_date >= end_date:
             return start_date  # Edge case: return start if no range
         time_delta = end_date - start_date
         random_days = random.randint(0, time_delta.days)
         return start_date + timedelta(days=random_days)
     ```
   - Use datetime.datetime objects only (not datetime.date)
   - Use fake.date_time_between() instead of fake.date_between() for consistency

Generate ONLY the Python code, no explanations or markdown. The code should be production-ready and executable as-is.
"""

        logger.info("🤖 Calling Claude to generate data creation code...")

        response = self.claude_client.messages.create(
            model="claude-sonnet-4-5@20250929",
            max_tokens=16000,
            temperature=0.3,  # Lower for consistent code generation
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Extract code from response
        generated_code = response.content[0].text

        # Remove markdown code fences if present
        if "```python" in generated_code:
            generated_code = generated_code.split("```python")[1].split("```")[0].strip()
        elif "```" in generated_code:
            generated_code = generated_code.split("```")[1].split("```")[0].strip()

        logger.info(f"✅ Generated {len(generated_code)} characters of Python code")

        # Log to job manager
        if "job_manager" in state and "job_id" in state:
            job_manager = state["job_manager"]
            job_id = state["job_id"]
            job_manager.add_log(
                job_id,
                "synthetic data generator code",
                f"✅ Claude generated {len(generated_code)} chars of Python code",
                "INFO"
            )

        return generated_code

    async def _execute_data_generation_code(
        self,
        python_code: str,
        schema: Dict,
        state: Dict
    ) -> List[str]:
        """Execute the generated Python code in a controlled environment."""

        # Save code to a temporary file
        code_file = os.path.join(self.output_dir, "generated_data_creator.py")
        with open(code_file, "w") as f:
            f.write(python_code)

        logger.info(f"💾 Saved generated code to {code_file}")

        # Log to job manager
        if "job_manager" in state and "job_id" in state:
            job_manager = state["job_manager"]
            job_id = state["job_id"]
            job_manager.add_log(
                job_id,
                "synthetic data generator code",
                f"⚙️  Executing generated code...",
                "INFO"
            )

        # Execute the code using subprocess (safer than exec())
        try:
            result = subprocess.run(
                [sys.executable, code_file],
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
                cwd=self.output_dir
            )

            if result.returncode != 0:
                logger.error(f"Code execution failed with return code {result.returncode}")
                logger.error(f"STDOUT: {result.stdout}")
                logger.error(f"STDERR: {result.stderr}")
                raise RuntimeError(f"Generated code failed: {result.stderr}")

            logger.info(f"✅ Code executed successfully")
            logger.info(f"Output: {result.stdout}")

            # Log to job manager
            if "job_manager" in state and "job_id" in state:
                job_manager.add_log(
                    job_id,
                    "synthetic data generator code",
                    f"✅ Code executed successfully",
                    "INFO"
                )

            # Parse output to extract row counts from BigQuery upload messages
            # Look for lines like: "✅ Successfully uploaded 6000 rows to bq-demos-469816.dataset.table_name"
            generated_files = []
            table_metadata = []

            import re
            upload_pattern = r"Successfully uploaded (\d+) rows to .+\.([a-z_]+)$"

            row_counts = {}
            for line in result.stdout.split('\n'):
                match = re.search(upload_pattern, line)
                if match:
                    row_count = int(match.group(1))
                    table_name = match.group(2)
                    row_counts[table_name] = row_count
                    logger.info(f"  📊 Parsed: {table_name} = {row_count:,} rows")

            # Build metadata from parsed row counts
            for table in schema.get("tables", []):
                table_name = table["name"]
                row_count = row_counts.get(table_name, 0)
                table_metadata.append({
                    "table_name": table_name,
                    "row_count": row_count,
                    "filename": f"{table_name}.csv"
                })

            state["table_file_metadata"] = table_metadata

            return generated_files

        except subprocess.TimeoutExpired:
            logger.error("Code execution timed out after 10 minutes")
            raise RuntimeError("Data generation code timed out")
        except Exception as e:
            logger.error(f"Code execution failed: {e}", exc_info=True)
            raise

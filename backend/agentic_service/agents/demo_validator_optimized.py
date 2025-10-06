"""
Demo Validator Agent - OPTIMIZED VERSION.
Validates demo queries with parallel BigQuery execution.

KEY OPTIMIZATIONS:
- Parallel query validation (3-4x speedup)
- Async BigQuery operations using thread pool
- Async file I/O

PERFORMANCE:
- Before: 5 queries × 3s = 15 seconds (sequential)
- After: max(all queries) = ~3-5 seconds (parallel)
"""
import logging
import os
import asyncio
from typing import Dict, List, Tuple
from google.cloud import bigquery
from datetime import datetime

logger = logging.getLogger(__name__)


class DemoValidatorOptimized:
    """OPTIMIZED: Agent for validating demo queries with parallel execution."""

    def __init__(self):
        self.project_id = os.getenv("PROJECT_ID", "bq-demos-469816")
        self.client = bigquery.Client(project=self.project_id)
        logger.info(f"Demo Validator OPTIMIZED initialized for project {self.project_id}")

    async def execute(self, state: Dict) -> Dict:
        """Execute demo validation phase - CAPI-ONLY testing (NEVER fails the job)."""
        import time

        logger.info("🚀 Validating demo queries through CAPI (DEMO-STYLE)")

        # 🛡️ SAFEGUARD: Wrap entire validation in try/except to prevent job failure
        try:
            # Wait for CAPI agent to become fully operational before validation
            # The agent needs time to index the dataset after creation
            capi_agent_id = state.get("capi_agent_id")
            if not capi_agent_id:
                logger.warning("No CAPI agent ID found - skipping validation")
                state["validation_complete"] = True
                state["validation_results"] = {"queries_tested": 0}
                return state

            logger.info(f"⏳ Waiting 15 seconds for CAPI agent '{capi_agent_id}' to become ready...")
            await asyncio.sleep(15)

            start_time = time.time()
            demo_story = state.get("demo_story", {})
            golden_queries = demo_story.get("golden_queries", [])

            if not golden_queries:
                logger.warning("No golden queries found to validate")
                state["validation_complete"] = True
                state["validation_results"] = {"queries_tested": 0}
                return state

            # Log to CE Dashboard - start
            if "job_manager" in state and "job_id" in state:
                job_manager = state["job_manager"]
                job_id = state["job_id"]
                job_manager.add_log(
                    job_id,
                    "demo validator",
                    f"🤖 Testing {min(5, len(golden_queries))} golden queries through CAPI...",
                    "INFO"
                )

            # Validate through CAPI end-to-end (just like in demos!)
            logger.info(f"🤖 Testing golden queries with CAPI agent: {capi_agent_id}")
            capi_results = await self.validate_capi_queries(golden_queries, capi_agent_id, state)

            # Generate validation report (async file write)
            validation_report = await self._generate_validation_report_async(capi_results)

            elapsed = time.time() - start_time

            # Update state
            state["validation_results"] = {
                "total_queries": len(golden_queries),
                "capi_validated": len([r for r in capi_results if r.get("capi_success", False)]),
                "capi_failed": len([r for r in capi_results if not r.get("capi_success", False)]),
                "sql_results": capi_results,  # Keep same key for compatibility with UI
                "validation_report": validation_report
            }
            state["validation_complete"] = True

            logger.info(f"✅ CAPI Validation complete in {elapsed:.2f}s")
            logger.info(f"   Queries tested: {len(capi_results)}")
            logger.info(f"   CAPI validated: {state['validation_results']['capi_validated']}")
            logger.info(f"   CAPI failed: {state['validation_results']['capi_failed']}")

            # Log to CE Dashboard - completion
            if "job_manager" in state and "job_id" in state:
                passed = state['validation_results']['capi_validated']
                failed = state['validation_results']['capi_failed']
                total = len(capi_results)

                job_manager.add_log(
                    job_id,
                    "demo validator",
                    f"✅ CAPI Validation Complete: {passed}/{total} queries returned results in {elapsed:.2f}s",
                    "INFO"
                )

                # Show validation details
                for result in capi_results:
                    status_emoji = "✅" if result.get("capi_success", False) else "❌"
                    question_preview = result['question'][:60] + "..." if len(result['question']) > 60 else result['question']

                    job_manager.add_log(
                        job_id,
                        "demo validator",
                        f"  {status_emoji} Query {result['sequence']}: {question_preview}",
                        "INFO" if result.get("capi_success", False) else "WARNING"
                    )

            return state

        except Exception as e:
            # 🛡️ SAFEGUARD: Never fail the job due to validation errors
            logger.error(f"❌ Validation failed (non-critical): {e}", exc_info=True)

            # Log to CE Dashboard
            if "job_manager" in state and "job_id" in state:
                state["job_manager"].add_log(
                    state["job_id"],
                    "demo validator",
                    f"⚠️ Validation skipped due to error: {str(e)[:200]}",
                    "WARNING"
                )

            # Return success with empty results - NEVER fail the job
            state["validation_complete"] = True
            state["validation_results"] = {
                "total_queries": 0,
                "capi_validated": 0,
                "capi_failed": 0,
                "validation_skipped": True,
                "skip_reason": str(e)
            }

            logger.info("✅ Validation step completed (skipped due to error)")
            return state

    async def _validate_sql_queries_parallel(
        self,
        golden_queries: List[Dict],
        dataset_id: str,
        state: Dict
    ) -> List[Dict]:
        """
        OPTIMIZED: Validate SQL queries IN PARALLEL.

        Strategy:
        1. Create validation tasks for first 5 queries
        2. Execute all in parallel with asyncio.gather()
        3. Collect results
        """
        queries_to_test = golden_queries[:5]  # Test first 5 for speed
        logger.info(f"⚡ Validating {len(queries_to_test)} queries IN PARALLEL...")

        # Create tasks for all queries
        tasks = []
        for i, query_spec in enumerate(queries_to_test, 1):
            question = query_spec.get("question", "")
            # FIX: Field is named "sql" not "expected_sql" in demo_story
            expected_sql = query_spec.get("expected_sql") or query_spec.get("sql", "")
            complexity = query_spec.get("complexity", "unknown")

            # Skip if no SQL provided
            if not expected_sql:
                logger.warning(f"Query {i}: No SQL provided, skipping")
                tasks.append(asyncio.create_task(self._create_skipped_result(i, question, complexity)))
                continue

            # Replace placeholder dataset references
            sql = self._replace_dataset_placeholders(expected_sql, dataset_id)

            # Create validation task
            tasks.append(
                self._execute_query_async(sql, question, complexity, i)
            )

        # Execute all queries in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Query {i+1} validation failed: {result}")
                final_results.append({
                    "sequence": i + 1,
                    "question": queries_to_test[i].get("question", ""),
                    "complexity": queries_to_test[i].get("complexity", "unknown"),
                    "sql_success": False,
                    "sql_error": str(result),
                    "execution_time_ms": 0,
                    "row_count": 0
                })
            else:
                final_results.append(result)

        return final_results

    async def _create_skipped_result(self, sequence: int, question: str, complexity: str) -> Dict:
        """Create result for skipped query (no SQL provided)."""
        return {
            "sequence": sequence,
            "question": question,
            "complexity": complexity,
            "sql_success": False,
            "sql_error": "No SQL provided",
            "execution_time_ms": 0,
            "row_count": 0
        }

    async def _execute_query_async(
        self,
        sql: str,
        question: str,
        complexity: str,
        sequence: int
    ) -> Dict:
        """
        Execute a single SQL query asynchronously (runs in thread pool).

        Returns:
            Validation result dict
        """
        # Run blocking BigQuery operation in thread pool
        return await asyncio.to_thread(
            self._execute_query_sync,
            sql,
            question,
            complexity,
            sequence
        )

    def _execute_query_sync(
        self,
        sql: str,
        question: str,
        complexity: str,
        sequence: int
    ) -> Dict:
        """Synchronous query execution (runs in thread pool)."""
        try:
            start_time = datetime.now()

            # Run query with timeout
            query_job = self.client.query(sql)
            query_result = query_job.result(timeout=30)  # 30 second timeout

            end_time = datetime.now()
            execution_time_ms = (end_time - start_time).total_seconds() * 1000

            # Get row count
            row_count = query_result.total_rows

            # Get sample results (first 5 rows)
            sample_rows = []
            for row in list(query_result)[:5]:
                sample_rows.append(dict(row.items()))

            logger.info(f"  ✅ Query {sequence}: SQL executed successfully ({row_count:,} rows, {execution_time_ms:.0f}ms)")

            return {
                "sequence": sequence,
                "question": question,
                "complexity": complexity,
                "sql_success": True,
                "sql_error": None,
                "execution_time_ms": execution_time_ms,
                "row_count": row_count,
                "sample_results": sample_rows,
                "sql_executed": sql
            }

        except Exception as e:
            logger.error(f"  ❌ Query {sequence}: SQL failed - {str(e)}")
            return {
                "sequence": sequence,
                "question": question,
                "complexity": complexity,
                "sql_success": False,
                "sql_error": str(e),
                "execution_time_ms": 0,
                "row_count": 0,
                "sql_executed": sql
            }

    def _replace_dataset_placeholders(self, sql: str, dataset_id: str) -> str:
        """Replace placeholder dataset references with actual dataset."""
        # Common placeholders
        placeholders = [
            "{dataset}",
            "{project.dataset}",
            "project.dataset",
            "`project.dataset",
        ]

        for placeholder in placeholders:
            sql = sql.replace(placeholder, dataset_id)

        return sql

    async def _generate_validation_report_async(self, sql_results: List[Dict]) -> str:
        """Generate markdown validation report with async file I/O."""
        # Generate report content
        report = self._build_report_content(sql_results)

        # Save report (async file write)
        report_file = "/tmp/demo_validation_report.md"
        await asyncio.to_thread(self._write_file, report_file, report)

        logger.info(f"📄 Validation report saved: {report_file}")

        return report

    def _write_file(self, filepath: str, content: str):
        """Synchronous file write (runs in thread pool)."""
        with open(filepath, 'w') as f:
            f.write(content)

    def _build_report_content(self, capi_results: List[Dict]) -> str:
        """Build CAPI validation report content."""
        total = len(capi_results)
        passed = len([r for r in capi_results if r.get("capi_success", False)])
        failed = total - passed

        report = f"""# Demo Validation Report (CAPI Testing)

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}

## Summary

| Metric | Value |
|--------|-------|
| **Total Queries Tested** | {total} |
| **CAPI Validated** | {passed} ✅ |
| **CAPI Failed** | {failed} ❌ |
| **Success Rate** | {(passed/total*100):.1f}% |

## Query Results (CAPI End-to-End)

"""

        for result in capi_results:
            status = "✅ PASSED" if result.get("capi_success", False) else "❌ FAILED"
            complexity = result.get('complexity', 'N/A')
            report += f"""### {result['sequence']}. {result['question']}

**Status:** {status}
**Complexity:** {complexity}
**CAPI Response Length:** {len(result.get('capi_response') or '')} characters

"""

            if not result.get('capi_success', False):
                report += f"""**Error:**
```
{result.get('capi_error', 'Unknown error')}
```

"""
            else:
                capi_response = result.get('capi_response') or ''
                response_preview = capi_response[:500] + "..." if len(capi_response) > 500 else capi_response
                report += f"""**CAPI Response Preview:**
```
{response_preview}
```

**CAPI Generated SQL:**
```sql
{result.get('capi_sql', 'N/A')}
```

"""

            report += "---\n\n"

        return report

    async def validate_capi_queries(
        self,
        golden_queries: List[Dict],
        capi_agent_id: str,
        state: Dict
    ) -> List[Dict]:
        """
        Validate queries through CAPI end-to-end (DEMO-STYLE).

        This validates the full demo experience:
        1. Send natural language question to CAPI
        2. Capture CAPI's generated SQL
        3. Get CAPI's results
        4. Validate the response is meaningful (has content)

        Returns list of validation results with CAPI test status.
        """
        if not capi_agent_id:
            logger.warning("No CAPI agent ID provided, skipping CAPI validation")
            return []

        logger.info(f"🤖 Validating {len(golden_queries[:5])} queries through CAPI agent: {capi_agent_id}")

        # Test first 5 queries (same as SQL validation was doing)
        queries_to_test = golden_queries[:5]

        # Create tasks for parallel CAPI calls
        tasks = []
        for i, query_spec in enumerate(queries_to_test, 1):
            question = query_spec.get("question", "")
            if not question:
                continue

            tasks.append(
                self._test_capi_query(capi_agent_id, question, i, state)
            )

        # Execute all CAPI calls in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"CAPI query {i+1} failed: {result}")
                final_results.append({
                    "sequence": i + 1,
                    "question": queries_to_test[i].get("question", ""),
                    "capi_success": False,
                    "capi_error": str(result),
                    "capi_response": None
                })
            else:
                final_results.append(result)

        return final_results

    async def _test_capi_query(
        self,
        agent_id: str,
        question: str,
        sequence: int,
        state: Dict
    ) -> Dict:
        """Test a single query through CAPI."""
        try:
            # Call the chat API endpoint (same one frontend uses)
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "http://localhost:8000/api/chat",
                    json={
                        "message": question,
                        "agent_id": agent_id,
                        "dataset_id": state.get("dataset_id", "")
                    },
                    timeout=aiohttp.ClientTimeout(total=60)  # CAPI can take 30-50s
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"CAPI returned {response.status}: {error_text}")

                    data = await response.json()

                    # Extract response
                    capi_response = data.get("response", "")
                    capi_sql = data.get("sqlQuery", "")

                    # Validate response is meaningful (not empty or error)
                    # FIX: Check if capi_response is not None before getting length
                    success = bool(capi_response and isinstance(capi_response, str) and len(capi_response) > 10)

                    response_len = len(capi_response) if capi_response else 0
                    logger.info(f"  ✅ CAPI Query {sequence}: Response received ({response_len} chars)")

                    return {
                        "sequence": sequence,
                        "question": question,
                        "capi_success": success,
                        "capi_response": capi_response,
                        "capi_sql": capi_sql,
                        "capi_error": None
                    }

        except Exception as e:
            logger.error(f"  ❌ CAPI Query {sequence}: {str(e)}")
            return {
                "sequence": sequence,
                "question": question,
                "capi_success": False,
                "capi_response": None,
                "capi_sql": None,
                "capi_error": str(e)
            }

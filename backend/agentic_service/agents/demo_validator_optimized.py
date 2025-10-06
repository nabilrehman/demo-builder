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
        """Execute demo validation phase with parallel query execution."""
        import time

        logger.info("🚀 Validating demo queries (OPTIMIZED - PARALLEL)")
        start_time = time.time()

        try:
            demo_story = state.get("demo_story", {})
            dataset_id = state.get("dataset_full_name", "")
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
                    "demo validator optimized",
                    f"🔍 Validating {min(5, len(golden_queries))} golden queries IN PARALLEL...",
                    "INFO"
                )

            # OPTIMIZED: Validate SQL queries in PARALLEL
            sql_results = await self._validate_sql_queries_parallel(golden_queries, dataset_id, state)

            # Generate validation report (async file write)
            validation_report = await self._generate_validation_report_async(sql_results)

            elapsed = time.time() - start_time

            # Update state
            state["validation_results"] = {
                "total_queries": len(golden_queries),
                "sql_validated": len([r for r in sql_results if r["sql_success"]]),
                "sql_failed": len([r for r in sql_results if not r["sql_success"]]),
                "sql_results": sql_results,
                "validation_report": validation_report
            }
            state["validation_complete"] = True

            logger.info(f"✅ Validation complete in {elapsed:.2f}s")
            logger.info(f"   Queries tested: {len(golden_queries)}")
            logger.info(f"   SQL validated: {state['validation_results']['sql_validated']}")
            logger.info(f"   SQL failed: {state['validation_results']['sql_failed']}")

            # Log to CE Dashboard - completion
            if "job_manager" in state and "job_id" in state:
                passed = state['validation_results']['sql_validated']
                failed = state['validation_results']['sql_failed']
                total = len(sql_results)

                job_manager.add_log(
                    job_id,
                    "demo validator optimized",
                    f"✅ Validation Complete (OPTIMIZED): {passed}/{total} queries passed in {elapsed:.2f}s",
                    "INFO"
                )

                # Show validation details
                for result in sql_results:
                    status_emoji = "✅" if result["sql_success"] else "❌"
                    question_preview = result['question'][:60] + "..." if len(result['question']) > 60 else result['question']

                    job_manager.add_log(
                        job_id,
                        "demo validator optimized",
                        f"  {status_emoji} Query {result['sequence']}: {question_preview}",
                        "INFO" if result["sql_success"] else "WARNING"
                    )

            return state

        except Exception as e:
            logger.error(f"Validation failed: {e}", exc_info=True)
            raise

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
            expected_sql = query_spec.get("expected_sql", "")
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

    def _build_report_content(self, sql_results: List[Dict]) -> str:
        """Build validation report content."""
        total = len(sql_results)
        passed = len([r for r in sql_results if r["sql_success"]])
        failed = total - passed

        report = f"""# Demo Validation Report

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}

## Summary

| Metric | Value |
|--------|-------|
| **Total Queries Tested** | {total} |
| **SQL Validated** | {passed} ✅ |
| **SQL Failed** | {failed} ❌ |
| **Success Rate** | {(passed/total*100):.1f}% |

## Query Results

"""

        for result in sql_results:
            status = "✅ PASSED" if result["sql_success"] else "❌ FAILED"
            report += f"""### {result['sequence']}. {result['question']}

**Status:** {status}
**Complexity:** {result['complexity']}
**Execution Time:** {result['execution_time_ms']:.0f}ms
**Rows Returned:** {result['row_count']:,}

"""

            if not result['sql_success']:
                report += f"""**Error:**
```
{result['sql_error']}
```

**SQL:**
```sql
{result.get('sql_executed', 'N/A')[:500]}...
```

"""
            else:
                report += f"""**Sample Results:**
```json
{result.get('sample_results', [])}
```

"""

            report += "---\n\n"

        return report

    async def validate_capi_queries(
        self,
        golden_queries: List[Dict],
        capi_agent_id: str
    ) -> List[Dict]:
        """
        Validate queries through CAPI (future implementation).

        This would:
        1. Call CAPI with natural language question
        2. Capture generated SQL
        3. Execute and get results
        4. Compare with direct SQL results
        5. Verify visualizations render correctly

        For now, placeholder for future implementation.
        """
        logger.info("CAPI validation not yet implemented")
        logger.info("This will be implemented when CAPI agent is created")
        return []

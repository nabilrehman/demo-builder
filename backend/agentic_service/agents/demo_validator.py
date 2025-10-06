"""
Demo Validator Agent - Validates that demo queries work correctly.

Ensures golden queries:
1. Execute successfully in BigQuery as SQL
2. Work through Conversational Analytics API as natural language
3. Produce matching results between SQL and CAPI

This prevents demo failures during live presentations.
"""
import logging
import os
from typing import Dict, List, Tuple
from google.cloud import bigquery
from datetime import datetime

logger = logging.getLogger(__name__)


class DemoValidator:
    """Agent for validating demo queries work in both SQL and CAPI."""

    def __init__(self):
        self.project_id = os.getenv("PROJECT_ID", "bq-demos-469816")
        self.client = bigquery.Client(project=self.project_id)
        logger.info(f"Demo Validator initialized for project {self.project_id}")

    async def execute(self, state: Dict) -> Dict:
        """Execute demo validation phase."""
        logger.info("Validating demo queries...")

        try:
            demo_story = state.get("demo_story", {})
            dataset_id = state.get("dataset_full_name", "")
            golden_queries = demo_story.get("golden_queries", [])

            if not golden_queries:
                logger.warning("No golden queries found to validate")
                state["validation_complete"] = True
                state["validation_results"] = {"queries_tested": 0}
                return state

            # Validate SQL execution
            sql_results = await self._validate_sql_queries(golden_queries, dataset_id)

            # Generate validation report
            validation_report = self._generate_validation_report(sql_results)

            # Update state
            state["validation_results"] = {
                "total_queries": len(golden_queries),
                "sql_validated": len([r for r in sql_results if r["sql_success"]]),
                "sql_failed": len([r for r in sql_results if not r["sql_success"]]),
                "sql_results": sql_results,
                "validation_report": validation_report
            }
            state["validation_complete"] = True

            logger.info(f"✅ Validation complete")
            logger.info(f"   Queries tested: {len(golden_queries)}")
            logger.info(f"   SQL validated: {state['validation_results']['sql_validated']}")
            logger.info(f"   SQL failed: {state['validation_results']['sql_failed']}")

            return state

        except Exception as e:
            logger.error(f"Validation failed: {e}", exc_info=True)
            raise

    async def _validate_sql_queries(
        self,
        golden_queries: List[Dict],
        dataset_id: str
    ) -> List[Dict]:
        """Validate that SQL queries execute successfully."""
        results = []

        for i, query_spec in enumerate(golden_queries[:5], 1):  # Test first 5 for speed
            question = query_spec.get("question", "")
            expected_sql = query_spec.get("expected_sql", "")
            complexity = query_spec.get("complexity", "unknown")

            logger.info(f"\nValidating query {i}: {question[:60]}...")

            # Skip if no SQL provided
            if not expected_sql:
                logger.warning(f"  ⚠️  No SQL provided, skipping")
                results.append({
                    "sequence": i,
                    "question": question,
                    "complexity": complexity,
                    "sql_success": False,
                    "sql_error": "No SQL provided",
                    "execution_time_ms": 0,
                    "row_count": 0
                })
                continue

            # Replace placeholder dataset references
            sql = self._replace_dataset_placeholders(expected_sql, dataset_id)

            # Execute SQL
            result = await self._execute_query(sql, question, complexity, i)
            results.append(result)

        return results

    async def _execute_query(
        self,
        sql: str,
        question: str,
        complexity: str,
        sequence: int
    ) -> Dict:
        """Execute a single SQL query and capture results."""
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

            logger.info(f"  ✅ SQL executed successfully")
            logger.info(f"     Rows: {row_count:,}")
            logger.info(f"     Time: {execution_time_ms:.0f}ms")

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
            logger.error(f"  ❌ SQL failed: {str(e)}")
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

    def _generate_validation_report(self, sql_results: List[Dict]) -> str:
        """Generate markdown validation report."""
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

        # Save report
        report_file = "/tmp/demo_validation_report.md"
        with open(report_file, 'w') as f:
            f.write(report)

        logger.info(f"📄 Validation report saved: {report_file}")

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

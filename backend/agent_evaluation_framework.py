"""
Agent Evaluation Framework
Tests agentic demo generation pipeline across multiple customer sites
and evaluates quality of demos, queries, and results.
"""
import asyncio
import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

from agentic_service.demo_orchestrator import DemoOrchestrator
from google.cloud import bigquery

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class EvaluationMetrics:
    """Metrics for evaluating demo quality."""
    # Site info
    customer_url: str
    company_name: str
    industry: str

    # Pipeline execution
    total_time_seconds: float
    success: bool
    failed_stage: str = None
    error_message: str = None

    # Agent performance
    research_time: float = 0
    demo_story_time: float = 0
    data_modeling_time: float = 0
    synthetic_data_time: float = 0
    infrastructure_time: float = 0
    capi_time: float = 0
    validation_time: float = 0

    # Demo quality metrics
    demo_title_length: int = 0
    demo_title_has_customer_name: bool = False
    demo_title_has_action_words: bool = False
    executive_summary_length: int = 0

    # Golden queries
    total_queries: int = 0
    simple_queries: int = 0
    medium_queries: int = 0
    complex_queries: int = 0
    expert_queries: int = 0
    queries_with_sql: int = 0
    avg_question_length: int = 0

    # Data schema
    total_tables: int = 0
    total_fields: int = 0
    total_relationships: int = 0
    has_repeated_fields: bool = False

    # Data volume
    total_rows: int = 0
    total_size_mb: float = 0
    largest_table_rows: int = 0
    smallest_table_rows: int = 0

    # CAPI YAML
    yaml_size_kb: float = 0
    yaml_has_system_instruction: bool = False
    yaml_tables_count: int = 0
    yaml_relationships_count: int = 0

    # Validation results
    queries_validated: int = 0
    queries_failed: int = 0
    sql_syntax_errors: int = 0

    # Quality scores (0-100)
    narrative_quality_score: int = 0
    schema_quality_score: int = 0
    query_complexity_score: int = 0
    overall_quality_score: int = 0


class DemoQualityEvaluator:
    """Evaluates quality of generated demos."""

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.bq_client = bigquery.Client(project=project_id)

    def evaluate_demo_title(self, title: str, company_name: str) -> Dict[str, Any]:
        """Evaluate quality of demo title."""
        action_words = ['from', 'to', 'how', 'accelerating', 'transforming',
                       'unlocking', 'empowering', 'driving', 'optimizing']

        return {
            'length': len(title),
            'has_customer_name': company_name.lower() in title.lower(),
            'has_action_words': any(word in title.lower() for word in action_words),
            'quality_score': min(100, len(title)) if 50 < len(title) < 150 else 50
        }

    def evaluate_queries(self, queries: List[Dict]) -> Dict[str, Any]:
        """Evaluate quality of golden queries."""
        if not queries:
            return {'total': 0, 'quality_score': 0}

        complexity_counts = {
            'SIMPLE': 0,
            'MEDIUM': 0,
            'COMPLEX': 0,
            'EXPERT': 0
        }

        for q in queries:
            complexity = q.get('complexity', 'MEDIUM')
            complexity_counts[complexity] = complexity_counts.get(complexity, 0) + 1

        # Calculate complexity score (more complex queries = higher score)
        complexity_score = (
            complexity_counts['SIMPLE'] * 10 +
            complexity_counts['MEDIUM'] * 25 +
            complexity_counts['COMPLEX'] * 40 +
            complexity_counts['EXPERT'] * 50
        ) / len(queries)

        avg_question_length = sum(len(q.get('question', '')) for q in queries) / len(queries)

        # Longer questions usually indicate more complex analysis
        length_score = min(100, (avg_question_length / 100) * 100)

        quality_score = int((complexity_score + length_score) / 2)

        return {
            'total': len(queries),
            'simple': complexity_counts['SIMPLE'],
            'medium': complexity_counts['MEDIUM'],
            'complex': complexity_counts['COMPLEX'],
            'expert': complexity_counts['EXPERT'],
            'avg_question_length': int(avg_question_length),
            'quality_score': quality_score
        }

    def evaluate_schema(self, schema: Dict) -> Dict[str, Any]:
        """Evaluate quality of data schema."""
        tables = schema.get('tables', [])

        total_fields = sum(len(t.get('fields', [])) for t in tables)
        total_relationships = len(schema.get('relationships', []))

        # Check for REPEATED fields (problematic)
        has_repeated = any(
            f.get('type', '').upper() == 'REPEATED' or f.get('mode', '').upper() == 'REPEATED'
            for t in tables
            for f in t.get('fields', [])
        )

        # Quality score based on:
        # - Number of tables (5-20 is ideal)
        # - Fields per table (5-15 is ideal)
        # - Has relationships defined
        # - No REPEATED fields

        tables_score = 100 if 5 <= len(tables) <= 20 else 50
        avg_fields_per_table = total_fields / len(tables) if tables else 0
        fields_score = 100 if 5 <= avg_fields_per_table <= 15 else 70
        relationships_score = min(100, total_relationships * 10)
        repeated_penalty = -50 if has_repeated else 0

        quality_score = int(
            (tables_score + fields_score + relationships_score + repeated_penalty) / 3
        )
        quality_score = max(0, min(100, quality_score))

        return {
            'total_tables': len(tables),
            'total_fields': total_fields,
            'avg_fields_per_table': round(avg_fields_per_table, 1),
            'total_relationships': total_relationships,
            'has_repeated_fields': has_repeated,
            'quality_score': quality_score
        }

    async def evaluate_data_quality(self, dataset_id: str) -> Dict[str, Any]:
        """Evaluate quality of generated data in BigQuery."""
        try:
            dataset_ref = f"{self.project_id}.{dataset_id}"
            dataset = self.bq_client.get_dataset(dataset_ref)

            tables = list(self.bq_client.list_tables(dataset))
            table_stats = []

            for table_ref in tables:
                table = self.bq_client.get_table(table_ref)
                table_stats.append({
                    'name': table.table_id,
                    'rows': table.num_rows,
                    'size_mb': table.num_bytes / 1024 / 1024
                })

            total_rows = sum(t['rows'] for t in table_stats)
            total_size = sum(t['size_mb'] for t in table_stats)

            # Data quality score based on:
            # - Total data volume (40K-500K rows is ideal)
            # - Reasonable size per row
            # - Balanced table sizes

            volume_score = 100 if 40000 <= total_rows <= 500000 else 70

            return {
                'total_rows': total_rows,
                'total_size_mb': round(total_size, 2),
                'table_count': len(table_stats),
                'largest_table_rows': max((t['rows'] for t in table_stats), default=0),
                'smallest_table_rows': min((t['rows'] for t in table_stats), default=0),
                'avg_rows_per_table': int(total_rows / len(table_stats)) if table_stats else 0,
                'quality_score': volume_score,
                'table_stats': table_stats[:5]  # Top 5 tables
            }
        except Exception as e:
            logger.error(f"Failed to evaluate data quality: {e}")
            return {
                'total_rows': 0,
                'total_size_mb': 0,
                'table_count': 0,
                'quality_score': 0,
                'error': str(e)
            }

    def calculate_overall_score(self, metrics: EvaluationMetrics) -> int:
        """Calculate overall demo quality score (0-100)."""
        if not metrics.success:
            return 0

        # Weighted average of component scores
        weights = {
            'narrative': 0.25,
            'schema': 0.25,
            'queries': 0.30,
            'data': 0.20
        }

        overall = int(
            metrics.narrative_quality_score * weights['narrative'] +
            metrics.schema_quality_score * weights['schema'] +
            metrics.query_complexity_score * weights['queries'] +
            (100 if metrics.total_rows > 10000 else 50) * weights['data']
        )

        return min(100, max(0, overall))


class AgentEvaluationFramework:
    """Comprehensive evaluation framework for agentic demo generation."""

    # Test sites across different industries
    TEST_SITES = [
        {
            'url': 'https://www.shopify.com',
            'expected_industry': 'E-commerce Platform',
            'description': 'Multi-tenant e-commerce SaaS platform'
        },
        {
            'url': 'https://www.klick.com',
            'expected_industry': 'Healthcare Marketing',
            'description': 'Life sciences commercialization'
        },
        {
            'url': 'https://www.snowflake.com',
            'expected_industry': 'Data Cloud Platform',
            'description': 'Cloud data platform provider'
        },
        {
            'url': 'https://www.stripe.com',
            'expected_industry': 'Payment Processing',
            'description': 'Financial infrastructure platform'
        },
        {
            'url': 'https://www.hubspot.com',
            'expected_industry': 'Marketing Automation',
            'description': 'CRM and marketing platform'
        },
        {
            'url': 'https://www.zendesk.com',
            'expected_industry': 'Customer Support',
            'description': 'Customer service platform'
        },
        {
            'url': 'https://www.atlassian.com',
            'expected_industry': 'Software Development',
            'description': 'Team collaboration tools'
        },
        {
            'url': 'https://www.slack.com',
            'expected_industry': 'Enterprise Communication',
            'description': 'Business messaging platform'
        },
        {
            'url': 'https://www.airbnb.com',
            'expected_industry': 'Travel & Hospitality',
            'description': 'Vacation rental marketplace'
        },
        {
            'url': 'https://www.doordash.com',
            'expected_industry': 'Food Delivery',
            'description': 'On-demand delivery platform'
        }
    ]

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.orchestrator = DemoOrchestrator()
        self.evaluator = DemoQualityEvaluator(project_id)
        self.results: List[EvaluationMetrics] = []

    async def evaluate_single_site(self, site: Dict) -> EvaluationMetrics:
        """Evaluate demo generation for a single site."""
        logger.info(f"\n{'='*80}")
        logger.info(f"EVALUATING: {site['url']}")
        logger.info(f"Expected Industry: {site['expected_industry']}")
        logger.info(f"{'='*80}\n")

        start_time = time.time()
        metrics = EvaluationMetrics(
            customer_url=site['url'],
            company_name='',
            industry='',
            total_time_seconds=0,
            success=False
        )

        try:
            # Run demo generation pipeline
            final_state = await self.orchestrator.generate_demo(
                customer_url=site['url'],
                project_id=self.project_id
            )

            total_time = time.time() - start_time
            metrics.total_time_seconds = round(total_time, 2)
            metrics.success = True

            # Extract data from final state
            customer_info = final_state.get('customer_info', {})
            demo_story = final_state.get('demo_story', {})
            schema = final_state.get('schema', {})
            dataset_id = final_state.get('dataset_id', '')

            metrics.company_name = customer_info.get('company_name', '')
            metrics.industry = customer_info.get('industry', '')

            # Evaluate demo title and narrative
            title_eval = self.evaluator.evaluate_demo_title(
                demo_story.get('demo_title', ''),
                metrics.company_name
            )
            metrics.demo_title_length = title_eval['length']
            metrics.demo_title_has_customer_name = title_eval['has_customer_name']
            metrics.demo_title_has_action_words = title_eval['has_action_words']
            metrics.narrative_quality_score = title_eval['quality_score']

            exec_summary = demo_story.get('executive_summary', '')
            metrics.executive_summary_length = len(exec_summary)

            # Evaluate golden queries
            queries = demo_story.get('golden_queries', [])
            query_eval = self.evaluator.evaluate_queries(queries)
            metrics.total_queries = query_eval['total']
            metrics.simple_queries = query_eval['simple']
            metrics.medium_queries = query_eval['medium']
            metrics.complex_queries = query_eval['complex']
            metrics.expert_queries = query_eval['expert']
            metrics.avg_question_length = query_eval['avg_question_length']
            metrics.query_complexity_score = query_eval['quality_score']
            metrics.queries_with_sql = sum(1 for q in queries if q.get('expected_sql'))

            # Evaluate schema
            schema_eval = self.evaluator.evaluate_schema(schema)
            metrics.total_tables = schema_eval['total_tables']
            metrics.total_fields = schema_eval['total_fields']
            metrics.total_relationships = schema_eval['total_relationships']
            metrics.has_repeated_fields = schema_eval['has_repeated_fields']
            metrics.schema_quality_score = schema_eval['quality_score']

            # Evaluate data quality
            if dataset_id:
                data_eval = await self.evaluator.evaluate_data_quality(dataset_id)
                metrics.total_rows = data_eval['total_rows']
                metrics.total_size_mb = data_eval['total_size_mb']
                metrics.largest_table_rows = data_eval['largest_table_rows']
                metrics.smallest_table_rows = data_eval['smallest_table_rows']

            # Evaluate CAPI YAML
            yaml_file = final_state.get('capi_yaml_file', '')
            if yaml_file and os.path.exists(yaml_file):
                yaml_size = os.path.getsize(yaml_file) / 1024
                metrics.yaml_size_kb = round(yaml_size, 2)

                with open(yaml_file, 'r') as f:
                    yaml_content = f.read()
                    metrics.yaml_has_system_instruction = 'system_instruction' in yaml_content
                    metrics.yaml_tables_count = yaml_content.count('- name: ')
                    metrics.yaml_relationships_count = yaml_content.count('relationship_type:')

            # Validation results
            validation = final_state.get('validation_results', {})
            metrics.queries_validated = validation.get('sql_validated', 0)
            metrics.queries_failed = validation.get('sql_failed', 0)

            # Calculate overall quality score
            metrics.overall_quality_score = self.evaluator.calculate_overall_score(metrics)

            logger.info(f"✅ SUCCESS: {site['url']}")
            logger.info(f"   Time: {metrics.total_time_seconds}s")
            logger.info(f"   Quality Score: {metrics.overall_quality_score}/100")
            logger.info(f"   Queries: {metrics.total_queries} ({metrics.expert_queries} expert)")
            logger.info(f"   Data: {metrics.total_rows:,} rows across {metrics.total_tables} tables")

        except Exception as e:
            total_time = time.time() - start_time
            metrics.total_time_seconds = round(total_time, 2)
            metrics.success = False
            metrics.error_message = str(e)

            # Try to determine which stage failed
            if 'Research' in str(e) or 'scraping' in str(e).lower():
                metrics.failed_stage = 'Research'
            elif 'Demo Story' in str(e) or 'narrative' in str(e).lower():
                metrics.failed_stage = 'Demo Story'
            elif 'Data Modeling' in str(e) or 'schema' in str(e).lower():
                metrics.failed_stage = 'Data Modeling'
            elif 'Synthetic Data' in str(e):
                metrics.failed_stage = 'Synthetic Data'
            elif 'Infrastructure' in str(e) or 'BigQuery' in str(e):
                metrics.failed_stage = 'Infrastructure'
            elif 'REPEATED' in str(e):
                metrics.failed_stage = 'Infrastructure (REPEATED field error)'
                metrics.has_repeated_fields = True
            else:
                metrics.failed_stage = 'Unknown'

            logger.error(f"❌ FAILED: {site['url']}")
            logger.error(f"   Stage: {metrics.failed_stage}")
            logger.error(f"   Error: {metrics.error_message[:200]}")

        return metrics

    async def run_evaluation(self, site_limit: int = None) -> Dict[str, Any]:
        """Run evaluation across all test sites."""
        logger.info("\n" + "="*80)
        logger.info("AGENT EVALUATION FRAMEWORK")
        logger.info("="*80)
        logger.info(f"Testing {len(self.TEST_SITES)} customer sites")
        logger.info(f"Project: {self.project_id}\n")

        sites_to_test = self.TEST_SITES[:site_limit] if site_limit else self.TEST_SITES

        for i, site in enumerate(sites_to_test, 1):
            logger.info(f"\n[{i}/{len(sites_to_test)}] Testing {site['url']}...")
            metrics = await self.evaluate_single_site(site)
            self.results.append(metrics)

            # Small delay between tests to avoid rate limiting
            if i < len(sites_to_test):
                logger.info("Waiting 10 seconds before next test...")
                await asyncio.sleep(10)

        # Generate evaluation report
        report = self._generate_report()

        # Save results
        self._save_results()

        return report

    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive evaluation report."""
        total_tests = len(self.results)
        successful = sum(1 for r in self.results if r.success)
        failed = total_tests - successful

        success_rate = (successful / total_tests * 100) if total_tests > 0 else 0

        # Average metrics for successful demos
        successful_results = [r for r in self.results if r.success]

        if successful_results:
            avg_time = sum(r.total_time_seconds for r in successful_results) / len(successful_results)
            avg_quality = sum(r.overall_quality_score for r in successful_results) / len(successful_results)
            avg_queries = sum(r.total_queries for r in successful_results) / len(successful_results)
            avg_tables = sum(r.total_tables for r in successful_results) / len(successful_results)
            avg_rows = sum(r.total_rows for r in successful_results) / len(successful_results)

            top_quality = sorted(successful_results, key=lambda x: x.overall_quality_score, reverse=True)[:3]
            fastest = sorted(successful_results, key=lambda x: x.total_time_seconds)[:3]
        else:
            avg_time = avg_quality = avg_queries = avg_tables = avg_rows = 0
            top_quality = fastest = []

        # Failure analysis
        failure_reasons = {}
        for r in self.results:
            if not r.success:
                reason = r.failed_stage or 'Unknown'
                failure_reasons[reason] = failure_reasons.get(reason, 0) + 1

        report = {
            'summary': {
                'total_tests': total_tests,
                'successful': successful,
                'failed': failed,
                'success_rate': round(success_rate, 1),
                'avg_generation_time': round(avg_time, 2),
                'avg_quality_score': round(avg_quality, 1)
            },
            'averages': {
                'queries_per_demo': round(avg_queries, 1),
                'tables_per_demo': round(avg_tables, 1),
                'rows_per_demo': int(avg_rows),
                'expert_queries_per_demo': round(
                    sum(r.expert_queries for r in successful_results) / len(successful_results)
                    if successful_results else 0, 1
                )
            },
            'top_performers': {
                'highest_quality': [
                    {
                        'url': r.customer_url,
                        'company': r.company_name,
                        'score': r.overall_quality_score
                    }
                    for r in top_quality
                ],
                'fastest_generation': [
                    {
                        'url': r.customer_url,
                        'company': r.company_name,
                        'time': r.total_time_seconds
                    }
                    for r in fastest
                ]
            },
            'failure_analysis': failure_reasons,
            'detailed_results': [asdict(r) for r in self.results]
        }

        return report

    def _save_results(self):
        """Save evaluation results to JSON and markdown."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Save JSON
        json_file = f"/tmp/agent_evaluation_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump([asdict(r) for r in self.results], f, indent=2)
        logger.info(f"📄 Saved JSON results: {json_file}")

        # Generate markdown report
        md_file = f"/tmp/agent_evaluation_report_{timestamp}.md"
        self._generate_markdown_report(md_file)
        logger.info(f"📄 Saved markdown report: {md_file}")

    def _generate_markdown_report(self, filename: str):
        """Generate markdown evaluation report."""
        total = len(self.results)
        successful = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]

        with open(filename, 'w') as f:
            f.write("# Agent Evaluation Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Project:** {self.project_id}\n\n")
            f.write("---\n\n")

            # Executive Summary
            f.write("## Executive Summary\n\n")
            f.write(f"- **Total Tests:** {total}\n")
            f.write(f"- **Successful:** {len(successful)} ({len(successful)/total*100:.1f}%)\n")
            f.write(f"- **Failed:** {len(failed)} ({len(failed)/total*100:.1f}%)\n\n")

            if successful:
                avg_time = sum(r.total_time_seconds for r in successful) / len(successful)
                avg_quality = sum(r.overall_quality_score for r in successful) / len(successful)

                f.write(f"### Successful Demos:\n")
                f.write(f"- **Avg Generation Time:** {avg_time:.1f}s\n")
                f.write(f"- **Avg Quality Score:** {avg_quality:.1f}/100\n")
                f.write(f"- **Avg Queries:** {sum(r.total_queries for r in successful) / len(successful):.1f}\n")
                f.write(f"- **Avg Tables:** {sum(r.total_tables for r in successful) / len(successful):.1f}\n\n")

            # Success Details
            f.write("---\n\n")
            f.write("## Successful Demos\n\n")

            for r in sorted(successful, key=lambda x: x.overall_quality_score, reverse=True):
                f.write(f"### {r.company_name} ({r.customer_url})\n\n")
                f.write(f"**Quality Score:** {r.overall_quality_score}/100\n\n")
                f.write(f"**Industry:** {r.industry}\n\n")
                f.write(f"**Generation Time:** {r.total_time_seconds}s\n\n")
                f.write(f"**Golden Queries:** {r.total_queries} ")
                f.write(f"({r.simple_queries} simple, {r.medium_queries} medium, ")
                f.write(f"{r.complex_queries} complex, {r.expert_queries} expert)\n\n")
                f.write(f"**Data:** {r.total_rows:,} rows, {r.total_tables} tables, {r.total_size_mb:.2f} MB\n\n")
                f.write(f"**CAPI YAML:** {r.yaml_size_kb:.1f} KB\n\n")
                f.write("---\n\n")

            # Failure Analysis
            if failed:
                f.write("## Failed Demos\n\n")

                for r in failed:
                    f.write(f"### {r.customer_url}\n\n")
                    f.write(f"**Failed Stage:** {r.failed_stage}\n\n")
                    f.write(f"**Error:** `{r.error_message[:500]}`\n\n")
                    f.write(f"**Time to Failure:** {r.total_time_seconds}s\n\n")
                    f.write("---\n\n")


async def main():
    """Run evaluation framework."""
    load_dotenv()

    project_id = os.getenv('GCP_PROJECT_ID', 'bq-demos-469816')

    framework = AgentEvaluationFramework(project_id)

    # Run evaluation on first 10 sites
    report = await framework.run_evaluation(site_limit=10)

    # Print summary
    logger.info("\n" + "="*80)
    logger.info("EVALUATION COMPLETE")
    logger.info("="*80)
    logger.info(f"\n📊 SUMMARY:")
    logger.info(f"   Tests: {report['summary']['total_tests']}")
    logger.info(f"   Success Rate: {report['summary']['success_rate']}%")
    logger.info(f"   Avg Quality: {report['summary']['avg_quality_score']}/100")
    logger.info(f"   Avg Time: {report['summary']['avg_generation_time']}s")

    if report['failure_analysis']:
        logger.info(f"\n❌ FAILURES BY STAGE:")
        for stage, count in report['failure_analysis'].items():
            logger.info(f"   {stage}: {count}")


if __name__ == "__main__":
    asyncio.run(main())

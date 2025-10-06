"""
Quick evaluation test with 3 diverse sites.
Tests the evaluation framework before running full 10-site evaluation.
"""
import asyncio
import logging
from dotenv import load_dotenv
from agent_evaluation_framework import AgentEvaluationFramework

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def main():
    load_dotenv()

    print("\n" + "="*80)
    print("QUICK EVALUATION TEST - 3 SITES")
    print("="*80)
    print("\nTesting:")
    print("  1. Snowflake (Data Cloud) - Different from e-commerce")
    print("  2. Stripe (Payments) - Financial infrastructure")
    print("  3. HubSpot (Marketing) - SaaS platform")
    print("\nThis will take approximately 20-30 minutes total.\n")

    framework = AgentEvaluationFramework(project_id='bq-demos-469816')

    # Override test sites for quick test
    framework.TEST_SITES = [
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
        }
    ]

    # Run evaluation
    report = await framework.run_evaluation()

    # Print detailed results
    print("\n" + "="*80)
    print("EVALUATION COMPLETE")
    print("="*80)

    print(f"\n📊 RESULTS:")
    print(f"   Total Tests: {report['summary']['total_tests']}")
    print(f"   Successful: {report['summary']['successful']}")
    print(f"   Failed: {report['summary']['failed']}")
    print(f"   Success Rate: {report['summary']['success_rate']}%")

    if report['summary']['successful'] > 0:
        print(f"\n⭐ QUALITY METRICS (Successful Demos):")
        print(f"   Avg Quality Score: {report['summary']['avg_quality_score']}/100")
        print(f"   Avg Generation Time: {report['summary']['avg_generation_time']}s")
        print(f"   Avg Queries per Demo: {report['averages']['queries_per_demo']}")
        print(f"   Avg Expert Queries: {report['averages']['expert_queries_per_demo']}")
        print(f"   Avg Tables: {report['averages']['tables_per_demo']}")
        print(f"   Avg Rows: {report['averages']['rows_per_demo']:,}")

    if report['failure_analysis']:
        print(f"\n❌ FAILURE BREAKDOWN:")
        for stage, count in report['failure_analysis'].items():
            print(f"   {stage}: {count} demos")

    if report['top_performers']['highest_quality']:
        print(f"\n🏆 TOP QUALITY DEMOS:")
        for i, demo in enumerate(report['top_performers']['highest_quality'], 1):
            print(f"   {i}. {demo['company']} - {demo['score']}/100")

    if report['top_performers']['fastest_generation']:
        print(f"\n⚡ FASTEST GENERATION:")
        for i, demo in enumerate(report['top_performers']['fastest_generation'], 1):
            print(f"   {i}. {demo['company']} - {demo['time']}s")

    print("\n" + "="*80)
    print("Check /tmp/ for detailed JSON and markdown reports")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(main())

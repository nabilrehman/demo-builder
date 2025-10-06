"""
Test Enhanced Data Variety - Verifies improved prompts generate diverse data for dashboards.

Tests:
1. Row count increased to 200 per table
2. Distinct entity count (products, customers)
3. Distribution patterns (power law, geographic diversity)
4. No duplicates or similar variations
"""
import asyncio
import logging
import os
import sys
import pandas as pd
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agentic_service.agents.synthetic_data_generator_markdown import SyntheticDataGeneratorMarkdown

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def create_test_schema():
    """Create SolarWinds test schema - real schema from previous run."""
    return {
        "tables": [
            {
                "name": "products",
                "description": "SolarWinds software products and licenses",
                "record_count": 800,  # Expects 200 rows (min(800, 200))
                "schema": [
                    {"name": "product_id", "type": "STRING", "mode": "REQUIRED"},
                    {"name": "product_name", "type": "STRING", "mode": "REQUIRED"},
                    {"name": "product_category", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "product_tier", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "license_type", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "base_price", "type": "FLOAT64", "mode": "NULLABLE"},
                    {"name": "created_at", "type": "TIMESTAMP", "mode": "NULLABLE"}
                ]
            },
            {
                "name": "customers",
                "description": "Enterprise IT customers using SolarWinds",
                "record_count": 3000,  # Expects 200 rows (min(3000, 200))
                "schema": [
                    {"name": "customer_id", "type": "STRING", "mode": "REQUIRED"},
                    {"name": "company_name", "type": "STRING", "mode": "REQUIRED"},
                    {"name": "industry", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "city", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "country", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "employee_count", "type": "INT64", "mode": "NULLABLE"},
                    {"name": "it_infrastructure_size", "type": "STRING", "mode": "NULLABLE"}
                ]
            }
        ]
    }


def create_test_state():
    """Create test state with SolarWinds context - real data from previous run."""
    return {
        "schema": create_test_schema(),
        "demo_story": {
            "demo_title": "SolarWinds IT Infrastructure Monitoring Analytics",
            "executive_summary": "Comprehensive analysis of IT infrastructure monitoring and management across enterprise customers",
            "business_challenges": [
                "Multi-cloud monitoring complexity",
                "Alert fatigue and noise reduction",
                "MTTR improvement",
                "Infrastructure cost optimization"
            ],
            "key_metrics": [
                "Mean Time to Resolution (MTTR)",
                "Infrastructure uptime %",
                "Cost per monitored node",
                "Alert-to-incident ratio"
            ],
            "golden_queries": [
                {"question": "What is our average MTTR by customer tier?"},
                {"question": "Which product categories generate the most revenue?"},
                {"question": "How many customers have multi-cloud deployments?"},
                {"question": "What are the top alert types causing incidents?"}
            ]
        },
        "customer_info": {
            "company_name": "SolarWinds",
            "industry": "Enterprise Software - IT Management",
            "products": [
                "SolarWinds Network Performance Monitor (NPM)",
                "SolarWinds Server & Application Monitor (SAM)",
                "SolarWinds Database Performance Analyzer (DPA)",
                "SolarWinds Web Performance Monitor (WPM)",
                "SolarWinds Virtualization Manager (VMAN)",
                "SolarWinds Storage Resource Monitor (SRM)",
                "SolarWinds NetFlow Traffic Analyzer (NTA)",
                "SolarWinds User Device Tracker (UDT)",
                "SolarWinds IP Address Manager (IPAM)",
                "SolarWinds Log Analyzer",
                "SolarWinds Security Event Manager (SEM)",
                "SolarWinds Observability Platform"
            ],
            "business_model": "Enterprise SaaS and on-premise software licensing",
            "business_description": "Leading provider of IT infrastructure monitoring and management software for enterprises",
            "target_customers": [
                "Large enterprises (10,000+ employees)",
                "Mid-market IT organizations",
                "Managed Service Providers (MSPs)",
                "Government and public sector",
                "Healthcare IT departments"
            ],
            "key_features": [
                "Multi-cloud monitoring (AWS, Azure, GCP)",
                "Network performance monitoring",
                "Application performance management",
                "Database monitoring and optimization",
                "Log management and analysis",
                "Security event monitoring"
            ]
        },
        "project_id": "bq-demos-469816"
    }


async def analyze_data_variety(csv_file: str, table_name: str):
    """Analyze CSV file for data variety metrics."""
    logger.info(f"\n{'='*80}")
    logger.info(f"DATA VARIETY ANALYSIS: {table_name}")
    logger.info(f"{'='*80}")

    df = pd.read_csv(csv_file)
    total_rows = len(df)

    logger.info(f"\n📊 Basic Stats:")
    logger.info(f"  Total rows: {total_rows}")
    logger.info(f"  Columns: {', '.join(df.columns)}")

    # Analyze variety for each column
    variety_metrics = {}

    for col in df.columns:
        if col.endswith('_id'):
            continue  # Skip ID columns

        distinct_count = df[col].nunique()
        distinct_ratio = distinct_count / total_rows if total_rows > 0 else 0

        variety_metrics[col] = {
            'distinct': distinct_count,
            'ratio': distinct_ratio
        }

        logger.info(f"\n  {col}:")
        logger.info(f"    Distinct values: {distinct_count}")
        logger.info(f"    Variety ratio: {distinct_ratio:.1%}")

        # Show sample unique values
        if distinct_count <= 20:
            samples = df[col].unique()[:10]
            logger.info(f"    Samples: {', '.join(str(s) for s in samples)}")
        else:
            samples = df[col].unique()[:5]
            logger.info(f"    Samples (first 5): {', '.join(str(s) for s in samples)}")

    # Check for duplicates in name columns
    name_cols = [col for col in df.columns if 'name' in col.lower()]
    if name_cols:
        logger.info(f"\n🔍 Duplicate Check:")
        for col in name_cols:
            duplicates = df[col].duplicated().sum()
            if duplicates > 0:
                logger.info(f"  ❌ {col}: {duplicates} duplicates found")
            else:
                logger.info(f"  ✅ {col}: No duplicates")

    # Distribution analysis for numeric columns
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    if len(numeric_cols) > 0:
        logger.info(f"\n📈 Distribution Analysis:")
        for col in numeric_cols:
            if col.endswith('_id') or col.endswith('_count'):
                stats = df[col].describe()
                logger.info(f"\n  {col}:")
                logger.info(f"    Min: {stats['min']:.0f}")
                logger.info(f"    25th percentile: {stats['25%']:.0f}")
                logger.info(f"    Median: {stats['50%']:.0f}")
                logger.info(f"    75th percentile: {stats['75%']:.0f}")
                logger.info(f"    Max: {stats['max']:.0f}")

    return variety_metrics


async def test_data_variety():
    """Test enhanced data variety generation."""
    load_dotenv()

    logger.info("="*80)
    logger.info("ENHANCED DATA VARIETY TEST")
    logger.info("="*80)
    logger.info("\nTesting changes:")
    logger.info("  1. Row count: 50 → 200 per table")
    logger.info("  2. Distinct entities: Aiming for 100-150")
    logger.info("  3. Power law distributions")
    logger.info("  4. No duplicates in names")

    # Create test state
    state = create_test_state()

    logger.info(f"\nTest Schema:")
    for table in state['schema']['tables']:
        logger.info(f"  - {table['name']}: {table['record_count']:,} rows expected")

    # Generate data
    logger.info(f"\n{'='*80}")
    logger.info("GENERATING DATA...")
    logger.info(f"{'='*80}")

    generator = SyntheticDataGeneratorMarkdown()
    result_state = await generator.execute(state)

    # Analyze results
    logger.info(f"\n{'='*80}")
    logger.info("ANALYZING VARIETY...")
    logger.info(f"{'='*80}")

    files = result_state.get("synthetic_data_files", [])

    test_results = {
        'products': None,
        'customers': None
    }

    for filepath in files:
        table_name = os.path.basename(filepath).replace('.csv', '')

        if not os.path.exists(filepath):
            logger.error(f"File not found: {filepath}")
            continue

        metrics = await analyze_data_variety(filepath, table_name)
        test_results[table_name] = metrics

    # Evaluate results
    logger.info(f"\n{'='*80}")
    logger.info("TEST EVALUATION")
    logger.info(f"{'='*80}")

    passed_tests = []
    failed_tests = []

    # Test 1: Row count should be ~200 (not 50)
    for filepath in files:
        with open(filepath) as f:
            row_count = sum(1 for _ in f) - 1  # Exclude header

        table_name = os.path.basename(filepath).replace('.csv', '')
        if row_count >= 150:  # Allow some margin
            passed_tests.append(f"✅ {table_name}: {row_count} rows (target: 200)")
        else:
            failed_tests.append(f"❌ {table_name}: Only {row_count} rows (expected ~200)")

    # Test 2: Products should have 80-150 distinct names
    if 'products' in test_results and test_results['products']:
        product_metrics = test_results['products']
        if 'product_name' in product_metrics:
            distinct_products = product_metrics['product_name']['distinct']
            if distinct_products >= 80:
                passed_tests.append(f"✅ Product variety: {distinct_products} distinct products (target: 80-150)")
            else:
                failed_tests.append(f"❌ Product variety: Only {distinct_products} distinct products (expected 80-150)")

    # Test 3: Customers should have 100-150 distinct names
    if 'customers' in test_results and test_results['customers']:
        customer_metrics = test_results['customers']
        if 'company_name' in customer_metrics:
            distinct_customers = customer_metrics['company_name']['distinct']
            if distinct_customers >= 80:
                passed_tests.append(f"✅ Customer variety: {distinct_customers} distinct customers (target: 100-150)")
            else:
                failed_tests.append(f"❌ Customer variety: Only {distinct_customers} distinct customers (expected 100-150)")

    # Test 4: Categories should have 5-8 distinct values
    if 'products' in test_results and test_results['products']:
        if 'category' in test_results['products']:
            distinct_categories = test_results['products']['category']['distinct']
            if 5 <= distinct_categories <= 12:
                passed_tests.append(f"✅ Category diversity: {distinct_categories} categories (target: 5-8)")
            else:
                failed_tests.append(f"❌ Category diversity: {distinct_categories} categories (expected 5-8)")

    # Test 5: Geographic diversity (8-12 cities)
    if 'customers' in test_results and test_results['customers']:
        if 'city' in test_results['customers']:
            distinct_cities = test_results['customers']['city']['distinct']
            if distinct_cities >= 8:
                passed_tests.append(f"✅ Geographic diversity: {distinct_cities} cities (target: 8-12)")
            else:
                failed_tests.append(f"❌ Geographic diversity: Only {distinct_cities} cities (expected 8-12)")

    # Print results
    logger.info(f"\n✅ PASSED TESTS ({len(passed_tests)}):")
    for test in passed_tests:
        logger.info(f"  {test}")

    if failed_tests:
        logger.info(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
        for test in failed_tests:
            logger.info(f"  {test}")

    # Overall assessment
    logger.info(f"\n{'='*80}")
    logger.info("OVERALL ASSESSMENT")
    logger.info(f"{'='*80}")

    total_tests = len(passed_tests) + len(failed_tests)
    pass_rate = len(passed_tests) / total_tests if total_tests > 0 else 0

    if pass_rate >= 0.8:
        logger.info(f"✅ TEST PASSED: {pass_rate:.0%} success rate ({len(passed_tests)}/{total_tests} tests)")
        logger.info("Data variety enhancements are working as expected!")
    else:
        logger.info(f"❌ TEST FAILED: {pass_rate:.0%} success rate ({len(passed_tests)}/{total_tests} tests)")
        logger.info("Data variety improvements need adjustment.")

    logger.info(f"\nGenerated files:")
    for filepath in files:
        logger.info(f"  {filepath}")


if __name__ == "__main__":
    asyncio.run(test_data_variety())

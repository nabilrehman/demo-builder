"""
Test synthetic data generation with timing analysis.
"""
import asyncio
import logging
import os
import sys
import json
import time
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agentic_service.agents.synthetic_data_generator import SyntheticDataGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_data_generation():
    """Test synthetic data generation with performance metrics."""
    load_dotenv()

    # Load existing schema from previous test
    schema_file = "/tmp/schema_shopify.json"
    demo_story_file = "/tmp/demo_story_shopify.json"

    if not os.path.exists(schema_file):
        logger.error(f"Schema file not found: {schema_file}")
        logger.info("Run test_full_pipeline.py first to generate schema")
        return

    with open(schema_file) as f:
        schema = json.load(f)

    with open(demo_story_file) as f:
        demo_story = json.load(f)

    # Create state
    state = {
        "schema": schema,
        "demo_story": demo_story,
        "project_id": "bq-demos-469816"
    }

    logger.info("="*80)
    logger.info("SYNTHETIC DATA GENERATION TEST")
    logger.info("="*80)
    logger.info(f"\nTables to generate: {len(schema['tables'])}")
    for table in schema['tables']:
        logger.info(f"  - {table['name']}: {table.get('record_count', 0):,} rows (suggested)")

    # Generate data with timing
    logger.info("\n" + "="*80)
    logger.info("Starting generation...")
    logger.info("="*80)

    start_time = time.time()
    generator = SyntheticDataGenerator()
    state = await generator.execute(state)
    end_time = time.time()

    generation_time = end_time - start_time

    # Analyze results
    logger.info("\n" + "="*80)
    logger.info("GENERATION RESULTS")
    logger.info("="*80)

    files = state.get("synthetic_data_files", [])
    total_rows = 0
    total_size_mb = 0

    for filepath in files:
        if os.path.exists(filepath):
            # Get file stats
            size_bytes = os.path.getsize(filepath)
            size_mb = size_bytes / (1024 * 1024)
            total_size_mb += size_mb

            # Count rows
            with open(filepath) as f:
                row_count = sum(1 for line in f) - 1  # Exclude header
            total_rows += row_count

            filename = os.path.basename(filepath)
            logger.info(f"\n  {filename}")
            logger.info(f"    Rows: {row_count:,}")
            logger.info(f"    Size: {size_mb:.2f} MB")
            logger.info(f"    Rows/sec: {row_count/generation_time:,.0f}")

    logger.info("\n" + "="*80)
    logger.info("SUMMARY")
    logger.info("="*80)
    logger.info(f"Total files: {len(files)}")
    logger.info(f"Total rows: {total_rows:,}")
    logger.info(f"Total size: {total_size_mb:.2f} MB")
    logger.info(f"Generation time: {generation_time:.1f} seconds")
    logger.info(f"Throughput: {total_rows/generation_time:,.0f} rows/sec")

    # Performance assessment
    logger.info("\n" + "="*80)
    logger.info("PERFORMANCE ASSESSMENT")
    logger.info("="*80)

    if generation_time < 60:
        logger.info("✅ EXCELLENT: Under 1 minute")
    elif generation_time < 300:
        logger.info("✅ GOOD: Under 5 minutes")
    elif generation_time < 600:
        logger.info("⚠️  ACCEPTABLE: Under 10 minutes")
    else:
        logger.info("❌ SLOW: Over 10 minutes - consider reducing volumes")

    if total_rows < 10000:
        logger.info("⚠️  Low volume: May not show patterns well")
    elif total_rows < 100000:
        logger.info("✅ Optimal volume: Good balance of speed and realism")
    else:
        logger.info("⚠️  High volume: May be slow to load into BigQuery")

    return state


if __name__ == "__main__":
    asyncio.run(test_data_generation())

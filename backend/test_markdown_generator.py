"""
Test the MARKDOWN-based synthetic data generator currently in use.
This is the actual generator running in production.
"""
import asyncio
import logging
import os
import sys
import json
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agentic_service.agents.synthetic_data_generator_markdown import SyntheticDataGeneratorMarkdown

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Test data - simple table
TEST_CUSTOMER_INFO = {
    "company_name": "Kijiji",
    "industry": "Online Classifieds / Marketplace",
    "business_model": "C2C Marketplace with Advertising Revenue",
    "products": ["Classified Listings", "Featured Ads", "Auto Classifieds"]
}

TEST_DEMO_STORY = {
    "demo_title": "Kijiji Marketplace Analytics",
    "executive_summary": "Kijiji connects buyers and sellers across Canada...",
    "business_challenges": [
        {"challenge": "Track listing conversion rates"}
    ]
}

TEST_SCHEMA = {
    "tables": [
        {
            "name": "categories",
            "description": "Product categories for marketplace listings",
            "schema": [
                {"name": "category_id", "type": "INT64", "mode": "REQUIRED"},
                {"name": "category_name", "type": "STRING", "mode": "REQUIRED"},
                {"name": "parent_category", "type": "STRING", "mode": "NULLABLE"},
                {"name": "is_active", "type": "BOOL", "mode": "REQUIRED"}
            ],
            "primary_key": "category_id",
            "record_count": 20
        }
    ]
}


async def test_single_table_generation():
    """Test generating a single simple table to diagnose issues."""
    load_dotenv()

    logger.info("="*80)
    logger.info("🧪 TESTING MARKDOWN SYNTHETIC DATA GENERATOR")
    logger.info("="*80)

    # Create state
    state = {
        "customer_info": TEST_CUSTOMER_INFO,
        "demo_story": TEST_DEMO_STORY,
        "schema": TEST_SCHEMA,
        "project_id": "bq-demos-469816"
    }

    logger.info(f"\n📋 Test Configuration:")
    logger.info(f"   Company: {TEST_CUSTOMER_INFO['company_name']}")
    logger.info(f"   Table: {TEST_SCHEMA['tables'][0]['name']}")
    logger.info(f"   Rows: {TEST_SCHEMA['tables'][0]['record_count']}")
    logger.info(f"   Fields: {len(TEST_SCHEMA['tables'][0]['schema'])}")

    # Generate data
    logger.info("\n" + "="*80)
    logger.info("🚀 Starting Generation...")
    logger.info("="*80)

    try:
        generator = SyntheticDataGeneratorMarkdown()
        state = await generator.execute(state)

        logger.info("\n" + "="*80)
        logger.info("✅ GENERATION SUCCESSFUL")
        logger.info("="*80)

        # Check results
        files = state.get("synthetic_data_files", [])
        logger.info(f"\n📁 Generated files: {len(files)}")

        for filepath in files:
            if os.path.exists(filepath):
                filename = os.path.basename(filepath)
                size_kb = os.path.getsize(filepath) / 1024

                # Read first few lines
                with open(filepath, 'r') as f:
                    lines = f.readlines()[:6]  # Header + 5 rows

                logger.info(f"\n📄 {filename} ({size_kb:.1f} KB)")
                logger.info(f"   Rows: {len(lines) - 1}")
                logger.info(f"   Preview:")
                for line in lines:
                    logger.info(f"      {line.strip()}")

                # VALIDATION: Check if data looks correct
                if len(lines) > 1:
                    # Check if first line is header
                    header = lines[0].strip()
                    if "category_id" in header and "category_name" in header:
                        logger.info("   ✅ Header looks correct")
                    else:
                        logger.warning(f"   ⚠️ Header unexpected: {header}")

                    # Check if second line has data (not more explanatory text)
                    data_line = lines[1].strip()
                    if data_line and not data_line.startswith("Join us") and not data_line.startswith("Ingest"):
                        logger.info("   ✅ Data looks valid")
                    else:
                        logger.error(f"   ❌ DATA CORRUPTION: Line contains wrong content")
                        logger.error(f"      Got: {data_line[:100]}...")
                        return False
                else:
                    logger.error("   ❌ File is empty or has only header")
                    return False

        # Save successful outputs for inspection
        logger.info(f"\n💾 Files saved to /tmp/synthetic_data/")
        logger.info(f"   LLM prompts saved to /tmp/llm_prompts/")

        return True

    except Exception as e:
        logger.error("\n" + "="*80)
        logger.error("❌ GENERATION FAILED")
        logger.error("="*80)
        logger.error(f"Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_with_real_job_data():
    """Test with actual data from a failed job if available."""

    # Check if we have saved state from previous runs
    state_file = "/tmp/failed_job_state.json"
    if os.path.exists(state_file):
        logger.info("Found saved job state, testing with real data...")
        with open(state_file) as f:
            state = json.load(f)

        generator = SyntheticDataGeneratorMarkdown()
        state = await generator.execute(state)
        return True
    else:
        logger.info("No saved job state found, run simple test")
        return await test_single_table_generation()


if __name__ == "__main__":
    logger.info("\n🔍 Testing MARKDOWN Synthetic Data Generator")
    logger.info("This is the version currently running in production\n")

    success = asyncio.run(test_single_table_generation())

    if success:
        logger.info("\n" + "="*80)
        logger.info("✅ TEST PASSED")
        logger.info("="*80)
        sys.exit(0)
    else:
        logger.info("\n" + "="*80)
        logger.info("❌ TEST FAILED - Check logs above")
        logger.info("="*80)
        sys.exit(1)

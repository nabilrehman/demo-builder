"""
Test CAPI System Instruction Generator.
"""
import asyncio
import logging
import os
import sys
import json
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agentic_service.agents.capi_instruction_generator import CAPIInstructionGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_capi_instructions():
    """Test CAPI system instruction generation."""
    load_dotenv()

    # Load existing data from previous tests
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
        "customer_info": {
            "company_name": "Shopify",
            "industry": "E-commerce Platform"
        },
        "dataset_full_name": "bq-demos-469816.shopify_capi_demo_20251004",
        "project_id": "bq-demos-469816"
    }

    logger.info("="*80)
    logger.info("CAPI SYSTEM INSTRUCTION GENERATOR TEST")
    logger.info("="*80)
    logger.info(f"\nDataset: {state['dataset_full_name']}")
    logger.info(f"Company: {state['customer_info']['company_name']}")
    logger.info(f"Tables: {len(schema['tables'])}")
    logger.info(f"Golden Queries: {len(demo_story.get('golden_queries', []))}")

    # Generate YAML
    logger.info("\n" + "="*80)
    logger.info("Generating CAPI system instructions...")
    logger.info("="*80)

    generator = CAPIInstructionGenerator()
    state = await generator.execute(state)

    # Display results
    logger.info("\n" + "="*80)
    logger.info("GENERATION RESULTS")
    logger.info("="*80)

    yaml_file = state.get("capi_yaml_file")
    yaml_content = state.get("capi_system_instructions", "")

    logger.info(f"\n✅ YAML Generated: {yaml_file}")
    logger.info(f"   Size: {len(yaml_content):,} characters")
    logger.info(f"   Lines: {len(yaml_content.split(chr(10))):,}")

    # Analyze YAML structure
    logger.info("\n" + "="*80)
    logger.info("YAML STRUCTURE ANALYSIS")
    logger.info("="*80)

    sections = {
        "system_instruction": "system_instruction:" in yaml_content,
        "tables": "tables:" in yaml_content,
        "relationships": "relationships:" in yaml_content,
        "glossaries": "glossaries:" in yaml_content,
        "golden_queries": "golden_queries:" in yaml_content
    }

    for section, present in sections.items():
        status = "✓" if present else "✗"
        logger.info(f"{status} {section}")

    # Show first 50 lines
    logger.info("\n" + "="*80)
    logger.info("YAML PREVIEW (First 50 lines)")
    logger.info("="*80)

    if os.path.exists(yaml_file):
        with open(yaml_file) as f:
            lines = f.readlines()[:50]
        logger.info("".join(lines))

    # Validate YAML syntax
    logger.info("\n" + "="*80)
    logger.info("YAML VALIDATION")
    logger.info("="*80)

    try:
        import yaml
        with open(yaml_file) as f:
            yaml_data = yaml.safe_load(f)
        logger.info("✅ YAML syntax is valid")

        # Count elements
        if yaml_data:
            logger.info(f"\nYAML Contents:")
            if 'tables' in yaml_data:
                logger.info(f"  Tables: {len(yaml_data['tables'])}")
            if 'relationships' in yaml_data:
                logger.info(f"  Relationships: {len(yaml_data['relationships'])}")
            if 'glossaries' in yaml_data:
                logger.info(f"  Glossary terms: {len(yaml_data['glossaries'])}")
    except Exception as e:
        logger.error(f"❌ YAML validation failed: {e}")

    logger.info("\n" + "="*80)
    logger.info("NEXT STEPS")
    logger.info("="*80)
    logger.info("1. Review YAML file for completeness")
    logger.info("2. Use this YAML as system_instruction when creating CAPI agent")
    logger.info("3. Test golden queries through CAPI interface")
    logger.info("4. Validate results match expected SQL")

    return state


if __name__ == "__main__":
    asyncio.run(test_capi_instructions())

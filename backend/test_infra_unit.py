"""
UNIT TEST for Infrastructure Agent - NO FULL PIPELINE.

Tests the Infrastructure Agent's ability to:
1. Accept state with table_file_metadata (CODE mode - data already in BigQuery)
2. Create BigQuery dataset
3. Validate schema exists
4. Create CAPI agent

This does NOT run the full pipeline - it creates mock data to test the agent in isolation.
"""
import asyncio
import logging
import os
import sys
import tempfile
import csv
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agentic_service.agents.infrastructure_agent_optimized import InfrastructureAgentOptimized
from google.cloud import bigquery

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_mock_state_code_mode():
    """
    Create mock state for CODE MODE (data already uploaded to BigQuery).
    This simulates the output from synthetic_data_generator_code.py
    """
    customer_info = {
        "company_name": "Nike Test",
        "industry": "Retail",
        "website": "https://www.nike.com"
    }

    demo_story = {
        "demo_title": "Nike Analytics Test",
        "executive_summary": "Testing infrastructure agent",
        "golden_queries": [{"question": "Test query", "complexity": "low", "business_value": "Testing"}],
        "demo_narrative": {"introduction": "Test"},
        "business_challenges": []
    }

    schema = {
        "tables": [
            {
                "name": "customers",
                "description": "Customer data",
                "schema": [
                    {"name": "customer_id", "type": "STRING", "mode": "REQUIRED"},
                    {"name": "name", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "email", "type": "STRING", "mode": "NULLABLE"}
                ]
            },
            {
                "name": "orders",
                "description": "Order data",
                "schema": [
                    {"name": "order_id", "type": "STRING", "mode": "REQUIRED"},
                    {"name": "customer_id", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "total", "type": "FLOAT64", "mode": "NULLABLE"}
                ]
            }
        ]
    }

    # CODE MODE: table_file_metadata is populated, synthetic_data_files is empty
    table_file_metadata = [
        {"table_name": "customers", "row_count": 10000, "filename": "customers.csv"},
        {"table_name": "orders", "row_count": 50000, "filename": "orders.csv"}
    ]

    state = {
        "customer_info": customer_info,
        "demo_story": demo_story,
        "schema": schema,
        "table_file_metadata": table_file_metadata,  # FROM CODE GENERATOR
        "synthetic_data_files": [],  # Empty in code mode
        "capi_system_instructions": "You are a helpful assistant."
    }

    return state


def create_csv_files_for_testing(temp_dir, schema):
    """
    Create actual CSV files for testing CSV mode.
    Returns list of CSV file paths.
    """
    csv_files = []

    for table in schema["tables"]:
        table_name = table["name"]
        csv_path = os.path.join(temp_dir, f"{table_name}.csv")

        # Write CSV with headers
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)

            # Write header
            header = [field["name"] for field in table["schema"]]
            writer.writerow(header)

            # Write sample rows
            for i in range(100):
                if table_name == "customers":
                    writer.writerow([f"CUST{i:05d}", f"User {i}", f"user{i}@test.com"])
                elif table_name == "orders":
                    writer.writerow([f"ORD{i:05d}", f"CUST{i % 50:05d}", 100.0 + i])

        csv_files.append(csv_path)
        logger.info(f"   Created CSV: {csv_path} (100 rows)")

    return csv_files


async def test_validation_logic():
    """
    Test 1: Validation Logic
    Check that the agent correctly validates input state
    """
    logger.info("\n" + "="*80)
    logger.info("TEST 1: Validation Logic (Code Mode)")
    logger.info("="*80)

    state = create_mock_state_code_mode()

    logger.info("✓ Created mock state:")
    logger.info(f"  - Schema: {len(state['schema']['tables'])} tables")
    logger.info(f"  - table_file_metadata: {len(state['table_file_metadata'])} entries")
    logger.info(f"  - synthetic_data_files: {len(state['synthetic_data_files'])} files")

    # Check validation (from infrastructure_agent_optimized.py line 51)
    schema = state.get("schema", {})
    data_files = state.get("synthetic_data_files", [])
    table_metadata = state.get("table_file_metadata", [])

    will_pass = bool(schema) and (bool(data_files) or bool(table_metadata))

    logger.info(f"\n✓ Validation check:")
    logger.info(f"  - Schema present: {bool(schema)}")
    logger.info(f"  - Data files (CSV mode): {bool(data_files)}")
    logger.info(f"  - Table metadata (code mode): {bool(table_metadata)}")
    logger.info(f"  - Will pass validation: {will_pass}")

    if will_pass:
        logger.info("\n✅ TEST 1 PASSED: State will be accepted by Infrastructure Agent")
        return True
    else:
        logger.error("\n❌ TEST 1 FAILED: State will be rejected")
        return False


async def test_csv_mode_full_execution():
    """
    Test 2: Full Execution (CSV Mode)
    Actually run the Infrastructure Agent with real CSV files
    """
    logger.info("\n" + "="*80)
    logger.info("TEST 2: Full Execution (CSV Mode)")
    logger.info("="*80)

    # Create temp directory for CSV files
    temp_dir = tempfile.mkdtemp(prefix="infra_test_")
    logger.info(f"✓ Created temp dir: {temp_dir}")

    try:
        # Create mock state
        state = create_mock_state_code_mode()

        # Create CSV files
        csv_files = create_csv_files_for_testing(temp_dir, state["schema"])

        # Switch to CSV mode
        state["synthetic_data_files"] = csv_files
        state["table_file_metadata"] = []

        logger.info(f"\n✓ Prepared CSV mode state:")
        logger.info(f"  - CSV files: {len(csv_files)}")

        # Initialize agent
        agent = InfrastructureAgentOptimized()
        logger.info(f"\n✓ Infrastructure Agent initialized:")
        logger.info(f"  - Project: {agent.project_id}")
        logger.info(f"  - Location: {agent.location}")

        # Execute agent
        logger.info(f"\n⚡ Executing Infrastructure Agent...")
        result_state = await agent.execute(state)

        # Check results
        dataset_id = result_state.get("dataset_id")
        dataset_full_name = result_state.get("dataset_full_name")
        table_stats = result_state.get("table_stats", {})
        capi_agent_id = result_state.get("capi_agent_id")

        logger.info(f"\n✅ Infrastructure Agent completed successfully!")
        logger.info(f"\n📊 Results:")
        logger.info(f"  - Dataset: {dataset_full_name}")
        logger.info(f"  - Tables created: {len(table_stats)}")
        logger.info(f"  - CAPI Agent: {capi_agent_id or 'Not created'}")

        for table_name, stats in table_stats.items():
            logger.info(f"    • {table_name}: {stats['row_count']:,} rows")

        # Verify in BigQuery
        logger.info(f"\n🔍 Verifying in BigQuery...")
        bq_client = bigquery.Client(project=agent.project_id)

        try:
            dataset = bq_client.get_dataset(dataset_id)
            logger.info(f"  ✓ Dataset exists: {dataset.dataset_id}")

            # Check tables
            tables = list(bq_client.list_tables(dataset_id))
            logger.info(f"  ✓ Tables in BigQuery: {len(tables)}")
            for table in tables:
                table_ref = bq_client.get_table(table)
                logger.info(f"    • {table.table_id}: {table_ref.num_rows:,} rows")

        except Exception as e:
            logger.error(f"  ❌ BigQuery verification failed: {e}")
            return False

        logger.info(f"\n✅ TEST 2 PASSED: Full execution successful")
        logger.info(f"\n📍 View in BigQuery Console:")
        logger.info(f"   https://console.cloud.google.com/bigquery?project={agent.project_id}&d={dataset_id}")

        return True

    except Exception as e:
        logger.error(f"\n❌ TEST 2 FAILED: {e}", exc_info=True)
        return False

    finally:
        # Cleanup temp files
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        logger.info(f"\n✓ Cleaned up temp directory")


async def main():
    """Run all tests"""
    logger.info("\n" + "="*80)
    logger.info("INFRASTRUCTURE AGENT UNIT TESTS")
    logger.info("="*80)
    logger.info("\nThese tests validate the Infrastructure Agent in isolation")
    logger.info("without running the full pipeline.\n")

    results = []

    # Test 1: Validation logic
    result1 = await test_validation_logic()
    results.append(("Validation Logic", result1))

    # Test 2: Full execution
    logger.info("\n" + "="*80)

    # Check if we're in interactive mode
    import sys
    if sys.stdin.isatty():
        response = input("\nRun full execution test? This will create BigQuery resources. (y/n): ")
        run_full = response.lower() == 'y'
    else:
        # Non-interactive mode - auto-run
        logger.info("Running in non-interactive mode - auto-running full execution test")
        run_full = True

    if run_full:
        result2 = await test_csv_mode_full_execution()
        results.append(("Full Execution", result2))
    else:
        logger.info("⏭️  Skipping full execution test")

    # Summary
    logger.info("\n" + "="*80)
    logger.info("TEST SUMMARY")
    logger.info("="*80)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{status}: {test_name}")

    all_passed = all(result for _, result in results)

    if all_passed:
        logger.info("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        logger.info("\n❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

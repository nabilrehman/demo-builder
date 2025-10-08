"""
Test the code generator via deployed API with mock upstream data.
This skips Research, Demo Story, and Data Modeling agents.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from agentic_service.agents.synthetic_data_generator_code import SyntheticDataGeneratorCode


async def test_code_generator_with_apple_schema():
    """Test code generator with Apple-like schema (simulates what Data Modeling Agent would return)."""

    print("🧪 Testing Code Generator with Apple-like Schema")
    print("=" * 80)

    # Mock state from upstream agents (Research, Demo Story, Data Modeling)
    mock_state = {
        "customer_info": {
            "company_name": "Apple Inc.",
            "business_description": "Technology company specializing in consumer electronics, software, and online services",
            "industry": "Technology",
            "products": ["iPhone", "Mac", "iPad", "Apple Watch", "AirPods"],
            "revenue_model": "Product sales and services"
        },
        "demo_story": {
            "demo_title": "Apple Product Performance Analytics",
            "demo_description": "Analyze sales trends, customer preferences, and product performance across Apple's ecosystem",
            "golden_queries": [
                "What are the top 3 best-selling products this quarter?",
                "Show customer purchase patterns across product categories",
                "Compare iPhone vs Mac sales over the last 6 months"
            ]
        },
        "schema": {
            "dataset_name": "apple_analytics_demo",
            "description": "Apple product sales and customer analytics",
            "tables": [
                {
                    "name": "customers",
                    "description": "Customer profiles",
                    "schema": [
                        {"name": "customer_id", "type": "STRING", "mode": "REQUIRED", "description": "Unique customer ID"},
                        {"name": "email", "type": "STRING", "mode": "NULLABLE", "description": "Customer email"},
                        {"name": "name", "type": "STRING", "mode": "NULLABLE", "description": "Customer name"},
                        {"name": "country", "type": "STRING", "mode": "NULLABLE", "description": "Country"},
                        {"name": "member_since", "type": "TIMESTAMP", "mode": "NULLABLE", "description": "Account creation date"},
                        {"name": "lifetime_value", "type": "FLOAT64", "mode": "NULLABLE", "description": "Total spending"}
                    ]
                },
                {
                    "name": "products",
                    "description": "Apple product catalog",
                    "schema": [
                        {"name": "product_id", "type": "STRING", "mode": "REQUIRED", "description": "Unique product ID"},
                        {"name": "product_name", "type": "STRING", "mode": "NULLABLE", "description": "Product name"},
                        {"name": "category", "type": "STRING", "mode": "NULLABLE", "description": "Product category (iPhone, Mac, iPad, etc.)"},
                        {"name": "price", "type": "FLOAT64", "mode": "NULLABLE", "description": "Product price USD"},
                        {"name": "release_date", "type": "TIMESTAMP", "mode": "NULLABLE", "description": "Product release date"}
                    ]
                },
                {
                    "name": "orders",
                    "description": "Customer orders",
                    "schema": [
                        {"name": "order_id", "type": "STRING", "mode": "REQUIRED", "description": "Unique order ID"},
                        {"name": "customer_id", "type": "STRING", "mode": "NULLABLE", "description": "FK to customers"},
                        {"name": "order_date", "type": "TIMESTAMP", "mode": "NULLABLE", "description": "Order date"},
                        {"name": "total_amount", "type": "FLOAT64", "mode": "NULLABLE", "description": "Total order amount"},
                        {"name": "store_type", "type": "STRING", "mode": "NULLABLE", "description": "Online or Retail"}
                    ]
                },
                {
                    "name": "order_items",
                    "description": "Line items in orders",
                    "schema": [
                        {"name": "order_item_id", "type": "STRING", "mode": "REQUIRED", "description": "Unique order item ID"},
                        {"name": "order_id", "type": "STRING", "mode": "NULLABLE", "description": "FK to orders"},
                        {"name": "product_id", "type": "STRING", "mode": "NULLABLE", "description": "FK to products"},
                        {"name": "quantity", "type": "INT64", "mode": "NULLABLE", "description": "Quantity purchased"},
                        {"name": "unit_price", "type": "FLOAT64", "mode": "NULLABLE", "description": "Price per unit"}
                    ]
                }
            ]
        },
        "project_id": "bq-demos-469816"
    }

    # Test code generation
    generator = SyntheticDataGeneratorCode()

    print("\n📝 Step 1: Generating Python code with Claude...")
    try:
        code = await generator._generate_data_creation_code(
            mock_state["customer_info"],
            mock_state["demo_story"],
            mock_state["schema"],
            mock_state["project_id"],
            mock_state
        )

        print(f"✅ Generated {len(code)} characters of code")
        print(f"✅ Code contains {code.count('def ')} function definitions")
        print(f"✅ Code contains {code.count('DataFrame')} DataFrame references")

        # Check for critical patterns
        checks = {
            "Faker import": "from faker import Faker" in code,
            "BigQuery import": "from google.cloud import bigquery" in code,
            "Pandas import": "import pandas as pd" in code,
            "UUID import": "import uuid" in code,
            "datetime import": "from datetime import datetime" in code,
            "generate_customers function": "def generate_customers" in code,
            "generate_products function": "def generate_products" in code,
            "generate_orders function": "def generate_orders" in code,
            "upload_to_bigquery function": "def upload_to_bigquery" in code,
            "WRITE_TRUNCATE": "WRITE_TRUNCATE" in code,
            "tz_localize": "tz_localize" in code or ".dt.tz_localize(None)" in code,
        }

        print("\n🔍 Code Quality Checks:")
        all_passed = True
        for check_name, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check_name}")
            if not passed:
                all_passed = False

        # Check for datetime handling (the fix we made)
        datetime_checks = {
            "Uses datetime objects": "datetime.datetime" in code or "fake.date_time_between" in code,
            "No date/datetime mixing": ".date()" not in code or code.count(".date()") < 3,  # Some usage is ok
        }

        print("\n🕐 DateTime Handling Checks (Bug Fix Verification):")
        for check_name, passed in datetime_checks.items():
            status = "✅" if passed else "⚠️"
            print(f"  {status} {check_name}")

        # Save code for inspection
        output_file = "/tmp/apple_generated_code.py"
        with open(output_file, "w") as f:
            f.write(code)
        print(f"\n💾 Full code saved to: {output_file}")

        # Show sample of generated code
        print("\n📄 Code Sample (first 50 lines):")
        print("=" * 80)
        for i, line in enumerate(code.split('\n')[:50], 1):
            print(f"{i:3d} | {line}")
        print("=" * 80)

        if all_passed:
            print("\n🎉 All checks passed! Code generator is working correctly.")
            return True
        else:
            print("\n⚠️  Some checks failed. Review the generated code.")
            return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_code_generator_with_apple_schema())
    sys.exit(0 if success else 1)

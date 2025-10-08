"""
Test script for the code-based synthetic data generator.
"""
import asyncio
import json
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from agentic_service.agents.synthetic_data_generator_code import SyntheticDataGeneratorCode


async def test_code_generator():
    """Test the code generator with sample schema."""

    print("🧪 Testing Code-Based Synthetic Data Generator\n")

    # Sample state data
    state = {
        "customer_info": {
            "company_name": "Acme E-Commerce",
            "business_description": "Online retail platform selling electronics and gadgets",
            "industry": "E-commerce"
        },
        "demo_story": {
            "demo_title": "E-Commerce Analytics Demo",
            "demo_description": "Analyze customer behavior and product performance"
        },
        "schema": {
            "dataset_name": "acme_ecommerce_demo",
            "tables": [
                {
                    "name": "customers",
                    "description": "Customer profiles",
                    "schema": [
                        {"name": "customer_id", "type": "STRING", "mode": "REQUIRED", "description": "Unique customer ID"},
                        {"name": "email", "type": "STRING", "mode": "NULLABLE", "description": "Customer email"},
                        {"name": "name", "type": "STRING", "mode": "NULLABLE", "description": "Customer name"},
                        {"name": "country", "type": "STRING", "mode": "NULLABLE", "description": "Customer country"},
                        {"name": "created_at", "type": "TIMESTAMP", "mode": "NULLABLE", "description": "Account creation date"}
                    ]
                },
                {
                    "name": "products",
                    "description": "Product catalog",
                    "schema": [
                        {"name": "product_id", "type": "STRING", "mode": "REQUIRED", "description": "Unique product ID"},
                        {"name": "product_name", "type": "STRING", "mode": "NULLABLE", "description": "Product name"},
                        {"name": "category", "type": "STRING", "mode": "NULLABLE", "description": "Product category"},
                        {"name": "price", "type": "FLOAT64", "mode": "NULLABLE", "description": "Product price"}
                    ]
                },
                {
                    "name": "orders",
                    "description": "Customer orders",
                    "schema": [
                        {"name": "order_id", "type": "STRING", "mode": "REQUIRED", "description": "Unique order ID"},
                        {"name": "customer_id", "type": "STRING", "mode": "NULLABLE", "description": "Foreign key to customers"},
                        {"name": "product_id", "type": "STRING", "mode": "NULLABLE", "description": "Foreign key to products"},
                        {"name": "quantity", "type": "INT64", "mode": "NULLABLE", "description": "Order quantity"},
                        {"name": "order_date", "type": "TIMESTAMP", "mode": "NULLABLE", "description": "Order date"}
                    ]
                }
            ]
        },
        "project_id": "bq-demos-469816"
    }

    # Initialize generator
    generator = SyntheticDataGeneratorCode()

    # Test code generation
    print("📝 Step 1: Generating Python code...")
    try:
        code = await generator._generate_data_creation_code(
            state["customer_info"],
            state["demo_story"],
            state["schema"],
            state["project_id"],
            state
        )

        print(f"✅ Generated {len(code)} characters of code\n")
        print("=" * 80)
        print("GENERATED CODE:")
        print("=" * 80)
        print(code[:2000])  # Print first 2000 chars
        if len(code) > 2000:
            print(f"\n... ({len(code) - 2000} more characters)")
        print("=" * 80)

        # Save to file for inspection
        output_file = "/tmp/generated_data_code.py"
        with open(output_file, "w") as f:
            f.write(code)
        print(f"\n💾 Full code saved to: {output_file}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_code_generator())
    sys.exit(0 if success else 1)

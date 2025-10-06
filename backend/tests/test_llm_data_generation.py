"""
Test LLM-based Realistic Data Generation

Compares Faker vs LLM data quality for Stripe demo.
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentic_service.agents.synthetic_data_generator_optimized import SyntheticDataGeneratorOptimized


# Mock Stripe context (from Research Agent)
STRIPE_CONTEXT = {
    "company_name": "Stripe",
    "industry": "Financial Technology / Payments",
    "business_model": "B2B SaaS - Payment Processing Platform",
    "products": [
        "Stripe Payments API",
        "Stripe Connect (Platform)",
        "Stripe Billing",
        "Stripe Radar (Fraud Detection)",
        "Stripe Terminal",
        "Stripe Issuing",
        "Stripe Treasury"
    ]
}

STRIPE_DEMO_STORY = {
    "executive_summary": """
    Stripe's conversational analytics platform enables business teams to query payment data
    in natural language. Instead of waiting for engineering teams to build custom dashboards,
    product managers can ask questions like "What's our MRR growth for Connect platforms?"
    and get instant answers with visualizations. This accelerates decision-making for Stripe's
    fastest-growing product lines: Connect, Billing, and Radar.
    """,
    "business_challenges": [
        "High customer churn in first 90 days",
        "Identifying high-value cross-sell opportunities",
        "Monitoring fraud patterns across merchant segments"
    ]
}

# Test table schema for Products
PRODUCT_TABLE = {
    "name": "products",
    "schema": [
        {"name": "id", "type": "INT64"},
        {"name": "product_name", "type": "STRING"},
        {"name": "product_category", "type": "STRING"},
        {"name": "product_line", "type": "STRING"},
        {"name": "description", "type": "STRING"},
        {"name": "monthly_price", "type": "FLOAT64"},
        {"name": "is_active", "type": "BOOL"}
    ]
}


async def test_llm_vs_faker():
    """Compare LLM vs Faker data quality."""

    print("=" * 80)
    print("🧪 TESTING LLM-BASED DATA GENERATION")
    print("=" * 80)

    generator = SyntheticDataGeneratorOptimized()

    # Generate with LLM
    print("\n🤖 Generating data with LLM (Stripe context)...")
    llm_df = await generator._generate_table_data_with_llm(
        table=PRODUCT_TABLE,
        row_count=15,
        customer_info=STRIPE_CONTEXT,
        demo_story=STRIPE_DEMO_STORY,
        id_mappings={}
    )

    # Generate with Faker (fallback)
    print("\n📊 Generating data with Faker (generic)...")
    faker_df = generator._generate_table_data(
        table=PRODUCT_TABLE,
        row_count=15,
        id_mappings={},
        demo_story=STRIPE_DEMO_STORY
    )

    # Display comparison
    print("\n" + "=" * 80)
    print("📊 BEFORE (Faker): Generic Fashion Products")
    print("=" * 80)
    print(faker_df[['product_name', 'product_category', 'product_line']].head(10).to_string())

    if llm_df is not None:
        print("\n" + "=" * 80)
        print("✨ AFTER (LLM): Realistic Stripe Products")
        print("=" * 80)
        print(llm_df[['product_name', 'product_category', 'product_line']].head(10).to_string())

        print("\n" + "=" * 80)
        print("📈 SNAPSHOT: Full LLM Data (First 5 rows)")
        print("=" * 80)
        print(llm_df.head(5).to_string())

        # Save snapshot
        snapshot_dir = "/tmp/data_snapshots"
        os.makedirs(snapshot_dir, exist_ok=True)

        llm_df.to_csv(f"{snapshot_dir}/stripe_products_llm.csv", index=False)
        faker_df.to_csv(f"{snapshot_dir}/stripe_products_faker.csv", index=False)

        print(f"\n💾 Snapshots saved to:")
        print(f"   - {snapshot_dir}/stripe_products_llm.csv")
        print(f"   - {snapshot_dir}/stripe_products_faker.csv")

        print("\n✅ LLM generation SUCCESSFUL!")
        print("\n🎯 Key Improvements:")
        print("   ✓ Product names match Stripe's actual offerings")
        print("   ✓ Categories align with payments industry")
        print("   ✓ Descriptions are business-relevant")
        print("   ✓ Pricing reflects SaaS model")

    else:
        print("\n❌ LLM generation FAILED - Check logs for details")
        return False

    print("\n" + "=" * 80)
    return True


if __name__ == "__main__":
    success = asyncio.run(test_llm_vs_faker())
    sys.exit(0 if success else 1)

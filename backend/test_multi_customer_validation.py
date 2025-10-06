"""
Multi-Customer Validation Test - Prompt Ninja Enhancement

Tests the enhanced query-aware data generation across 5 different industries:
1. Stripe (FinTech - Payments)
2. Notion (Productivity SaaS)
3. Figma (Design/Collaboration)
4. Datadog (Observability/Monitoring)
5. Shopify (E-commerce Platform)

Validates:
- Data variety across different industries
- Query alignment for diverse query types
- Prompt adaptability to different business models
"""
import asyncio
import logging
import os
import sys
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agentic_service.agents.synthetic_data_generator_markdown import SyntheticDataGeneratorMarkdown

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


# 5 Test Customers from Different Industries
TEST_CUSTOMERS = {
    "stripe": {
        "customer_info": {
            "company_name": "Stripe",
            "industry": "FinTech - Payment Processing",
            "business_model": "API-first payment infrastructure platform",
            "business_description": "Stripe builds economic infrastructure for the internet. Businesses of every size use Stripe's software to accept payments and manage their businesses online.",
            "products": [
                "Stripe Payments - Payment processing API",
                "Stripe Billing - Subscription management",
                "Stripe Connect - Marketplace payments",
                "Stripe Radar - Fraud prevention",
                "Stripe Issuing - Card issuing platform",
                "Stripe Terminal - In-person payments",
                "Stripe Treasury - Banking-as-a-Service"
            ],
            "target_customers": [
                "E-commerce businesses",
                "SaaS companies",
                "Marketplaces",
                "Subscription businesses",
                "Platform businesses"
            ],
            "key_features": [
                "Global payment methods",
                "Real-time fraud detection",
                "Subscription billing",
                "Multi-currency support",
                "Developer-first APIs"
            ]
        },
        "demo_story": {
            "demo_title": "Stripe Payment Analytics & Revenue Optimization",
            "executive_summary": "Analyze payment processing patterns and revenue optimization across global merchants",
            "business_challenges": [
                "Payment fraud prevention",
                "Revenue leakage reduction",
                "Global expansion complexity",
                "Subscription churn management"
            ],
            "key_metrics": [
                "Payment success rate",
                "Fraud detection accuracy",
                "Revenue growth rate",
                "Customer lifetime value"
            ],
            "golden_queries": [
                {"question": "What are the top payment methods by transaction volume?"},
                {"question": "Which merchant categories have the highest fraud rates?"},
                {"question": "How has monthly recurring revenue grown over time?"},
                {"question": "What is the average transaction value by region?"}
            ]
        },
        "schema": {
            "tables": [
                {
                    "name": "transactions",
                    "description": "Payment transactions processed through Stripe",
                    "record_count": 5000,
                    "schema": [
                        {"name": "transaction_id", "type": "STRING", "mode": "REQUIRED"},
                        {"name": "merchant_id", "type": "STRING", "mode": "REQUIRED"},
                        {"name": "payment_method", "type": "STRING", "mode": "NULLABLE"},
                        {"name": "amount", "type": "FLOAT64", "mode": "NULLABLE"},
                        {"name": "currency", "type": "STRING", "mode": "NULLABLE"},
                        {"name": "status", "type": "STRING", "mode": "NULLABLE"},
                        {"name": "fraud_score", "type": "FLOAT64", "mode": "NULLABLE"},
                        {"name": "created_at", "type": "TIMESTAMP", "mode": "NULLABLE"}
                    ]
                }
            ]
        }
    },

    "notion": {
        "customer_info": {
            "company_name": "Notion",
            "industry": "Productivity SaaS",
            "business_model": "Freemium workspace collaboration platform",
            "business_description": "Notion is an all-in-one workspace for notes, tasks, wikis, and databases. Teams use Notion to collaborate and stay organized.",
            "products": [
                "Notion Personal - Individual workspace",
                "Notion Team - Team collaboration",
                "Notion Enterprise - Enterprise workspace",
                "Notion AI - AI-powered writing assistant",
                "Notion Templates - Pre-built workspaces",
                "Notion Calendar - Calendar integration",
                "Notion API - Programmatic access"
            ],
            "target_customers": [
                "Knowledge workers",
                "Remote teams",
                "Startups",
                "Engineering teams",
                "Product teams"
            ],
            "key_features": [
                "Block-based editor",
                "Real-time collaboration",
                "Databases and wikis",
                "Template gallery",
                "API and integrations"
            ]
        },
        "demo_story": {
            "demo_title": "Notion Workspace Analytics & User Engagement",
            "executive_summary": "Understand workspace usage patterns and collaboration metrics across teams",
            "business_challenges": [
                "User activation and retention",
                "Feature adoption tracking",
                "Workspace organization",
                "Team collaboration optimization"
            ],
            "key_metrics": [
                "Daily active users",
                "Pages created per user",
                "Collaboration score",
                "Template usage rate"
            ],
            "golden_queries": [
                {"question": "Which workspace features have the highest adoption rates?"},
                {"question": "How does team size impact daily active usage?"},
                {"question": "What are the most popular template categories?"},
                {"question": "Which user segments have the lowest churn rates?"}
            ]
        },
        "schema": {
            "tables": [
                {
                    "name": "workspaces",
                    "description": "Notion workspaces and teams",
                    "record_count": 1000,
                    "schema": [
                        {"name": "workspace_id", "type": "STRING", "mode": "REQUIRED"},
                        {"name": "workspace_name", "type": "STRING", "mode": "REQUIRED"},
                        {"name": "plan_type", "type": "STRING", "mode": "NULLABLE"},
                        {"name": "team_size", "type": "INT64", "mode": "NULLABLE"},
                        {"name": "industry", "type": "STRING", "mode": "NULLABLE"},
                        {"name": "pages_created", "type": "INT64", "mode": "NULLABLE"},
                        {"name": "created_at", "type": "TIMESTAMP", "mode": "NULLABLE"}
                    ]
                }
            ]
        }
    },

    "figma": {
        "customer_info": {
            "company_name": "Figma",
            "industry": "Design & Collaboration Software",
            "business_model": "Cloud-based design and prototyping platform",
            "business_description": "Figma is a collaborative interface design tool. Design, prototype, and gather feedback all in one place with Figma.",
            "products": [
                "Figma Design - Interface design tool",
                "FigJam - Online whiteboard",
                "Figma Prototyping - Interactive prototypes",
                "Figma Dev Mode - Developer handoff",
                "Figma Community - Design resources",
                "Figma Slides - Presentation tool"
            ],
            "target_customers": [
                "Design teams",
                "Product teams",
                "Design agencies",
                "Startups",
                "Enterprise design systems teams"
            ],
            "key_features": [
                "Real-time multiplayer collaboration",
                "Version control and branching",
                "Component libraries",
                "Auto-layout",
                "Developer handoff"
            ]
        },
        "demo_story": {
            "demo_title": "Figma Design Collaboration & Productivity Analytics",
            "executive_summary": "Track design system adoption and team collaboration metrics",
            "business_challenges": [
                "Design system consistency",
                "Cross-team collaboration",
                "Design-to-development handoff",
                "Asset organization at scale"
            ],
            "key_metrics": [
                "Component reuse rate",
                "Collaboration sessions",
                "Design-to-dev cycle time",
                "File organization score"
            ],
            "golden_queries": [
                {"question": "Which design components are most frequently reused?"},
                {"question": "How many collaborative editing sessions occur daily?"},
                {"question": "What is the average design iteration count by project type?"},
                {"question": "Which teams have the highest component library adoption?"}
            ]
        },
        "schema": {
            "tables": [
                {
                    "name": "design_files",
                    "description": "Figma design files and projects",
                    "record_count": 2000,
                    "schema": [
                        {"name": "file_id", "type": "STRING", "mode": "REQUIRED"},
                        {"name": "file_name", "type": "STRING", "mode": "REQUIRED"},
                        {"name": "project_type", "type": "STRING", "mode": "NULLABLE"},
                        {"name": "team_id", "type": "STRING", "mode": "NULLABLE"},
                        {"name": "components_used", "type": "INT64", "mode": "NULLABLE"},
                        {"name": "collaborators", "type": "INT64", "mode": "NULLABLE"},
                        {"name": "created_at", "type": "TIMESTAMP", "mode": "NULLABLE"}
                    ]
                }
            ]
        }
    },

    "datadog": {
        "customer_info": {
            "company_name": "Datadog",
            "industry": "Cloud Monitoring & Observability",
            "business_model": "SaaS-based monitoring and analytics platform",
            "business_description": "Datadog is a monitoring and analytics platform for developers, IT operations, and security teams.",
            "products": [
                "Infrastructure Monitoring",
                "APM (Application Performance Monitoring)",
                "Log Management",
                "Security Monitoring",
                "Network Performance Monitoring",
                "Real User Monitoring (RUM)",
                "Database Monitoring"
            ],
            "target_customers": [
                "DevOps teams",
                "SRE teams",
                "Cloud-native companies",
                "Enterprise IT",
                "Security teams"
            ],
            "key_features": [
                "Unified observability",
                "500+ integrations",
                "Machine learning insights",
                "Distributed tracing",
                "Real-time dashboards"
            ]
        },
        "demo_story": {
            "demo_title": "Datadog Platform Usage & Performance Analytics",
            "executive_summary": "Analyze monitoring coverage and incident response patterns",
            "business_challenges": [
                "Alert fatigue reduction",
                "MTTR improvement",
                "Monitoring coverage gaps",
                "Cost optimization"
            ],
            "key_metrics": [
                "Mean time to detect (MTTD)",
                "Alert-to-incident ratio",
                "Infrastructure coverage",
                "Query performance"
            ],
            "golden_queries": [
                {"question": "Which monitoring integrations generate the most alerts?"},
                {"question": "What is the average MTTR by incident severity?"},
                {"question": "How many hosts are monitored across different cloud providers?"},
                {"question": "Which customers have the highest log ingestion volume?"}
            ]
        },
        "schema": {
            "tables": [
                {
                    "name": "monitoring_hosts",
                    "description": "Monitored infrastructure hosts",
                    "record_count": 3000,
                    "schema": [
                        {"name": "host_id", "type": "STRING", "mode": "REQUIRED"},
                        {"name": "hostname", "type": "STRING", "mode": "REQUIRED"},
                        {"name": "cloud_provider", "type": "STRING", "mode": "NULLABLE"},
                        {"name": "instance_type", "type": "STRING", "mode": "NULLABLE"},
                        {"name": "tags", "type": "STRING", "mode": "NULLABLE"},
                        {"name": "integrations_count", "type": "INT64", "mode": "NULLABLE"},
                        {"name": "created_at", "type": "TIMESTAMP", "mode": "NULLABLE"}
                    ]
                }
            ]
        }
    },

    "shopify": {
        "customer_info": {
            "company_name": "Shopify",
            "industry": "E-commerce Platform",
            "business_model": "Multi-channel commerce platform for businesses",
            "business_description": "Shopify is a leading commerce platform that enables businesses to start, grow, and manage their online stores.",
            "products": [
                "Shopify POS - Point of sale",
                "Shopify Payments - Payment processing",
                "Shopify Shipping - Fulfillment",
                "Shopify Markets - International sales",
                "Shopify Plus - Enterprise commerce",
                "Shop App - Mobile shopping",
                "Shopify Flow - Automation"
            ],
            "target_customers": [
                "Direct-to-consumer brands",
                "Retail stores",
                "Wholesalers",
                "Enterprise merchants",
                "Multi-channel retailers"
            ],
            "key_features": [
                "Multi-channel selling",
                "Customizable storefronts",
                "App ecosystem",
                "Built-in payments",
                "International commerce"
            ]
        },
        "demo_story": {
            "demo_title": "Shopify Merchant Performance & Sales Analytics",
            "executive_summary": "Analyze merchant sales patterns and platform engagement metrics",
            "business_challenges": [
                "Merchant churn reduction",
                "GMV growth acceleration",
                "App ecosystem monetization",
                "International expansion"
            ],
            "key_metrics": [
                "Gross Merchandise Volume (GMV)",
                "Average order value (AOV)",
                "Merchant retention rate",
                "App installation rate"
            ],
            "golden_queries": [
                {"question": "Which merchant categories have the highest GMV?"},
                {"question": "What is the average order value by sales channel?"},
                {"question": "How has mobile commerce grown compared to desktop?"},
                {"question": "Which Shopify apps have the highest installation rates?"}
            ]
        },
        "schema": {
            "tables": [
                {
                    "name": "merchants",
                    "description": "Shopify merchant stores",
                    "record_count": 2500,
                    "schema": [
                        {"name": "merchant_id", "type": "STRING", "mode": "REQUIRED"},
                        {"name": "store_name", "type": "STRING", "mode": "REQUIRED"},
                        {"name": "merchant_category", "type": "STRING", "mode": "NULLABLE"},
                        {"name": "plan_tier", "type": "STRING", "mode": "NULLABLE"},
                        {"name": "monthly_gmv", "type": "FLOAT64", "mode": "NULLABLE"},
                        {"name": "sales_channels", "type": "STRING", "mode": "NULLABLE"},
                        {"name": "created_at", "type": "TIMESTAMP", "mode": "NULLABLE"}
                    ]
                }
            ]
        }
    }
}


async def test_customer(customer_name: str, customer_data: dict):
    """Test data generation for a single customer."""
    logger.info(f"\n{'='*100}")
    logger.info(f"TESTING: {customer_data['customer_info']['company_name'].upper()}")
    logger.info(f"Industry: {customer_data['customer_info']['industry']}")
    logger.info(f"{'='*100}")

    # Create state
    state = {
        "customer_info": customer_data["customer_info"],
        "demo_story": customer_data["demo_story"],
        "schema": customer_data["schema"],
        "project_id": "bq-demos-469816"
    }

    # Log golden queries
    logger.info(f"\n🎯 Golden Queries for {customer_name.upper()}:")
    for i, query in enumerate(customer_data["demo_story"]["golden_queries"], 1):
        logger.info(f"  {i}. {query['question']}")

    # Generate data
    generator = SyntheticDataGeneratorMarkdown()
    result_state = await generator.execute(state)

    # Analyze results
    files = result_state.get("synthetic_data_files", [])

    if not files:
        logger.error(f"❌ No files generated for {customer_name}")
        return None

    # Analyze the generated CSV
    for filepath in files:
        table_name = os.path.basename(filepath).replace('.csv', '')

        if not os.path.exists(filepath):
            logger.error(f"❌ File not found: {filepath}")
            continue

        df = pd.read_csv(filepath)

        logger.info(f"\n📊 Data Analysis for {table_name}:")
        logger.info(f"  Total rows: {len(df)}")
        logger.info(f"  Columns: {list(df.columns)}")

        # Find name/title column
        name_col = None
        for col in df.columns:
            if 'name' in col.lower() or 'title' in col.lower():
                name_col = col
                break

        if name_col:
            distinct = df[name_col].nunique()
            variety_pct = distinct / len(df) * 100
            logger.info(f"\n  ✅ Distinct {name_col}: {distinct} / {len(df)} ({variety_pct:.1f}% unique)")

            # Show samples
            logger.info(f"\n  Sample {name_col}:")
            for i, name in enumerate(df[name_col].head(10), 1):
                logger.info(f"    {i}. {name}")

        # Check for variety in categorical columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        categorical_cols = [col for col in categorical_cols if not col.endswith('_id')]

        if len(categorical_cols) > 0:
            logger.info(f"\n  📊 Category Distributions:")
            for col in categorical_cols[:3]:  # Show first 3
                unique_count = df[col].nunique()
                if unique_count < 20:  # Only show if reasonable number
                    value_counts = df[col].value_counts()
                    logger.info(f"\n    {col} ({unique_count} categories):")
                    for cat, count in value_counts.head(5).items():
                        pct = count / len(df) * 100
                        logger.info(f"      {cat}: {count} ({pct:.1f}%)")

    return {
        "customer": customer_name,
        "company": customer_data['customer_info']['company_name'],
        "industry": customer_data['customer_info']['industry'],
        "files": files,
        "success": len(files) > 0
    }


async def run_multi_customer_test():
    """Run tests for all 5 customers."""
    logger.info("="*100)
    logger.info("MULTI-CUSTOMER VALIDATION TEST - Prompt Ninja Enhancement")
    logger.info("="*100)
    logger.info(f"\nTesting {len(TEST_CUSTOMERS)} customers across different industries:\n")

    for customer_name in TEST_CUSTOMERS.keys():
        company = TEST_CUSTOMERS[customer_name]['customer_info']['company_name']
        industry = TEST_CUSTOMERS[customer_name]['customer_info']['industry']
        logger.info(f"  • {company} ({industry})")

    logger.info(f"\n{'='*100}\n")

    # Run tests sequentially (could be parallel but want to see output clearly)
    results = []
    for customer_name, customer_data in TEST_CUSTOMERS.items():
        try:
            result = await test_customer(customer_name, customer_data)
            results.append(result)
        except Exception as e:
            logger.error(f"❌ Failed for {customer_name}: {e}", exc_info=True)
            results.append({
                "customer": customer_name,
                "success": False,
                "error": str(e)
            })

    # Summary
    logger.info(f"\n{'='*100}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*100}\n")

    successful = [r for r in results if r and r.get('success')]
    failed = [r for r in results if not r or not r.get('success')]

    logger.info(f"✅ Successful: {len(successful)}/{len(results)}")
    logger.info(f"❌ Failed: {len(failed)}/{len(results)}")

    if successful:
        logger.info(f"\n✅ PASSED:")
        for r in successful:
            logger.info(f"  • {r['company']} ({r['industry']})")

    if failed:
        logger.info(f"\n❌ FAILED:")
        for r in failed:
            logger.info(f"  • {r.get('customer', 'Unknown')}")

    # Overall assessment
    success_rate = len(successful) / len(results) * 100
    logger.info(f"\n{'='*100}")
    if success_rate >= 80:
        logger.info(f"🎉 TEST PASSED: {success_rate:.0f}% success rate")
        logger.info("Prompt Ninja enhancement works across diverse industries!")
    else:
        logger.info(f"⚠️ TEST NEEDS IMPROVEMENT: {success_rate:.0f}% success rate")
    logger.info(f"{'='*100}")


if __name__ == "__main__":
    asyncio.run(run_multi_customer_test())

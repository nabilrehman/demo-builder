# 🎯 Customer Engineer Improvements Roadmap
## Conversational Analytics API Demo Platform

**Document Version:** 1.0
**Last Updated:** October 5, 2025
**Target Audience:** Product Team, Engineering, Customer Engineers

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current State Analysis](#current-state-analysis)
3. [Proposed Improvements](#proposed-improvements)
   - [1. Demo Template Library](#1-demo-template-library-critical)
   - [2. Two-Mode Provisioning](#2-two-mode-provisioning-critical)
   - [3. Demo Management Dashboard](#3-demo-management-dashboard-critical)
   - [4. Preview & Customize](#4-preview--customize-before-provisioning-high)
   - [5. Demo Sharing & Handoff](#5-demo-sharing--handoff-high)
   - [6. Persistent Storage](#6-persistent-storage--history-high)
   - [7. Cost & Resource Management](#7-cost--resource-management-medium)
   - [8. Industry Quick Starts](#8-industry-specific-quick-starts-medium)
4. [Implementation Roadmap](#implementation-roadmap)
5. [CE Best Practices](#ce-best-practices-guide)
6. [Success Metrics](#key-metrics-for-success)
7. [Quick Win Implementation](#quick-win-template-library-in-1-week)
8. [Technical Specifications](#technical-specifications)

---

## 📊 Executive Summary

### The Problem
Current platform generates demos autonomously but lacks features essential for Customer Engineers (CEs) conducting live demos:
- **6-10 minute provisioning** is too slow for live demonstrations
- **No reusability** - Every demo starts from scratch
- **No preparation workflow** - Can't prepare demos ahead of time
- **Limited collaboration** - Hard to share demos or hand off to customers

### The Solution
Transform the platform from a "one-off generator" into a **Demo Management Platform** with:
- ⚡ **45-second quick provisioning** using pre-built templates
- 📚 **Template library** with industry-specific pre-validated demos
- 🔄 **Demo reusability** through cloning, pinning, and sharing
- 🤝 **Collaboration features** for team sharing and customer handoff

### Business Impact
- **10x faster** demo provisioning (45s vs 6min)
- **3x more demos** per CE per week (reusability)
- **Higher conversion** through better preparation and follow-up
- **Reduced costs** through automated lifecycle management

---

## 🔍 Current State Analysis

### Pain Points for Customer Engineers

| Issue | Impact on CE Workflow | Business Impact | Priority |
|-------|----------------------|-----------------|----------|
| **6-10 min provisioning time** | Can't provision during live demos; must prepare days ahead | Missed opportunities, awkward delays | 🔴 CRITICAL |
| **No demo reusability** | Recreate similar demos repeatedly; wasted time/resources | Low CE efficiency | 🔴 CRITICAL |
| **No template library** | Can't browse proven demos; start from scratch each time | Inconsistent quality | 🔴 CRITICAL |
| **Can't customize before provision** | One-size-fits-all; hope it matches customer needs | Generic demos, less impactful | 🟡 HIGH |
| **No demo sharing** | Hard to collaborate with team or hand off to customer | Knowledge silos | 🟡 HIGH |
| **In-memory state only** | Lose all history on backend restart; can't review past demos | No audit trail, lost work | 🟡 HIGH |
| **No industry presets** | Research customer's industry each time | Time-consuming prep | 🟢 MEDIUM |
| **Can't clone/fork demos** | Repetitive customization work | Inefficiency | 🟢 MEDIUM |
| **No cost management** | Old datasets accumulate forever | Unnecessary costs | 🟢 MEDIUM |

### Current CE Workflow (Problematic)

```
Day 1: Schedule demo with prospect
Day 2: Research prospect's industry
Day 3: Submit provisioning job (wait 6-10 min)
Day 3: Hope generated demo is relevant
Day 4: Test queries, find issues
Day 4: Re-provision with different settings (wait 6-10 min)
Day 5: Demo day - Cross fingers it works
```

**Total time investment:** 4-6 hours
**Success rate:** ~60% (demos often need re-generation)

### Desired CE Workflow (With Improvements)

```
Day 1: Schedule demo with prospect
Day 1: Browse template library → Pick "Retail Analytics"
Day 1: Customize company branding (2 min)
Day 1: Clone & provision (45 seconds)
Day 1: Test 3 queries (5 min)
Day 2-4: Other work
Day 5: Demo day - Launch pinned demo
```

**Total time investment:** 20 minutes
**Success rate:** 95% (pre-validated templates)

---

## 🚀 Proposed Improvements

### 1. Demo Template Library (CRITICAL)

**Current:** Every demo generates from scratch (6-10 minutes)
**Proposed:** Pre-built, battle-tested templates (45 seconds)

#### UI Mockup: Template Library

```
┌─────────────────────────────────────────────────────────────────┐
│  📚 Demo Template Library                    [+ Create Template] │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  🔍 Search: [____________________]  Filter: [All Industries ▼]  │
│                                                                   │
│  ⭐ MOST USED TEMPLATES                                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  🛒 Shopify E-commerce Analytics              47 uses   │   │
│  │  15 tables • 145K rows • 18 golden queries              │   │
│  │  Provision time: 45 seconds                              │   │
│  │  Last updated: Oct 1, 2025                               │   │
│  │  [Preview] [Quick Start] [Clone & Customize]            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  🏦 Banking Customer 360                      39 uses   │   │
│  │  22 tables • 500K rows • 25 golden queries              │   │
│  │  Provision time: 60 seconds                              │   │
│  │  Last updated: Sep 28, 2025                              │   │
│  │  [Preview] [Quick Start] [Clone & Customize]            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  📂 BY INDUSTRY                                                  │
│  • Retail & E-commerce (5 templates)                            │
│  • Financial Services (4 templates)                             │
│  • Healthcare & Life Sciences (3 templates)                     │
│  • Technology & SaaS (3 templates)                              │
│  • Manufacturing & Supply Chain (2 templates)                   │
│                                                                   │
│  [View All Templates →]                                          │
└─────────────────────────────────────────────────────────────────┘
```

#### Technical Implementation

**Backend: Template Registry**

```python
# backend/templates/template_registry.py

from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime

@dataclass
class DemoTemplate:
    """Pre-built demo template with all artifacts."""
    template_id: str
    display_name: str
    industry: str
    description: str

    # Data artifacts
    schema: Dict  # Pre-designed schema
    golden_queries: List[Dict]  # Pre-validated queries
    data_files: str  # GCS path to parquet files

    # Metadata
    table_count: int
    total_rows: int
    estimated_provision_time: str  # "45s"
    thumbnail_url: str

    # Usage tracking
    usage_count: int
    last_updated: datetime
    created_by: str
    tags: List[str]

    # CAPI agent config
    agent_template_yaml: str  # Path to YAML file


class TemplateRegistry:
    """Manages demo template library."""

    def __init__(self):
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, DemoTemplate]:
        """Load all available templates."""
        return {
            "shopify_analytics": DemoTemplate(
                template_id="shopify_analytics",
                display_name="Shopify E-commerce Analytics",
                industry="Retail & E-commerce",
                description="Complete merchant analytics platform with orders, payments, inventory, and customer data",
                schema=self._load_schema("shopify"),
                golden_queries=self._load_queries("shopify"),
                data_files="gs://capi-templates/shopify/*.parquet",
                table_count=15,
                total_rows=145000,
                estimated_provision_time="45s",
                thumbnail_url="https://storage.googleapis.com/capi-templates/thumbnails/shopify.png",
                usage_count=47,
                last_updated=datetime(2025, 10, 1),
                created_by="team@google.com",
                tags=["retail", "ecommerce", "merchants", "payments"],
                agent_template_yaml="templates/agents/shopify_agent.yaml"
            ),
            "banking_customer_360": DemoTemplate(
                template_id="banking_customer_360",
                display_name="Banking Customer 360",
                industry="Financial Services",
                description="Complete banking analytics with accounts, transactions, customer profiles, and product holdings",
                schema=self._load_schema("banking"),
                golden_queries=self._load_queries("banking"),
                data_files="gs://capi-templates/banking/*.parquet",
                table_count=22,
                total_rows=500000,
                estimated_provision_time="60s",
                thumbnail_url="https://storage.googleapis.com/capi-templates/thumbnails/banking.png",
                usage_count=39,
                last_updated=datetime(2025, 9, 28),
                created_by="team@google.com",
                tags=["banking", "finance", "customer360", "accounts"],
                agent_template_yaml="templates/agents/banking_agent.yaml"
            ),
            # Add more templates...
        }

    def get_template(self, template_id: str) -> DemoTemplate:
        """Retrieve specific template."""
        return self.templates.get(template_id)

    def list_templates(self, industry: str = None, tags: List[str] = None) -> List[DemoTemplate]:
        """List templates with optional filtering."""
        templates = list(self.templates.values())

        if industry:
            templates = [t for t in templates if t.industry == industry]

        if tags:
            templates = [t for t in templates if any(tag in t.tags for tag in tags)]

        # Sort by usage count (most popular first)
        templates.sort(key=lambda t: t.usage_count, reverse=True)

        return templates

    def increment_usage(self, template_id: str):
        """Track template usage."""
        if template_id in self.templates:
            self.templates[template_id].usage_count += 1
```

**Backend: Fast Provisioning from Template**

```python
# backend/templates/quick_provision.py

from google.cloud import bigquery, storage
import time

class QuickProvisioner:
    """Provision demos quickly from templates."""

    def __init__(self):
        self.bq = bigquery.Client()
        self.storage = storage.Client()
        self.registry = TemplateRegistry()

    async def provision_from_template(
        self,
        template_id: str,
        customer_name: str,
        custom_branding: Dict = None
    ) -> Dict:
        """
        Provision demo from template in ~45 seconds.

        Speed optimization:
        - Pre-generated parquet files (no data generation needed)
        - Pre-validated schema (no LLM calls)
        - Pre-configured agent YAML (no instruction generation)
        """
        start_time = time.time()

        # 1. Get template (instant)
        template = self.registry.get_template(template_id)
        self.registry.increment_usage(template_id)

        # 2. Create dataset (~5 seconds)
        dataset_id = self._generate_dataset_name(customer_name, template_id)
        await self._create_dataset(dataset_id, template, custom_branding)

        # 3. Load data from parquet files (~30-40 seconds)
        #    This is MUCH faster than generating synthetic data
        await self._load_parquet_files(
            source=template.data_files,
            destination=dataset_id
        )

        # 4. Create CAPI agent (~5-10 seconds)
        agent_id = await self._create_agent_from_template(
            template=template,
            dataset_id=dataset_id,
            customer_name=customer_name,
            custom_branding=custom_branding
        )

        elapsed = time.time() - start_time

        return {
            "dataset_id": dataset_id,
            "dataset_full_name": f"{self.bq.project}.{dataset_id}",
            "agent_id": agent_id,
            "golden_queries": template.golden_queries,
            "schema": template.schema,
            "provision_time_seconds": elapsed,
            "template_used": template_id,
            "metadata": {
                "template_name": template.display_name,
                "total_rows": template.total_rows,
                "table_count": template.table_count
            }
        }

    async def _load_parquet_files(self, source: str, destination: str):
        """
        Load pre-generated parquet files into BigQuery.

        This is 5-10x faster than generating synthetic data because:
        - Data already exists
        - Parquet is optimized for BigQuery
        - No need for CSV → BigQuery conversion
        """
        # List all parquet files
        bucket_name, prefix = self._parse_gcs_path(source)
        bucket = self.storage.bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=prefix)

        jobs = []
        for blob in blobs:
            if blob.name.endswith('.parquet'):
                # Extract table name from filename
                # e.g., "shopify/customers.parquet" → "customers"
                table_name = blob.name.split('/')[-1].replace('.parquet', '')

                # Load job config
                job_config = bigquery.LoadJobConfig(
                    source_format=bigquery.SourceFormat.PARQUET,
                    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
                )

                # Start load job
                table_ref = f"{self.bq.project}.{destination}.{table_name}"
                uri = f"gs://{bucket_name}/{blob.name}"

                load_job = self.bq.load_table_from_uri(
                    uri,
                    table_ref,
                    job_config=job_config
                )
                jobs.append(load_job)

        # Wait for all jobs to complete (parallel loading)
        for job in jobs:
            job.result()  # Wait for completion

    async def _create_agent_from_template(
        self,
        template: DemoTemplate,
        dataset_id: str,
        customer_name: str,
        custom_branding: Dict
    ) -> str:
        """Create CAPI agent using template YAML."""
        from google.cloud import geminidataanalytics

        client = geminidataanalytics.DataAgentServiceClient()

        # Load template YAML
        with open(template.agent_template_yaml, 'r') as f:
            yaml_content = f.read()

        # Customize with customer name if provided
        if custom_branding and 'company_name' in custom_branding:
            yaml_content = yaml_content.replace(
                "{COMPANY_NAME}",
                custom_branding['company_name']
            )
        else:
            yaml_content = yaml_content.replace("{COMPANY_NAME}", customer_name)

        # Create agent
        agent = geminidataanalytics.DataAgent()
        agent.display_name = f"{customer_name} - {template.display_name}"

        published_context = geminidataanalytics.Context()
        published_context.system_instruction = yaml_content

        # Link to dataset
        data_source = geminidataanalytics.DataSource()
        data_source.bigquery_dataset = f"projects/{self.bq.project}/datasets/{dataset_id}"
        published_context.data_sources = [data_source]

        agent.published_context = published_context

        # Create agent
        request = geminidataanalytics.CreateDataAgentRequest(
            parent=f"projects/{self.bq.project}/locations/global",
            data_agent=agent
        )

        created_agent = client.create_data_agent(request=request)
        agent_id = created_agent.name.split('/')[-1]

        return agent_id
```

**API Endpoint: Quick Provision**

```python
# backend/routes/provisioning.py

@router.post("/quick-provision", response_model=ProvisionResponse)
async def quick_provision_from_template(
    template_id: str,
    customer_name: str,
    custom_branding: Optional[Dict] = None,
    background_tasks: BackgroundTasks
):
    """
    Quick provision from template (45-60 seconds).

    Much faster than custom generation because:
    - Uses pre-generated data (no synthetic generation needed)
    - Uses pre-validated schema (no LLM calls)
    - Uses pre-configured agent (no YAML generation)
    """
    job_id = str(uuid.uuid4())

    # Create job
    job_manager.create_job(
        job_id=job_id,
        customer_url=f"template:{template_id}",
        mode="quick_template"
    )

    # Run quick provisioning in background
    async def run_quick_provision():
        try:
            provisioner = QuickProvisioner()
            result = await provisioner.provision_from_template(
                template_id=template_id,
                customer_name=customer_name,
                custom_branding=custom_branding
            )

            # Update job with results
            job_manager.set_results(
                job_id=job_id,
                dataset_id=result["dataset_id"],
                demo_title=f"{customer_name} - {result['metadata']['template_name']}",
                golden_queries=result["golden_queries"],
                schema=result["schema"],
                metadata=result["metadata"]
            )
            job_manager.update_job_status(job_id, "completed")

        except Exception as e:
            job_manager.add_error(job_id, str(e))
            job_manager.update_job_status(job_id, "failed")

    background_tasks.add_task(run_quick_provision)

    return ProvisionResponse(
        job_id=job_id,
        status="pending",
        message=f"Quick provisioning from template: {template_id}",
        customer_url=f"template:{template_id}"
    )
```

#### Initial Templates to Include

1. **Shopify E-commerce Analytics** (Retail)
   - 15 tables, 145K rows
   - Merchant performance, orders, payments, inventory

2. **Banking Customer 360** (Financial Services)
   - 22 tables, 500K rows
   - Accounts, transactions, customer profiles, products

3. **Healthcare Patient Journey** (Healthcare)
   - 19 tables, 180K rows
   - Patient records, treatments, outcomes, providers

4. **SaaS Product Analytics** (Technology)
   - 12 tables, 200K rows
   - Users, events, subscriptions, features

5. **Supply Chain Operations** (Manufacturing)
   - 16 tables, 300K rows
   - Inventory, shipments, suppliers, warehouses

---

### 2. Two-Mode Provisioning (CRITICAL)

**Current:** Only "Full Custom" mode (6-10 minutes)
**Proposed:** Quick Mode + Custom Mode

#### UI Mockup: Mode Selection

```
┌─────────────────────────────────────────────────────────────────┐
│  🎬 Create New Demo                                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Choose your provisioning mode:                                  │
│                                                                   │
│  ┌───────────────────────────────┐  ┌──────────────────────────┐│
│  │ ⚡ QUICK MODE                 │  │ 🔧 CUSTOM MODE          ││
│  │                               │  │                          ││
│  │ Provision time: 45-60 seconds │  │ Provision time: 6-10 min││
│  │                               │  │                          ││
│  │ ✓ Use pre-built template     │  │ ✓ Fully autonomous gen  ││
│  │ ✓ Customize branding only    │  │ ✓ Tailored to customer  ││
│  │ ✓ Battle-tested queries      │  │ ✓ Custom schema design  ││
│  │ ✓ Instant availability       │  │ ✓ Unique demo story     ││
│  │                               │  │                          ││
│  │ Best for:                     │  │ Best for:                ││
│  │ • Live demos                  │  │ • Bespoke demos          ││
│  │ • Quick POCs                  │  │ • Complex scenarios      ││
│  │ • Standard scenarios          │  │ • Special requirements   ││
│  │                               │  │                          ││
│  │ [Select Quick Mode →]         │  │ [Select Custom Mode →]  ││
│  └───────────────────────────────┘  └──────────────────────────┘│
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 📋 CLONE EXISTING DEMO                                   │  │
│  │                                                           │  │
│  │ Copy and modify an existing demo                         │  │
│  │ Provision time: 30 seconds                               │  │
│  │                                                           │  │
│  │ [Browse My Demos →]                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

#### Quick Mode Workflow

```
Step 1: Select Template
┌─────────────────────────────────────┐
│ Choose from 15 industry templates   │
│ [Shopify Analytics ▼]              │
└─────────────────────────────────────┘
          ↓
Step 2: Customize Branding (Optional)
┌─────────────────────────────────────┐
│ Customer Name: [Acme Corp______]   │
│ Logo URL: [https://acme.com/logo]  │
│ Primary Color: [#8b5cf6]           │
└─────────────────────────────────────┘
          ↓
Step 3: Preview (5 seconds)
┌─────────────────────────────────────┐
│ Dataset: acme_corp_shopify_20251005│
│ Tables: 15                          │
│ Golden Queries: 18                  │
│ [Provision Now →]                   │
└─────────────────────────────────────┘
          ↓
Step 4: Provision (45 seconds)
┌─────────────────────────────────────┐
│ ⚡ Quick provisioning...            │
│ [████████████░░░░] 75%             │
└─────────────────────────────────────┘
          ↓
Step 5: Ready!
┌─────────────────────────────────────┐
│ ✅ Demo ready!                      │
│ [Launch Chat Interface]             │
└─────────────────────────────────────┘
```

---

### 3. Demo Management Dashboard (CRITICAL)

**Current:** CE Dashboard shows only job history
**Proposed:** Full demo lifecycle management with pinning, cloning, archiving

#### UI Mockup: Enhanced CE Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│  🏠 CE Dashboard                    john.doe@google.com  [⚙️ ]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ⚡ QUICK ACTIONS                                                │
│  [🚀 Launch Template] [🔧 Custom Demo] [📚 Browse Library]     │
│                                                                   │
│  📊 MY STATS (Last 30 days)                                      │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐     │
│  │ Demos       │ Templates   │ Most Used   │ Avg Time    │     │
│  │ Delivered   │ Created     │ Template    │ to Provision│     │
│  │    14       │     3       │  Shopify    │    52s      │     │
│  └─────────────┴─────────────┴─────────────┴─────────────┘     │
│                                                                   │
│  📌 PINNED DEMOS                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ 🛒 Shopify Demo v3 (Acme Corp)                         │    │
│  │ Dataset: shopify_acme_20251004                         │    │
│  │ Agent: acme-shopify-agent-abc123                       │    │
│  │ Status: 🟢 Active | Last used: 2 days ago             │    │
│  │ [Launch Chat] [Share] [Clone] [Archive] [📌 Unpin]    │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ 🏦 Banking Demo (BigBank Inc.)                         │    │
│  │ Dataset: banking_bigbank_20251001                      │    │
│  │ Agent: bigbank-banking-360-xyz789                      │    │
│  │ Status: 🟢 Active | Last used: 5 days ago             │    │
│  │ [Launch Chat] [Share] [Clone] [Archive] [📌 Unpin]    │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  📂 RECENT DEMOS (Last 30 days)                  [View All →]  │
│  • Healthcare Analytics (MedCo) - Oct 3 🟢                      │
│  • Retail Analytics (Fashion Co.) - Sep 28 🟡 Expiring soon    │
│  • SaaS Product Analytics (TechCo) - Sep 25 🟢                 │
│                                                                   │
│  📚 MY TEMPLATES                                  [Create New]  │
│  • Custom Retail Demo v2 ⭐ 12 uses by team                    │
│  • Financial Services Extended ⭐ 8 uses                        │
│  • Healthcare Specialized ⭐ 5 uses                             │
│                                                                   │
│  🔥 TRENDING TEMPLATES (This Month)                             │
│  1. 🛒 Shopify Analytics - 47 uses                              │
│  2. 🏦 Banking Customer 360 - 39 uses                           │
│  3. 🏥 Healthcare Patient Journey - 28 uses                     │
│                                                                   │
│  🎯 SUGGESTED FOR YOU                                           │
│  Based on your recent demos: Financial Services                 │
│  [View Payment Processing Template →]                           │
│                                                                   │
│  🗑️  ARCHIVED (Auto-deleted in 90 days)          [Manage →]    │
│  • 7 demos archived                                             │
│  • 2 expiring this week                                         │
└─────────────────────────────────────────────────────────────────┘
```

#### Backend: Demo Management

```python
# backend/models/demo.py

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Demo:
    """Represents a provisioned demo instance."""
    demo_id: str
    created_by: str  # CE email
    customer_name: str
    customer_url: str

    # Resources
    dataset_id: str
    dataset_full_name: str
    agent_id: str

    # Content
    demo_title: str
    golden_queries: List[Dict]
    schema: List[Dict]
    industry: str

    # Lifecycle
    status: str  # active, archived, deleted
    created_at: datetime
    last_used: datetime
    expires_at: datetime  # Auto-archive after 90 days

    # Features
    is_pinned: bool
    is_template: bool  # If saved as reusable template
    template_source: Optional[str]  # If created from template

    # Usage tracking
    usage_count: int
    shared_count: int
    tags: List[str]

    # Metadata
    metadata: Dict


class DemoManager:
    """Manages demo lifecycle and operations."""

    def __init__(self):
        self.db = firestore.Client()

    def create_demo(self, demo: Demo) -> str:
        """Create new demo record."""
        self.db.collection('demos').document(demo.demo_id).set(demo.__dict__)
        return demo.demo_id

    def pin_demo(self, demo_id: str, ce_email: str):
        """Pin demo for quick access."""
        self.db.collection('demos').document(demo_id).update({
            'is_pinned': True,
            'pinned_by': ce_email,
            'pinned_at': datetime.utcnow()
        })

    def clone_demo(self, source_demo_id: str, new_customer_name: str) -> Demo:
        """Clone existing demo with new customer name."""
        source = self.get_demo(source_demo_id)

        # Create new demo with same template but new name
        new_demo = Demo(
            demo_id=str(uuid.uuid4()),
            created_by=source.created_by,
            customer_name=new_customer_name,
            customer_url=source.customer_url,
            dataset_id=f"{new_customer_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}",
            # ... copy other fields
            template_source=source_demo_id,
            is_pinned=False
        )

        return new_demo

    def archive_demo(self, demo_id: str):
        """Archive demo (keeps metadata, marks for deletion)."""
        self.db.collection('demos').document(demo_id).update({
            'status': 'archived',
            'archived_at': datetime.utcnow()
        })

    def get_pinned_demos(self, ce_email: str) -> List[Demo]:
        """Get CE's pinned demos."""
        docs = self.db.collection('demos')\
            .where('created_by', '==', ce_email)\
            .where('is_pinned', '==', True)\
            .where('status', '==', 'active')\
            .order_by('last_used', direction=firestore.Query.DESCENDING)\
            .stream()

        return [Demo(**doc.to_dict()) for doc in docs]

    def get_recent_demos(self, ce_email: str, limit: int = 10) -> List[Demo]:
        """Get CE's recent demos."""
        docs = self.db.collection('demos')\
            .where('created_by', '==', ce_email)\
            .where('status', '==', 'active')\
            .order_by('created_at', direction=firestore.Query.DESCENDING)\
            .limit(limit)\
            .stream()

        return [Demo(**doc.to_dict()) for doc in docs]

    def auto_archive_old_demos(self):
        """Archive demos older than 90 days (cron job)."""
        cutoff = datetime.utcnow() - timedelta(days=90)

        old_demos = self.db.collection('demos')\
            .where('status', '==', 'active')\
            .where('last_used', '<', cutoff)\
            .where('is_pinned', '==', False)\
            .stream()

        for doc in old_demos:
            self.archive_demo(doc.id)
```

---

### 4. Preview & Customize Before Provisioning (HIGH)

**Current:** Generate → Hope it's good
**Proposed:** Preview → Customize → Provision

#### UI Mockup: Preview Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  👀 Preview Demo Plan - Stripe Inc.                [Edit Mode]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  📊 SCHEMA (15 tables, ~320K total rows)                         │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Table Name       │ Rows    │ Fields │        [Actions] │    │
│  ├──────────────────┼─────────┼────────┼──────────────────┤    │
│  │ payments         │ 250,000 │   18   │ [✏️ Edit] [❌]   │    │
│  │ customers        │  80,000 │   22   │ [✏️ Edit] [❌]   │    │
│  │ transactions     │ 1.2M    │   15   │ [✏️ Edit] [❌]   │    │
│  │ subscriptions    │  45,000 │   12   │ [✏️ Edit] [❌]   │    │
│  └────────────────────────────────────────────────────────┘    │
│  [+ Add Table]                                                   │
│                                                                   │
│  💡 GOLDEN QUERIES (18 queries)              [Reorder] [Test]  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ 1. [SIMPLE] "What's total revenue this month?"         │    │
│  │    Expected SQL: SELECT SUM(amount) FROM payments...   │    │
│  │    [✏️ Edit] [▶️ Test] [❌ Remove]                      │    │
│  │                                                         │    │
│  │ 2. [MEDIUM] "Show top 10 customers by payment volume"  │    │
│  │    Expected SQL: SELECT c.name, SUM(p.amount)...       │    │
│  │    [✏️ Edit] [▶️ Test] [❌ Remove]                      │    │
│  │                                                         │    │
│  │ 3. [COMPLEX] "Analyze churn by customer cohort"        │    │
│  │    Expected SQL: WITH cohorts AS (...                  │    │
│  │    [✏️ Edit] [▶️ Test] [❌ Remove]                      │    │
│  └────────────────────────────────────────────────────────┘    │
│  [+ Add Query]                                                   │
│                                                                   │
│  🎨 CUSTOMIZATION                                                │
│  Company Name: [Stripe Inc._________________]                   │
│  Logo URL: [https://stripe.com/logo.png____]                   │
│  Primary Color: [#635BFF] [🎨]                                  │
│                                                                   │
│  ⏱️  Estimated Provision Time: 6 min 30s                        │
│  💾 Storage Estimate: 12.4 MB                                   │
│  💰 Monthly Cost: ~$0.03                                         │
│                                                                   │
│  [← Back] [💾 Save as Template] [🚀 Provision Now →]           │
└─────────────────────────────────────────────────────────────────┘
```

#### Edit Query Modal

```
┌─────────────────────────────────────────────────────────────────┐
│  ✏️  Edit Golden Query                                    [✕]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Query ID: 2                                                     │
│  Complexity: [MEDIUM ▼]                                         │
│                                                                   │
│  Natural Language Question:                                      │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Show top 10 customers by payment volume in last 90 days│    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  Expected SQL:                                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ SELECT                                                  │    │
│  │   c.customer_name,                                      │    │
│  │   SUM(p.amount) as total_volume                         │    │
│  │ FROM `{dataset}.customers` c                            │    │
│  │ JOIN `{dataset}.payments` p ON c.customer_id = p.cust...│    │
│  │ WHERE p.payment_date >= DATE_SUB(CURRENT_DATE(), INT...│    │
│  │ GROUP BY c.customer_name                                │    │
│  │ ORDER BY total_volume DESC                              │    │
│  │ LIMIT 10                                                │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  Business Value:                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Identify high-value customers for retention strategies │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  [▶️  Test SQL] [🔄 Generate SQL from Question]                │
│                                                                   │
│  [Cancel] [Save Changes]                                         │
└─────────────────────────────────────────────────────────────────┘
```

---

### 5. Demo Sharing & Handoff (HIGH)

**Current:** No sharing mechanism
**Proposed:** Share links, export packages, customer transfers

#### UI Mockup: Share Demo

```
┌─────────────────────────────────────────────────────────────────┐
│  🔗 Share Demo: "Shopify Analytics for Acme Corp"         [✕]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  📧 SHARE LINK                                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ https://capi-demo.run.app/shared/abc123xyz             │    │
│  │ [📋 Copy Link] [✉️  Email to Customer]                 │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ⏰ Link expires in: [7 days ▼] [30 days] [Never]              │
│  🔒 Password protect: [ Enable] [_______________]               │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ ℹ️  Shared link includes:                               │    │
│  │ • Read-only chat interface                              │    │
│  │ • Demo golden queries                                   │    │
│  │ • BigQuery console access (if customer has permissions)│    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  📦 EXPORT PACKAGE                                               │
│  Select what to include:                                         │
│  [✓] Demo documentation (PDF)                                   │
│  [✓] Golden queries list (CSV)                                  │
│  [✓] CAPI agent configuration (YAML)                            │
│  [✓] Dataset schema (JSON)                                      │
│  [ ] SQL query examples                                          │
│  [✓] Setup guide for customer                                   │
│                                                                   │
│  [📥 Download Package] [✉️  Email Package]                      │
│                                                                   │
│  🤝 TRANSFER TO CUSTOMER                                         │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Customer Email: [john.smith@acme.com_____________]     │    │
│  │ Customer GCP Project: [acme-analytics-prod________]    │    │
│  │                                                         │    │
│  │ This will:                                              │    │
│  │ [✓] Copy dataset to customer's project                 │    │
│  │ [✓] Create CAPI agent in customer's project            │    │
│  │ [✓] Send setup instructions to customer                │    │
│  │ [ ] Delete demo from our project (after transfer)      │    │
│  │                                                         │    │
│  │ [🚀 Transfer Demo]                                      │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  👥 SHARE WITH TEAM                                              │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ [✓] Save as team template                               │    │
│  │ Template name: [Acme Shopify Pattern______________]    │    │
│  │ Tags: [retail] [shopify] [payments]                    │    │
│  │ [💾 Save to Team Library]                               │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  [Close]                                                         │
└─────────────────────────────────────────────────────────────────┘
```

#### Backend: Demo Sharing

```python
# backend/routes/sharing.py

from datetime import datetime, timedelta
import secrets

@router.post("/share/{demo_id}")
async def create_share_link(
    demo_id: str,
    expires_in_days: int = 7,
    password: Optional[str] = None
):
    """Create shareable link for demo."""
    demo = demo_manager.get_demo(demo_id)

    # Generate secure token
    share_token = secrets.token_urlsafe(32)

    # Store share metadata
    share_record = {
        'share_token': share_token,
        'demo_id': demo_id,
        'created_by': demo.created_by,
        'created_at': datetime.utcnow(),
        'expires_at': datetime.utcnow() + timedelta(days=expires_in_days),
        'password_hash': hashlib.sha256(password.encode()).hexdigest() if password else None,
        'access_count': 0
    }

    db.collection('demo_shares').document(share_token).set(share_record)

    # Generate share URL
    share_url = f"https://capi-demo.run.app/shared/{share_token}"

    return {
        'share_url': share_url,
        'expires_at': share_record['expires_at'].isoformat(),
        'password_protected': password is not None
    }


@router.get("/shared/{share_token}")
async def access_shared_demo(
    share_token: str,
    password: Optional[str] = None
):
    """Access shared demo via token."""
    # Get share record
    share_doc = db.collection('demo_shares').document(share_token).get()

    if not share_doc.exists:
        raise HTTPException(status_code=404, detail="Share link not found or expired")

    share_data = share_doc.to_dict()

    # Check expiration
    if datetime.utcnow() > share_data['expires_at']:
        raise HTTPException(status_code=410, detail="Share link has expired")

    # Check password if protected
    if share_data['password_hash']:
        if not password:
            raise HTTPException(status_code=401, detail="Password required")

        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if password_hash != share_data['password_hash']:
            raise HTTPException(status_code=401, detail="Incorrect password")

    # Increment access count
    db.collection('demo_shares').document(share_token).update({
        'access_count': firestore.Increment(1),
        'last_accessed': datetime.utcnow()
    })

    # Get demo data
    demo = demo_manager.get_demo(share_data['demo_id'])

    # Return read-only demo view
    return {
        'demo_title': demo.demo_title,
        'customer_name': demo.customer_name,
        'agent_id': demo.agent_id,
        'golden_queries': demo.golden_queries,
        'dataset_id': demo.dataset_id,
        'shared_by': share_data['created_by'],
        'read_only': True
    }


@router.post("/transfer/{demo_id}")
async def transfer_to_customer(
    demo_id: str,
    customer_email: str,
    customer_project_id: str,
    delete_after_transfer: bool = False
):
    """Transfer demo to customer's GCP project."""
    demo = demo_manager.get_demo(demo_id)

    # 1. Copy BigQuery dataset
    bq_client = bigquery.Client()
    source_dataset = f"{demo.dataset_full_name}"
    dest_dataset = f"{customer_project_id}.{demo.dataset_id}"

    # Copy all tables
    source_dataset_ref = bq_client.dataset(demo.dataset_id)
    dest_dataset_ref = bigquery.DatasetReference(customer_project_id, demo.dataset_id)

    # Create destination dataset
    dest_dataset = bigquery.Dataset(dest_dataset_ref)
    bq_client.create_dataset(dest_dataset, exists_ok=True)

    # Copy tables
    for table in bq_client.list_tables(source_dataset_ref):
        source_table = f"{source_dataset}.{table.table_id}"
        dest_table = f"{dest_dataset}.{table.table_id}"

        job = bq_client.copy_table(source_table, dest_table)
        job.result()

    # 2. Create CAPI agent in customer project
    # (Use existing agent config, point to new dataset)

    # 3. Send setup email to customer
    send_transfer_email(
        to=customer_email,
        demo_title=demo.demo_title,
        dataset_id=demo.dataset_id,
        project_id=customer_project_id
    )

    # 4. Optionally delete original demo
    if delete_after_transfer:
        demo_manager.archive_demo(demo_id)

    return {
        'success': True,
        'transferred_dataset': dest_dataset,
        'setup_email_sent': True
    }
```

---

### 6. Persistent Storage & History (HIGH)

**Current:** In-memory (lost on restart)
**Proposed:** Firestore for metadata, Cloud Storage for artifacts

#### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  STORAGE ARCHITECTURE                                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  📦 FIRESTORE (Demo Metadata)                                   │
│  ├─ demos/                                                       │
│  │  ├─ {demo_id}/                                               │
│  │  │  ├─ created_by: string                                    │
│  │  │  ├─ customer_name: string                                 │
│  │  │  ├─ dataset_id: string                                    │
│  │  │  ├─ agent_id: string                                      │
│  │  │  ├─ status: string                                        │
│  │  │  ├─ is_pinned: boolean                                    │
│  │  │  ├─ created_at: timestamp                                 │
│  │  │  └─ ... (other metadata)                                  │
│  │                                                               │
│  ├─ templates/                                                   │
│  │  ├─ {template_id}/                                           │
│  │  │  ├─ display_name: string                                  │
│  │  │  ├─ industry: string                                      │
│  │  │  ├─ usage_count: number                                   │
│  │  │  └─ ... (template config)                                 │
│  │                                                               │
│  └─ demo_shares/                                                 │
│     ├─ {share_token}/                                           │
│        ├─ demo_id: string                                        │
│        ├─ expires_at: timestamp                                  │
│        └─ access_count: number                                   │
│                                                                   │
│  ☁️  CLOUD STORAGE (Binary Artifacts)                           │
│  ├─ gs://capi-templates/                                        │
│  │  ├─ shopify/                                                  │
│  │  │  ├─ customers.parquet                                     │
│  │  │  ├─ orders.parquet                                        │
│  │  │  └─ ... (pre-generated data)                              │
│  │  ├─ banking/                                                  │
│  │  └─ ... (other templates)                                    │
│  │                                                               │
│  └─ gs://capi-demos/                                            │
│     ├─ reports/                                                  │
│     │  ├─ {demo_id}/demo_report.pdf                             │
│     │  └─ {demo_id}/export_package.zip                          │
│     └─ backups/                                                  │
│                                                                   │
│  🗄️  BIGQUERY (Actual Data)                                     │
│  └─ Datasets created per demo                                    │
│     ├─ shopify_acme_20251005                                    │
│     ├─ banking_bigbank_20251001                                 │
│     └─ ... (provisioned datasets)                               │
└─────────────────────────────────────────────────────────────────┘
```

#### Implementation

```python
# backend/storage/firestore_repository.py

from google.cloud import firestore
from datetime import datetime
from typing import List, Optional

class FirestoreDemoRepository:
    """Persistent demo storage using Firestore."""

    def __init__(self):
        self.db = firestore.Client()

    def save_demo(self, demo: Demo):
        """Save demo to Firestore."""
        self.db.collection('demos').document(demo.demo_id).set({
            'demo_id': demo.demo_id,
            'created_by': demo.created_by,
            'customer_name': demo.customer_name,
            'customer_url': demo.customer_url,
            'dataset_id': demo.dataset_id,
            'agent_id': demo.agent_id,
            'demo_title': demo.demo_title,
            'industry': demo.industry,
            'status': demo.status,
            'is_pinned': demo.is_pinned,
            'is_template': demo.is_template,
            'created_at': demo.created_at,
            'last_used': demo.last_used,
            'usage_count': demo.usage_count,
            'golden_queries': demo.golden_queries,
            'schema': demo.schema,
            'metadata': demo.metadata
        })

    def get_demo(self, demo_id: str) -> Optional[Demo]:
        """Retrieve demo from Firestore."""
        doc = self.db.collection('demos').document(demo_id).get()
        if doc.exists:
            data = doc.to_dict()
            return Demo(**data)
        return None

    def list_demos(
        self,
        ce_email: str,
        status: str = 'active',
        limit: int = 50
    ) -> List[Demo]:
        """List demos for CE."""
        query = self.db.collection('demos')\
            .where('created_by', '==', ce_email)\
            .where('status', '==', status)\
            .order_by('created_at', direction=firestore.Query.DESCENDING)\
            .limit(limit)

        return [Demo(**doc.to_dict()) for doc in query.stream()]

    def search_demos(
        self,
        ce_email: str,
        industry: Optional[str] = None,
        customer_name: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Demo]:
        """Search demos with filters."""
        query = self.db.collection('demos')\
            .where('created_by', '==', ce_email)\
            .where('status', '==', 'active')

        if industry:
            query = query.where('industry', '==', industry)

        if customer_name:
            query = query.where('customer_name', '==', customer_name)

        results = []
        for doc in query.stream():
            demo = Demo(**doc.to_dict())

            # Filter by tags if provided
            if tags:
                if any(tag in demo.tags for tag in tags):
                    results.append(demo)
            else:
                results.append(demo)

        return results

    def update_last_used(self, demo_id: str):
        """Update last used timestamp."""
        self.db.collection('demos').document(demo_id).update({
            'last_used': datetime.utcnow(),
            'usage_count': firestore.Increment(1)
        })
```

---

### 7. Cost & Resource Management (MEDIUM)

**Current:** Datasets accumulate forever
**Proposed:** Automatic lifecycle management with policies

#### UI Mockup: Resource Management

```
┌─────────────────────────────────────────────────────────────────┐
│  💰 Resource Management                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  📊 CURRENT USAGE                                                │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Active Datasets:     12                                 │    │
│  │ Archived Datasets:    7                                 │    │
│  │ CAPI Agents:          8                                 │    │
│  │ Total Storage:     2.4 GB                               │    │
│  │ Monthly Cost:     ~$0.05                                │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  🔄 LIFECYCLE POLICIES                                           │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Automatic Archiving                                     │    │
│  │ Archive demos after: [90 days ▼]                       │    │
│  │ Exceptions: Pinned demos, Templates                     │    │
│  │                                                         │    │
│  │ Automatic Deletion                                      │    │
│  │ Delete archived demos after: [180 days ▼]             │    │
│  │ Keep metadata: [✓]                                      │    │
│  │                                                         │    │
│  │ CE Limits                                               │    │
│  │ Max active datasets per CE: [20 ▼]                     │    │
│  │ Max pinned demos: [5 ▼]                                │    │
│  │                                                         │    │
│  │ [Save Policies]                                         │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  🚨 EXPIRING SOON (Auto-archive in <7 days)                     │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ • shopify_demo_20250705 (Acme Corp)                    │    │
│  │   Last used: 83 days ago | Expires in: 7 days         │    │
│  │   [📌 Pin] [⏰ Extend 90 days] [🗑️  Delete Now]        │    │
│  │                                                         │    │
│  │ • banking_poc_20250710 (BigBank)                       │    │
│  │   Last used: 88 days ago | Expires in: 2 days         │    │
│  │   [📌 Pin] [⏰ Extend 90 days] [🗑️  Delete Now]        │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  📈 USAGE TRENDS (Last 90 days)                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                           Datasets Created             │    │
│  │     15│                                        ╭─╮     │    │
│  │       │                                    ╭───╯ │     │    │
│  │     10│                          ╭─────╮  │     │     │    │
│  │       │                    ╭─────╯     ╰──╯     │     │    │
│  │      5│          ╭─────────╯                     │     │    │
│  │       │  ────────╯                               ╰───  │    │
│  │      0├────────────────────────────────────────────────┤    │
│  │       Sep            Oct            Nov           Dec  │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  💡 RECOMMENDATIONS                                              │
│  • Consider archiving 3 unused demos from August                │
│  • Template "Shopify Analytics" can be reused instead of new   │
│  • Pin your most-used demo "Banking Customer 360"               │
└─────────────────────────────────────────────────────────────────┘
```

#### Backend: Lifecycle Management

```python
# backend/jobs/lifecycle_manager.py

from datetime import datetime, timedelta
from google.cloud import bigquery
import logging

logger = logging.getLogger(__name__)

class DemoLifecycleManager:
    """Manages automatic archiving and cleanup of demos."""

    def __init__(self):
        self.bq = bigquery.Client()
        self.db = firestore.Client()
        self.demo_manager = DemoManager()

    def run_lifecycle_policies(self):
        """
        Run lifecycle policies (called by Cloud Scheduler daily).

        Policies:
        1. Archive demos inactive for 90 days (unless pinned/template)
        2. Delete archived demos after 180 days
        3. Send reminder emails 7 days before archive/delete
        """
        logger.info("Running demo lifecycle policies...")

        # Archive old demos
        archived_count = self._archive_old_demos()

        # Delete very old archived demos
        deleted_count = self._delete_old_archived_demos()

        # Send expiration warnings
        warning_count = self._send_expiration_warnings()

        logger.info(f"Lifecycle policies complete: {archived_count} archived, "
                   f"{deleted_count} deleted, {warning_count} warnings sent")

    def _archive_old_demos(self) -> int:
        """Archive demos inactive for 90+ days."""
        cutoff_date = datetime.utcnow() - timedelta(days=90)

        # Query demos eligible for archiving
        query = self.db.collection('demos')\
            .where('status', '==', 'active')\
            .where('last_used', '<', cutoff_date)\
            .where('is_pinned', '==', False)\
            .where('is_template', '==', False)\
            .stream()

        count = 0
        for doc in query:
            demo = Demo(**doc.to_dict())

            logger.info(f"Archiving demo: {demo.demo_id} (last used: {demo.last_used})")

            # Mark as archived in Firestore
            self.demo_manager.archive_demo(demo.demo_id)

            # Optionally: Convert BigQuery tables to long-term storage
            # (cheaper storage tier but slower access)

            count += 1

        return count

    def _delete_old_archived_demos(self) -> int:
        """Delete demos archived for 180+ days."""
        cutoff_date = datetime.utcnow() - timedelta(days=180)

        query = self.db.collection('demos')\
            .where('status', '==', 'archived')\
            .where('archived_at', '<', cutoff_date)\
            .stream()

        count = 0
        for doc in query:
            demo = Demo(**doc.to_dict())

            logger.info(f"Deleting archived demo: {demo.demo_id}")

            # Delete BigQuery dataset
            dataset_ref = self.bq.dataset(demo.dataset_id)
            self.bq.delete_dataset(dataset_ref, delete_contents=True, not_found_ok=True)

            # Delete CAPI agent
            # (Use CAPI client to delete agent)

            # Keep Firestore metadata but mark as deleted
            self.db.collection('demos').document(demo.demo_id).update({
                'status': 'deleted',
                'deleted_at': datetime.utcnow(),
                'dataset_id': None,  # Clear sensitive data
                'agent_id': None
            })

            count += 1

        return count

    def _send_expiration_warnings(self) -> int:
        """Send email warnings 7 days before archive/delete."""
        # Find demos expiring in 7 days
        warning_date = datetime.utcnow() - timedelta(days=83)  # 90 - 7

        query = self.db.collection('demos')\
            .where('status', '==', 'active')\
            .where('last_used', '<', warning_date)\
            .where('is_pinned', '==', False)\
            .stream()

        count = 0
        for doc in query:
            demo = Demo(**doc.to_dict())

            # Calculate days until archiving
            days_inactive = (datetime.utcnow() - demo.last_used).days
            days_until_archive = 90 - days_inactive

            if 0 <= days_until_archive <= 7:
                # Send warning email
                send_expiration_email(
                    to=demo.created_by,
                    demo_title=demo.demo_title,
                    days_remaining=days_until_archive,
                    demo_id=demo.demo_id
                )
                count += 1

        return count


def send_expiration_email(to: str, demo_title: str, days_remaining: int, demo_id: str):
    """Send expiration warning email to CE."""
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail

    message = Mail(
        from_email='noreply@google.com',
        to_emails=to,
        subject=f'Demo expiring in {days_remaining} days: {demo_title}',
        html_content=f'''
        <h2>Demo Expiration Warning</h2>
        <p>Your demo <strong>{demo_title}</strong> will be archived in {days_remaining} days.</p>

        <p><strong>What happens when archived:</strong></p>
        <ul>
            <li>Dataset becomes read-only</li>
            <li>Demo removed from active list</li>
            <li>Automatically deleted after 180 days</li>
        </ul>

        <p><strong>To prevent archiving:</strong></p>
        <ul>
            <li>Pin the demo</li>
            <li>Use it again (updates last_used timestamp)</li>
            <li>Extend expiration manually</li>
        </ul>

        <a href="https://capi-demo.run.app/demos/{demo_id}">Manage Demo</a>
        '''
    )

    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    sg.send(message)
```

**Cloud Scheduler Setup:**

```bash
# Run lifecycle manager daily at 2am UTC
gcloud scheduler jobs create http lifecycle-manager \
  --schedule="0 2 * * *" \
  --uri="https://capi-demo.run.app/api/admin/run-lifecycle" \
  --http-method=POST \
  --oidc-service-account-email=scheduler@PROJECT.iam.gserviceaccount.com
```

---

### 8. Industry-Specific Quick Starts (MEDIUM)

Pre-configured scenarios CEs can launch with one click.

#### UI Mockup: Quick Starts Library

```
┌─────────────────────────────────────────────────────────────────┐
│  🎯 Quick Start Scenarios                                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Filter by: [All Industries ▼]  Search: [__________________]   │
│                                                                   │
│  🛒 RETAIL & E-COMMERCE                                          │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ ⚡ Shopify Merchant Analytics              45s | 47 uses│    │
│  │ Complete merchant platform analytics                    │    │
│  │ [Preview] [Quick Launch →]                              │    │
│  ├────────────────────────────────────────────────────────┤    │
│  │ ⚡ Omnichannel Retail Analytics            50s | 31 uses│    │
│  │ Online + in-store unified customer view                │    │
│  │ [Preview] [Quick Launch →]                              │    │
│  ├────────────────────────────────────────────────────────┤    │
│  │ ⚡ Fashion E-commerce Dashboard            45s | 24 uses│    │
│  │ Product catalog, inventory, and sales                  │    │
│  │ [Preview] [Quick Launch →]                              │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  🏦 FINANCIAL SERVICES                                           │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ ⚡ Banking Customer 360                    60s | 39 uses│    │
│  │ Complete banking customer analytics                     │    │
│  │ [Preview] [Quick Launch →]                              │    │
│  ├────────────────────────────────────────────────────────┤    │
│  │ ⚡ Payment Processing Analytics            50s | 28 uses│    │
│  │ Transaction monitoring and fraud detection             │    │
│  │ [Preview] [Quick Launch →]                              │    │
│  ├────────────────────────────────────────────────────────┤    │
│  │ ⚡ Wealth Management Platform              55s | 19 uses│    │
│  │ Portfolio analysis and client segmentation             │    │
│  │ [Preview] [Quick Launch →]                              │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  🏥 HEALTHCARE & LIFE SCIENCES                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ ⚡ Clinical Trials Analytics               70s | 22 uses│    │
│  │ Trial outcomes, patient cohorts, efficacy              │    │
│  │ [Preview] [Quick Launch →]                              │    │
│  ├────────────────────────────────────────────────────────┤    │
│  │ ⚡ Patient Journey Analytics               65s | 18 uses│    │
│  │ Care pathways, readmissions, outcomes                  │    │
│  │ [Preview] [Quick Launch →]                              │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  💻 TECHNOLOGY & SAAS                                            │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ ⚡ Product Analytics Dashboard             50s | 26 uses│    │
│  │ User behavior, feature adoption, retention             │    │
│  │ [Preview] [Quick Launch →]                              │    │
│  ├────────────────────────────────────────────────────────┤    │
│  │ ⚡ Customer Success Metrics                55s | 21 uses│    │
│  │ Health scores, churn risk, engagement                  │    │
│  │ [Preview] [Quick Launch →]                              │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  [View All Templates →]                                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📅 Implementation Roadmap

### Phase 1: MVP for CEs (Weeks 1-3)

**Goal:** Enable fast demos with template library

| Week | Feature | Deliverable | Impact |
|------|---------|-------------|--------|
| 1 | **Template Registry** | Backend registry with 5 industry templates | Foundation for quick provisioning |
| 1-2 | **Pre-generate Data** | Create parquet files for all templates | 10x faster provisioning |
| 2 | **Quick Provision API** | `/quick-provision` endpoint | 45-second demos |
| 2-3 | **Template Library UI** | Browse & launch templates | CE can prepare demos instantly |
| 3 | **Firestore Storage** | Persistent demo metadata | No data loss on restart |

**Success Metrics:**
- ✅ 5 templates available
- ✅ < 60 second average provision time
- ✅ 100% uptime (no in-memory data loss)

### Phase 2: Polish & Usability (Weeks 4-5)

**Goal:** Make CEs more productive

| Week | Feature | Deliverable | Impact |
|------|---------|-------------|--------|
| 4 | **Pin/Clone Features** | Pin favorite demos, clone existing | Reusability |
| 4 | **Demo Management UI** | Enhanced CE dashboard | Better organization |
| 5 | **Share Links** | Generate shareable demo links | Easy customer sharing |
| 5 | **Auto-archive** | Lifecycle management | Cost optimization |

**Success Metrics:**
- ✅ 70%+ demos reuse existing templates
- ✅ 50%+ demos shared with customers
- ✅ Automated cleanup of old datasets

### Phase 3: Advanced Features (Weeks 6-8)

**Goal:** Team collaboration & customization

| Week | Feature | Deliverable | Impact |
|------|---------|-------------|--------|
| 6 | **Preview & Edit** | Customize before provisioning | More control |
| 7 | **Team Templates** | Share templates across CE team | Knowledge sharing |
| 7 | **Customer Transfer** | Hand off demos to customer projects | Better follow-up |
| 8 | **Usage Analytics** | Track template usage, success rates | Data-driven improvements |

**Success Metrics:**
- ✅ Team templates used across 5+ CEs
- ✅ 30%+ conversion rate (customer handoff)
- ✅ Template success tracking

---

## 🎓 CE Best Practices Guide

### Pre-Demo Preparation Checklist

**1 Week Before Demo:**
```
☑ Research customer's industry
☑ Browse template library for relevant demos
☑ Clone template or create custom demo
☑ Customize company branding (logo, colors)
☑ Pin demo to dashboard for quick access
```

**1 Day Before Demo:**
```
☑ Test 3-5 golden queries in chat interface
☑ Bookmark BigQuery console URL for customer
☑ Prepare share link (if sending afterward)
☑ Review talking track for key insights
☑ Have backup demo ready (just in case)
```

**Time investment:** 10-15 minutes
**Demo readiness:** 100%

### During Live Demo

**Recommended Flow (15-20 minutes):**

```
1. Introduction (2 min)
   "We've created a demo environment specifically for [Company Name]
    using your industry's data patterns"

2. Show CE Dashboard (1 min)
   "Here's what we pre-built for you..."
   → Quick preview of dataset, tables, queries

3. Launch Chat Interface (10s)
   "Let's see Conversational Analytics in action"
   → Already provisioned, instant launch

4. Run Golden Queries (5-7 min)
   Start simple → medium → complex
   → Show natural language → SQL translation
   → Highlight insights relevant to customer

5. Show BigQuery Console (2 min)
   "This is your actual data in BigQuery"
   → Show tables, run SQL manually
   → Explain how CAPI generated the SQL

6. Invite Customer to Try (5 min)
   "Now you try - ask any business question"
   → Hands-on exploration
   → Help refine queries

7. Share & Follow-up (1 min)
   "I'm sharing this demo with you right now"
   → Send share link
   → Explain next steps
```

**Pro Tips:**
- ✅ Always have a pinned backup demo
- ✅ Start with simple queries to build confidence
- ✅ Let customer drive the last 5 minutes
- ✅ Share link during the demo, not after

### Post-Demo Follow-up

**Immediately After Demo:**
```
☑ Update demo last_used timestamp
☑ Note what queries worked well (for future)
☑ Share demo link via email
☑ Log demo in CRM
```

**Within 24 Hours:**
```
☑ Send export package (PDF, YAML, setup guide)
☑ Offer to transfer to customer's project
☑ If successful, save as team template
```

**Within 1 Week:**
```
☑ Follow up on customer's usage
☑ Offer to customize further
☑ Schedule next conversation
```

### Common Pitfalls to Avoid

| ❌ Don't | ✅ Do Instead |
|----------|--------------|
| Provision during live demo | Pre-provision and pin |
| Use generic demo | Customize with customer branding |
| Jump to complex queries first | Build up from simple to complex |
| Forget to share afterward | Share link during demo |
| Let demo sit unused | Pin frequently used demos |
| Create new demo each time | Clone and customize existing |

---

## 📊 Key Metrics for Success

### For CEs (Individual Performance)

| Metric | Current | Target | How to Improve |
|--------|---------|--------|----------------|
| **Avg provision time** | 6 min | < 60s | Use templates instead of custom |
| **Demos per week** | 2-3 | 6-8 | Reuse templates, pin favorites |
| **Preparation time** | 4-6 hrs | < 30 min | Use quick starts, clone existing |
| **Share rate** | ~20% | > 60% | Share during demo, not after |
| **Template reuse** | 0% | > 70% | Browse library first |

### For Platform (Product Metrics)

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| **Template usage rate** | N/A | > 70% | Quick vs Custom provision ratio |
| **Demo completion rate** | ~60% | > 95% | Successful provisions / total attempts |
| **Customer handoff rate** | ~10% | > 30% | Transfers / total demos |
| **CE satisfaction** | N/A | 4.5/5 | Quarterly survey |
| **Template library growth** | N/A | +5/quarter | New templates added |

### For Business (ROI Metrics)

| Metric | Current | Target | Business Value |
|--------|---------|--------|----------------|
| **Time saved per demo** | 0 min | 5 min | CE productivity |
| **Demos per CE per month** | 8-12 | 25-30 | 3x increase |
| **Customer conversion** | 15% | 25% | Better demos = more deals |
| **Cost per demo** | ~$0.10 | ~$0.03 | Resource optimization |

**How to Track:**
```python
# backend/analytics/metrics_tracker.py

class MetricsTracker:
    """Track CE and platform metrics."""

    def track_provision(
        self,
        ce_email: str,
        provision_type: str,  # "quick" or "custom"
        provision_time_seconds: int,
        template_id: Optional[str]
    ):
        """Track each provisioning event."""
        self.db.collection('metrics').add({
            'ce_email': ce_email,
            'provision_type': provision_type,
            'provision_time_seconds': provision_time_seconds,
            'template_id': template_id,
            'timestamp': datetime.utcnow()
        })

    def track_demo_share(self, demo_id: str, share_type: str):
        """Track demo sharing."""
        self.db.collection('metrics').add({
            'event_type': 'demo_shared',
            'demo_id': demo_id,
            'share_type': share_type,  # "link", "email", "transfer"
            'timestamp': datetime.utcnow()
        })

    def get_ce_stats(self, ce_email: str, days: int = 30) -> Dict:
        """Get CE performance stats."""
        cutoff = datetime.utcnow() - timedelta(days=days)

        provisions = self.db.collection('metrics')\
            .where('ce_email', '==', ce_email)\
            .where('timestamp', '>', cutoff)\
            .stream()

        total = 0
        quick_count = 0
        total_time = 0

        for doc in provisions:
            data = doc.to_dict()
            total += 1
            if data['provision_type'] == 'quick':
                quick_count += 1
            total_time += data['provision_time_seconds']

        return {
            'total_demos': total,
            'quick_provision_rate': quick_count / total if total > 0 else 0,
            'avg_provision_time': total_time / total if total > 0 else 0,
            'demos_per_week': total / (days / 7)
        }
```

---

## 🚀 Quick Win: Template Library in 1 Week

**Minimal viable implementation to get started fast:**

### Day 1-2: Backend Registry

```python
# backend/templates/__init__.py

QUICK_TEMPLATES = {
    "shopify": {
        "id": "shopify_analytics",
        "name": "Shopify E-commerce Analytics",
        "industry": "Retail & E-commerce",
        "parquet_path": "gs://capi-templates/shopify/*.parquet",
        "agent_yaml": "templates/shopify_agent.yaml",
        "schema": {...},  # Pre-defined schema
        "golden_queries": [...],  # Pre-validated queries
        "provision_time_estimate": "45s"
    },
    "banking": {
        "id": "banking_customer_360",
        "name": "Banking Customer 360",
        "industry": "Financial Services",
        "parquet_path": "gs://capi-templates/banking/*.parquet",
        "agent_yaml": "templates/banking_agent.yaml",
        "schema": {...},
        "golden_queries": [...],
        "provision_time_estimate": "60s"
    }
    # Add 3 more...
}

async def quick_provision(template_id: str, customer_name: str):
    """Provision from template in < 60 seconds."""
    template = QUICK_TEMPLATES[template_id]

    # 1. Create dataset (5s)
    dataset_id = f"{customer_name}_{template_id}_{timestamp}"
    create_dataset(dataset_id)

    # 2. Load parquet files (30-40s) - FAST!
    load_from_parquet(template['parquet_path'], dataset_id)

    # 3. Create CAPI agent (10s)
    agent_id = create_agent_from_yaml(template['agent_yaml'], dataset_id)

    # Total: ~45-60 seconds
    return {"dataset_id": dataset_id, "agent_id": agent_id}
```

### Day 3-4: Pre-generate Data

```bash
# Generate parquet files for templates
python scripts/generate_template_data.py --template shopify --output gs://capi-templates/shopify/
python scripts/generate_template_data.py --template banking --output gs://capi-templates/banking/
```

### Day 5: API Endpoint

```python
# backend/routes/provisioning.py

@router.post("/quick-provision")
async def quick_provision_from_template(
    template_id: str,
    customer_name: str
):
    """Quick provision (45-60 seconds)."""
    result = await quick_provision(template_id, customer_name)
    return result
```

### Day 6-7: Simple UI

```typescript
// frontend/src/components/TemplateSelector.tsx

const TEMPLATES = [
  { id: 'shopify', name: 'Shopify Analytics', time: '45s' },
  { id: 'banking', name: 'Banking Customer 360', time: '60s' },
  // ...
];

function TemplateSelector() {
  return (
    <div>
      <h2>Quick Start Templates</h2>
      {TEMPLATES.map(t => (
        <button onClick={() => quickProvision(t.id)}>
          {t.name} ({t.time})
        </button>
      ))}
    </div>
  );
}
```

**This alone would provide:**
- ✅ 10x faster provisioning (45s vs 6min)
- ✅ Pre-validated demos (no surprises)
- ✅ Immediate CE productivity boost

---

## 🔧 Technical Specifications

### API Endpoints Summary

| Endpoint | Method | Purpose | Response Time |
|----------|--------|---------|---------------|
| `/api/templates` | GET | List all templates | < 100ms |
| `/api/templates/{id}` | GET | Get template details | < 100ms |
| `/api/provision/quick` | POST | Quick provision from template | 45-60s |
| `/api/provision/custom` | POST | Custom generation (existing) | 6-10 min |
| `/api/demos` | GET | List CE's demos | < 200ms |
| `/api/demos/{id}` | GET | Get demo details | < 100ms |
| `/api/demos/{id}/pin` | POST | Pin demo | < 100ms |
| `/api/demos/{id}/clone` | POST | Clone demo | 30-45s |
| `/api/demos/{id}/share` | POST | Create share link | < 100ms |
| `/api/demos/{id}/transfer` | POST | Transfer to customer | 2-5 min |
| `/api/shared/{token}` | GET | Access shared demo | < 200ms |

### Data Models

```typescript
// Core data structures

interface DemoTemplate {
  template_id: string;
  display_name: string;
  industry: string;
  description: string;
  table_count: number;
  total_rows: number;
  estimated_provision_time: string;
  usage_count: number;
  golden_queries: GoldenQuery[];
  schema: TableSchema[];
  data_files_path: string;
  agent_template_path: string;
  thumbnail_url: string;
  tags: string[];
  created_at: string;
  last_updated: string;
}

interface Demo {
  demo_id: string;
  created_by: string;
  customer_name: string;
  customer_url: string;
  dataset_id: string;
  dataset_full_name: string;
  agent_id: string;
  demo_title: string;
  industry: string;
  status: 'active' | 'archived' | 'deleted';
  is_pinned: boolean;
  is_template: boolean;
  template_source?: string;
  created_at: string;
  last_used: string;
  expires_at: string;
  usage_count: number;
  golden_queries: GoldenQuery[];
  schema: TableSchema[];
  metadata: Record<string, any>;
  tags: string[];
}

interface ShareLink {
  share_token: string;
  demo_id: string;
  created_by: string;
  created_at: string;
  expires_at: string;
  password_hash?: string;
  access_count: number;
  last_accessed?: string;
}
```

### Database Schema (Firestore)

```
/demos/{demo_id}
  - demo_id: string
  - created_by: string (CE email)
  - customer_name: string
  - dataset_id: string
  - agent_id: string
  - status: string
  - is_pinned: boolean
  - created_at: timestamp
  - last_used: timestamp
  - ... (full Demo model)

/templates/{template_id}
  - template_id: string
  - display_name: string
  - industry: string
  - usage_count: number
  - ... (full DemoTemplate model)

/demo_shares/{share_token}
  - share_token: string
  - demo_id: string
  - expires_at: timestamp
  - access_count: number

/metrics/{metric_id}
  - event_type: string
  - ce_email: string
  - timestamp: timestamp
  - ... (event-specific fields)
```

### Cloud Storage Structure

```
gs://capi-templates/
  ├── shopify/
  │   ├── customers.parquet
  │   ├── orders.parquet
  │   ├── payments.parquet
  │   └── ... (all tables)
  ├── banking/
  │   ├── accounts.parquet
  │   ├── transactions.parquet
  │   └── ...
  └── ... (other templates)

gs://capi-demos/
  ├── reports/
  │   └── {demo_id}/
  │       ├── demo_report.pdf
  │       └── export_package.zip
  └── backups/
      └── {demo_id}/
          └── schema_backup.json
```

---

## 📝 Conclusion

These improvements would transform the CAPI demo platform from a "one-off generator" into a **complete Demo Management Platform** that CEs can rely on for daily customer engagements.

### Immediate Impact (Phase 1):
- **10x faster demos** (45s vs 6min)
- **3x more demos per CE** (through reusability)
- **Zero downtime** (persistent storage)

### Long-term Impact (Phase 3):
- **Team knowledge sharing** (collaborative templates)
- **Higher conversion rates** (better preparation + follow-up)
- **Lower costs** (automated lifecycle management)

### Next Steps:
1. Review and prioritize features
2. Allocate engineering resources
3. Start with Phase 1 (Template Library) - **Quick win!**
4. Gather CE feedback continuously
5. Iterate based on usage metrics

---

**Questions? Feedback?**
Contact: [product-team@google.com]

**Last Updated:** October 5, 2025
**Version:** 1.0

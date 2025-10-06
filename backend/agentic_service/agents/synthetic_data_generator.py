"""
Synthetic Data Generator - Creates realistic demo data efficiently.

Strategy: Generate 40K-80K rows across all tables in ~6-10 minutes.
Uses smart batching, realistic distributions, and embedded patterns.
"""
import logging
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List
import pandas as pd
from faker import Faker

logger = logging.getLogger(__name__)

# Initialize Faker
fake = Faker()
Faker.seed(42)  # Reproducible data
random.seed(42)


class SyntheticDataGenerator:
    """Generates realistic synthetic data for BigQuery demos."""

    def __init__(self):
        self.output_dir = "/tmp/synthetic_data"
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"Synthetic Data Generator initialized. Output: {self.output_dir}")

    async def execute(self, state: Dict) -> Dict:
        """Execute synthetic data generation phase."""
        logger.info("Generating synthetic data with smart volume strategy")

        try:
            schema = state.get("schema", {})
            demo_story = state.get("demo_story", {})

            if not schema:
                raise ValueError("No schema found in state. Run Data Modeling Agent first.")

            # Generate data for all tables
            generated_files = await self._generate_all_tables(schema, demo_story, state)

            # Update state
            state["synthetic_data_files"] = generated_files
            state["data_generation_complete"] = True

            logger.info(f"✅ Data generation complete. {len(generated_files)} CSV files created")

            # Log to CE Dashboard - summary
            if "job_manager" in state and "job_id" in state:
                job_manager = state["job_manager"]
                job_id = state["job_id"]

                total_rows = sum(f.get("row_count", 0) for f in state.get("table_file_metadata", []))
                job_manager.add_log(
                    job_id,
                    "synthetic data generator",
                    f"✅ Data Generation Complete: {total_rows:,} rows across {len(generated_files)} tables",
                    "INFO"
                )

            return state

        except Exception as e:
            logger.error(f"Data generation failed: {e}", exc_info=True)
            raise

    async def _generate_all_tables(self, schema: Dict, demo_story: Dict, state: Dict) -> List[str]:
        """Generate data for all tables with smart volume allocation."""
        tables = schema.get("tables", [])
        generated_files = []
        table_file_metadata = []

        # Optimal row counts by table type
        volume_strategy = {
            "dimension_small": 50,      # channels, categories, stores
            "dimension_medium": 800,    # products, inventory
            "entity_medium": 3000,      # customers
            "entity_large": 3500,       # customer_addresses
            "transaction_medium": 15000, # orders
            "transaction_large": 40000   # order_items
        }

        # Track generated IDs for foreign keys
        id_mappings = {}

        # Sort tables by dependency (dimension tables first)
        sorted_tables = self._sort_tables_by_dependency(tables)

        # Log start to CE Dashboard
        if "job_manager" in state and "job_id" in state:
            job_manager = state["job_manager"]
            job_id = state["job_id"]
            job_manager.add_log(
                job_id,
                "synthetic data generator",
                f"🔄 Generating synthetic data for {len(sorted_tables)} tables...",
                "INFO"
            )

        for table in sorted_tables:
            table_name = table["name"]
            logger.info(f"Generating data for {table_name}...")

            # Determine row count
            row_count = self._determine_row_count(table, volume_strategy)

            # Generate table data
            df = self._generate_table_data(table, row_count, id_mappings, demo_story)

            # Save to CSV
            filename = f"{self.output_dir}/{table_name}.csv"
            df.to_csv(filename, index=False)
            generated_files.append(filename)

            # Store metadata
            table_file_metadata.append({
                "table_name": table_name,
                "row_count": len(df),
                "filename": filename
            })

            # Store IDs for foreign key relationships
            if "id" in df.columns or f"{table_name}_id" in df.columns:
                id_col = "id" if "id" in df.columns else f"{table_name}_id"
                id_mappings[table_name] = df[id_col].tolist()

            logger.info(f"  ✓ {table_name}: {len(df):,} rows → {filename}")

            # Log each table to CE Dashboard
            if "job_manager" in state and "job_id" in state:
                job_manager.add_log(
                    job_id,
                    "synthetic data generator",
                    f"  ✅ {table_name}: {len(df):,} rows generated",
                    "INFO"
                )

        # Store metadata in state for summary logging
        state["table_file_metadata"] = table_file_metadata

        return generated_files

    def _sort_tables_by_dependency(self, tables: List[Dict]) -> List[Dict]:
        """Sort tables so dimension tables are generated before fact tables."""
        # Simple heuristic: smaller tables first
        return sorted(tables, key=lambda t: t.get("record_count", 0))

    def _determine_row_count(self, table: Dict, strategy: Dict) -> int:
        """Determine optimal row count for table."""
        table_name = table["name"]
        suggested_count = table.get("record_count", 1000)

        # Apply smart volume strategy
        if suggested_count < 100:
            return strategy["dimension_small"]
        elif suggested_count < 1000:
            return strategy["dimension_medium"]
        elif suggested_count < 10000:
            return strategy["entity_medium"]
        elif suggested_count < 50000:
            return strategy["entity_large"]
        elif suggested_count < 100000:
            return strategy["transaction_medium"]
        else:
            return strategy["transaction_large"]

    def _generate_table_data(
        self,
        table: Dict,
        row_count: int,
        id_mappings: Dict,
        demo_story: Dict
    ) -> pd.DataFrame:
        """Generate data for a single table."""
        schema_fields = table.get("schema", [])
        table_name = table["name"]

        # Build data dictionary
        data = {}

        for field in schema_fields:
            field_name = field["name"]
            field_type = field["type"]

            data[field_name] = self._generate_field_data(
                field_name,
                field_type,
                row_count,
                table_name,
                id_mappings,
                demo_story
            )

        return pd.DataFrame(data)

    def _generate_field_data(
        self,
        field_name: str,
        field_type: str,
        row_count: int,
        table_name: str,
        id_mappings: Dict,
        demo_story: Dict
    ) -> List:
        """Generate data for a single field with realistic patterns."""

        # Primary keys
        if field_name in ['id', f'{table_name}_id', 'order_id', 'customer_id', 'product_id', 'store_id']:
            if field_name == 'id' or field_name == f'{table_name}_id':
                return list(range(1, row_count + 1))

        # Foreign keys
        if field_name.endswith('_id') and field_name != 'id':
            # Extract referenced table name
            ref_table = field_name.replace('_id', '') + 's'  # Simple pluralization
            if ref_table in id_mappings:
                return random.choices(id_mappings[ref_table], k=row_count)
            # Fallback
            return [random.randint(1, 1000) for _ in range(row_count)]

        # Timestamps
        if field_type == 'TIMESTAMP' or 'created_at' in field_name or 'updated_at' in field_name or '_at' in field_name:
            return self._generate_timestamps(row_count, field_name)

        # Dates
        if field_type == 'DATE' or '_date' in field_name:
            return [fake.date_between('-12m', 'today') for _ in range(row_count)]

        # Strings
        if field_type == 'STRING':
            return self._generate_string_data(field_name, row_count)

        # Numbers
        if field_type in ['INT64', 'INTEGER']:
            return self._generate_integer_data(field_name, row_count)

        if field_type in ['FLOAT64', 'NUMERIC', 'DECIMAL']:
            return self._generate_float_data(field_name, row_count)

        # Booleans
        if field_type in ['BOOL', 'BOOLEAN']:
            return [random.choice([True, False]) for _ in range(row_count)]

        # Default
        return [None] * row_count

    def _generate_timestamps(self, count: int, field_name: str) -> List[datetime]:
        """Generate timestamps with patterns."""
        base_date = datetime.now()

        if 'created' in field_name:
            # Spread over last 12 months with seasonal patterns
            timestamps = []
            for _ in range(count):
                days_ago = random.randint(0, 365)
                # More recent data is more common
                if random.random() < 0.3:
                    days_ago = random.randint(0, 90)  # 30% in last 90 days

                ts = base_date - timedelta(days=days_ago)
                timestamps.append(ts)
            return timestamps

        elif 'updated' in field_name:
            # Updated timestamps are more recent
            return [base_date - timedelta(days=random.randint(0, 60)) for _ in range(count)]

        else:
            return [base_date - timedelta(days=random.randint(0, 365)) for _ in range(count)]

    def _generate_string_data(self, field_name: str, count: int) -> List[str]:
        """Generate string data based on field name."""
        field_lower = field_name.lower()

        # Names
        if 'name' in field_lower and 'product' in field_lower:
            products = ["T-Shirt", "Jeans", "Dress", "Sneakers", "Jacket", "Hoodie",
                       "Shorts", "Skirt", "Boots", "Sandals", "Hat", "Scarf"]
            adjectives = ["Classic", "Premium", "Vintage", "Modern", "Casual", "Formal"]
            return [f"{random.choice(adjectives)} {random.choice(products)}" for _ in range(count)]

        if 'first_name' in field_lower or 'fname' in field_lower:
            return [fake.first_name() for _ in range(count)]

        if 'last_name' in field_lower or 'lname' in field_lower:
            return [fake.last_name() for _ in range(count)]

        if 'company' in field_lower or 'merchant' in field_lower:
            return [fake.company() for _ in range(count)]

        # Contact
        if 'email' in field_lower:
            return [fake.email() for _ in range(count)]

        if 'phone' in field_lower:
            return [fake.phone_number() for _ in range(count)]

        # Address
        if 'address' in field_lower or 'street' in field_lower:
            return [fake.street_address() for _ in range(count)]

        if 'city' in field_lower:
            return [fake.city() for _ in range(count)]

        if 'state' in field_lower or 'province' in field_lower:
            return [fake.state_abbr() for _ in range(count)]

        if 'country' in field_lower:
            return [fake.country_code() for _ in range(count)]

        if 'zip' in field_lower or 'postal' in field_lower:
            return [fake.zipcode() for _ in range(count)]

        # Status fields
        if 'status' in field_lower:
            statuses = ["pending", "processing", "completed", "shipped", "delivered", "cancelled", "returned"]
            # Realistic distribution (most orders are completed)
            weights = [0.05, 0.10, 0.50, 0.20, 0.10, 0.03, 0.02]
            return random.choices(statuses, weights=weights, k=count)

        # Channel
        if 'channel' in field_lower:
            channels = ["online_store", "pos", "instagram", "facebook", "mobile_app", "amazon", "tiktok"]
            return random.choices(channels, k=count)

        # Category
        if 'category' in field_lower:
            categories = ["Apparel", "Footwear", "Accessories", "Electronics", "Home & Garden",
                         "Beauty", "Sports", "Books", "Toys", "Food & Beverage"]
            return random.choices(categories, k=count)

        # Default
        return [fake.word() for _ in range(count)]

    def _generate_integer_data(self, field_name: str, count: int) -> List[int]:
        """Generate integer data based on field name."""
        field_lower = field_name.lower()

        if 'quantity' in field_lower or 'qty' in field_lower:
            return [random.randint(1, 10) for _ in range(count)]

        if 'count' in field_lower or 'num_of' in field_lower:
            return [random.randint(1, 5) for _ in range(count)]

        if 'age' in field_lower:
            return [random.randint(18, 75) for _ in range(count)]

        if 'stock' in field_lower or 'inventory' in field_lower:
            return [random.randint(0, 500) for _ in range(count)]

        # Default
        return [random.randint(1, 1000) for _ in range(count)]

    def _generate_float_data(self, field_name: str, count: int) -> List[float]:
        """Generate float data based on field name."""
        field_lower = field_name.lower()

        if 'price' in field_lower or 'cost' in field_lower:
            return [round(random.uniform(10.0, 500.0), 2) for _ in range(count)]

        if 'total' in field_lower or 'amount' in field_lower or 'revenue' in field_lower:
            return [round(random.uniform(20.0, 2000.0), 2) for _ in range(count)]

        if 'tax' in field_lower:
            return [round(random.uniform(0.0, 50.0), 2) for _ in range(count)]

        if 'discount' in field_lower:
            return [round(random.uniform(0.0, 100.0), 2) for _ in range(count)]

        if 'shipping' in field_lower:
            return [round(random.uniform(0.0, 50.0), 2) for _ in range(count)]

        if 'rate' in field_lower or 'percentage' in field_lower:
            return [round(random.uniform(0.0, 1.0), 4) for _ in range(count)]

        # Default
        return [round(random.uniform(0.0, 1000.0), 2) for _ in range(count)]

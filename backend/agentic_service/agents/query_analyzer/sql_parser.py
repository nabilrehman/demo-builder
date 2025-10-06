"""
SQL Requirement Extractor - Parses expected_sql from golden queries.

Extracts:
1. Temporal filters (WHERE date clauses, DATE_TRUNC, EXTRACT)
2. Aggregation requirements (GROUP BY, SUM, COUNT, TOP N)
3. Table dependencies (FROM, JOIN clauses)
4. Meaningful thresholds (what makes a result "interesting")
"""
import re
import logging
from typing import Dict, List, Set, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SQLRequirementExtractor:
    """Extracts data requirements from SQL queries."""

    def __init__(self):
        self.current_date = datetime.now().date()

    def extract_all_requirements(self, sql: str, query_metadata: Dict) -> Dict:
        """
        Extract complete data requirements from a SQL query.

        Args:
            sql: The expected_sql from golden query
            query_metadata: Additional context (question, complexity, etc.)

        Returns:
            Dictionary with temporal, aggregation, and threshold requirements
        """
        return {
            "temporal": self.extract_temporal_filters(sql),
            "aggregation": self.extract_aggregation_requirements(sql),
            "tables": self.extract_table_dependencies(sql),
            "thresholds": self.infer_meaningful_thresholds(sql, query_metadata)
        }

    def extract_temporal_filters(self, sql: str) -> Dict:
        """
        Finds date filters in WHERE clauses.

        Examples:
          - "WHERE DATE_TRUNC(transaction_date, MONTH) = DATE '2025-10-01'"
            → {"field": "transaction_date", "filter": "october 2025", "type": "month"}

          - "WHERE EXTRACT(YEAR FROM date) = 2025"
            → {"field": "date", "filter": "year 2025", "type": "year"}

          - "WHERE date BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)"
            → {"field": "date", "filter": "last 90 days", "type": "relative"}
        """
        temporal_filters = []

        # Pattern 1: DATE_TRUNC(..., MONTH/QUARTER/YEAR) = DATE 'YYYY-MM-DD'
        pattern_date_trunc = r"DATE_TRUNC\(\s*(\w+)\s*,\s*(MONTH|QUARTER|YEAR|DAY)\s*\)\s*=\s*DATE\s*['\"](\d{4}-\d{2}-\d{2})['\"]"
        for match in re.finditer(pattern_date_trunc, sql, re.IGNORECASE):
            field, granularity, date_value = match.groups()
            temporal_filters.append({
                "field": field,
                "filter_type": "date_trunc",
                "granularity": granularity.lower(),
                "target_date": date_value,
                "description": f"{field} in {granularity.lower()} of {date_value}"
            })

        # Pattern 2: EXTRACT(YEAR/MONTH/QUARTER FROM field) = value
        pattern_extract = r"EXTRACT\((YEAR|MONTH|QUARTER|DAY)\s+FROM\s+(\w+)\)\s*=\s*(\d+)"
        for match in re.finditer(pattern_extract, sql, re.IGNORECASE):
            part, field, value = match.groups()
            temporal_filters.append({
                "field": field,
                "filter_type": "extract",
                "granularity": part.lower(),
                "target_value": int(value),
                "description": f"{field} {part.lower()} = {value}"
            })

        # Pattern 3: field BETWEEN date1 AND date2
        pattern_between = r"(\w+)\s+BETWEEN\s+DATE\s*['\"](\d{4}-\d{2}-\d{2})['\"]?\s+AND\s+DATE\s*['\"](\d{4}-\d{2}-\d{2})['\"]"
        for match in re.finditer(pattern_between, sql, re.IGNORECASE):
            field, start_date, end_date = match.groups()
            temporal_filters.append({
                "field": field,
                "filter_type": "range",
                "start_date": start_date,
                "end_date": end_date,
                "description": f"{field} between {start_date} and {end_date}"
            })

        # Pattern 4: Relative dates (CURRENT_DATE, DATE_SUB, INTERVAL)
        pattern_relative = r"(\w+)\s*[><=]+\s*DATE_SUB\(CURRENT_DATE\(\)\s*,\s*INTERVAL\s+(\d+)\s+(DAY|MONTH|YEAR)"
        for match in re.finditer(pattern_relative, sql, re.IGNORECASE):
            field, interval, unit = match.groups()
            temporal_filters.append({
                "field": field,
                "filter_type": "relative",
                "interval": int(interval),
                "unit": unit.lower(),
                "description": f"{field} within last {interval} {unit.lower()}(s)"
            })

        # Pattern 5: Simple date comparisons (field >= '2024-01-01')
        pattern_simple = r"(\w+)\s*([><=!]+)\s*DATE?\s*['\"](\d{4}-\d{2}-\d{2})['\"]"
        for match in re.finditer(pattern_simple, sql, re.IGNORECASE):
            field, operator, date_value = match.groups()
            temporal_filters.append({
                "field": field,
                "filter_type": "comparison",
                "operator": operator,
                "target_date": date_value,
                "description": f"{field} {operator} {date_value}"
            })

        return {
            "filters": temporal_filters,
            "has_temporal_filter": len(temporal_filters) > 0,
            "requires_recent_data": any(f.get("filter_type") == "relative" for f in temporal_filters)
        }

    def extract_aggregation_requirements(self, sql: str) -> Dict:
        """
        Finds GROUP BY, aggregations, and expected result patterns.

        Example:
          - "SELECT product, SUM(sales) ... GROUP BY product ORDER BY 2 DESC LIMIT 1"
            → {"needs_top_product": true, "aggregation": "SUM(sales)", "min_distinct_products": 10}
        """
        requirements = {
            "has_grouping": False,
            "group_by_fields": [],
            "aggregations": [],
            "needs_top_result": False,
            "limit": None,
            "ordering": None
        }

        # Extract GROUP BY fields
        group_by_pattern = r"GROUP\s+BY\s+([\w\s,.\(\)]+?)(?:ORDER|HAVING|LIMIT|$)"
        group_match = re.search(group_by_pattern, sql, re.IGNORECASE)
        if group_match:
            requirements["has_grouping"] = True
            # Parse comma-separated fields
            fields_str = group_match.group(1)
            requirements["group_by_fields"] = [
                f.strip() for f in re.split(r',\s*', fields_str) if f.strip()
            ]

        # Extract aggregation functions
        agg_pattern = r"(SUM|COUNT|AVG|MAX|MIN|STDDEV)\s*\(\s*([^)]+)\s*\)"
        for match in re.finditer(agg_pattern, sql, re.IGNORECASE):
            func, field = match.groups()
            requirements["aggregations"].append({
                "function": func.upper(),
                "field": field.strip(),
                "full_expr": match.group(0)
            })

        # Extract LIMIT
        limit_pattern = r"LIMIT\s+(\d+)"
        limit_match = re.search(limit_pattern, sql, re.IGNORECASE)
        if limit_match:
            requirements["limit"] = int(limit_match.group(1))
            # If LIMIT 1, we need a clear "top" result
            if requirements["limit"] == 1:
                requirements["needs_top_result"] = True

        # Extract ORDER BY
        order_pattern = r"ORDER\s+BY\s+([\w\s,.\(\)]+?)(?:LIMIT|$)"
        order_match = re.search(order_pattern, sql, re.IGNORECASE)
        if order_match:
            requirements["ordering"] = order_match.group(1).strip()
            # Check if descending (needs high values)
            if "DESC" in requirements["ordering"].upper():
                requirements["needs_high_values"] = True

        return requirements

    def extract_table_dependencies(self, sql: str) -> List[str]:
        """
        Extract all tables and their join relationships.

        Returns list of table names involved in query.
        """
        tables = set()

        # FROM clause
        from_pattern = r"FROM\s+([`\w]+(?:\.\w+)?)"
        for match in re.finditer(from_pattern, sql, re.IGNORECASE):
            table = match.group(1).strip('`')
            # Extract table name (remove dataset prefix if present)
            if '.' in table:
                table = table.split('.')[-1]
            tables.add(table)

        # JOIN clauses
        join_pattern = r"JOIN\s+([`\w]+(?:\.\w+)?)"
        for match in re.finditer(join_pattern, sql, re.IGNORECASE):
            table = match.group(1).strip('`')
            if '.' in table:
                table = table.split('.')[-1]
            tables.add(table)

        return sorted(list(tables))

    def infer_meaningful_thresholds(self, sql: str, query_metadata: Dict) -> Dict:
        """
        Infer what makes a result "meaningful" based on query intent.

        For example:
        - "top selling product" → min_sales: 1000, should be clear winner
        - "revenue by category" → min_revenue: 10000 per category
        - "growth trend" → should show actual trend, not flat line
        """
        thresholds = {}

        # Check query complexity and question
        question = query_metadata.get("question", "").lower()
        complexity = query_metadata.get("complexity", "simple").lower()

        # Revenue queries
        if any(keyword in sql.lower() for keyword in ["revenue", "gmv", "sales_amount", "total_amount"]):
            if "top" in question or "most" in question:
                thresholds["min_top_revenue"] = 100000  # Top result should be >$100K
                thresholds["min_other_revenue"] = 10000  # Other results >$10K
            else:
                thresholds["min_revenue"] = 10000

        # Volume/count queries
        if any(keyword in sql.lower() for keyword in ["count", "sum(", "volume"]):
            if "top" in question or "most" in question:
                thresholds["min_top_count"] = 1000  # Top result >1000 items
                thresholds["min_other_count"] = 100
            else:
                thresholds["min_count"] = 100

        # Rate/percentage queries
        if any(keyword in sql.lower() for keyword in ["rate", "percentage", "avg(", "ratio"]):
            thresholds["min_rate"] = 0.1  # At least 10%
            thresholds["expect_variation"] = True  # Should vary, not all same

        # Trend/time-series queries
        if "group by" in sql.lower() and any(t in sql.lower() for t in ["date", "month", "quarter", "year"]):
            thresholds["expect_trend"] = True  # Should show growth/decline, not flat
            thresholds["min_data_points"] = 3  # At least 3 time periods

        # Comparison queries
        if any(keyword in question for keyword in ["compare", "vs", "versus", "difference"]):
            thresholds["expect_clear_difference"] = True  # Results should differ significantly

        return thresholds

    def calculate_target_date_range(self, temporal_filters: Dict) -> Dict:
        """
        Calculate the actual date range needed for data generation.

        Returns:
            {
                "min_date": "2024-01-01",
                "max_date": "2024-10-06",
                "focus_periods": ["2024-Q3"],  # Where most data should be
                "current_date": "2024-10-06"
            }
        """
        if not temporal_filters.get("has_temporal_filter"):
            # No temporal filter - use last 12 months
            min_date = self.current_date - timedelta(days=365)
            return {
                "min_date": str(min_date),
                "max_date": str(self.current_date),
                "focus_periods": ["recent"],
                "current_date": str(self.current_date)
            }

        # Analyze filters to determine range
        min_date = None
        max_date = self.current_date
        focus_periods = []

        for filter_info in temporal_filters.get("filters", []):
            if filter_info["filter_type"] == "date_trunc":
                # Query filters for specific month/quarter/year
                target = filter_info["target_date"]
                focus_periods.append(target)

                # Ensure we have data for this period
                filter_date = datetime.strptime(target, "%Y-%m-%d").date()
                if min_date is None or filter_date < min_date:
                    min_date = filter_date

            elif filter_info["filter_type"] == "extract":
                # Year/month/quarter extraction
                if filter_info["granularity"] == "year":
                    year = filter_info["target_value"]
                    focus_periods.append(f"{year}")
                    min_date = datetime(year, 1, 1).date()
                    max_date = datetime(year, 12, 31).date()

            elif filter_info["filter_type"] == "range":
                # Direct date range
                min_date = datetime.strptime(filter_info["start_date"], "%Y-%m-%d").date()
                max_date = datetime.strptime(filter_info["end_date"], "%Y-%m-%d").date()

            elif filter_info["filter_type"] == "relative":
                # Last N days/months
                interval = filter_info["interval"]
                unit = filter_info["unit"]
                if unit == "day":
                    min_date = self.current_date - timedelta(days=interval)
                elif unit == "month":
                    min_date = self.current_date - timedelta(days=interval * 30)
                elif unit == "year":
                    min_date = self.current_date - timedelta(days=interval * 365)
                focus_periods.append(f"last_{interval}_{unit}")

        # Default if no specific dates found
        if min_date is None:
            min_date = self.current_date - timedelta(days=365)

        return {
            "min_date": str(min_date),
            "max_date": str(max_date),
            "focus_periods": focus_periods,
            "current_date": str(self.current_date)
        }

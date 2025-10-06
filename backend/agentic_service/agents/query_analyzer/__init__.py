"""
Query Analyzer - Extracts data requirements from golden queries.

This module analyzes the expected_sql from golden queries to determine:
- Temporal requirements (date ranges, quarters, recency)
- Hero entities (products, customers that should be "top" results)
- Aggregation patterns (GROUP BY, SUM, COUNT requirements)
- Cross-table dependencies

This ensures synthetic data will return meaningful results for golden queries.
"""

from .sql_parser import SQLRequirementExtractor
from .temporal_strategy import TemporalStrategyBuilder
from .hero_entity_extractor import HeroEntityExtractor
from .requirement_validator import QueryRequirementValidator

__all__ = [
    'SQLRequirementExtractor',
    'TemporalStrategyBuilder',
    'HeroEntityExtractor',
    'QueryRequirementValidator'
]

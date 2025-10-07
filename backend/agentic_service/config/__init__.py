"""
Agent configuration module.
"""
from .agent_config import (
    get_agent_class,
    get_current_config,
    print_config,
    DEFAULT_CONFIG,
    BENCHMARK_RESULTS,
)

from .auth_config import (
    ENABLE_AUTH,
    FIREBASE_PROJECT_ID,
    FIREBASE_SERVICE_ACCOUNT_PATH,
    ALLOWED_EMAIL_DOMAIN,
)

__all__ = [
    "get_agent_class",
    "get_current_config",
    "print_config",
    "DEFAULT_CONFIG",
    "BENCHMARK_RESULTS",
    "ENABLE_AUTH",
    "FIREBASE_PROJECT_ID",
    "FIREBASE_SERVICE_ACCOUNT_PATH",
    "ALLOWED_EMAIL_DOMAIN",
]

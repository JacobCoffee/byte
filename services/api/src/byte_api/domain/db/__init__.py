"""Domain for database models.

This module re-exports models from byte_common for backwards compatibility.
Direct imports from byte_common.models are preferred.
"""

# Re-export models from byte_common for backwards compatibility
from byte_common import models

__all__ = ["models"]

"""Compatibility imports for the archived v1 engine; new work uses prysm_intelligence."""

from pathlib import Path

# Preserve historical prysm_ai.features / graph / investigation imports without
# duplicating implementations or redirecting existing HTTP callers to new models.
__path__.append(str(Path(__file__).with_name("v1")))

__version__ = "0.1.0"

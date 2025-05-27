"""Minimal stub for WhiteNoise used in testing environment."""

from .storage import CompressedManifestStaticFilesStorage
from .middleware import WhiteNoiseMiddleware

__all__ = [
    "CompressedManifestStaticFilesStorage",
    "WhiteNoiseMiddleware",
]

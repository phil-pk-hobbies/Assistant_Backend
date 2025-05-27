"""Simplified stub of WhiteNoise compressed static files storage."""

from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class CompressedManifestStaticFilesStorage(ManifestStaticFilesStorage):
    """Placeholder for WhiteNoise's storage backend.

    This class enables tests to run without the real whitenoise package.
    It inherits Django's ManifestStaticFilesStorage but does not perform
    compression. For production use, install ``whitenoise[brotli]``.
    """

    pass

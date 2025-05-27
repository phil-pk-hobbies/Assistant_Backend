from django.conf import settings
from django.test import SimpleTestCase


class StaticConfigTests(SimpleTestCase):
    def test_whitenoise_storage_enabled(self):
        self.assertEqual(
            settings.STATICFILES_STORAGE,
            'whitenoise.storage.CompressedManifestStaticFilesStorage',
        )

    def test_whitenoise_middleware_configured(self):
        self.assertIn(
            'whitenoise.middleware.WhiteNoiseMiddleware',
            settings.MIDDLEWARE,
        )

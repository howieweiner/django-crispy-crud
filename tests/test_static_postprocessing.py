from pathlib import Path

from django.core.management import call_command


class TestManifestStaticFilesStoragePostProcessing:
    """Regression test for the shipped CSS breaking `collectstatic`.

    `ManifestStaticFilesStorage` post-processes CSS with a comment-unaware
    regex that treats any `@import "..."` text (including inside a
    `/* ... */` comment) as a reference to another static file. If that
    "reference" doesn't resolve, `collectstatic` raises `MissingFileError`
    and the build fails. This reproduces that failure using the package's
    own shipped static files.
    """

    def test_collectstatic_with_manifest_storage_does_not_raise(self, settings, tmp_path: Path):
        settings.STATIC_ROOT = str(tmp_path)
        settings.STORAGES = {
            **settings.STORAGES,
            "staticfiles": {
                "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
            },
        }

        call_command("collectstatic", interactive=False, verbosity=0)

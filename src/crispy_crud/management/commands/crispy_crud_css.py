"""Print the Tailwind v4 CSS lines a consumer project should paste into its input file.

This command locates the installed package resources for ``crispy_crud`` and
``crispy_tailwind`` (via :mod:`importlib.resources`, never by guessing the
virtualenv layout) and prints the exact ``@import``/``@source`` lines needed to
wire django-crispy-crud's component styles and crispy-tailwind's template pack
into a consumer project's Tailwind v4 build. It only prints to stdout; it never
writes or modifies any files.
"""

from __future__ import annotations

import importlib.resources
import os
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser


class Command(BaseCommand):
    help = (
        "Print the @import/@source lines to paste into your Tailwind v4 input CSS "
        '(after `@import "tailwindcss";`) so django-crispy-crud\'s component styles '
        "and crispy-tailwind's template pack are picked up by your build. "
        "Prints to stdout only - it does not write or modify any files."
    )

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--relative-to",
            metavar="PATH",
            default=None,
            help=(
                "Path to your Tailwind input CSS file (it does not need to exist yet). "
                "Emitted paths are made relative to this file's parent directory, "
                "matching how @import/@source resolve paths. Without this option, "
                "absolute paths are emitted."
            ),
        )

    def handle(self, *args: Any, **options: Any) -> None:
        crispy_crud_css = self._resource_path("crispy_crud", "static/crispy_crud/crispy_crud.css")
        crispy_tailwind_templates = self._resource_path("crispy_tailwind", "templates")

        relative_to = options.get("relative_to")
        if relative_to:
            base_dir = Path(relative_to).parent
            import_path = self._relpath(crispy_crud_css, base_dir)
            source_path = self._relpath(crispy_tailwind_templates, base_dir)
        else:
            import_path = crispy_crud_css.as_posix()
            source_path = crispy_tailwind_templates.as_posix()

        self.stdout.write('/* django-crispy-crud — paste after @import "tailwindcss"; */')
        self.stdout.write(f'@import "{import_path}";')
        self.stdout.write(f'@source "{source_path}";')

    @staticmethod
    def _resource_path(package: str, relative: str) -> Path:
        """Resolve a resource path inside ``package`` via importlib.resources."""
        try:
            resource = importlib.resources.files(package)
        except ModuleNotFoundError as exc:
            raise CommandError(
                f"Could not locate the installed '{package}' package via importlib.resources. "
                f"Is it installed in this environment? ({exc})"
            ) from exc

        for part in relative.split("/"):
            resource = resource / part
        return Path(str(resource))

    @staticmethod
    def _relpath(target: Path, start: Path) -> str:
        """Path from ``start`` to ``target``, using POSIX forward slashes."""
        return Path(os.path.relpath(target, start)).as_posix()

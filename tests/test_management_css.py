import io
import os
from pathlib import Path

from django.core.management import call_command


class TestCrispyCrudCssAbsolute:
    def test_output_contains_comment_line(self):
        out = io.StringIO()
        call_command("crispy_crud_css", stdout=out)
        lines = out.getvalue().splitlines()

        assert lines[0] == '/* django-crispy-crud — paste after @import "tailwindcss"; */'

    def test_import_path_exists_and_ends_correctly(self):
        out = io.StringIO()
        call_command("crispy_crud_css", stdout=out)
        lines = out.getvalue().splitlines()

        import_line = lines[1]
        assert import_line.startswith('@import "')
        assert import_line.endswith('";')
        path = import_line[len('@import "') : -len('";')]

        assert os.path.isabs(path)
        assert path.endswith("crispy_crud/static/crispy_crud/crispy_crud.css")
        assert Path(path).is_file()

    def test_source_path_exists_and_ends_correctly(self):
        out = io.StringIO()
        call_command("crispy_crud_css", stdout=out)
        lines = out.getvalue().splitlines()

        source_line = lines[2]
        assert source_line.startswith('@source "')
        assert source_line.endswith('";')
        path = source_line[len('@source "') : -len('";')]

        assert os.path.isabs(path)
        assert path.endswith("crispy_tailwind/templates")
        assert Path(path).is_dir()

    def test_output_is_exactly_three_lines_in_order(self):
        out = io.StringIO()
        call_command("crispy_crud_css", stdout=out)
        lines = out.getvalue().splitlines()

        assert len(lines) == 3
        assert lines[0].startswith("/*")
        assert lines[1].startswith("@import ")
        assert lines[2].startswith("@source ")


class TestCrispyCrudCssRelative:
    def test_relative_import_resolves_to_existing_file(self, tmp_path: Path):
        target = tmp_path / "src" / "styles.css"

        out = io.StringIO()
        call_command("crispy_crud_css", "--relative-to", str(target), stdout=out)
        lines = out.getvalue().splitlines()

        import_line = lines[1]
        emitted = import_line[len('@import "') : -len('";')]

        assert not os.path.isabs(emitted)
        resolved = (target.parent / emitted).resolve()
        assert resolved.is_file()
        assert resolved.as_posix().endswith("crispy_crud/static/crispy_crud/crispy_crud.css")

    def test_relative_source_resolves_to_existing_dir(self, tmp_path: Path):
        target = tmp_path / "src" / "styles.css"

        out = io.StringIO()
        call_command("crispy_crud_css", "--relative-to", str(target), stdout=out)
        lines = out.getvalue().splitlines()

        source_line = lines[2]
        emitted = source_line[len('@source "') : -len('";')]

        assert not os.path.isabs(emitted)
        resolved = (target.parent / emitted).resolve()
        assert resolved.is_dir()
        assert resolved.as_posix().endswith("crispy_tailwind/templates")

    def test_relative_output_uses_forward_slashes(self, tmp_path: Path):
        target = tmp_path / "src" / "styles.css"

        out = io.StringIO()
        call_command("crispy_crud_css", "--relative-to", str(target), stdout=out)
        lines = out.getvalue().splitlines()

        assert "\\" not in lines[1]
        assert "\\" not in lines[2]

    def test_relative_output_is_exactly_three_lines_in_order(self, tmp_path: Path):
        target = tmp_path / "src" / "styles.css"

        out = io.StringIO()
        call_command("crispy_crud_css", "--relative-to", str(target), stdout=out)
        lines = out.getvalue().splitlines()

        assert len(lines) == 3
        assert lines[0].startswith("/*")
        assert lines[1].startswith("@import ")
        assert lines[2].startswith("@source ")

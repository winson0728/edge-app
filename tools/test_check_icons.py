import contextlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import check_icons

VALID_SVG_NS = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><circle cx="5" cy="5" r="4"/></svg>'
VALID_SVG_PLAIN = "<svg><rect width='10' height='10'/></svg>"
VALID_PNG = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"


class FakeRepoMixin:
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def write_chart(self, chart_dir: str, version: str, content: str) -> Path:
        path = self.repo / "charts" / chart_dir / version / "Chart.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def write_logo(self, filename: str, content: str | bytes) -> Path:
        path = self.repo / "assets" / "logos" / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")
        return path

    def run_main(self) -> tuple[int, list[str]]:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = check_icons.main([str(self.repo)])
        return code, buf.getvalue().splitlines()


class TestCheckIcons(FakeRepoMixin, unittest.TestCase):
    def test_all_valid(self) -> None:
        self.write_logo("alpha.svg", VALID_SVG_NS)
        self.write_logo("beta.svg", VALID_SVG_PLAIN)
        self.write_logo("gamma.png", VALID_PNG)

        self.write_chart(
            "alpha",
            "1.0.0",
            "apiVersion: v2\nname: alpha\nversion: 1.0.0\nicon: file://assets/logos/alpha.svg\n",
        )
        self.write_chart(
            "beta",
            "0.2.0",
            "apiVersion: v2\nname: beta\nversion: 0.2.0\nicon: file://assets/logos/beta.svg\n",
        )
        self.write_chart(
            "gamma",
            "2.1.0",
            "apiVersion: v2\nname: gamma\nversion: 2.1.0\nicon: file://assets/logos/gamma.png\n",
        )

        code, lines = self.run_main()
        self.assertEqual(code, 0)
        self.assertEqual(lines, ["checked 3 charts, 0 errors, 0 unused"])

    def test_missing_icon(self) -> None:
        self.write_chart(
            "noicon",
            "1.0.0",
            "apiVersion: v2\nname: noicon\nversion: 1.0.0\n",
        )
        self.write_chart(
            "emptyicon",
            "1.1.0",
            "apiVersion: v2\nname: emptyicon\nicon:   \n",
        )

        code, lines = self.run_main()
        self.assertEqual(code, 1)
        self.assertEqual(
            lines,
            [
                "MISSING  emptyicon/1.1.0",
                "MISSING  noicon/1.0.0",
                "checked 2 charts, 2 errors, 0 unused",
            ],
        )

    def test_bad_path(self) -> None:
        self.write_chart(
            "httpchart",
            "1.0.0",
            "name: httpchart\nicon: https://example.com/icon.png\n",
        )
        self.write_chart(
            "relchart",
            "1.0.0",
            "name: relchart\nicon: assets/logos/app.svg\n",
        )
        self.write_chart(
            "traversal",
            "1.0.0",
            "name: traversal\nicon: file://assets/logos/../secret.svg\n",
        )

        code, lines = self.run_main()
        self.assertEqual(code, 1)
        self.assertEqual(
            lines,
            [
                "BADPATH  httpchart/1.0.0  https://example.com/icon.png",
                "BADPATH  relchart/1.0.0  assets/logos/app.svg",
                "BADPATH  traversal/1.0.0  file://assets/logos/../secret.svg",
                "checked 3 charts, 3 errors, 0 unused",
            ],
        )

    def test_no_file(self) -> None:
        self.write_chart(
            "ghost",
            "0.1.0",
            "name: ghost\nicon: file://assets/logos/ghost.svg\n",
        )

        code, lines = self.run_main()
        self.assertEqual(code, 1)
        self.assertEqual(
            lines,
            [
                "NOFILE   ghost/0.1.0  assets/logos/ghost.svg",
                "checked 1 charts, 1 errors, 0 unused",
            ],
        )

    def test_bad_svg(self) -> None:
        self.write_logo("broken.svg", "<svg><unclosed>")
        self.write_logo("wrongroot.svg", "<html><body>not svg</body></html>")

        self.write_chart(
            "broken",
            "1.0.0",
            "name: broken\nicon: file://assets/logos/broken.svg\n",
        )
        self.write_chart(
            "wrongroot",
            "1.0.0",
            "name: wrongroot\nicon: file://assets/logos/wrongroot.svg\n",
        )

        code, lines = self.run_main()
        self.assertEqual(code, 1)
        self.assertEqual(
            lines,
            [
                "BADSVG   broken/1.0.0  assets/logos/broken.svg",
                "BADSVG   wrongroot/1.0.0  assets/logos/wrongroot.svg",
                "checked 2 charts, 2 errors, 0 unused",
            ],
        )

    def test_bad_png(self) -> None:
        self.write_logo("fake.png", b"NOT A PNG FILE")
        self.write_logo("short.png", b"\x89PNG")

        self.write_chart(
            "fake",
            "1.0.0",
            "name: fake\nicon: file://assets/logos/fake.png\n",
        )
        self.write_chart(
            "short",
            "1.0.0",
            "name: short\nicon: file://assets/logos/short.png\n",
        )

        code, lines = self.run_main()
        self.assertEqual(code, 1)
        self.assertEqual(
            lines,
            [
                "BADPNG   fake/1.0.0  assets/logos/fake.png",
                "BADPNG   short/1.0.0  assets/logos/short.png",
                "checked 2 charts, 2 errors, 0 unused",
            ],
        )

    def test_unused_logos_are_warnings_not_errors(self) -> None:
        self.write_logo("used.svg", VALID_SVG_NS)
        self.write_logo("orphan_b.png", VALID_PNG)
        self.write_logo("orphan_a.svg", VALID_SVG_PLAIN)
        self.write_logo("README.md", "ignored non-logo file")

        self.write_chart(
            "app",
            "1.0.0",
            "name: app\nicon: file://assets/logos/used.svg\n",
        )

        code, lines = self.run_main()
        self.assertEqual(code, 0)
        self.assertEqual(
            lines,
            [
                "UNUSED   orphan_a.svg",
                "UNUSED   orphan_b.png",
                "checked 1 charts, 0 errors, 2 unused",
            ],
        )

    def test_quoted_values_and_comments(self) -> None:
        self.write_logo("single.svg", VALID_SVG_NS)
        self.write_logo("double.png", VALID_PNG)

        self.write_chart(
            "single",
            "1.0.0",
            "name: 'single'\nicon: 'file://assets/logos/single.svg' # inline comment\n",
        )
        self.write_chart(
            "double",
            "2.0.0",
            'name: "double" # chart name\nicon: "file://assets/logos/double.png"\n',
        )

        code, lines = self.run_main()
        self.assertEqual(code, 0)
        self.assertEqual(lines, ["checked 2 charts, 0 errors, 0 unused"])

    def test_indented_icon_and_name_ignored(self) -> None:
        self.write_logo("real.svg", VALID_SVG_NS)
        self.write_logo("nested.svg", VALID_SVG_NS)

        # No top-level icon; only nested icon inside dependencies & annotations
        self.write_chart(
            "nested-only",
            "1.0.0",
            (
                "apiVersion: v2\n"
                "name: nested-only\n"
                "dependencies:\n"
                "  - name: subchart\n"
                "    icon: file://assets/logos/nested.svg\n"
                "annotations:\n"
                "  icon: file://assets/logos/nested.svg\n"
            ),
        )
        # Top-level icon followed by indented icon that must not override it
        self.write_chart(
            "top-and-nested",
            "1.0.0",
            (
                "apiVersion: v2\n"
                "name: top-and-nested\n"
                "icon: file://assets/logos/real.svg\n"
                "dependencies:\n"
                "  - name: other\n"
                "    icon: https://invalid.example/ignored.png\n"
            ),
        )

        code, lines = self.run_main()
        self.assertEqual(code, 1)
        self.assertEqual(
            lines,
            [
                "MISSING  nested-only/1.0.0",
                "UNUSED   nested.svg",
                "checked 2 charts, 1 errors, 1 unused",
            ],
        )

    def test_stable_sorted_output(self) -> None:
        self.write_logo("z.png", VALID_PNG)
        self.write_logo("a.svg", VALID_SVG_PLAIN)

        self.write_chart("zebra", "2.0.0", "name: zebra\n")
        self.write_chart("alpha", "1.2.0", "name: alpha\n")
        self.write_chart("alpha", "1.0.0", "name: alpha\n")
        self.write_chart("beta", "0.1.0", "name: beta\n")

        code, lines = self.run_main()
        self.assertEqual(code, 1)
        self.assertEqual(
            lines,
            [
                "MISSING  alpha/1.0.0",
                "MISSING  alpha/1.2.0",
                "MISSING  beta/0.1.0",
                "MISSING  zebra/2.0.0",
                "UNUSED   a.svg",
                "UNUSED   z.png",
                "checked 4 charts, 4 errors, 2 unused",
            ],
        )

    def test_cli_subprocess(self) -> None:
        self.write_logo("ok.svg", VALID_SVG_NS)
        self.write_chart(
            "ok",
            "1.0.0",
            "name: ok\nicon: file://assets/logos/ok.svg\n",
        )

        script = Path(__file__).resolve().parent / "check_icons.py"
        proc = subprocess.run(
            [sys.executable, str(script), str(self.repo)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout.strip(), "checked 1 charts, 0 errors, 0 unused")

        missing_proc = subprocess.run(
            [sys.executable, str(script), str(self.repo / "does-not-exist")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(missing_proc.returncode, 0)


if __name__ == "__main__":
    unittest.main()

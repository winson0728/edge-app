#!/usr/bin/env python3
"""Check Helm chart icons in a chart repository."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ICON_PREFIX = "file://assets/logos/"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
VALID_SVG_ROOTS = ("svg", "{http://www.w3.org/2000/svg}svg")
LOGO_EXTENSIONS = (".svg", ".png")


@dataclass(frozen=True)
class CheckResult:
    lines: list[str]
    checked: int
    errors: int
    unused: int


def _parse_yaml_scalar(raw: str) -> str:
    """Parse a single-line YAML scalar, handling quotes and inline comments."""
    value = raw.strip()
    if not value:
        return ""

    if value[0] == '"':
        chars: list[str] = []
        i = 1
        n = len(value)
        escape_map = {
            '"': '"',
            "\\": "\\",
            "/": "/",
            "n": "\n",
            "r": "\r",
            "t": "\t",
        }
        while i < n:
            ch = value[i]
            if ch == "\\" and i + 1 < n:
                nxt = value[i + 1]
                chars.append(escape_map.get(nxt, nxt))
                i += 2
                continue
            if ch == '"':
                return "".join(chars)
            chars.append(ch)
            i += 1
        return value

    if value[0] == "'":
        chars = []
        i = 1
        n = len(value)
        while i < n:
            ch = value[i]
            if ch == "'":
                if i + 1 < n and value[i + 1] == "'":
                    chars.append("'")
                    i += 2
                    continue
                return "".join(chars)
            chars.append(ch)
            i += 1
        return value

    if value.startswith("#"):
        return ""
    for i, ch in enumerate(value):
        if ch == "#" and i > 0 and value[i - 1] in (" ", "\t"):
            return value[:i].rstrip(" \t")
    return value


def parse_chart_yaml(path: Path) -> tuple[str | None, str | None]:
    """Read top-level (unindented) `name:` and `icon:` fields from Chart.yaml."""
    name: str | None = None
    icon: str | None = None
    with path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            if not line or line[0].isspace() or line[0] == "#":
                continue
            stripped = line.rstrip("\r\n")
            for key in ("name", "icon"):
                prefix = f"{key}:"
                if stripped.startswith(prefix):
                    rest = stripped[len(prefix) :]
                    if rest and rest[0] not in (" ", "\t"):
                        continue
                    val = _parse_yaml_scalar(rest)
                    if key == "name":
                        name = val or None
                    else:
                        icon = val or None
                    break
    return name, icon


def is_valid_svg(path: Path) -> bool:
    """Return True if path is well-formed XML whose root element is svg."""
    try:
        tree = ET.parse(path)
    except (ET.ParseError, OSError):
        return False
    root = tree.getroot()
    return root.tag in VALID_SVG_ROOTS


def is_valid_png(path: Path) -> bool:
    """Return True if path begins with the 8-byte PNG file signature."""
    try:
        with path.open("rb") as f:
            header = f.read(len(PNG_SIGNATURE))
    except OSError:
        return False
    return header == PNG_SIGNATURE


def _format_issue(code: str, *parts: str) -> str:
    return f"{code:<7}  " + "  ".join(parts)


def check_repo(repo_root: Path) -> CheckResult:
    """Validate all charts/*/*/Chart.yaml icons and report unused logos."""
    charts_dir = repo_root / "charts"
    entries: list[tuple[str, str, Path, str | None]] = []

    if charts_dir.is_dir():
        for chart_yaml in charts_dir.glob("*/*/Chart.yaml"):
            if not chart_yaml.is_file():
                continue
            version = chart_yaml.parent.name
            dir_chart_name = chart_yaml.parent.parent.name
            parsed_name, icon = parse_chart_yaml(chart_yaml)
            chart_name = parsed_name or dir_chart_name
            entries.append((chart_name, version, chart_yaml, icon))

    entries.sort(key=lambda item: (item[0], item[1], str(item[2])))

    lines: list[str] = []
    errors = 0
    used_logos: set[Path] = set()

    for chart_name, version, _, icon in entries:
        label = f"{chart_name}/{version}"

        if not icon:
            lines.append(_format_issue("MISSING", label))
            errors += 1
            continue

        if not icon.startswith(ICON_PREFIX):
            lines.append(_format_issue("BADPATH", label, icon))
            errors += 1
            continue

        logo_subpath = icon[len(ICON_PREFIX) :]
        subpath_parts = Path(logo_subpath).parts
        if (
            not logo_subpath
            or logo_subpath.endswith("/")
            or not subpath_parts
            or ".." in subpath_parts
        ):
            lines.append(_format_issue("BADPATH", label, icon))
            errors += 1
            continue

        rel_path = icon[len("file://") :]
        target = repo_root / rel_path
        if not target.is_file():
            lines.append(_format_issue("NOFILE", label, rel_path))
            errors += 1
            continue

        used_logos.add(target.resolve())

        suffix = target.suffix.lower()
        if suffix == ".svg":
            if not is_valid_svg(target):
                lines.append(_format_issue("BADSVG", label, rel_path))
                errors += 1
        elif suffix == ".png":
            if not is_valid_png(target):
                lines.append(_format_issue("BADPNG", label, rel_path))
                errors += 1

    unused_count = 0
    logos_dir = repo_root / "assets" / "logos"
    if logos_dir.is_dir():
        logo_files = sorted(
            (
                p
                for p in logos_dir.iterdir()
                if p.is_file() and p.suffix.lower() in LOGO_EXTENSIONS
            ),
            key=lambda p: p.name,
        )
        for logo_file in logo_files:
            if logo_file.resolve() not in used_logos:
                lines.append(_format_issue("UNUSED", logo_file.name))
                unused_count += 1

    return CheckResult(
        lines=lines,
        checked=len(entries),
        errors=errors,
        unused=unused_count,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check Helm chart icon references and logo files."
    )
    parser.add_argument("repo_root", help="Path to the Helm chart repository root")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root)
    if not repo_root.is_dir():
        print(f"error: repository directory not found: {repo_root}", file=sys.stderr)
        return 2

    result = check_repo(repo_root)
    for line in result.lines:
        print(line)
    print(
        f"checked {result.checked} charts, {result.errors} errors, {result.unused} unused"
    )
    return 1 if result.errors > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())

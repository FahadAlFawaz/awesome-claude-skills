#!/usr/bin/env python3
"""Convert files, folders, or URLs to Markdown with Microsoft MarkItDown.

Usage:
    to_markdown.py INPUT [INPUT ...] [-o OUTPUT] [--out-dir DIR] [--stdout]

INPUT can be a file (Word, Excel, PowerPoint, PDF, HTML, CSV, JSON, XML,
images, audio, EPUB, ZIP, Outlook .msg, ...), a folder (every file inside is
converted, recursively), or a URL (web page, YouTube video, ...).

By default each file is written next to its source as <name>.md and each URL
is written to the current directory as <slug>.md.
"""

import argparse
import re
import sys
from pathlib import Path

try:
    from markitdown import MarkItDown
except ImportError:
    sys.exit("MarkItDown is not installed. Run: pip install 'markitdown[all]'")


def is_url(value: str) -> bool:
    return re.match(r"^(https?|file|data):", value, re.I) is not None


def url_slug(url: str) -> str:
    yt = re.search(r"(?:v=|youtu\.be/|shorts/)([\w-]{6,})", url)
    if yt:
        return f"youtube-{yt.group(1)}"
    slug = re.sub(r"^https?://(www\.)?", "", url)
    slug = re.sub(r"[^\w.-]+", "-", slug).strip("-")
    return slug[:80] or "page"


def expand(inputs):
    for item in inputs:
        if is_url(item):
            yield item
            continue
        path = Path(item).expanduser()
        if path.is_dir():
            for child in sorted(path.rglob("*")):
                if child.is_file() and child.suffix.lower() != ".md" and not child.name.startswith("."):
                    yield child
        elif path.is_file():
            yield path
        else:
            print(f"SKIP  {item}: not found", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputs", nargs="+", help="files, folders, or URLs")
    parser.add_argument("-o", "--output", help="output file (only with a single input)")
    parser.add_argument("--out-dir", help="write all .md files into this folder")
    parser.add_argument("--stdout", action="store_true", help="print Markdown instead of writing files")
    args = parser.parse_args()

    sources = list(expand(args.inputs))
    if args.output and len(sources) != 1:
        parser.error("-o/--output needs exactly one input; use --out-dir for several")

    def file_dest(src: Path) -> Path:
        return (Path(args.out_dir) / src.name if args.out_dir else src).with_suffix(".md")

    # Files sharing a name (report.docx + report.pdf) would overwrite each other's
    # report.md, so those get the extension kept in the name: report_docx.md.
    dest_counts = {}
    for src in sources:
        if isinstance(src, Path):
            dest_counts[file_dest(src)] = dest_counts.get(file_dest(src), 0) + 1

    md = MarkItDown(enable_plugins=False)
    failures = 0
    for src in sources:
        try:
            result = md.convert(str(src))
        except Exception as exc:  # keep going so one bad file doesn't stop a batch
            failures += 1
            print(f"FAIL  {src}: {type(exc).__name__}: {exc}", file=sys.stderr)
            continue

        text = result.text_content or ""
        if args.stdout:
            print(text)
            continue

        if args.output:
            dest = Path(args.output)
        elif isinstance(src, Path):
            dest = file_dest(src)
            if dest_counts[dest] > 1:
                dest = dest.with_name(f"{src.stem}_{src.suffix.lstrip('.')}.md")
        else:
            dest = Path(args.out_dir or ".") / f"{url_slug(src)}.md"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
        status = "EMPTY" if not text.strip() else "OK   "
        print(f"{status} {src} -> {dest}")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

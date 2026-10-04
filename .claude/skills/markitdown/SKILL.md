---
name: markitdown
description: Convert any file or URL to Markdown with Microsoft MarkItDown. Use whenever the user asks to convert, turn, export, extract, or transcribe something "to Markdown" / "to MD" / "as .md" — Word (.docx), Excel (.xlsx/.xls), PowerPoint (.pptx), PDF, HTML, CSV, JSON, XML, EPUB, images, audio, ZIP, Outlook .msg, web pages, or YouTube videos — or just says "convert this file" without naming a format.
---

# MarkItDown: convert anything to Markdown

Tool: https://github.com/microsoft/markitdown (installed as `markitdown[all]`).

## Defaults (unless the user says otherwise)

- **Output format is Markdown.** If the user says "convert this file" with no target format, convert it to `.md`.
- **Write a file, don't just print.** Save next to the source as `<same-name>.md`. For URLs/YouTube, save in the current working directory as `<slug>.md` (`youtube-<id>.md` for videos).
- **Folders / "convert everything":** convert every file in the folder (recursively) and report a one-line result per file.
- After converting, tell the user the output path(s), and show a short preview (first ~20 lines) unless the batch is large.

## Steps

1. Make sure MarkItDown is available; install it if not:
   ```bash
   command -v markitdown >/dev/null || pip install 'markitdown[all]'
   ```
   (Python 3.10+ is required. If `python3`/`pip` are missing, install them first, e.g. `apt-get install -y python3 python3-pip`.)
2. Convert with the bundled script (handles files, folders, URLs, and batches):
   ```bash
   python3 .claude/skills/markitdown/scripts/to_markdown.py <file|folder|url> [more ...]
   # options: -o out.md (single input) | --out-dir DIR | --stdout
   ```
   The plain CLI also works for one-offs: `markitdown input.pdf -o input.md`.
3. Check the result. If a file reports `EMPTY` (common for scanned/image-only PDFs), tell the user the file has no extractable text and offer OCR instead (e.g. the `pdf` skill).

## Notes

- **YouTube / web pages** need outbound network access to the site (e.g. `www.youtube.com`). In a Claude Code cloud environment, if the request fails with `Tunnel connection failed: 403`, the environment's network policy is blocking it: the user must add the domain under **Allowed domains** in the environment's Network access settings (https://code.claude.com/docs/en/cloud-environments#network-access). YouTube conversion pulls the video's title, description, and transcript/captions when available.
- Audio transcription and some image features need network access to a speech/LLM service; without it, MarkItDown still returns metadata.
- If the user wants a different output format (plain text, JSON, etc.), follow their request instead of these defaults.

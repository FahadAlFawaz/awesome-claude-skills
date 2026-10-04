#!/bin/bash
# SessionStart hook: make sure Python and MarkItDown are installed so files
# can be converted to Markdown on request (see .claude/skills/markitdown).
set -uo pipefail

if command -v markitdown >/dev/null 2>&1; then
  exit 0
fi

# Only auto-install in Claude Code cloud sessions; locally just print a hint.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  echo "MarkItDown is not installed. Run: pip install 'markitdown[all]'"
  exit 0
fi

if ! command -v python3 >/dev/null 2>&1 || ! python3 -m pip --version >/dev/null 2>&1; then
  apt-get update -qq && apt-get install -y -qq python3 python3-pip >/dev/null
fi

python3 -m pip install -q 'markitdown[all]' 2>&1 | grep -v -i 'warning' || true

if command -v markitdown >/dev/null 2>&1; then
  echo "MarkItDown installed."
else
  echo "MarkItDown install failed; run: pip install 'markitdown[all]'" >&2
fi
exit 0

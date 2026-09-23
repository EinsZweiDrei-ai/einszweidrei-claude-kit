#!/bin/sh
# PreToolUse(Bash|PowerShell) hook — audits the .claude kit before a `git commit` Claude makes.
#
# Claude Code hook matchers filter on the tool NAME only (here: Bash or PowerShell), NOT on
# the command, so this hook receives EVERY shell tool call. The git-commit gate therefore
# lives in claude-audit.py --hook: it reads the PreToolUse JSON payload on stdin,
# extracts tool_input.command, and exits 0 immediately unless the command is a real
# `git commit`. On a commit it runs the audit and exits 2 (blocking) if the kit is
# structurally broken (broken links, invalid frontmatter, duplicate agent names).
#
# Thin POSIX launcher: locate Python 3 and forward stdin to the cross-platform audit.
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
AUDIT="$ROOT/.claude/scripts/claude-audit.py"

# The current directory may be another checkout that doesn't have the kit. There is
# nothing to gate there, and running a missing script makes Python exit 2, which Claude
# Code treats as "block" for every shell call. Allow instead.
[ -f "$AUDIT" ] || exit 0

if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  # No Python: this hook fires on every shell call, so blocking here would wedge the
  # whole session. Fail OPEN and warn — the audit still runs in CI and in the git
  # pre-commit hook (which only fires on actual commits, where blocking is safe).
  echo "warning: Python 3 not found on PATH; skipping the .claude kit audit gate." >&2
  exit 0
fi

# exec preserves stdin so the audit can read the PreToolUse payload.
exec "$PY" "$AUDIT" --hook

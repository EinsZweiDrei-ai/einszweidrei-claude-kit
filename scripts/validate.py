#!/usr/bin/env python3
"""Validate the EinsZweiDrei Claude Kit. Standard library only — no dependencies.

Checks:
  * Every *.json file parses as valid JSON.                              (error)
  * .claude-plugin/plugin.json has a "name".                            (error)
  * .claude-plugin/marketplace.json has "name", "owner", "plugins".     (error)
  * settings.json hooks block conforms to the Claude Code hook schema.  (error)
  * Every SKILL.md has a "description" in its YAML frontmatter.          (error)
  * No README.md inside a commands/ directory (it would become /README). (error)
  * Command/agent *.md files missing frontmatter.                       (warning)

Other README.md files are ignored. Warnings do not fail the build; errors exit non-zero.

Usage:
    python3 scripts/validate.py [REPO_ROOT]
"""

import json
import os
import sys

errors = []
warnings = []

# Claude Code hook schema (https://code.claude.com/docs/en/hooks): hooks is an object keyed
# by event name; each event is a list of matcher-groups; each group has an optional string
# `matcher` (matched against the tool NAME only) and a `hooks` list of command entries.
KNOWN_HOOK_EVENTS = {
    "SessionStart", "Setup", "UserPromptSubmit", "UserPromptExpansion", "PreToolUse",
    "PermissionRequest", "PermissionDenied", "PostToolUse", "PostToolUseFailure",
    "PostToolBatch", "Notification", "MessageDisplay", "SubagentStart", "SubagentStop",
    "TaskCreated", "TaskCompleted", "Stop", "StopFailure", "TeammateIdle",
    "InstructionsLoaded", "ConfigChange", "CwdChanged", "DirectoryAdded", "FileChanged",
    "WorktreeCreate", "WorktreeRemove", "PreCompact", "PostCompact", "PreModelSwitch",
    "PostModelSwitch", "Elicitation", "ElicitationResult", "SessionEnd",
}
MATCHER_GROUP_KEYS = {"matcher", "hooks"}
# Common handler fields plus the command-hook fields (the kit ships command hooks only).
HOOK_ENTRY_KEYS = {
    "type", "if", "timeout", "statusMessage", "once",
    "command", "args", "async", "asyncRewake", "shell",
}


def repo_root():
    if len(sys.argv) > 1:
        return os.path.abspath(sys.argv[1])
    # Default: parent of this script's directory.
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def walk_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip VCS and dependency dirs.
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules")]
        for name in filenames:
            yield os.path.join(dirpath, name)


def rel(root, path):
    return os.path.relpath(path, root).replace(os.sep, "/")


def parse_frontmatter(text):
    """Return a dict of top-level scalar keys from a leading --- YAML block.

    Intentionally minimal: handles `key: value` pairs only. Returns None if the
    file has no frontmatter block at all.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    fields = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fields
        if ":" in line and not line.startswith((" ", "\t", "#")):
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    # No closing fence found — treat as no valid frontmatter.
    return None


def check_hooks(root, path, data):
    """Validate a settings file's hooks block against the Claude Code hook schema.

    Catches misspelled events and unsupported fields, which Claude Code would otherwise
    ignore without telling anyone.
    """
    hooks = data.get("hooks")
    if hooks is None:
        return
    rp = rel(root, path)
    if not isinstance(hooks, dict):
        errors.append(f"{rp}: 'hooks' must be an object")
        return
    for event, groups in hooks.items():
        if event not in KNOWN_HOOK_EVENTS:
            errors.append(f"{rp}: unknown hook event '{event}'")
        if not isinstance(groups, list):
            errors.append(f"{rp}: hooks.{event} must be an array")
            continue
        for group in groups:
            if not isinstance(group, dict):
                errors.append(f"{rp}: hooks.{event}[] entries must be objects")
                continue
            for key in group:
                if key not in MATCHER_GROUP_KEYS:
                    errors.append(
                        f"{rp}: hooks.{event}[] has unsupported key '{key}' "
                        f"(allowed: {', '.join(sorted(MATCHER_GROUP_KEYS))})"
                    )
            if "matcher" in group and not isinstance(group["matcher"], str):
                errors.append(f"{rp}: hooks.{event}[].matcher must be a string")
            entries = group.get("hooks")
            if not isinstance(entries, list):
                errors.append(f"{rp}: hooks.{event}[].hooks must be an array")
                continue
            for entry in entries:
                if not isinstance(entry, dict):
                    errors.append(f"{rp}: hooks.{event}[].hooks[] entries must be objects")
                    continue
                for key in entry:
                    if key not in HOOK_ENTRY_KEYS:
                        errors.append(
                            f"{rp}: hook command has unsupported field '{key}' "
                            f"(allowed: {', '.join(sorted(HOOK_ENTRY_KEYS))})"
                        )
                if entry.get("type") != "command":
                    errors.append(f"{rp}: hooks.{event}[].hooks[].type must be 'command'")
                if not isinstance(entry.get("command"), str) or not entry.get("command"):
                    errors.append(f"{rp}: hooks.{event}[].hooks[] missing a 'command' string")


def check_json(root, path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            json.load(fh)
    except (json.JSONDecodeError, ValueError) as exc:
        errors.append(f"{rel(root, path)}: invalid JSON: {exc}")
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main():
    root = repo_root()

    plugin_path = os.path.join(root, ".claude-plugin", "plugin.json")
    marketplace_path = os.path.join(root, ".claude-plugin", "marketplace.json")

    for path in walk_files(root):
        base = os.path.basename(path)

        if base.lower() == "readme.md":
            if f"{os.sep}commands{os.sep}" in path:
                errors.append(
                    f"{rel(root, path)}: every *.md in commands/ becomes a slash command, "
                    "so this README would register as /README - move the guide elsewhere"
                )
            continue

        if path.endswith(".json"):
            data = check_json(root, path)
            if data is None:
                continue
            if os.path.abspath(path) == os.path.abspath(plugin_path):
                if "name" not in data:
                    errors.append("plugin.json: missing required field 'name'")
            if os.path.abspath(path) == os.path.abspath(marketplace_path):
                for field in ("name", "owner", "plugins"):
                    if field not in data:
                        errors.append(
                            f"marketplace.json: missing required field '{field}'"
                        )
            if base in ("settings.json", "settings.local.json") and isinstance(data, dict):
                check_hooks(root, path, data)

        elif base == "SKILL.md":
            with open(path, "r", encoding="utf-8") as fh:
                fm = parse_frontmatter(fh.read())
            if not fm or not fm.get("description"):
                errors.append(
                    f"{rel(root, path)}: SKILL.md must have a 'description' in frontmatter"
                )

        elif path.endswith(".md") and (
            f"{os.sep}commands{os.sep}" in path or f"{os.sep}agents{os.sep}" in path
        ):
            with open(path, "r", encoding="utf-8") as fh:
                fm = parse_frontmatter(fh.read())
            if fm is None:
                warnings.append(
                    f"{rel(root, path)}: no frontmatter found (scaffold ok, but add one for a real component)"
                )

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")

    print()
    print(f"{len(errors)} error(s), {len(warnings)} warning(s)")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

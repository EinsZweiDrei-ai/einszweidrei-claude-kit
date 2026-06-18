#!/usr/bin/env python3
"""install.py — copy the EinsZweiDrei Claude Kit template into a project.

Cross-platform (Windows + Linux + macOS). Standard library only — no dependencies.

Usage:
    python install.py [TARGET_DIR] [--packs=a,b] [--force] [--no-verify]
    python install.py update [TARGET_DIR] [--no-verify]
    python install.py prune  [TARGET_DIR] --packs=a,b [--no-verify]

    TARGET_DIR    Directory to install into. Defaults to the current directory.
    --packs       Comma-separated stack packs to include (e.g. --packs=dotnet,frontend).
                  Core files (untagged) are always included; pack-tagged files (those
                  with a `pack:` frontmatter field) are included only when their pack is
                  listed. Omit to install everything — the full kit stays copy-paste-able.
    --force       Overwrite files that already exist (default: skip them). The
                  FORCE=1 environment variable is honored too, for parity with
                  install.sh.
    --no-verify   Skip the post-install self-audit (not recommended).

    update        Refresh the PORTABLE kit files (CLAUDE.md, rules, agents, commands,
                  scripts, hooks, skills, settings) to this kit version WITHOUT
                  touching project state — .claude/project/** (context.md, tech-debt.md)
                  and .claude/settings.local.json are preserved. The existing
                  .claude/settings.json is backed up to settings.json.bak before it is
                  refreshed, so any custom permissions can be re-merged.

    prune         Remove pack-tagged files NOT in --packs from an already-installed repo,
                  and record the selection so `update` keeps them out. /kit-init runs this
                  after detecting the stack.

These commands stamp the kit version into .claude/.kit-version and then run the kit's
own audit against the result, failing loudly (non-zero exit) if it does not PASS — so
it is impossible to leave behind an artifact that fails the kit's own audit.

Non-destructive by default: an install skips existing files unless --force/FORCE=1.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys

# Personal, per-developer config that must never be distributed into a target
# project — it is gitignored in this repo for the same reason.
SKIP_SUFFIXES = ("settings.local.json",)

# On `update`, these are the per-repo project state — never overwrite them.
PRESERVE_ON_UPDATE_PREFIXES = (".claude/project/",)

# settings.json is portable but commonly carries team permission edits, so `update`
# backs it up before refreshing it.
SETTINGS_REL = os.path.join(".claude", "settings.json")

# Pack selection: a file's `pack:` frontmatter field (if any) names its stack pack.
# Untagged files are core and always installed. The chosen selection is recorded here.
KIT_PACKS_REL = os.path.join(".claude", ".kit-packs")
FRONTMATTER_PACK_RE = re.compile(r"^\s*pack:\s*(\S+)\s*$")


def parse_args(argv):
    parser = argparse.ArgumentParser(
        prog="install.py",
        description="Copy or update the EinsZweiDrei Claude Kit template in a project.",
    )
    parser.add_argument(
        "target_dir",
        nargs="?",
        default=".",
        help="Directory to install into (default: current directory).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        default=os.environ.get("FORCE") == "1",
        help="Overwrite files that already exist (default: skip them).",
    )
    parser.add_argument(
        "--packs",
        default=None,
        help="Comma-separated stack packs to include (e.g. --packs=dotnet,frontend). "
        "Core (untagged) files are always included; omit to install everything.",
    )
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="Skip the post-install self-audit (not recommended).",
    )
    return parser.parse_args(argv)


def kit_version(script_dir):
    """The kit version — single source of truth is .claude-plugin/plugin.json."""
    path = os.path.join(script_dir, ".claude-plugin", "plugin.json")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            value = json.load(fh).get("version")
        if isinstance(value, str) and value.strip():
            return value.strip()
    except (OSError, ValueError):
        pass
    return "0.0.0"


def read_installed_version(target_dir):
    path = os.path.join(target_dir, ".claude", ".kit-version")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return None


def stamp_version(target_dir, version):
    path = os.path.join(target_dir, ".claude", ".kit-version")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(version + "\n")
    print(f"  stamped .claude/.kit-version = {version}")


def file_pack(path):
    """The `pack:` frontmatter value for a file, or None (= core, always installed).

    Only the leading `---`-fenced block is inspected; non-.md or untagged files are core.
    Never raises — selection must not crash the installer.
    """
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            if fh.readline().strip() != "---":
                return None
            for line in fh:
                if line.strip() == "---":
                    break
                m = FRONTMATTER_PACK_RE.match(line)
                if m:
                    return m.group(1)
    except OSError:
        pass
    return None


def parse_packs(value):
    """Parse a --packs value (comma/space separated) into a set, or None if empty."""
    if not value:
        return None
    packs = {p.strip() for p in value.replace(",", " ").split() if p.strip()}
    return packs or None


def read_installed_packs(target_dir):
    """The recorded pack selection, or None for a full install (= all packs)."""
    try:
        with open(os.path.join(target_dir, KIT_PACKS_REL), "r", encoding="utf-8") as fh:
            content = fh.read().strip()
    except OSError:
        return None
    if not content or content == "all":
        return None
    return {p.strip() for p in content.replace(",", " ").split() if p.strip()}


def write_installed_packs(target_dir, packs):
    """Record the selection (or 'all' for a full install) in .claude/.kit-packs."""
    path = os.path.join(target_dir, KIT_PACKS_REL)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    value = "all" if packs is None else " ".join(sorted(packs))
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(value + "\n")
    print(f"  stamped .claude/.kit-packs = {value}")


def iter_template(src_dir):
    """Yield (src, rel, rel_display) for every template file, deterministically.

    Skips __pycache__ bytecode entirely — the kit forbids committing build artifacts,
    so it must never ship them either.
    """
    for dirpath, dirnames, filenames in os.walk(src_dir):
        dirnames.sort()
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for name in sorted(filenames):
            if name.endswith((".pyc", ".pyo")):
                continue
            src = os.path.join(dirpath, name)
            rel = os.path.relpath(src, src_dir)
            yield src, rel, rel.replace(os.sep, "/")


def run_self_audit(target_dir):
    """Run the just-installed audit against target_dir. Returns its exit code."""
    audit = os.path.join(target_dir, ".claude", "scripts", "claude-audit.py")
    if not os.path.isfile(audit):
        print("error: post-install audit script missing; cannot self-validate.", file=sys.stderr)
        return 1
    print()
    print("Self-check: running claude-audit.py on the installed kit...")
    # Flush so our buffered stdout lands before the child writes its report (matters
    # when stdout is a pipe, e.g. CI logs).
    sys.stdout.flush()
    # Pass target_dir explicitly so the audit never escapes to a parent git root.
    return subprocess.run([sys.executable, audit, target_dir]).returncode


def _finish_with_audit(target_dir, version, args, verb):
    """Stamp the version, then self-audit unless --no-verify. Returns an exit code."""
    stamp_version(target_dir, version)
    if args.no_verify:
        print("Skipped self-check (--no-verify). Run /claude-audit before committing.")
        return 0
    rc = run_self_audit(target_dir)
    if rc != 0:
        print()
        print(
            f"FAILED: the {verb} kit did not pass its own audit (see report above).",
            file=sys.stderr,
        )
        print(
            "This is a packaging bug. Nothing was rolled back; re-run after fixing.",
            file=sys.stderr,
        )
        return rc
    print(f"Self-check: PASS - the {verb} kit is consistent.")
    return 0


def print_next_steps():
    print()
    print("Next steps:")
    print("  1. Run /kit-init in Claude Code - it inspects this repo and writes")
    print("     .claude/project/context.md, then wires the git pre-commit audit hook.")
    print("  2. (optional) Put personal, per-developer permissions in")
    print("     .claude/settings.local.json (never committed).")


def do_install(args, src_dir, version):
    os.makedirs(args.target_dir, exist_ok=True)
    target_dir = os.path.abspath(args.target_dir)
    selected = parse_packs(args.packs)

    print("Installing EinsZweiDrei Claude Kit")
    print(f"  from: {src_dir}")
    print(f"  into: {target_dir}")
    print(
        "  mode: FORCE (overwriting existing files)"
        if args.force
        else "  mode: non-destructive (skipping existing files)"
    )
    if selected is not None:
        print(f"  packs: core + {', '.join(sorted(selected))}")
    print()

    wrote = 0
    skipped = 0
    for src, rel, rel_display in iter_template(src_dir):
        dest = os.path.join(target_dir, rel)

        if rel_display.endswith(SKIP_SUFFIXES):
            print(f"  skip   {rel_display} (personal config, never distributed)")
            continue
        pack = file_pack(src)
        if selected is not None and pack is not None and pack not in selected:
            print(f"  skip   {rel_display} (pack '{pack}' not selected)")
            continue
        if os.path.exists(dest) and not args.force:
            print(f"  skip   {rel_display} (exists)")
            skipped += 1
            continue

        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(src, dest)
        print(f"  write  {rel_display}")
        wrote += 1

    print()
    print(f"Done. {wrote} written, {skipped} skipped.")
    write_installed_packs(target_dir, selected)
    rc = _finish_with_audit(target_dir, version, args, "installed")
    if rc == 0:
        print_next_steps()
    return rc


def do_update(args, src_dir, version):
    target_dir = os.path.abspath(args.target_dir)
    if not os.path.isdir(os.path.join(target_dir, ".claude")):
        print(
            f"error: no .claude/ found in {target_dir}; run an install first.",
            file=sys.stderr,
        )
        return 1

    previous = read_installed_version(target_dir)
    selected = read_installed_packs(target_dir)
    print("Updating EinsZweiDrei Claude Kit")
    print(f"  from: {src_dir}")
    print(f"  into: {target_dir}")
    print(f"  version: {previous or 'unknown'} -> {version}")
    print("  preserving: .claude/project/**, .claude/settings.local.json")
    if selected is not None:
        print(f"  packs: core + {', '.join(sorted(selected))} (pruned packs stay out)")
    print()

    refreshed = 0
    preserved = 0
    for src, rel, rel_display in iter_template(src_dir):
        if rel_display.endswith(SKIP_SUFFIXES):
            continue  # never distribute personal config
        if rel_display.startswith(PRESERVE_ON_UPDATE_PREFIXES):
            print(f"  keep   {rel_display} (project-specific)")
            preserved += 1
            continue
        pack = file_pack(src)
        if selected is not None and pack is not None and pack not in selected:
            continue  # pruned pack — don't re-add it

        dest = os.path.join(target_dir, rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        # Back up settings.json before refreshing so custom permissions aren't lost.
        if rel == SETTINGS_REL and os.path.exists(dest):
            shutil.copy2(dest, dest + ".bak")
            print(f"  backup {rel_display} -> {rel_display}.bak (re-merge custom permissions)")
        shutil.copy2(src, dest)
        print(f"  write  {rel_display}")
        refreshed += 1

    print()
    print(f"Done. {refreshed} refreshed, {preserved} preserved.")
    return _finish_with_audit(target_dir, version, args, "updated")


def do_prune(args, version):
    target_dir = os.path.abspath(args.target_dir)
    claude_dir = os.path.join(target_dir, ".claude")
    if not os.path.isdir(claude_dir):
        print(f"error: no .claude/ found in {target_dir}; run an install first.", file=sys.stderr)
        return 1
    selected = parse_packs(args.packs)
    if selected is None:
        print("error: prune requires --packs (e.g. --packs=dotnet,frontend).", file=sys.stderr)
        return 1

    print("Pruning EinsZweiDrei Claude Kit packs")
    print(f"  in:   {target_dir}")
    print(f"  keep: core + {', '.join(sorted(selected))}")
    print()

    removed = 0
    for dirpath, dirnames, filenames in os.walk(claude_dir):
        dirnames.sort()
        for name in sorted(filenames):
            if not name.endswith(".md"):
                continue
            path = os.path.join(dirpath, name)
            pack = file_pack(path)
            if pack is not None and pack not in selected:
                os.remove(path)
                print(f"  remove {os.path.relpath(path, target_dir).replace(os.sep, '/')} (pack '{pack}')")
                removed += 1

    print()
    print(f"Done. {removed} pack file(s) removed.")
    write_installed_packs(target_dir, selected)
    return _finish_with_audit(target_dir, version, args, "pruned")


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    command = "install"
    if argv and argv[0] in ("install", "update", "prune"):
        command = argv.pop(0)
    args = parse_args(argv)

    # Resolve paths relative to this script so it works from any CWD.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(script_dir, "template")
    if not os.path.isdir(src_dir):
        print(f"error: template directory not found at {src_dir}", file=sys.stderr)
        return 1
    version = kit_version(script_dir)

    if command == "update":
        return do_update(args, src_dir, version)
    if command == "prune":
        return do_prune(args, version)
    return do_install(args, src_dir, version)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Tests for the kit's commit review gate, installer, and validator. Standard library only.

Each test installs the kit into a throwaway git repo under the system temp dir and drives
the installed scripts the way Claude Code and git do.

Usage:
    python3 scripts/test_kit.py
"""

import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest

KIT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INSTALL = os.path.join(KIT, "install.py")
VALIDATE = os.path.join(KIT, "scripts", "validate.py")
AUDIT_REL = os.path.join(".claude", "scripts", "claude-audit.py")
LAUNCHER_REL = os.path.join(".claude", "hooks", "pre-commit-audit.sh")


def run(args, cwd=None, stdin=None):
    return subprocess.run(
        args, cwd=cwd, input=stdin, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )


def git(cwd, *args):
    out = run(["git"] + list(args), cwd=cwd)
    if out.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {out.stderr}")
    return out


def init_repo(path):
    os.makedirs(path, exist_ok=True)
    git(path, "init", "-q")
    git(path, "config", "user.email", "test@example.com")
    git(path, "config", "user.name", "Kit Test")
    git(path, "config", "commit.gpgsign", "false")
    # Keep any global core.hooksPath from firing inside the throwaway repo.
    git(path, "config", "core.hooksPath", os.path.join(path, ".no-hooks"))


def write(path, text="x\n"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def install(target, *extra):
    out = run([sys.executable, INSTALL, target] + list(extra))
    if out.returncode != 0:
        raise AssertionError(f"install.py {' '.join(extra)} failed:\n{out.stdout}\n{out.stderr}")
    return out


def _force_remove(func, path, _exc):
    os.chmod(path, stat.S_IWRITE)  # git marks object files read-only on Windows
    func(path)


class TempDirTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="kit-test-")

    def tearDown(self):
        shutil.rmtree(self.tmp, onerror=_force_remove)


class ReviewGateTest(TempDirTest):
    def setUp(self):
        super().setUp()
        self.repo = os.path.join(self.tmp, "proj")
        init_repo(self.repo)
        install(self.repo, "--no-verify")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "chore: install kit")

    def hook(self, command, tool="Bash"):
        """Run the gate as the PreToolUse hook would; return (exit code, stderr)."""
        payload = json.dumps({"tool_name": tool, "tool_input": {"command": command}})
        out = run([sys.executable, AUDIT_REL, "--hook"], cwd=self.repo, stdin=payload)
        return out.returncode, out.stderr

    def assertGate(self, command, expected, tool="Bash"):
        code, err = self.hook(command, tool)
        self.assertEqual(code, expected, f"{command!r} -> {code}; stderr:\n{err}")

    def test_non_commit_commands_pass(self):
        write(os.path.join(self.repo, "src", "App.cs"))
        self.assertGate("git status", 0)
        self.assertGate("git log --grep commit", 0)

    def test_unreviewed_source_blocks_until_review_recorded(self):
        write(os.path.join(self.repo, "src", "App.cs"))
        self.assertGate('git commit -am "feat: add app"', 2)
        self.assertGate("git commit -m @'\nfeat: add app\n'@", 2, tool="PowerShell")
        run([sys.executable, AUDIT_REL, "--record-review"], cwd=self.repo)
        self.assertGate('git commit -am "feat: add app"', 0)

    def test_skip_review_applies_to_one_commit_only(self):
        write(os.path.join(self.repo, "src", "A.cs"))
        self.assertGate('git commit -am "fix: typo [skip-review]"', 0)
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "fix: typo [skip-review]")
        # COMMIT_EDITMSG now holds the [skip-review] message; it must not carry over.
        write(os.path.join(self.repo, "src", "B.cs"))
        git(self.repo, "add", "-A")  # staged, so only the skip logic is under test
        self.assertGate('git commit -m "feat: next"', 2)

    def test_assets_and_review_ignore_skip_the_gate(self):
        write(os.path.join(self.repo, "img", "hero.webp"))
        write(os.path.join(self.repo, "fonts", "a.woff2"))
        self.assertGate('git commit -am "chore: assets"', 0)
        write(os.path.join(self.repo, "mockups", "page.html"))
        self.assertGate('git commit -am "docs: mockup"', 2)
        write(os.path.join(self.repo, ".claude", "project", "review-ignore"), "# mockups\nmockups/\n")
        self.assertGate('git commit -am "docs: mockup"', 0)

    def test_hook_matcher_covers_bash_and_powershell(self):
        with open(os.path.join(self.repo, ".claude", "settings.json"), encoding="utf-8") as fh:
            groups = json.load(fh)["hooks"]["PreToolUse"]
        matchers = [
            g["matcher"] for g in groups
            if any("pre-commit-audit.sh" in h.get("command", "") for h in g["hooks"])
        ]
        self.assertEqual(len(matchers), 1)
        for tool in ("Bash", "PowerShell"):
            self.assertTrue(re.fullmatch(matchers[0], tool), f"matcher misses {tool}")

    def test_launcher_allows_repo_without_kit(self):
        shell = shutil.which("sh") or shutil.which("bash")
        if not shell:
            self.skipTest("no POSIX shell on PATH")
        other = os.path.join(self.tmp, "other")
        init_repo(other)
        write(os.path.join(other, "src", "App.cs"))
        payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": "git commit -am x"}})
        launcher = os.path.join(self.repo, LAUNCHER_REL)
        out = run([shell, launcher], cwd=other, stdin=payload)
        self.assertEqual(out.returncode, 0, out.stderr)


class InstallerTest(TempDirTest):
    def test_install_skips_excluded_files(self):
        target = os.path.join(self.tmp, "proj")
        write(os.path.join(target, ".claude", ".kit-exclude"), "# opt-outs\n.claude/agents/infra/azure-*.md\n")
        install(target)
        agents = os.path.join(target, ".claude", "agents", "infra")
        self.assertFalse(os.path.exists(os.path.join(agents, "azure-infra-engineer.md")))
        self.assertTrue(os.path.exists(os.path.join(agents, "docker-expert.md")))

    def test_update_removes_obsolete_files_and_keeps_exclusions(self):
        target = os.path.join(self.tmp, "proj")
        install(target)
        # Simulate an install from a kit version that still shipped commands/README.md,
        # plus a core agent the project deleted and opted out of.
        obsolete = os.path.join(target, ".claude", "commands", "README.md")
        write(obsolete, "# Slash commands\n")
        sql_pro = os.path.join(target, ".claude", "agents", "backend", "sql-pro.md")
        os.remove(sql_pro)
        write(os.path.join(target, ".claude", ".kit-exclude"), ".claude/agents/backend/sql-pro.md\n")
        out = run([sys.executable, INSTALL, "update", target])
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertFalse(os.path.exists(obsolete), "update left commands/README.md behind")
        self.assertFalse(os.path.exists(sql_pro), "update re-added an excluded agent")


class ValidatorTest(TempDirTest):
    def test_readme_in_commands_is_an_error(self):
        write(os.path.join(self.tmp, "commands", "README.md"), "# guide\n")
        out = run([sys.executable, VALIDATE, self.tmp])
        self.assertEqual(out.returncode, 1, out.stdout)
        self.assertIn("/README", out.stdout)

    def test_kit_repo_is_valid(self):
        out = run([sys.executable, VALIDATE, KIT])
        self.assertEqual(out.returncode, 0, out.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)

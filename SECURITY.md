# Security Policy

## Supported Versions

Only the **latest released version** of this kit receives security fixes.
Pin to a specific git tag or GitHub release rather than tracking a moving branch
so you know exactly which version you are running.

## Reporting a Vulnerability

Please report security vulnerabilities **privately** — do not open a public
issue.

1. Use GitHub's private vulnerability reporting: open the repository's
   **Security** tab and click **Report a vulnerability**.
2. Alternatively, email hallo@einszweidrei.ai.

We will acknowledge your report as soon as possible and work with you on a
coordinated disclosure timeline.

## Trust and Review Before Use

This developer kit ships **commands, agents, skills, shell scripts, and a Git
hook that Claude Code (or your shell) executes on your machine**. Treat every
component like source code you would run locally:

- **Review** the contents before installing or enabling them in a project —
  especially the things that run automatically: `template/.claude/scripts/`
  (e.g. `claude-audit.sh`) and `template/.claude/hooks/` (the pre-commit hook
  wired up in `settings.json`), alongside `commands/`, `agents/`, and `skills/`.
- **Pin** to a specific git tag or release so you can audit exactly what you
  install instead of silently picking up changes from a branch.
- **Customize** permissions in `template/.claude/settings.json` (or your
  project copy) to match your security posture.

If you discover a vulnerability in this repository, please report it using the
process above.

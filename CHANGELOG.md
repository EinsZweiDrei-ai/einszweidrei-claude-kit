# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Pinned an explicit `model` to every subagent (quality-first): all application-code
  agents (backend, frontend) and the reasoning-heavy reviewers/analysts
  (`architect-reviewer`, `code-reviewer`, `security-auditor`, `security-engineer`,
  `performance-engineer`, `debugger`) run on `opus`; infra, test-automation, and
  documentation agents run on `sonnet`.

## [0.1.0] - 2026-06-17

### Added

- Initial release of the EinsZweiDrei Claude Kit.
- Hybrid distribution: plugin + marketplace manifests under `.claude-plugin/`,
  both pointing at `template/.claude/` as a single source of truth.
- `template/CLAUDE.md` engineering-standards guide (SOLID, KISS/DRY/YAGNI,
  security and testing fundamentals, quality gates).
- Subagent roster under `template/.claude/agents/` (backend, frontend, infra,
  quality), plus a format-guide README.
- Stack rules under `template/.claude/rules/` that auto-apply by file type
  (.NET, controllers, repositories, services, frontend, testing) plus always-on
  `code-review.md` and `security.md`.
- Per-repo project instance scaffold under `template/.claude/project/`
  (`context.md` profile + `tech-debt.md` register placeholders).
- `/claude-audit` command + `scripts/claude-audit.sh` consistency audit and a
  `pre-commit-audit.sh` hook that blocks commits on structural failures.
- `template/.claude/settings.json` (shared permissions + commit-audit hook) and
  `workflow.md` working-loop / agent-routing guide.
- `install.sh` copy-in installer (non-destructive unless `FORCE=1`; never copies
  personal `settings.local.json`).
- `scripts/validate.py` dependency-free validator.
- Project docs: README, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY.
- GitHub issue/PR templates and a CI workflow.

### Fixed

- Audit no longer fails a freshly-copied kit: `project/` links are tolerated until
  the per-repo instance exists, and README format-guides are excluded from the
  agent/rule frontmatter checks.

[Unreleased]: https://github.com/EinsZweiDrei-ai/einszweidrei-claude-kit/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/EinsZweiDrei-ai/einszweidrei-claude-kit/releases/tag/v0.1.0

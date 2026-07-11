# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **`ponytail` skill (first shipped skill).** Vendored the "lazy senior dev" minimalism skill —
  a YAGNI → stdlib → platform → existing-dep → one-line → minimal-code ladder with `lite/full/ultra`
  intensity levels, and explicit "never lazy about" guardrails (input validation, error handling,
  security, accessibility). Ships as **core** (always installed) via both the plugin and the
  copy-in installer. From [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)
  (MIT), pinned at v4.8.4; attribution in `template/.claude/skills/ponytail/NOTICE`.
- **`nodejs` stack pack.** New `nodejs-developer` agent (`pack: nodejs`) for server-side
  Node.js + TypeScript — APIs/services (Express/Fastify/NestJS/Hono), CLIs, and libraries:
  strict typing, async correctness, error handling, ESM/CJS packaging, and testing. `/kit-init`
  now detects a server-side `package.json` and keeps the `nodejs` pack (a full-stack repo can
  keep `frontend` + `nodejs`); `install.py --packs=nodejs` installs it on its own.

## [0.9.0] - 2026-06-18

### Added

- **Project memory log.** New `.claude/project/decisions.md` — a committed, team-shared
  decisions & learnings log that completes the project-state trio (state / debt / decisions).
  Agents record durable choices, gotchas, and adopted conventions there; `workflow.md` says
  when to write it, `/kit-init` ships it ready, and `install.py update` preserves it (it lives
  under `.claude/project/`). Personal / cross-project facts stay in Claude Code's own memory.

## [0.8.0] - 2026-06-18

### Added

- **Stack packs (opt-in pruning).** Stack-specific rules and agents now carry a `pack:`
  frontmatter tag (`dotnet` / `frontend`); untagged files are core. `install.py --packs=…`
  installs core + the chosen packs, a new `install.py prune --packs=…` trims an existing
  install, and `/kit-init` auto-trims to the detected stack. The selection is recorded in
  `.claude/.kit-packs` and honored by `install.py update`. The full kit still installs by
  default, so a plain copy-paste of `template/.claude/` keeps working in any stack.

### Changed

- `code-reviewer` and `architect-reviewer` are now stack-neutral — they review against
  `CLAUDE.md` + whatever rules auto-apply from `.claude/rules/` + `context.md` rather than
  hardcoding .NET/EF Core, so they sharpen correctly on any stack.
- `code-review.md` no longer hard-links the stack rules, so a pruned install stays audit-clean.

## [0.7.0] - 2026-06-18

### Added

- **Enforced review loop.** The commit-time gate (`claude-audit.py`) now blocks **Claude's
  own commits** when source files changed since the last commit without a recorded
  code-review, and **warns (never blocks) human commits**. The `code-reviewer` and
  `architect-reviewer` agents record the review with `--record-review` (writing the
  gitignored `.claude/.last-review` = reviewed `HEAD`); `[skip-review]` in the commit message
  bypasses the gate for trivial edits, and docs/config-only commits never trigger it. No new
  hook events — it reuses the existing `PreToolUse(Bash)` / `pre-commit` audit path.

## [0.6.0] - 2026-06-18

### Changed

- **Standards are sharper and de-duplicated.** `code-review.md` is now the single source of
  truth for the blocking gate thresholds (complexity, method/class size, coverage); `CLAUDE.md`
  keeps the principles and links to them instead of restating the numbers (removes drift with
  `CLAUDE.md` and `services.md`).
- **Core gates de-coupled from .NET.** The universal "Docs synced" gate no longer hard-codes
  ASP.NET specifics (`[ProducesResponseType]`, XML docs) — those moved to the controllers
  rule; the core gate now names the stack's own doc convention (XML docs / JSDoc / docstrings).
- **Vague/bypassable gates made checkable** — "unless anonymity is justified", "no
  over-engineering", "thin controllers / no business logic", "only at proven hotspots", and
  "avoid `async void`" are now concrete, objectively reviewable rules.

### Added

- **New gates:** dependency approval (no new third-party dependency without a recorded
  reason), an explicit error-handling rule (no empty catch / rethrow-with-context), test
  determinism (no real clock/network/sleep/randomness), and API backward-compatibility
  (breaking changes versioned or flagged).
- Each layer/stack rule now cross-links the applicable gates in `code-review.md`.

## [0.5.0] - 2026-06-18

### Added

- **Commit conventions** — new always-on `rules/commits.md` standardizing Conventional
  Commits (`type(scope): summary`, `BREAKING CHANGE`/issue trailers) plus the imperative
  50/72 message style, referenced from `workflow.md`.

### Changed

- **`release-manager`** now maps commit types to changelog sections and the SemVer bump
  (`feat`→Added/minor, `fix`→Fixed/patch, `BREAKING CHANGE`→major), tying the release
  ritual to the new commit convention.

## [0.4.0] - 2026-06-18

### Added

- **Swagger/OpenAPI doc-sync standard** — the controllers rule and the code-review
  "Docs synced" gate now require the OpenAPI spec (XML docs, `[ProducesResponseType]`,
  request/response schemas) to stay in sync with every added, changed, or removed
  endpoint in projects that expose Swagger/OpenAPI.

## [0.3.0] - 2026-06-17

### Added

- **`/kit-init`** — one first-run command that inspects the target repo (stack,
  layout, key libraries, test setup), generates `.claude/project/context.md` (and
  removes its placeholder banner), wires the git pre-commit audit hook, and verifies.
  Collapses all per-project setup into a single step.
- **Self-validating install** — `install.py` now runs the kit's own audit against
  the freshly-installed files as its last step and exits non-zero on FAIL, so it is
  impossible to leave behind an artifact that fails the kit's own audit.
- **`install.py update`** — refreshes the portable kit files to a newer version
  while preserving project state: `.claude/project/**` (`context.md`, `tech-debt.md`)
  and `.claude/settings.local.json` are never touched, and `settings.json` is backed
  up to `settings.json.bak` before it is refreshed.
- **Kit versioning** — the installed version is stamped into `.claude/.kit-version`
  (single source of truth: `plugin.json`).
- **`.githooks/pre-commit`** — a real git pre-commit audit hook that gates *human*
  commits (the PreToolUse hook only sees commits Claude makes). Enabled via
  `git config core.hooksPath .githooks` (done automatically by `/kit-init`).
- **`session-start.sh`** — a toolchain-agnostic `SessionStart` bootstrap hook that
  runs a project setup script (`$KIT_SETUP_SCRIPT`, else `scripts/setup*.sh`) so
  cloud/web containers can install their toolchain on session start; safe no-op when
  no setup script exists.

### Changed

- Cross-platform installer and audit: ported `install.sh` and the bash
  `claude-audit.sh` to standard-library Python (`install.py`,
  `template/.claude/scripts/claude-audit.py`) so they run natively on Windows,
  Linux, and macOS with no Git Bash dependency. `install.sh` and
  `pre-commit-audit.sh` are now thin POSIX launchers that forward to the Python
  scripts (single source of truth). CI now runs the validator and installer on
  both `ubuntu-latest` and `windows-latest`.
- The curated agent roster is now the supported set — the README no longer tells
  consumers to prune it; updates keep every repo's kit identical.
- CI now also runs the kit's own audit against the installed copy and validates the
  `settings.json` hooks block against the Claude Code hook schema (rejecting
  unsupported per-hook fields such as `if:`).
- `install.py` no longer copies `__pycache__`/`*.pyc` bytecode into targets.

### Fixed

- **Audit hook fired on every Bash call.** `settings.json` gated the PreToolUse
  hook with an unsupported `if: "Bash(git commit*)"` field, which Claude Code
  silently ignores (matchers filter on the tool NAME only). The git-commit gate now
  lives in `claude-audit.py --hook`, which reads the PreToolUse stdin payload and
  runs the audit only on an actual `git commit` — and no longer blocks unrelated
  Bash calls (e.g. when Python is unavailable).

### Removed

- `template/.claude/scripts/claude-audit.sh` (replaced by `claude-audit.py`).

## [0.2.0] - 2026-06-17

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

[Unreleased]: https://github.com/EinsZweiDrei-ai/einszweidrei-claude-kit/compare/v0.9.0...HEAD
[0.9.0]: https://github.com/EinsZweiDrei-ai/einszweidrei-claude-kit/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/EinsZweiDrei-ai/einszweidrei-claude-kit/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/EinsZweiDrei-ai/einszweidrei-claude-kit/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/EinsZweiDrei-ai/einszweidrei-claude-kit/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/EinsZweiDrei-ai/einszweidrei-claude-kit/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/EinsZweiDrei-ai/einszweidrei-claude-kit/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/EinsZweiDrei-ai/einszweidrei-claude-kit/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/EinsZweiDrei-ai/einszweidrei-claude-kit/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/EinsZweiDrei-ai/einszweidrei-claude-kit/releases/tag/v0.1.0

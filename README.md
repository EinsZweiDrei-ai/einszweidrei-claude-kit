# einszweidrei-claude-kit

> A reusable Claude Code developer kit — an opinionated `CLAUDE.md`, subagents,
> slash commands, skills, and settings you can drop into any project, and improve
> together.

Published by [EinsZweiDrei.ai](https://einszweidrei.ai) under the MIT license.

The kit ships **two ways**, because Claude Code's plugin system distributes
commands, agents, and skills — but it **cannot** inject a project-owned `CLAUDE.md`
or `.claude/settings.json` into your repo. So:

- Use the **plugin** for versioned, auto-updatable commands / agents / skills.
- Use the **copy-in installer** to drop `CLAUDE.md` and `.claude/settings.json`
  (and, if you prefer, everything else) directly into your project.

You can use either or both.

## What's inside

| Component          | Location                                  | What it is                                                                      |
| ------------------ | ----------------------------------------- | ------------------------------------------------------------------------------- |
| `CLAUDE.md`        | `template/CLAUDE.md`                       | Stack-agnostic engineering standards — SOLID, KISS/DRY/YAGNI, security, testing, quality gates. |
| Settings           | `template/.claude/settings.json`          | Shared permissions + a commit-audit hook and a session-start bootstrap hook.     |
| Workflow           | `template/.claude/workflow.md`            | The working loop (plan → implement → review → done) and task→agent routing.     |
| Subagents          | `template/.claude/agents/`                | A **curated** ~21 specialist agents in `backend/`, `frontend/`, `infra/`, `quality/`. Stack-specific ones carry a `pack:` tag (`dotnet`/`frontend`) so an install can be trimmed; the rest are core. |
| Stack rules        | `template/.claude/rules/`                  | File-type rules that auto-apply by path. **Core:** always-on `code-review.md`, `commits.md`, `security.md`. **Pack-tagged:** `dotnet` (dotnet/controllers/repositories/services/testing) and `frontend`. |
| Slash commands     | `template/.claude/commands/`              | `*.md` commands (`/claude-audit`, `/kit-init`); format guide in the README there. |
| Audit tooling      | `template/.claude/scripts/` + `hooks/` + `.githooks/` | `claude-audit.py` consistency check, the `pre-commit-audit.sh` PreToolUse launcher, the `session-start.sh` bootstrap, and a `.githooks/pre-commit` for human commits. |
| Project instance   | `template/.claude/project/`               | Per-repo `context.md` profile, `tech-debt.md` register, and `decisions.md` memory log — committed project state (placeholders to fill). |
| Skills             | `template/.claude/skills/`                | `<name>/SKILL.md` skills. Ships **`ponytail`** — "lazy senior dev" minimalism (YAGNI, stdlib-first, `lite/full/ultra` levels), vendored from [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) (MIT). Format guide in the README there. |

Everything lives under `template/.claude/` as a **single source of truth** — the
plugin manifests point at it, and the installer copies from it.

## Usage

### Option 1 — Install as a plugin

Add this repo as a marketplace, then install the plugin:

```
/plugin marketplace add EinsZweiDrei-ai/einszweidrei-claude-kit
/plugin install ezd-claude-kit@einszweidrei-ai
```

Plugin commands are namespaced — invoke them as `/ezd-claude-kit:<name>`. The plugin
delivers commands, agents, and skills, and stays updatable.

> Note: the plugin distributes only **commands, agents, and skills**. Project-owned
> and copy-in-only content — `CLAUDE.md`, `.claude/settings.json`, and the kit's
> `rules/`, `hooks/`, and `scripts/` (the consistency audit + pre-commit hook) — is
> **not** delivered by the plugin. Use Option 2 to get those.

### Option 2 — Copy into your project

Clone the repo and run the installer against your project directory. The installer
is **Python 3, standard-library only** — no dependencies — and runs the same on
Windows, Linux, and macOS:

```sh
git clone https://github.com/EinsZweiDrei-ai/einszweidrei-claude-kit.git
cd einszweidrei-claude-kit
python install.py /path/to/your/project
```

On Linux/macOS you can also use the `./install.sh` shim (it just forwards to
`install.py`):

```sh
./install.sh /path/to/your/project
```

The installer **self-validates**: its last step runs the kit's own audit against the
freshly-installed files and exits non-zero if anything fails — so you can't end up with a
broken kit. It also stamps the kit version into `.claude/.kit-version`.

After installing, run **`/kit-init`** in Claude Code once. It inspects your repo, writes
`.claude/project/context.md` from what it finds, **trims the kit to your stack's packs**, and
enables the git pre-commit audit hook (`git config core.hooksPath .githooks`) so human commits
are gated too.

The installer is non-destructive: it skips files that already exist. To overwrite,
pass `--force` (or set `FORCE=1`):

```sh
python install.py /path/to/your/project --force
```

### Lean, stack-specific installs (packs)

By default the installer copies the **full kit** — so a plain copy-paste of `template/.claude/`
also works in any project (pack rules self-scope by file type, and agents are inert until
invoked). To install only what a stack needs, pass `--packs`:

```sh
python install.py /path/to/your/project --packs=dotnet     # packs: dotnet, frontend, nodejs (combine: dotnet,nodejs)
```

Core files are always included; pack-tagged files (those with a `pack:` frontmatter field) are
included only when their pack is listed. The selection is recorded in `.claude/.kit-packs`, and
`update` honors it. You can also trim an existing full install — `python install.py prune
/path/to/your/project --packs=frontend` — or just run **`/kit-init`**, which detects the stack
and trims to the matching pack(s) for you.

### Updating an installed kit

To pull a newer kit version into a project **without touching your project state**:

```sh
python install.py update /path/to/your/project
```

`update` refreshes the portable files (CLAUDE.md, rules, agents, commands, scripts, hooks,
settings) and **preserves** `.claude/project/**` (your `context.md` + `tech-debt.md`) and
`.claude/settings.local.json`. It backs up `.claude/settings.json` to `settings.json.bak`
before refreshing it, so you can re-merge any custom permissions. Like install, it
self-validates and re-stamps `.claude/.kit-version`.

With no argument either command operates on the current directory. Copy-in commands are
invoked as `/<name>` (no namespace).

## Repository layout

```
einszweidrei-claude-kit/
├── .claude-plugin/
│   ├── plugin.json          # reads content from template/.claude/*
│   └── marketplace.json     # one plugin, "source": "./"
├── template/                # single source of truth (the open-sourced kit)
│   ├── CLAUDE.md            # engineering standards (stays at repo root when copied)
│   ├── .githooks/           # git pre-commit audit hook (for human commits)
│   └── .claude/
│       ├── README.md        # explains the .claude/ layout
│       ├── workflow.md      # working loop + agent routing
│       ├── settings.json    # permissions + pre-commit & session-start hooks
│       ├── commands/        # *.md slash commands (/claude-audit, /kit-init) (+ format guide)
│       ├── agents/          # subagents in backend/ frontend/ infra/ quality/ (+ format guide)
│       ├── rules/           # stack rules that auto-apply by file type
│       ├── scripts/         # claude-audit.py consistency check
│       ├── hooks/           # pre-commit-audit.sh + session-start.sh launchers
│       ├── project/         # per-repo context.md + tech-debt.md (placeholders)
│       └── skills/          # <name>/SKILL.md (+ format guide)
├── install.py               # cross-platform installer + `update` (self-validating)
├── install.sh               # POSIX shim that forwards to install.py
├── scripts/validate.py      # no-dependency validator for CI
├── .gitattributes           # forces LF for scripts on every platform
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── LICENSE
└── .github/
```

## Contributing

Improvements are welcome — that's the whole point. See [CONTRIBUTING.md](CONTRIBUTING.md)
for where each component type lives, the frontmatter formats, and the PR workflow.

## Credits

The `ponytail` skill (`template/.claude/skills/ponytail/`) is vendored from
[DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) by Dietrich Gebert,
used under the MIT license — see the `NOTICE` beside it. Pinned at v4.8.4.

Prefer the full upstream suite (the additional `ponytail-audit` / `-debt` / `-gain` /
`-review` / `-help` skills, hooks, and always-on ruleset) or auto-updates? Install it as a
companion plugin instead:

```
/plugin marketplace add DietrichGebert/ponytail
/plugin install ponytail@ponytail
```

The plugin defines a skill of the same name as the vendored copy — use one or the other.

## License

MIT © EinsZweiDrei.ai — see [LICENSE](LICENSE).

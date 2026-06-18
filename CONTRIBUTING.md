# Contributing

Thanks for helping improve the EinsZweiDrei Claude Kit! This kit is meant to be
shared and improved by its users — corrections, new commands, agents, and skills
are all welcome.

## Where things live

Everything distributable lives under **`template/.claude/`** — a single source of
truth that both the plugin manifests and the copy-in installer read from. Add your
contribution in the matching directory:

| You're adding…   | Put it here                                            | Shape                                          |
| ---------------- | ------------------------------------------------------ | ---------------------------------------------- |
| A slash command  | `template/.claude/commands/<name>.md`                  | One `*.md` file with frontmatter.              |
| A subagent       | `template/.claude/agents/<area>/<name>.md`             | One `*.md` file with frontmatter; `<area>` is `backend`/`frontend`/`infra`/`quality` (organization only — identity comes from the `name` field). Add a `pack:` tag (`dotnet`/`frontend`) for stack-specific agents; omit it for core. |
| A stack rule     | `template/.claude/rules/<name>.md`                     | One `*.md` file with `description` (and optional `paths:` to scope by file type, plus an optional `pack:` tag like `dotnet`/`frontend` so it can be trimmed — omit `pack:` for core rules). |
| A skill          | `template/.claude/skills/<name>/SKILL.md`              | A directory containing `SKILL.md`.             |

Each component directory has a `README.md` with the full format guide and an example —
read it before adding files. See [`template/.claude/README.md`](template/.claude/README.md)
for how the whole `.claude/` layout fits together.

## Frontmatter formats (quick reference)

**Command** (`commands/<name>.md`):

```markdown
---
description: required — shown in the command picker
argument-hint: optional
allowed-tools: optional
model: optional
---
Body prompt. Use $ARGUMENTS / $1, !shell-cmd, and @file.
```

**Agent** (`agents/<area>/<name>.md`):

```markdown
---
name: required — unique across all agents
description: required — when to use this agent
tools: optional
model: optional
pack: optional — stack tag (e.g. dotnet/frontend) so the file can be trimmed; omit for core
---
> **Project precedence:** This project's CLAUDE.md is authoritative. If anything
> below conflicts with it, CLAUDE.md wins.

System prompt body.
```

> The kit's audit (`/claude-audit`) requires every agent to have a `name`, a
> `description`, and a **"Project precedence"** line — keep that line so the audit
> and the pre-commit hook stay green.

**Skill** (`skills/<name>/SKILL.md`):

```markdown
---
description: required — when Claude should use this skill
name: optional
allowed-tools: optional
disable-model-invocation: optional
---
Step-by-step instructions. May reference supporting files in the same dir.
```

## Validate locally

Before opening a PR, run the same checks CI runs:

```sh
python3 scripts/validate.py     # JSON parses; manifests & SKILL.md frontmatter valid
sh -n install.sh                # install.sh has no shell syntax errors
```

The validator treats missing command/agent frontmatter as a warning (so the empty
scaffold stays green) but a missing `SKILL.md` description is an error.

If you touched agents, rules, or `project/` docs, also exercise the kit's consistency
audit (the same one the pre-commit hook enforces in a copied-in repo). The audit
operates on an installed `.claude/` at the repo root, so run it against a scratch
copy of the template rather than the kit repo itself:

```sh
tmp=$(mktemp -d) && git -C "$tmp" init -q
cp template/CLAUDE.md "$tmp"/ && cp -r template/.claude "$tmp"/.claude
( cd "$tmp" && python .claude/scripts/claude-audit.py )
```

It checks broken links, agent/rule frontmatter, the "Project precedence" line, and
agent-name uniqueness. (Inside a real copied-in project you'd just run `/claude-audit`.)

If you change behavior or add a component, add an entry to `CHANGELOG.md` under
`## [Unreleased]`.

## PR workflow

1. Fork and create a branch (`feature/my-command`, `fix/agent-typo`, …).
2. Make your change under `template/.claude/`.
3. Run the local validation steps above.
4. Update `CHANGELOG.md` if relevant.
5. Open a PR using the template and fill in the "how I tested" checklist.

Be kind and constructive — see our [Code of Conduct](CODE_OF_CONDUCT.md).

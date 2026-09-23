<!--
  ┌─────────────────────────────────────────────────────────────────────┐
  │  PLACEHOLDER — REPLACE THIS FILE                                       │
  │                                                                       │
  │  This is the PROJECT-SPECIFIC profile for THIS repo. The portable     │
  │  kit (CLAUDE.md + .claude/rules + agents) defers all project          │
  │  specifics to this file.                                              │
  │                                                                       │
  │  On the first task in a freshly-copied repo, populate the sections    │
  │  below by inspecting the codebase — language, framework, folder       │
  │  layout, key libraries, test setup — then delete this banner.         │
  │                                                                       │
  │  This file IS committed in each repo (the team needs it) but is NOT   │
  │  carried to other repos — regenerate it per project.                  │
  └─────────────────────────────────────────────────────────────────────┘
-->

# Project context

> Read this before any project work. Everything stack-specific lives here so the
> portable kit stays generic.

## Stack — framework & runtime

[e.g. ASP.NET Core 8 Web API, .NET 8, C# 12 — or Node 20 / React 18 / Vue 3, etc.]

## Solution & folder layout

[The solution/workspace name and the layer/folder map. Name each project/folder and
its responsibility, e.g.:]

- `[Acme.Api]` — [HTTP edge: controllers, middleware, DI composition]
- `[Acme.Application]` — [services, use-cases, DTOs, mapping]
- `[Acme.Domain]` — [entities, value objects, domain rules]
- `[Acme.Infrastructure]` — [EF Core DbContext, repositories, external clients]
- `[tests/...]` — [test projects]

## Key libraries

[The libraries the project standardizes on — and the canonical helper for each
cross-cutting concern, so Claude reuses them instead of inventing new ones.]

- **Mapping:** [e.g. AutoMapper / Mapster / manual]
- **Validation:** [e.g. FluentValidation / DataAnnotations]
- **Logging:** [e.g. Serilog — structured, no PII/secrets]
- **Error handling:** [e.g. global exception-handling middleware → typed exceptions]
- **Data access:** [e.g. EF Core + IUnitOfWork; repositories own DbContext]
- **Testing:** [e.g. xUnit + FluentAssertions + Moq]

## Conventions & namespaces

[Root namespace, naming conventions, and anything that differs from the portable
defaults in CLAUDE.md / .claude/rules.]

- **Root namespace:** [e.g. `Acme.*`]
- **Naming:** [e.g. async methods end in `Async`; interfaces prefixed `I`]
- **[other]:** [...]

## Build & run

[The commands to build, test, lint, and run locally.]

- **Restore / build:** `[dotnet restore && dotnet build]`
- **Test:** `[dotnet test]`
- **Format / lint:** `[dotnet format]`
- **Run:** `[dotnet run --project Acme.Api]`

## Deliberate deviations from the kit

Permanent, intentional choices that differ from a portable rule (CLAUDE.md or
`.claude/rules/`). They override that rule in this repo, and reviewers don't report them.
Put the reasoning in [decisions.md](decisions.md). A violation you mean to fix later
belongs in [tech-debt.md](tech-debt.md) instead. Project-specific agent routing goes here
too, since `workflow.md` is refreshed on `install.py update`.

| Kit rule (file) | What this project does instead | Why |
| --------------- | ------------------------------ | --- |
| _(none yet)_ | | |

## Related project docs

- Tracked technical debt: [tech-debt.md](tech-debt.md)
- Decisions & learnings (project memory): [decisions.md](decisions.md)
- [Add ADRs, refactor plans, or other repo-specific docs here as they appear.]

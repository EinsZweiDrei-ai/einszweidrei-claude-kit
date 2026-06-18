---
description: Always-on code review checklist and quality gates (stack-agnostic)
---

# Code Review Checklist

Companion to [CLAUDE.md](../../CLAUDE.md). Reviewers and the `code-reviewer` /
`architect-reviewer` agents enforce this on every change. A PR is not approvable
while any **Gate** item fails.

> Universal gates are below. **Stack-specific gates** apply when editing that file type —
> .NET DB/async in [dotnet.md](dotnet.md), frontend a11y/security in [frontend.md](frontend.md).
> Project stack/helpers: [project/context.md](../project/context.md).

---

## 🚦 Gates (blocking)

- [ ] No new **Forbidden Anti-Pattern** (see CLAUDE.md): god class, magic strings, service locator, swallowed error, newing dependencies, dead/commented code.
- [ ] Cyclomatic complexity **< 10** per method.
- [ ] Method **≤ ~50 lines**; class/module **≤ ~500 lines** (new/changed types).
- [ ] Inputs validated; access secured (authn/authz) unless anonymity is justified.
- [ ] No secrets in code; no internal error detail leaked to clients.
- [ ] Changed core logic has tests; coverage **≥ 80%** on changed code.
- [ ] **Docs synced** with the change: public API/behavior changes have updated in-code docs (XML/docstrings); new or changed endpoints, config, env vars, or setup reflected in README/usage docs; user-facing changes have a changelog/release-notes entry (`release-manager`); when the project exposes Swagger/OpenAPI, the spec is current — annotations (`[ProducesResponseType]`, XML docs, request/response schemas) match every added, changed, or removed endpoint, with no stale or missing operations.
- [ ] **Structure & placement**: new/moved files are in the correct folder per `.claude/project/context.md`; dead files removed when their code is removed; no stray files at the repo root; no build artifacts/temp/`.bak` committed; folder & naming conventions followed.
- [ ] **Stack-specific gates pass** for the files touched (see the matching rule).

---

## ✅ SOLID

- [ ] **SRP** — class/module has one reason to change; no mixed responsibilities.
- [ ] **OCP** — extension via new types, not edits to existing branch ladders.
- [ ] **LSP** — implementations honor the full interface contract.
- [ ] **ISP** — interfaces are small and role-specific.
- [ ] **DIP** — depends on abstractions via DI; nothing `new`ed that should be injected.

## ✅ Design & OOP

- [ ] Reuses a well-known pattern rather than reinventing; no over-engineering.
- [ ] Composition preferred over inheritance.
- [ ] Encapsulation intact — no invariant-breaking public setters.
- [ ] Named constants/enums instead of magic values; no primitive obsession.

## ✅ KISS / DRY / YAGNI

- [ ] Simplest solution that meets the requirement; no speculative abstraction.
- [ ] No duplicated logic that should be shared.
- [ ] Nothing built "just in case."

## ✅ Cross-Cutting

- [ ] Validation, mapping, logging, and error handling use the project's configured stack ([project/context.md](../project/context.md)) — no ad-hoc substitutes.
- [ ] Structured logs only; no PII/secrets logged.
- [ ] Errors handled by the project's error-handling approach; nothing swallowed.

## ✅ Code Quality

- [ ] Meaningful names; small, focused functions; return early.
- [ ] Public APIs documented.
- [ ] No dead/commented-out code; no leftover `TODO` without a tracked item in [tech-debt.md](../project/tech-debt.md).
- [ ] One main type per file.

---

### Reviewer note
Findings must be **specific and actionable**: cite `file:line`, name the principle/anti-pattern, and give the concrete fix. Acknowledge good patterns too. Pre-existing violations touched by a PR should be fixed or added to [tech-debt.md](../project/tech-debt.md).

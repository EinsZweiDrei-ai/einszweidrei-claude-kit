---
description: Rust conventions, ownership, and error handling
pack: rust
paths:
  - "**/*.rs"
---

# Rust rules

Auto-applies when editing Rust. Extends [CLAUDE.md](../../CLAUDE.md). Use the project's edition, async runtime, and tooling (see [project/context.md](../project/context.md)); the `rust-developer` agent carries deeper guidance.

## Language & naming
- **`snake_case`** for functions/variables/modules, **`CamelCase`** for types/traits/enums, **`SCREAMING_SNAKE_CASE`** for consts/statics.
- Borrow over clone; take `&str`/`&[T]` in APIs rather than `String`/`Vec<T>`. Model domain with enums and newtypes, not primitives/booleans; `derive` standard traits instead of hand-rolling.

## Error handling & safety
- Fallible functions return `Result` and propagate with `?`. `thiserror` for libraries, `anyhow` (or the project's type) for apps. No `unwrap`/`expect`/`panic!` on reachable input — reserve for real invariants, with a message.
- No swallowed errors; preserve the source (`#[source]`/`#[from]`). Avoid `unsafe`; when unavoidable, isolate it behind a safe API and document the invariants with a `// SAFETY:` comment.

## Concurrency & async
- Use the project's runtime (usually `tokio`); keep `Send`/`Sync` bounds correct. Never block the async executor with sync I/O or heavy CPU (`spawn_blocking`/workers). Prefer channels or a deliberate `Arc<Mutex<_>>`; hold locks for the shortest scope.

## Quality
- Code passes **`cargo fmt`** and **`cargo clippy`** (warnings as errors) with no new warnings.
- Document public items with `///` doc comments.
- **Tests:** `cargo test` — unit `#[cfg(test)]` modules, integration tests under `tests/`, and doctests on public APIs; cover edge and failure paths.

Applicable gates: [code-review.md](code-review.md).

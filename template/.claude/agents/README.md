# Subagents

Each `*.md` file in this directory defines a subagent — a specialized assistant that
Claude Code can delegate focused tasks to, with its own system prompt and (optionally)
its own tool allowlist and model.

This README is a format guide and keepfile — drop your own `*.md` agents beside it.

## Frontmatter

```markdown
---
name: code-reviewer                                     # required — the agent's identifier
description: Reviews diffs for bugs and style issues.   # required — when to use this agent
tools: Read, Grep, Bash(git diff:*)                     # optional — restrict tools (defaults to all)
model: sonnet                                           # optional — override the model
effort: high                                            # optional — override the reasoning effort
---
```

| Field         | Required | Purpose                                                          |
| ------------- | -------- | ---------------------------------------------------------------- |
| `name`        | yes      | Unique identifier used to invoke/select the agent.              |
| `description` | yes      | Tells Claude when to delegate to this agent. Be specific.        |
| `tools`       | no       | Comma-separated tool allowlist. Omit to inherit all tools.       |
| `model`       | no       | `opus`, `sonnet`, `haiku`, `fable`, a full model ID, or `inherit`. Omit to use the session's model. |
| `effort`      | no       | `low`, `medium`, `high`, `xhigh`, or `max` (levels depend on the model). Overrides the session's effort; omit to inherit it. |

## Choosing a model

Use an **alias** (`opus`, `sonnet`), not a full model ID. Aliases track the newest
release, and they work on every provider; full IDs freeze the version and differ per
provider (Bedrock, for example, uses `us.anthropic.…` IDs).

The kit's convention: application-code agents and the reviewers/analysts run on `opus`;
infra, test-automation, and documentation agents run on `sonnet`. The reviewers/analysts
also set `effort: high`, because `opus` (Opus 5.5) defaults to `medium` effort.

**On Bedrock, Google Cloud, or Microsoft Foundry**, aliases can map to older models
(for example, `sonnet` → Sonnet 4.5). Pin the newest models your provider offers with
environment variables instead of editing agent files:

```sh
export ANTHROPIC_DEFAULT_OPUS_MODEL='<provider model ID>'
export ANTHROPIC_DEFAULT_SONNET_MODEL='<provider model ID>'
```

## Body

Everything after the frontmatter is the agent's **system prompt**. Write it as
direct instructions to the agent: its role, how it should work, what it should
return, and any constraints.

## Example

`test-writer.md`:

```markdown
---
name: test-writer
description: Writes unit tests for a given module. Use when new code lacks coverage.
tools: Read, Write, Edit, Bash
---

You are a focused test author. Given a target module:

1. Read the module and its existing tests.
2. Identify uncovered branches and edge cases.
3. Write tests that match the project's existing testing conventions.
4. Run the test suite and report results.

Return a summary of what you added and the final test outcome.
```

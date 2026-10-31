---
name: delegating-work
description: "Use when work would flood the main context: broad search or reading, datasheet extraction, long build/test/simulation output, an approved implementation step, or an independent review. Keeps the main session for decisions, plan and verification."
---

# Delegating engineering work

Adapted from Superpowers subagent-driven-development and
dispatching-parallel-agents. The main session keeps the user dialogue,
decisions, the approved plan and verification of results. Bulky work goes to a
worker with a fresh context that returns a compact result.

If the project defines its own delegation workflow (planner, handoff format,
module memory, review skill), follow it; this skill supplies the defaults and
the worker contract.

## When to delegate

Delegate when obtaining the result needs far more reading or output than the
result itself:
- broad code/repository search, unfamiliar codebase survey;
- datasheet, reference manual, errata or standard extraction for a narrow question;
- digesting build, ctest, Renode, ERC/DRC or log output;
- an approved, bounded implementation step;
- review of a non-trivial change (independent context finds more).

Keep in the main session: decisions and anything needing user agreement, small
edits faster to make than to describe, and checking what workers return.

## Choosing the worker

- **Read-only work** (search, reading, logs, review): an in-session subagent
  where the client supports one. Independent questions may run in parallel.
- **Steps that write files**: a separate client session (window) prepared by the
  main session and opened by the user, on its own worktree unless the user
  chooses otherwise. Never run parallel writers in one checkout; one writer per
  KiCad document.
- Without a subagent facility, do read-only work inline and say so.
- Model: suggest a cheaper model for mechanical search/reading/log digestion and
  the main model for implementation, judgment and review. A recommendation only;
  very cheap models often spend more turns on multi-step work.

## Brief (input)

Construct the context; never pass session history. A brief contains:
- one line on where the task fits;
- goal and the exact question or step;
- allowed scope (files/module/documents) and what is forbidden;
- binding constraints and exact values, copied from the spec or plan;
- stop conditions: return instead of guessing on scope, interface or safety doubts;
- where to write the full report and what to return.

Hand large artifacts over as files (brief, plan excerpt, diff package, logs),
not pasted text: pasted text stays resident in the main context. A worker never
spawns further agents. Writing workers do not commit, push or merge unless the
brief authorizes it.

## Result (output)

The worker writes details to the report file and returns only:
- status: `complete`, `partial`, `blocked` or `plan-invalid`;
- changed files and commits, if any;
- evidence: check report paths with PASS/FAIL/BLOCKED (use `scripts/check.py`
  where it supports the check), not a retelling of logs;
- deviations, open questions and limitations.

Read-only workers return the answer with file/line or document/page citations.

## Verifying a result

Do not trust narrative. Inspect the diff and the evidence reports, spot-check
cited sources for material claims and rerun or extend checks when doubtful.
For parallel results check for conflicting edits before integrating.

## Review by a fresh worker

For non-trivial changes (more than a few lines, interfaces, concurrency,
hardware/power paths) give a reviewer: the brief, the worker report and a diff
file generated from the recorded base commit (`git diff BASE..HEAD`), plus the
binding constraints. Do not pre-judge findings ("do not flag X"). Trivial
changes get a self-review labeled as such. Fix confirmed findings in the same
worker session where possible, then re-review the fix diff.

## Pacing

Writing steps follow the plan the user approved, one step at a time, with
review before the next step or merge. Read-only delegation needs no approval.
Do not poll workers in short loops; continue local work and collect results as
they arrive.

# Architecture audit — 2026-10-31

Examined citypaul baseline `cd4028d57d6e4e95814f7b8ee55ca13c23a9c2f0` and
Superpowers `2ce8aa15d05bd57213e6f746f953aafb7ded7a8b` before this refactor.

| Finding | Conflict | Resolution |
|---|---|---|
| `install-claude.sh` downloads citypaul files and web/design skills | Fork changes bypassed; duplicate workflows | Archive it; one offline Python installer |
| `claude/.claude/CLAUDE.md` demands TypeScript strict and broad TDD | Wrong domain, inappropriate PCB tests | Shared engineering policy, domain-specific evidence |
| Claude settings run Prettier/ESLint shell hooks and enable web plugins | Linux shell assumptions, hidden fixes, extra dependencies | No inherited settings/hooks installed |
| citypaul planning/debugging/testing/review overlaps Superpowers | Two competing process owners | Superpowers is the sole active workflow source |
| Superpowers bootstrap demands a skill before every response | Excessive work for trivial tasks | Engineering-only routing, minimum relevant skills |
| Superpowers brainstorming/plans enforce approval rituals | Repeated confirmations for already specified work | Clarify only material gaps, small tasks inline |
| Superpowers executors/reviewers dispatch subagents and require worktrees | Heavy fixed ritual; conflicts with project workflows | `delegating-work`: compact worker contract, read-only subagents, writing steps in separate worktree sessions, project workflow takes precedence |
| Original installation uses separate client copies | Drift and reinstall on updates | Both discovery directories link to canonical `skills/` |
| No shared durable experience | Repeated mistakes; unverified advice becomes doctrine | SQLite local ledger, observations separate from practices |
| Existing release workflow automatically tags upstream version | Misleading releases in a fork | Archive upstream workflows; engineering CI only |

The original citypaul agent material (`legacy/citypaul/`) and the personal shell,
terminal and GnuPG dotfiles with `setup-dotfiles.sh` were removed from the tree
in the toolkit cleanup; they remain in Git history at `cd4028d` and `0e62f80`.
No web skills are present.

Superpowers is vendored selectively into canonical `skills/` (no parallel vendor
copy). The manifest pins the upstream commit and every imported path. Local
adaptations are maintained by three-way updates using Git upstream blobs, not by
silently replacing local skills with newer upstream instructions. Omitted skills:
the full subagent-driven-development ritual (fix-loop caps, helper scripts,
continuous execution without check-ins) and parallel dispatch as separate skills
(their worker contract is condensed into `delegating-work`), automatic branch
finishing/worktrees, meta-authoring and transcript diagnostics. No marketplace plugin is also installed.

## Acceptance limitations

Directory identity and loading by an actual model are distinct checks. Tests
verify filesystem discovery paths, live edits, ledger concurrency and tool wrappers.
Actual Claude/Codex invocation requires installed and authenticated clients.
Actual ERC/DRC and firmware simulation require KiCad/Renode. Missing tools are
reported BLOCKED, never silently replaced by mock tests counted as integrations.

The installer cannot make unrelated enterprise/user plugins disappear. Conflicting
existing skill directories require explicit `--migrate`, which archives them. Known
legacy instruction files are archived on migration; unknown rules are preserved.
Doctor reports other installed plugins/configuration that require review.

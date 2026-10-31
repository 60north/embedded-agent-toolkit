# Vendored Superpowers

Canonical runtime files are under ../skills/, not duplicated here.
`superpowers.json` records the exact upstream commit and imported paths, with
upstream and post-adaptation SHA-256. `SUPERPOWERS-LICENSE` is the upstream license.
The original upstream file is recovered from Git for three-way updates.

Local adaptations: engineering-only/proportional bootstrap, no forced subagents,
worktrees or planning for small tasks, no destructive TDD restart, shared memory
lifecycle, native unqualified skill names, domain-appropriate verification.
The audit documents exclusions. Retained references illustrate concepts and do
not impose TypeScript as the engineering language. Unused platform wrappers,
visual servers and orchestration helper scripts are not vendored.

Update with scripts/update_superpowers.py using a reviewed 40-character commit.
No automatic network downloads, marketplace plugin installation or telemetry.

# Verification — 2026-10-31

| Check | Result | Scope |
|---|---|---|
| Python stdlib unit/integration suite on Linux, Python 3.12 | PASS | Actual links, live skill edits/new files, installer preservation/migration/rollback, concurrent SQLite writes, scoped recall/promotion/integrity, command runner, Robot XML handling, three-way merge |
| Claude Code live discovery + memory | BLOCKED | `claude` executable not present |
| Codex live discovery + memory | BLOCKED | `codex` executable not present |
| KiCad DRC fixture | BLOCKED | `kicad-cli` executable not present; fixture parsing not verified |
| KiCad ERC and visual inspection | NOT RUN | Requires an actual project and KiCad |
| Renode Robot fixture | BLOCKED | `renode-test` executable not present; fixture not executed |
| Actual STM32U5/FreeRTOS firmware scenario | NOT RUN | Requires project models/platform, ELF and Renode |
| Python stdlib unit/integration suite on Windows 10, Python 3.14.7 | PASS | Same suite incl. junction install into a temporary home, run ledger, curation review/finish/prune, shared lessons (18 tests) |
| Real global Windows installation | NOT RUN | Not yet installed on a user profile |

Executed availability/probe commands:

```
python3 -m unittest discover -s tests -v
python3 scripts/live_acceptance.py
python3 scripts/check.py --project . kicad drc fixtures/kicad/unrouted.kicad_pcb
python3 scripts/check.py --project . renode fixtures/renode/register-smoke.robot
```

Missing-tool probes returned BLOCKED (exit 2), not PASS. Private runtime reports
are under ignored `experience/`. The fixtures document what must be asserted when
tools become available; a parse error is not a successful negative DRC test.
Mock/fake-client results are not included in this report as live-client evidence.

Acceptance is implemented but not fully verified: after installation on the user's
machine run the live probe and real project ERC/DRC/Renode scenarios. Any failed
client discovery, permission prompt, missing memory record or version incompatibility
must be investigated before calling end-to-end acceptance passed.

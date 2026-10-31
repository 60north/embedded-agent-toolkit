# Maintaining the shared engineering toolkit

Follow policies/ENGINEERING.md and policies/MEMORY.md for engineering work.
Canonical skills: skills/. Scripts: scripts/. Default memory: experience/.
Superpowers is selectively vendored into skills/ with revision/license in vendor/.
Use scripts/update_superpowers.py for three-way updates; preserve local adaptations.

Do not introduce agent-specific skill copies. Delegation follows skills/delegating-work.
Both clients can edit separate user-assigned scopes in the same project. Never
stage, commit or reset another agent's files. Install into temporary homes for tests.

Run python -m unittest discover -s tests -v for changes to scripts/installations.
Run scripts/live_acceptance.py --run only with available authenticated clients.
Use fixtures/ for representative KiCad/Renode checks and report unavailable tools
as BLOCKED. Mock and filesystem checks are not evidence of actual client discovery.
Do not commit private memory, logs, tokens or local installation manifests.

---
name: engineering-python
description: "Implement, debug or review Python tools, test benches, automation and data processing using the project environment and meaningful tests."
---

# Python
1. Read pyproject.toml/requirements, supported Python versions, lockfiles and
   existing test commands. Use the project's environment and package manager;
   do not upgrade global packages or replace its toolchain without a reason.
2. Keep I/O, parsing and deterministic logic separable without unnecessary layers.
   Use explicit units, encodings, timeouts and resource ownership. Validate data
   at external boundaries; preserve useful exception context.
3. For serial/network/subprocess tools, bound waits, handle partial messages and
   cancellation, and clean up resources. Use subprocess argument lists rather
   than shell interpolation. Do not log credentials or device secrets.
4. For numerical work, test units, empty inputs, NaNs and tolerances appropriate
   to the requirement. Do not introduce NumPy for trivial scalar calculations.
5. Add regression tests and boundary cases at public interfaces. Mock only true
   external dependencies; do not mock away the behavior being tested.
6. Run configured tests, linting and typing checks. Use pytest/Ruff/mypy or
   alternatives only where installed/configured or explicitly adopted. Inspect
   collection counts: zero tests is not a passing verification result.
7. Report the environment, commands, actual results and dependencies on hardware.

## Shared experience
At task start recall relevant records using policies/MEMORY.md and the shared scripts. Before finishing, record useful approaches, failures, successful script paths/hashes and verification evidence in the same ledger. Keep observations separate from validated practices.

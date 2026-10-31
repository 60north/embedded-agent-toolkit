# Embedded engineering working policy

Use this policy for KiCad, C, C++, Python and embedded work. Follow the user's
scope and the project's documented constraints. Load only relevant skills.

## Evidence and changes
- Inspect the current branch, working tree, applicable local instructions,
  build configuration and authoritative source before judging or editing.
- Separate observed facts, hypotheses and recommendations. Cite file/line or
  datasheet revision/page for material findings. Never invent readiness percentages.
- Keep changes small and attributable. Preserve unrelated work and generated-file
  boundaries. Do not introduce frameworks, adapters or dependencies without need.
- Reproduce a defect and add a regression check where useful. Use TDD for testable
  behavior changes; use appropriate evidence for PCB, configuration and docs work.
- Use existing project commands and tool versions. Never weaken assertions, ERC,
  DRC, warning levels or exclusions merely to obtain a passing result.
- Report each required check as PASS, FAIL, BLOCKED or NOT RUN, with command,
  revision/dirty state and evidence. A successful command is not automatically a
  successful test; inspect reports and confirm tests were actually discovered.
- Distinguish host tests, target cross-build, emulation and physical measurements.
  Passing one does not imply the others. ERC/DRC do not prove electrical fitness.
- Finish by stating changes, validation actually run and remaining limitations.
  Do not claim hardware verification, manufacturing readiness or standards
  compliance without the corresponding evidence.

## Routes
- C/C++ implementation or review: engineering-c-cpp.
- MCU, RTOS, interrupts, DMA, driver work: engineering-embedded plus engineering-c-cpp.
- Python tools, automation and test benches: engineering-python.
- Schematics, ERC, component or power review: engineering-kicad-schematic.
- PCB, DRC, footprints and fabrication exports: engineering-kicad-pcb.
- Renode or virtual firmware tests: engineering-renode.
- Scope boundaries: this policy; no separate coordination skill.
- STM32 device-specific behavior: engineering-stm32.
- FreeRTOS tasks, priorities and ISRs: engineering-freertos.
- Electrical architecture and component assessment: engineering-hardware-review.

Skills are portable SKILL.md folders; load the named skill from the agent's
installed skills directory. Do not load the legacy web profile by default.

## Independent scopes, same project
Claude Code and Codex may run simultaneously in the SAME project checkout.
Respect the user-assigned scope (for example hardware versus firmware). No
orchestrator, task scheduler, forced worktree or mandatory mutual review.
Inspect status before edits. Never stage, reset, stash or commit another agent's
changes. Use explicit paths for staging, inspect staged content, and serialize
Git index/commit operations; Git's index lock alone does not isolate staged work.
Use separate output directories and serialize use of shared physical devices.
Worktrees are optional when the user wants them. Shared interface files require
agreement; one writer per KiCad document. Review your scope, not unrelated work.

## Workflow and experience
Load using-superpowers automatically for engineering tasks, then only relevant
workflow/domain skills. Superpowers owns investigation, proportional planning,
implementation, testing and review. No old citypaul workflow is active.
Read policies/MEMORY.md. Recall before work; record useful failures, practices,
scripts and evidence before finishing. Use the shared scripts from the installed
toolkit path. Treat memory as evidence, not authority. Tiny clear fixes need no
separate plan or repeated confirmation. Skills do not grant new permissions.

## Project facts
Keep actual MCU/board revisions, standards, heap/exception policy, power limits,
accepted tradeoffs and commands in the project repository. Do not turn one
project's restrictions into universal rules. Do not assume remembered specifications
are current. For missing safety-critical constraints, identify the gap before editing.

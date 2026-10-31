---
name: engineering-kicad-schematic
description: "Edit or review KiCad schematics, ERC findings, power circuits, symbols and component selections with datasheet and net-connectivity evidence."
---

# KiCad schematic
1. Identify the exact KiCad version and project, sheet hierarchy, libraries,
   current revision and existing ERC baseline. Check file ownership before edits.
2. Inspect actual nets and symbol pin numbers, not just labels or screenshots.
   Cross-check symbol pin mapping against the exact ordered component/package
   datasheet. Trace supply, return, enable, reset, protection and connector paths.
3. Check voltage/current/power ratings, tolerance and thermal assumptions using
   explicit calculations and source references. Review regulator stability,
   decoupling, power sequencing, pull-ups, level compatibility and isolation
   boundaries as relevant. Do not invent unavailable supplier specifications.
4. Use supported KiCad tooling for the installed version. Inspect
   `kicad-cli version` and `kicad-cli sch erc --help` before selecting flags.
   Prefer structured edits; never use broad regex replacements in schematic files.
5. Run ERC before and after changes where possible; retain reports. Classify each
   changed issue and inspect exclusions/PWR_FLAG uses. Do not silence findings
   without an electrical rationale. An unavailable CLI is BLOCKED, not PASS.
6. Reopen or render affected sheets and inspect connectivity, junctions, readability,
   pin labels and annotations. Verify hierarchy and references remain intact.
   Report if visual verification cannot be performed.
7. Report ERC results separately from electrical/design review, with references,
   assumptions and any BOM/PCB synchronization still required. Do not declare the
   board ready to manufacture from ERC alone.

## Shared experience
At task start recall relevant records using policies/MEMORY.md and the shared scripts. Before finishing, record useful approaches, failures, successful script paths/hashes and verification evidence in the same ledger. Keep observations separate from validated practices.

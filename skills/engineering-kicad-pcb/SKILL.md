---
name: engineering-kicad-pcb
description: "Edit or review KiCad PCB layout, DRC, footprints, stackup and fabrication exports; verify design rules and visually inspect affected copper and manufacturing layers."
---

# KiCad PCB
1. Identify KiCad/project/board revisions, stackup, manufacturer capabilities,
   net classes and baseline DRC. Establish a single writer for the board file.
2. Cross-check schematic connectivity, footprint package/pad numbering, pin 1,
   orientation and connector mating direction against authoritative drawings.
   Review clearances, return paths, current-carrying geometry and thermal paths
   against declared loads and stackup, not unsupported universal trace widths.
3. For edits, preserve unrelated placement/routing and UUID relationships.
   Inspect the installed CLI/API before using it. Avoid bulk text edits to
   nested PCB syntax and unrequested format-version migrations.
4. Refill zones with a supported tool before final DRC. Check
   `kicad-cli pcb drc --help` for available flags. Run DRC and inspect violations,
   unconnected items, severity configuration and exclusions. Record baseline
   versus introduced findings; never disable a rule simply to pass.
5. Visually inspect affected copper, thermals, zone islands, outline, solder mask,
   paste, silkscreen and courtyards. A DRC report alone cannot substantiate this.
   Record any visual checks not performed.
6. Generate requested Gerber/drill/BOM/placement outputs from one identified
   revision with project-owned settings. Inspect exported layers and drill
   alignment. Verify units, origin and assembly rotation conventions where used.
7. Report DRC, visual review and fabrication-output validation separately. Treat
   creepage/isolation requirements and manufacturing limits as explicit inputs;
   do not infer compliance from a generic preset. Do not submit fabrication orders
   unless separately requested.

## Shared experience
At task start recall relevant records using policies/MEMORY.md and the shared scripts. Before finishing, record useful approaches, failures, successful script paths/hashes and verification evidence in the same ledger. Keep observations separate from validated practices.

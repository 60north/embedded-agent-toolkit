---
name: engineering-hardware-review
description: "Use for electrical architecture, component selection, power/protection/thermal analysis and hardware design review beyond KiCad ERC/DRC."
---

# Hardware review
Read the current schematic/PCB/BOM revision and constraints. Establish input power,
loads, interfaces, environment, assembly method and operating margins. Distinguish
specified requirements from assumptions; ask only for missing material constraints.
Trace power and signal paths. Check absolute maxima versus operating conditions,
tolerances/derating, transient protection, startup, reverse polarity, charging,
thermal dissipation and return paths as relevant. Cite exact component datasheets,
package drawings and calculations with units. Do not invent supplier ratings.
Check symbol-to-footprint-to-ordered-part consistency and connector orientation.
Use engineering-kicad-schematic/pcb for tool checks; do not duplicate their process.
Rank findings by concrete failure effect, cite reference designators/nets and offer
the smallest justified correction. Treat compliance, EMC, analog performance and
manufacturability as unverified unless supported by the appropriate evidence.

Read policies/MEMORY.md: recall relevant shared experience before work and record useful outcomes, failures, script paths/hashes and evidence before finishing.

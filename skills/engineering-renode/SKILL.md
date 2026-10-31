---
name: engineering-renode
description: "Build or debug Renode peripheral models and firmware scenarios, including register contracts, interrupts, DMA, virtual time and framebuffer checks."
---

# Renode verification
1. Pin Renode version/commit, platform description, peripheral models, firmware ELF
   and scenario version. Identify which peripherals are models, stubs or absent.
2. Derive model behavior from the exact MCU manual and errata: reset values,
   widths, access restrictions, side effects, IRQ assertion/clearing and DMA paths.
   Do not change a model merely to make the current firmware pass.
3. Test model contracts separately from full-firmware scenarios. Include negative
   and boundary cases, independent known vectors and interrupt clearing/rearming.
   Guard against a matching mistake in firmware and model producing a false pass.
4. Use deterministic virtual-time scenarios, bounded waits and fixed inputs. Test
   startup, normal flows, missing/stale data and error recovery as relevant.
5. For display checks, capture the actual firmware framebuffer. Distinguish a
   pixel comparison from proof that the underlying alarm/state logic is correct;
   assert both when the requirement needs both.
6. Run the real firmware ELF through the documented scenario runner and inspect
   assertions, logs and captured artifacts. Compilation or a simulator launch
   alone is not a passed integration test.
7. Report modeled coverage and explicit hardware gaps: analog behavior, electrical
   margins, physical timing and unmodeled peripheral interactions remain unproven.

## Shared experience
At task start recall relevant records using policies/MEMORY.md and the shared scripts. Before finishing, record useful approaches, failures, successful script paths/hashes and verification evidence in the same ledger. Keep observations separate from validated practices.

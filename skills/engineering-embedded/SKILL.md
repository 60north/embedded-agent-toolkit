---
name: engineering-embedded
description: "Implement or review MCU firmware, RTOS tasks, ISRs, DMA and peripheral drivers; verify register behavior and resource constraints against the exact device and board."
---

# Embedded firmware
1. Identify the exact MCU variant/revision, board revision, SDK/HAL version,
   RTOS configuration, clock tree, linker script and current project constraints.
   Read the applicable datasheet, reference manual and errata before making
   claims about a peripheral. Cite document revision and section for fixes.
2. Check reset/clock sequencing, pin alternate functions, register access widths,
   reserved bits, W1C/read-to-clear behavior, interrupts and power transitions.
   Do not extrapolate register semantics from another STM32 family.
3. Define task/ISR ownership and synchronization. Use permitted FromISR APIs,
   correct interrupt priorities and bounded work. volatile is neither mutual
   exclusion nor a general memory-ordering primitive.
4. Check DMA buffer lifetime, placement, alignment and accessibility, cache
   maintenance where applicable and completion/error paths. Check stack and
   memory budgets from actual build artifacts and measurements where available.
5. Make waits bounded and recovery explicit. Review watchdog behavior, overflow
   of tick counters, disconnects, stale data, startup and brownout assumptions.
6. Test pure logic on the host, cross-build the actual firmware, then exercise
   relevant emulation or hardware tests. Do not install a new test stack merely
   because a preferred tool exists. Use available project harnesses first.
7. Document unmeasured timing, electrical behavior and hardware gaps. Do not claim
   MISRA/IEC compliance from coding style or a partial analyzer run.

## Shared experience
At task start recall relevant records using policies/MEMORY.md and the shared scripts. Before finishing, record useful approaches, failures, successful script paths/hashes and verification evidence in the same ledger. Keep observations separate from validated practices.

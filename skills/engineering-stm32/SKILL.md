---
name: engineering-stm32
description: "Use for STM32 register, clock, pinmux, power, security and peripheral behavior; verify the exact family, part and silicon revision."
---

# STM32
Identify the exact part, package, silicon revision, board and firmware/HAL versions.
Read the applicable datasheet, reference manual and errata; cite document/revision
and register section for material findings. U5/H5/F4 are not interchangeable.
Verify clock sources/dividers and peripheral bus clocks, reset/enable sequence,
voltage scaling and flash latency where relevant. Trace GPIO alternate function,
pin numbers and board routing. Check access widths, reserved bits, reset state,
W1C/read-clear side effects and IRQ acknowledgment against the manual.
For DMA/cache/security domains, verify memory accessibility, address aliases,
alignment, cache coherence and privilege attribution. Check boot/vector/linker
addresses and startup initialization. Preserve the project's generated-code seams.
Test driver contracts and cross-build the actual target; use Renode or hardware
for appropriate runtime behavior. Do not repair a peripheral model merely to match
incorrect firmware. Record unsupported peripherals and unmeasured timing explicitly.

Read policies/MEMORY.md: recall relevant shared experience before work and record useful outcomes, failures, script paths/hashes and evidence before finishing.

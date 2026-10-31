---
name: engineering-freertos
description: "Use for FreeRTOS task design, scheduler/interrupt configuration, synchronization, queues, timers and resource analysis in embedded firmware."
---

# FreeRTOS
Read the actual kernel version, port, FreeRTOSConfig.h, allocation policy and
interrupt priority configuration. Identify owners of shared state and each task's
blocking conditions, stack budget and deadlines before changing concurrency.
Check FromISR API use, allowed IRQ priorities, required yield behavior, critical
section bounds, task notification semantics and queue element lifetimes. Do not
use a mutex from an ISR or equate volatile with synchronization. Consider priority
inversion, lock ordering, starvation, cancellation and queue overflow.
Keep timer callbacks bounded and honor timer service task constraints. Check tick
rollover and conversions rather than assuming tick rate equals milliseconds.
Preserve static/dynamic allocation policy; validate stack/high-water measurements
and heap behavior on the actual build when available. Test timeout, backpressure,
startup and error recovery, not only nominal scheduling. Host tests and emulation
cannot establish worst-case execution time or physical interrupt latency.

Read policies/MEMORY.md: recall relevant shared experience before work and record useful outcomes, failures, script paths/hashes and evidence before finishing.

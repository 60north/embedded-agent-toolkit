---
name: engineering-c-cpp
description: "Implement and review C/C++ code, build changes and regression tests, including ownership, undefined behavior, ABI and cross-compilation. Use for C/C++ tasks; pair with engineering-embedded for hardware-facing code."
---

# C/C++
1. Read the build system, selected language standard, compiler/target, warning
   policy and existing tests. Reuse CMake presets/toolchain or the existing build
   procedure; do not substitute host compilation for a target build.
2. Establish ownership, lifetime, bounds, error propagation and concurrency
   contracts before edits. In C, document allocation/free and cleanup paths; in
   C++, prefer RAII and explicit ownership where compatible with the project.
3. Check overflow and signedness, shifts, alignment, aliasing, object lifetime,
   uninitialized reads, endianness, packed structures and serialization lengths.
   Do not use native struct layout as a wire format without a proven contract.
4. Preserve ABI and public contracts unless the requested change needs a break.
   Follow project policy on exceptions, RTTI, allocation and STL; do not impose
   blanket bans or blanket adoption. Keep hardware side effects at explicit seams.
5. Add behavioral regression tests for changed paths and relevant boundaries.
   For a defect, establish that the test catches the old behavior when feasible.
   For refactoring, preserve existing behavior; do not invent structural tests.
6. Run the project build/test commands and applicable formatting/static analysis.
   Use compile_commands.json with the correct target when running clang-tidy.
   Run supported host sanitizers where useful, noting their target limitations.
7. Report tested build configurations, tests actually executed, new warnings,
   and unavailable checks. Treat a successful cross-build as compilation evidence,
   not proof of runtime timing, hardware behavior or absence of undefined behavior.

## Shared experience
At task start recall relevant records using policies/MEMORY.md and the shared scripts. Before finishing, record useful approaches, failures, successful script paths/hashes and verification evidence in the same ledger. Keep observations separate from validated practices.

---
name: requesting-code-review
description: "Use after engineering changes and before completion to check the scoped diff, requirements, verification evidence and regressions."
---

# Engineering review

Adapted from Superpowers requesting-code-review. Establish the exact diff/base and
owned files, read the requirements and inspect actual code/design and test output.
Check correctness, error paths, resource constraints, interfaces and regression
coverage with relevant engineering skills. For hardware include electrical and
visual review beyond ERC/DRC. Rank actionable findings with file/line or component
references and evidence. Do not invent findings to fill a quota.

For non-trivial changes use a fresh reviewer per delegating-work: hand it the
brief, the report and a diff file from the recorded base, plus binding
constraints, without pre-judging findings. Trivial changes get a self-review
labeled as such. A project's own review skill takes precedence. If another
client has a review assignment, let it work independently. Fix confirmed defects, rerun changed
checks and report unresolved limitations with verification-before-completion.

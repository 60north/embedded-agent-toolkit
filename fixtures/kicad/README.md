# Representative PCB gate

`unrouted.kicad_pcb` is an intentionally unrouted two-pad net, not a reference
production board. Expected: the DRC gate rejects it and reports unconnected items.
Do not turn a parse error into proof the DRC test worked. KiCad execution has not
been performed in the authoring environment; file-format compatibility remains
unverified until a real run. Inspect the generated JSON for unconnected items.

```
python scripts/check.py --project . kicad drc fixtures/kicad/unrouted.kicad_pcb
```

For a real schematic/PCB edit: capture the initial ERC/DRC, make one requested
change within scope, refill PCB zones, repeat the checks and compare findings.
Export affected sheets/layers with the installed version's supported commands,
visually inspect them, and record that evidence separately. Use an actual project
schematic for ERC; an empty schematic would not be a representative acceptance test.

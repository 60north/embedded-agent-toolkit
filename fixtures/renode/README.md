# Renode representative workflows

`register-smoke.robot` uses a bundled STM32F4 platform to exercise runner startup,
mapped memory and an observable assertion. It is NOT proof of STM32U5 support or
of a working firmware. Compatibility with the installed Renode release must be
checked by running it; it was not executed in the authoring environment.

```
python scripts/check.py --project . renode fixtures/renode/register-smoke.robot
```

For the actual U5/FreeRTOS workflow, supply the project's platform/models and ELF:
load the existing `.resc`, boot to an observable state, inject a UART/CAN event,
assert the firmware response/IRQ acknowledgment and capture the framebuffer when
relevant. Run the project's Robot scenario through the same wrapper. Include a
missing/stale-input case and a model contract test independent of the firmware.
Keep ELF/platform hashes with the report. Do not substitute the F4 memory smoke
for this firmware-level acceptance check.

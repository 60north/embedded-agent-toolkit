*** Settings ***
Suite Setup       Setup
Suite Teardown    Teardown
Test Setup        Reset Emulation
Resource          ${RENODEKEYWORDS}

*** Test Cases ***
STM32F4 RAM Register Access Smoke
    Execute Command    mach create
    Execute Command    machine LoadPlatformDescription @platforms/cpus/stm32f4.repl
    Execute Command    sysbus WriteDoubleWord 0x20000000 0x12345678
    ${value}=    Execute Command    sysbus ReadDoubleWord 0x20000000
    Should Contain    ${value}    12345678

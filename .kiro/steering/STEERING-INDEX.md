---
inclusion: always
---
# Steering Documentation Index

Quick-reference catalog of all steering files for the Choir Practice project.

## Always-Loaded (Every Conversation)

| File | Topic | Key Contents |
|------|-------|-------------|
| `00-project-overview.md` | Project goals, hardware summary | CH-8 specs, nRF52840, what we know vs don't, project phases |
| `01-core-workflow.md` | Dev workflow, tools, safety rules | J-Link usage, flash dump procedures, git workflow, golden rules |
| `STEERING-INDEX.md` | This file | Catalog of all steering docs |

## Conditional — File Pattern Match

| File | Pattern | Topic |
|------|---------|-------|
| `10-firmware-analysis.md` | `*.bin, *.hex, *.elf, *.map, *.ld, *.ghidra, *firmware*` | Ghidra workflow, flash layout, ARM Cortex-M4 analysis patterns |
| `11-nrf52840-reference.md` | `*.c, *.h, *.dts, *.overlay, *.conf, CMakeLists.txt, prj.conf` | nRF52840 peripherals, memory map, SoftDevice, Zephyr SDK patterns |
| `12-ble-midi-protocol.md` | `*ble*, *midi*, *bluetooth*, *sync*` | BLE MIDI CC mappings, inter-doll sync, phoneme tables |

## Topic Routing

| Topic | Go To |
|-------|-------|
| Project goals, what we're building | `00-project-overview.md` |
| Hardware specs, SoC, amplifier, battery | `00-project-overview.md` |
| .tfw file format, encryption | `00-project-overview.md` |
| J-Link setup, SWD connection, flash dump | `01-core-workflow.md` |
| APPROTECT, flash protection | `01-core-workflow.md` |
| Git workflow, commits | `01-core-workflow.md` |
| Ghidra analysis, disassembly | `10-firmware-analysis.md` |
| nRF52840 peripherals, memory map | `11-nrf52840-reference.md` |
| Zephyr RTOS, nRF Connect SDK | `11-nrf52840-reference.md` |
| BLE MIDI, phoneme control, CC mappings | `12-ble-midi-protocol.md` |
| Inter-doll sync protocol | `12-ble-midi-protocol.md` |
| USB mass storage, CDC-ACM | `00-project-overview.md` |
| Song data format, synthesis engine | `10-firmware-analysis.md` |

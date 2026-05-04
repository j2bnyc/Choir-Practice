---
inclusion: always
---

# Choir Practice — Project Overview

## What This Is

Custom firmware and companion app for the Teenage Engineering Choir (CH-8) — eight wooden dolls with nRF52840 SoCs that sing a cappella via BLE-synced synthesis.

**Goal:** Retain all 22 stock songs, add ability to load and play user-composed songs via a companion app.

## Hardware Quick Reference

| Component | Detail |
|-----------|--------|
| SoC | Nordic nRF52840 (ARM Cortex-M4F, 1 MB flash, 256 KB RAM) |
| Variant | N52840-Q1AAD0-2025KR |
| Amplifier | MAX98390 (boosted Class-D, I2C controlled) |
| Power IC | BQ25892 charger, 3.7V 850mAh LiPo, USB-C |
| Other ICs | C4066 analog switch, unknown 6W808 2025QBR |
| Comms | BLE (inter-doll beacons + MIDI over BLE) |
| USB | Composite: CDC-ACM (unresponsive) + Mass Storage (FAT12, 1 MB) |
| Sensors | Accelerometer/vibration (tap/tilt/smack gestures) |
| Debug | Circular test pads on upper board — likely SWD |

## The Eight Dolls

| Doll | Voice Type | Range | Frequency | Serial Prefix |
|------|-----------|-------|-----------|---------------|
| Hatsheput | Mezzo soprano | A3–F5 | 220–698 Hz | S7DPQ |
| Leila | Soprano | C#4–A5 | 277–880 Hz | S4DPQ |
| Olga | Contralto | E3–C5 | 162–523 Hz | S8DPQ |
| Bogdan | Bass | E2–C4 | 82–262 Hz | S6DPQ |
| Carlo | Baritone | G2–D#4 | 98–294 Hz | S2DPQ |
| Ivana | Alto | F#3–D5 | 175–587 Hz | S5DPQ |
| Miki | Tenor | B2–G4 | 117–392 Hz | S1DPQ |
| Giesela | Mezzo soprano | B3–G5 | 247–784 Hz | S3DPQ |

## .tfw Firmware Format (Reverse-Engineered)

- 64-byte outer header: magic `BABE CAFE`, firmware_type, version, SKU bitfield
- CH-8 uses firmware_type=2 (no inner header, encrypted payload from byte 64)
- ALL .tfw payloads are encrypted (7.99+ bits/byte entropy)
- Decryption key lives in the on-chip bootloader — cannot decrypt without SWD dump
- Stock firmware: v1.1.3 (2022-12-22), 485,230 bytes

## USB Interfaces

| Interface | What It Does | Status |
|-----------|-------------|--------|
| Mass Storage | FAT12 virtual disk, firmware update via file copy | Working, full R/W |
| CDC-ACM Serial | Unknown purpose, `/dev/cu.usbmodem01` | Completely unresponsive |

## What We Know vs Don't

**Known:** .tfw header format, payload encryption confirmed, USB mass storage DFU path, BLE MIDI CC mappings (CC1=vibrato, CC2=consonant, CC3=vowel, CC4=reverb), CDC-ACM is dead.

**Unknown (need SWD dump):** Flash layout, RTOS identity, synthesis engine type, song data format, inter-doll sync protocol details, APPROTECT status, I2C config for MAX98390, accelerometer model, .tfw decryption key/algorithm.

## Project Phases

1. **Flash Dump & Initial Analysis** — J-Link SWD connection, APPROTECT check, full flash dump
2. **Firmware Analysis** — Ghidra disassembly, map flash layout, find synthesis engine and song data
3. **Dev Environment Setup** — nRF Connect SDK, custom board definition, build and flash test firmware
4. **Custom Firmware** — Retain stock songs, add user song bank, BLE upload service
5. **Companion App** — Import audio/MIDI, transcribe to counterpoint notation, upload via BLE

## Key Resources

| Resource | URL |
|----------|-----|
| Choirama (community teardown) | https://github.com/jetztgradnet/Choirama |
| nRF52840 Datasheet | https://infocenter.nordicsemi.com/pdf/nRF52840_PS_v1.1.pdf |
| nRF Connect SDK | https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/ |
| MAX98390 Datasheet | https://www.analog.com/en/products/max98390.html |
| TE Firmware RE Blog | https://wmealing.github.io/reverse-engineering-teenage-engineering.html |
| TE Web Updater JS | https://teenage.engineering/apps/update/assets/index-0vVGeHxM.js |

## Reference Files

Detailed research and teardown notes are in `TE-Files/`:
- `choir-custom-firmware-project.md` — Full project doc with .tfw format details, DFU protocol, session log
- `choir-info.md` — Product research and hardware teardown
- `choir-homepage.md` — TE product page content
- `choir-user-guide.pdf` — Official user guide
- `choir-firmware-1.1.3.tfw` — Stock firmware binary (encrypted)

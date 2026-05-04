---
inclusion: always
---

# Firmware Analysis Patterns

## Ghidra Setup for nRF52840

- Language: ARM Cortex (little-endian)
- Compiler: GCC (ARM)
- Base address: 0x00000000
- Import as raw binary, not ELF (unless we have an ELF)

## nRF52840 Memory Map

| Region | Address Range | Size | Contents |
|--------|--------------|------|----------|
| Flash | 0x00000000–0x000FFFFF | 1 MB | Bootloader + SoftDevice + App + Data |
| RAM | 0x20000000–0x2003FFFF | 256 KB | Stack, heap, BLE buffers |
| UICR | 0x10001000–0x10001FFF | 4 KB | User config registers |
| FICR | 0x10000000–0x10000FFF | 4 KB | Factory info (read-only) |

## Typical nRF52840 Flash Layout (with SoftDevice)

```
0x00000000  ┌─────────────────────┐
            │ MBR (4 KB)          │  Master Boot Record
0x00001000  ├─────────────────────┤
            │ SoftDevice (~152 KB)│  BLE stack (if used)
0x00026000  ├─────────────────────┤
            │ Application         │  Main firmware
            │                     │
            ├─────────────────────┤
            │ App Data / Songs?   │  Likely location for song data
            ├─────────────────────┤
            │ Bootloader (~32 KB) │  DFU bootloader (contains .tfw decryption key)
0x000FF000  ├─────────────────────┤
            │ Bootloader Settings │  1 page
0x00100000  └─────────────────────┘
```

This is speculative until we have the actual dump. The CH-8 may not use SoftDevice at all.

## What to Look For in the Dump

1. **Vector table** at 0x00000000 — initial SP (expect ~0x20040000) and reset handler
2. **SoftDevice signature** — look for "SOFTDEVICE" string or known SD magic bytes
3. **Bootloader** — usually in upper flash, contains .tfw decryption routine
4. **Song data** — large structured blocks, likely in upper application region
5. **String table** — phoneme names, doll names, error messages
6. **I2C init sequences** — MAX98390 register writes (look for 0x39 or 0x3A addresses)
7. **BLE service UUIDs** — 128-bit UUIDs for custom services

## Entropy Analysis

Use entropy analysis to identify encrypted vs plaintext regions in the flash dump:
- Encrypted/compressed: ~7.5–8.0 bits/byte
- Code (.text): ~5.0–6.5 bits/byte
- Structured data: ~3.0–5.0 bits/byte
- Padding/empty: ~0.0 bits/byte (0xFF fill)

## ARM Cortex-M4 Patterns

- Function prologues: `PUSH {r4-r7, lr}` or `PUSH {r3-r7, lr}`
- Function epilogues: `POP {r4-r7, pc}`
- Thumb-2 instruction set (16-bit and 32-bit mixed)
- Literal pools after functions (constants loaded via PC-relative addressing)
- SVC instructions indicate SoftDevice API calls

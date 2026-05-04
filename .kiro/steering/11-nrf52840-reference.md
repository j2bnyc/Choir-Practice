---
inclusion: fileMatch
fileMatchPattern: "*.c, *.h, *.dts, *.overlay, *.conf, CMakeLists.txt, prj.conf"
---

# nRF52840 Development Reference

## nRF Connect SDK / Zephyr

The custom firmware will be built with the nRF Connect SDK (based on Zephyr RTOS).

### Project Structure (Zephyr convention)

```
firmware/
├── CMakeLists.txt
├── prj.conf              # Kconfig options
├── boards/
│   └── ch8_sound_module.overlay   # Device tree overlay for CH-8 hardware
├── src/
│   ├── main.c
│   └── ...
└── dts/
    └── bindings/         # Custom device tree bindings if needed
```

### Key Peripherals to Configure

| Peripheral | Use | Notes |
|-----------|-----|-------|
| I2C/TWI | MAX98390 amplifier control | Find address from dump (likely 0x39 or 0x3A) |
| I2S or PWM | Audio output to amplifier | Depends on how TE routes audio |
| BLE (SoftDevice or Zephyr BLE) | MIDI, inter-doll sync, song upload | Must match stock BLE behavior for compatibility |
| USB | Mass storage + CDC-ACM composite | For firmware update path |
| GPIO | Button, LED | Single button, status LED |
| SPI/I2C | Accelerometer | Model unknown until dump analysis |
| Flash (internal) | Song storage | NVS or raw flash partitions |
| DMA | Audio streaming | For continuous audio output |

### nRF52840 Key Specs

- CPU: ARM Cortex-M4F @ 64 MHz
- Flash: 1 MB (0x00000000–0x000FFFFF)
- RAM: 256 KB (0x20000000–0x2003FFFF)
- Flash page size: 4 KB
- Flash write: word-aligned (4 bytes)
- Erase: page-level only (4 KB granularity)

### Useful nRF52840 Registers

| Register | Address | Purpose |
|----------|---------|---------|
| APPROTECT | 0x10001208 | Flash read protection (0x00 = protected, 0xFF = open) |
| PSELRESET[0] | 0x10001200 | Reset pin config |
| PSELRESET[1] | 0x10001204 | Reset pin config |
| NFCPINS | 0x1000120C | NFC pin mode |
| REGOUT0 | 0x10001304 | Regulator output voltage |

### Build Commands (nRF Connect SDK)

```bash
# Build for custom board
west build -b ch8_sound_module firmware/

# Flash via J-Link
west flash

# Debug via J-Link GDB server
west debug
```

## Safety Notes

- Never erase flash without a verified backup
- The bootloader region contains the .tfw decryption key — preserve it
- If using SoftDevice, it occupies the first ~152 KB of flash and must not be overwritten
- UICR writes are persistent and survive soft resets — be careful with UICR modifications

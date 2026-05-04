# Teenage Engineering Choir (CH-8) — Custom Firmware Project

## Goal

Build custom firmware for the CH-8 Choir that retains all 22 stock songs but adds the ability to load and play user-composed songs via a companion app. The app will handle importing audio/MIDI, transcribing to the Choir's counterpoint notation format, and uploading new compositions to the dolls.

---

## Hardware Summary

| Component | Detail |
|-----------|--------|
| SoC | Nordic Semiconductor nRF52840 (ARM Cortex-M4F, 1 MB flash, 256 KB RAM) |
| Variant | N52840-Q1AAD0-2025KR |
| Amplifier | Maxim Integrated MAX98390 (boosted Class-D with dynamic speaker management) |
| Power IC | Texas Instruments BQ25892 charger |
| Battery | 3.7V LiPo, 850mAh (3.145Wh), ~4 hours continuous, USB-C charging |
| Other ICs | C4066 analog switch, unknown chip marked 6W808 2025QBR |
| Comms | BLE (beacons for inter-doll sync, MIDI over BLE for controller input) |
| USB | Composite device: CDC-ACM serial + USB Mass Storage (FAT12) |
| Sensors | Accelerometer/vibration (tap to play/pause, tilt for volume, smack to off) |
| Test pads | Circular pads on upper board — likely SWD programming/debug |

### USB Device Identity (verified 2026-03-21)

| Field | Value |
|-------|-------|
| Vendor ID | 0x2367 / 9063 (Teenage Engineering AB) |
| Product ID | 0x0018 / 24 |
| Product String | "CH_8 Firmware Upgrade" |
| Vendor String | "Teenage Engineering AB" |
| Serial | "0" |
| Speed | Full Speed (12 Mbps, USB 2.0) |
| bcdDevice | 519 (0x0207) |
| bcdUSB | 512 (0x0200) |
| Max Packet Size | 64 bytes |
| Power | 500 mA |

### USB Interfaces

| Interface | Class | Description |
|-----------|-------|-------------|
| 0 | CDC-ACM Control (2/2/0) | Serial port control, EP 0x81 IN (16 byte) |
| 1 | CDC-ACM Data (10/0/0) | Serial data, EP 0x82 IN + EP 0x01 OUT (64 byte) |
| 2 | Mass Storage (8/6/80) | Bulk-Only SCSI, EP 0x83 IN + EP 0x02 OUT (64 byte) |

### The Eight Dolls

| Doll | Origin | Voice Type | Range | Frequency | Serial Prefix | Module Orientation |
|------|--------|-----------|-------|-----------|---------------|-------------------|
| Hatsheput | Egypt | Mezzo soprano | A3–F5 | 220–698 Hz | S7DPQ___ | Horizontal |
| Leila | Palestine | Soprano | C#4–A5 | 277–880 Hz | S4DPQ___ | Horizontal |
| Olga | Russia | Contralto | E3–C5 | 162–523 Hz | S8DPQ___ | Vertical |
| Bogdan | Cossack | Bass | E2–C4 | 82–262 Hz | S6DPQ___ | Vertical |
| Carlo | Italy | Baritone | G2–D#4 | 98–294 Hz | S2DPQ___ | Horizontal |
| Ivana | Netherlands | Alto | F#3–D5 | 175–587 Hz | S5DPQ___ | Vertical |
| Miki | Japan | Tenor | B2–G4 | 117–392 Hz | S1DPQ___ | Horizontal |
| Giesela | Germany | Mezzo soprano | B3–G5 | 247–784 Hz | S3DPQ___ | Horizontal |

---

## Current Firmware

- Latest version: **1.1.3** (released 2022-12-22)
- File: `choir-firmware-1.1.3.tfw` (485,230 bytes)
- Download: https://teenage.engineering/downloads
- Local copy: `choir-firmware-1.1.3.tfw`
- CH-8 is NOT in the TE releases.json — firmware only available from the downloads page

### Verified Doll Info (Giesela, 2026-03-21)

```
product: CH-8
variant: Giesela
software version: 1.1.3+0
product serial: S3DPQ1NT
pcba serial: 830000683232900010
upgrade status: ok
```

---

## .tfw File Format (Reverse-Engineered from TE Web Updater JS)

The `.tfw` format is Teenage Engineering's proprietary firmware container used across all their products. The format was reverse-engineered from the JavaScript source of the TE web updater at `teenage.engineering/apps/update/assets/index-0vVGeHxM.js`.

### Outer Header (64 bytes, all products)

```
Offset  Size  Field              CH-8 Value         Notes
------  ----  -----------------  -----------------  --------------------------------
0x00    4     Magic              BA BE CA FE        Constant across all TE products
0x04    1     firmware_type      0x02               0=has inner header, 2=encrypted only
0x05    2     checksum           B4 AC              Purpose TBD
0x07    8     version            00 01 00 01        4× big-endian uint16:
                                 00 03 00 00          major.minor.patch+build = 1.1.3+0
0x0F    4     sku                00 06 00 01        Packed bitfield (see below)
0x13    45    padding            all zeros
```

### SKU Bitfield Encoding

```
sku_raw = (byte[15] << 24) | (byte[16] << 16) | (byte[17] << 8) | byte[18]
sku_number  = (sku_raw >> 14) & 0x3FF   // product number
sku_type    = (sku_raw >> 10) & 0xF     // 0="AS", nonzero="??"
sku_variant = sku_raw & 0x3FF           // variant number
sku_string  = "TE" + sku_number.padStart(3) + sku_type + sku_variant.padStart(3)
// CH-8: TE024AS001
```

### Firmware Type Field

| Type | Inner Header | Payload | Products |
|------|-------------|---------|----------|
| 0 | BEEF CAFE at 0x40 (1088 bytes metadata) | Encrypted from 0x480 | EP-133, TX-6, OP-1 Field, etc. |
| 2 | None | Encrypted from 0x40 | CH-8 |

### BEEF CAFE Inner Header (Type 0 only, not present in CH-8)

Products with `firmware_type=0` have a second header at 0x40:

```
Offset  Content
0x0040  BEEF CAFE — inner header magic
0x0044  inner type (1 byte)
0x0045  payload size (3 bytes, big-endian)
0x0048  hash/metadata
0x0080  more metadata (hash at 0x80, sizes at 0x88/0x8C)
0x00A0  padding (zeros)
0x0480  encrypted firmware payload begins
```

### Encryption

ALL .tfw payloads are encrypted regardless of firmware_type. Confirmed by entropy analysis:

| Product | firmware_type | Payload Entropy | Verdict |
|---------|--------------|-----------------|---------|
| CH-8 v1.1.3 | 2 | 7.9996 bits/byte | Encrypted |
| EP-133 v2.0.5 | 0 | 7.9194 bits/byte | Encrypted |
| TX-6 v1.3.3 | 0 | ~7.9 bits/byte | Encrypted |

(8.0 = perfectly random = strong encryption. Unencrypted ARM firmware typically shows 5-6 bits/byte.)

The decryption key is stored in the bootloader on the nRF52840. The web updater JS sends the encrypted payload as-is to the device — no decryption happens on the computer side. The .tfw file cannot be decrypted without dumping the bootloader via SWD.

### Firmware Releases JSON

All TE firmware URLs (except CH-8) are discoverable at:
```
https://teenage.engineering/_software/releases.json
```

---

## TE DFU Protocol (Reverse-Engineered from Web Updater JS)

The web updater uses MIDI SysEx over USB to flash firmware — NOT the CDC-ACM serial port. This protocol is used by products listed in the web updater (EP-133, TX-6, etc.) but NOT the CH-8, which uses USB mass storage instead.

Documented here for reference and potential future use:

### Transport

TE proprietary SysEx over USB MIDI. SysEx group ID: 3 (DFU).

### Commands

| ID | Name | Direction | Payload | Description |
|----|------|-----------|---------|-------------|
| 1 | DFU_ENTER | Host→Device | none | Enter DFU/bootloader mode |
| 2 | DFU_BEGIN | Host→Device | version(8) + 0xB0 + sku(4) + size(4) + type(1) | Start transfer, negotiate chunk size |
| 3 | DFU_CHUNK | Host→Device | chunk_number(1) + data(N) | Send firmware data chunk |
| 4 | DFU_PERFORM | Host→Device | none | Execute the firmware update |
| 5 | DFU_EXIT | Host→Device | none | Exit DFU mode, reboot |
| 64 | DFU_ENTER_RESPONSE_READY | Device→Host | none | Device ready for in-app update |
| 127 | BAD_REQUEST | Device→Host | none | Error response |

### Chunk Size Negotiation

Device responds to DFU_BEGIN with a 2-byte max chunk size. Host calculates:
```
actual_chunk_size = Math.ceil(negotiated_size * (7/8)) - 12
```
The 7/8 ratio accounts for MIDI's 7-bit encoding of 8-bit data. Default chunk size is 235 bytes.

### Flow

```
1. Host sends DFU_BEGIN with firmware metadata
2. Device responds with max chunk size (or DFU_ENTER_RESPONSE_READY)
3. If device responds with error status 3:
   a. Host waits for device to enter bootloader mode
   b. Host retries DFU_BEGIN
4. Host sends DFU_CHUNK packets sequentially (chunk_number wraps at 256)
5. Host sends DFU_PERFORM
6. Device processes update, sends progress via callback
7. Host sends DFU_EXIT
8. Device reboots, host waits for reconnection
9. Host verifies new firmware version matches expected
```

---

## USB Mass Storage

The mass storage interface presents a 1 MB FAT12 virtual disk containing:

- `version.txt` — product info, serial, firmware version
- `readme.txt` — firmware upgrade instructions

The drive mounts on macOS as `/Volumes/{DOLL_NAME}` (e.g., `/Volumes/GIESELA`) with full read/write access. Firmware updates are done by copying a `.tfw` file to the drive.

### Disk Details (verified from Giesela, 2026-03-21)

| Field | Value |
|-------|-------|
| Device Name | TEENAGE USB DISK |
| Volume Name | GIESELA |
| Filesystem | MS-DOS FAT12 |
| Total Size | 1.0 MB (1,016,320 bytes, 1985 sectors × 512) |
| Used | 210 KB (21%) |
| Free | 802 KB (79%) |
| Block Size | 512 bytes |
| macOS Device | /dev/disk5 |

---

## CDC-ACM Serial Port

The device exposes a serial port at `/dev/cu.usbmodem01`. Extensive probing (2026-03-21) confirmed it is completely unresponsive:

### What Was Tested

| Test | Baud Rates | Result |
|------|-----------|--------|
| Text commands (help, version, AT) | 9600 | No response |
| CRLF / null byte | 9600, 115200 | No response |
| ACK/NAK bytes | 9600 | No response |
| Nordic SLIP DFU protocol | 9600, 115200 | No response |
| Nordic DFU opcodes (raw) | 9600 | No response |
| DTR/RTS toggle | 115200 | No response |
| All baud rates | 1200–921600 | No response or pending data at any rate |

The CDC-ACM port appears to be part of the composite USB device descriptor but is not actively used by the CH-8 bootloader. The CH-8 is not listed in the TE web updater's compatible devices (which use MIDI SysEx DFU over this port for other products).

---

## Firmware Update Path (CH-8 Specific)

The CH-8 uses USB mass storage for firmware updates (not MIDI SysEx DFU like other TE products):

1. Plug doll in via USB-C — mounts as `/Volumes/{DOLL_NAME}`
2. Copy `.tfw` file to root of the drive
3. Safely eject
4. Unplug USB cable
5. Press and hold button for 2 seconds (LED turns on)
6. Wait ~1 minute for upgrade (LED turns off when done)

---

## MIDI Over BLE — Control Interface

When connected via BLE MIDI (pair PIN: 000000):

| CC | Function | Notes |
|----|----------|-------|
| CC1 | Vibrato | Most noticeable on longer notes |
| CC2 | Consonant selection | Maps CC value to specific consonant phoneme |
| CC3 | Vowel selection | Maps CC value to specific vowel phoneme |
| CC4 | Reverb duration | Most noticeable on longer notes |

- Voicing changes take effect on the NEXT note only (not mid-note)
- Notes are auto-distributed across active dolls in the ensemble
- Any subset of dolls works (even a single doll for solo)
- Compatible with: OP-1 Field, OP-Z, iPad, MacBook, any BLE MIDI device

---

## Stock Repertoire (22 Songs)

1. Ernest Ball, Dave Reed Jr. — Love Me, and the World Is Mine
2. Tom Pitts, Raymond Egan, Roy Marsh — I Never Knew
3. Wilhelm Stenhammar — Sverige
4. Theodore Morse, Henry Buck — Dear Old Girl
5. Robert Schumann, Friedrich Rückert — Gute Nacht
6. Harry Armstrong, Richard Gerard Husch — Sweet Adeline
7. Trad. European — Warm-Up Exercise: Signore
8. Al Piantadosi, Joe McCarthy — In All My Dreams, I Dream of You
9. Trad. Israel Kolmodin — Den Blomstertid Nu Kommer
10. Trad. American Folk — I've Been Working on the Railroad
11. Mykola Leontovych — Shchedryk (Carol of the Bells)
12. Trad. via Robert Burns — Auld Lang Syne
13. Thomas Morley — Now Is the Month of Maying
14. Trad. Medieval — Gaudeamus Igitur
15. Trad. European — Warm-Up Exercise: Zing-a-Mama
16. Shelton Brooks — The Darktown Strutters' Ball
17. Ludwig van Beethoven — An die Freude
18. Charles Wood, Thomas Oliphant — Deck the Halls
19. Adolf Fredrik Lindblad — En Sommarafton
20. Pierre Attaingnant, César Geoffray — Tourdion
21. Les Applegate — Goodbye My Coney Island Baby
22. Johann Sebastian Bach — O Haupt voll Blut und Wunden

Songs are generated using an algorithm based on **counterpoint melody** — independent but complementary melodic lines played simultaneously across the voice parts.

---

## Custom Firmware Project — Vision

### What We Want to Build

1. **Custom firmware** for the nRF52840 that:
   - Retains all 22 stock songs
   - Adds a "user songs" bank stored in a separate flash region
   - Exposes a BLE service for uploading new songs from the companion app
   - Maintains all existing functionality (gesture control, BLE MIDI, inter-doll sync)

2. **Companion app** (iOS/Android or web) that:
   - Imports audio files (MP3, WAV, MIDI)
   - Transcribes/arranges into multi-voice counterpoint notation compatible with the Choir's synthesis engine
   - Assigns voice parts across the 8 dolls based on their vocal ranges
   - Uploads composed songs to the dolls via BLE
   - Provides a conductor interface for real-time performance control

---

## Plan of Attack

### Phase 1: Flash Dump & Initial Analysis (J-Link arrives)

**Goal:** Get the raw firmware binary off the chip and understand the high-level structure.

**Critical risk:** If TE enabled APPROTECT (nRF52840's flash read-protection), SWD reads will fail. This is the go/no-go gate for the entire project. APPROTECT can be bypassed with voltage glitching, but that's a significant escalation in difficulty and equipment.

#### Steps

1. **Identify SWD pads on the board**
   - Open the sound module (unscrew speaker lid)
   - Locate the circular test pads on the upper board
   - Identify SWDIO, SWCLK, VCC, GND (minimum 4 pads needed)
   - Photograph and document pad layout

2. **Connect J-Link EDU Mini**
   - Use pogo pin probes or fine-tip test clips on the SWD pads
   - Connect J-Link to Mac via USB
   - Install nRF Command Line Tools (`nrfjprog`) and nRF Connect for Desktop

3. **Check APPROTECT status**
   ```bash
   nrfjprog --recover   # attempts to connect and read protection status
   nrfjprog --readregs   # read CPU registers (will fail if protected)
   ```
   - If APPROTECT is enabled: registers read as zero, flash reads return 0xFF
   - If APPROTECT is disabled: we're in business

4. **Dump the full 1 MB flash**
   ```bash
   nrfjprog --readcode --file ch8_flash_dump.hex
   nrfjprog --readcode --file ch8_flash_dump.bin --format bin
   ```
   - Also dump UICR (User Information Configuration Registers):
   ```bash
   nrfjprog --readuicr --file ch8_uicr.hex
   ```

5. **Dump RAM snapshot** (optional, captures runtime state)
   ```bash
   nrfjprog --readram --file ch8_ram_dump.bin
   ```

6. **Back up everything before touching anything else**
   - Store `ch8_flash_dump.bin`, `ch8_uicr.hex`, `ch8_ram_dump.bin`
   - These are your golden copies — never modify them

### Phase 2: Firmware Analysis (Ghidra)

**Goal:** Understand the firmware structure, find the song data, map the synthesis engine.

1. **Load into Ghidra**
   - Create new project, import `ch8_flash_dump.bin`
   - Processor: ARM Cortex-M4 (little-endian)
   - Base address: 0x00000000 (nRF52840 flash starts here)
   - Auto-analyze

2. **Identify the vector table**
   - First 4 bytes: initial stack pointer (expect ~0x20040000)
   - Next 4 bytes: reset handler address
   - Map all interrupt vectors

3. **Map the flash layout**
   - Bootloader region (typically first 16-64 KB)
   - Application region (main firmware)
   - Song data region (look for large data blocks with musical structure)
   - BLE SoftDevice region (if using Nordic SoftDevice, typically 0x00000-0x26000)
   - Look for the .tfw decryption key in the bootloader

4. **Find the synthesis engine**
   - Search for I2C/TWI peripheral access (MAX98390 communication)
   - Look for audio buffer management (DMA, I2S, or PWM output)
   - Identify wavetable/formant/sample data
   - Map the phoneme system (consonant + vowel CC mapping suggests structured phoneme tables)

5. **Find the song data format**
   - Look for large structured data blocks in flash
   - 22 songs × multiple voice parts = significant data
   - Likely a custom notation format with timing, pitch, phoneme, and dynamics per voice
   - Cross-reference with BLE MIDI CC mappings (CC2=consonant, CC3=vowel)

6. **Map the BLE stack**
   - Identify if using Nordic SoftDevice or Zephyr BLE
   - Find the inter-doll sync protocol (BLE beacons)
   - Document the MIDI over BLE implementation
   - Look for any hidden SysEx commands

### Phase 3: Development Environment Setup

**Goal:** Be able to build and flash custom firmware.

1. **Install nRF Connect SDK + Zephyr toolchain**
   - Follow Nordic's getting started guide
   - Target: nRF52840 with custom board definition

2. **Create board definition for CH-8**
   - Pin mapping (from flash dump analysis): SWD, I2C (MAX98390), USB, BLE antenna, accelerometer, button, LED
   - Clock configuration
   - Memory layout matching the original

3. **Build minimal "hello world" firmware**
   - Blink LED or produce a simple tone through MAX98390
   - Flash via J-Link, verify it runs
   - **Keep the original flash dump to restore stock firmware**

4. **Incrementally add features**
   - Audio output (I2C to MAX98390)
   - BLE (MIDI + inter-doll sync)
   - Gesture control (accelerometer)
   - Song playback (using reverse-engineered format)
   - User song bank + BLE upload

### Phase 4: Companion App

**Goal:** Import, arrange, and upload songs to the dolls.

1. **MIDI import** — parse standard MIDI files, extract note data
2. **Voice assignment** — distribute notes across 8 dolls based on vocal ranges
3. **Phoneme mapping** — assign consonant/vowel phonemes to notes
4. **BLE upload** — send composed songs to dolls via custom BLE service
5. **Conductor mode** — real-time tempo/dynamics control

---

## Required Hardware

| Item | Purpose | Status | Cost |
|------|---------|--------|------|
| J-Link EDU Mini | SWD programmer for nRF52840 | Ordered | $20 |
| SWD pogo pin probes or test clips | Connect to board test pads | Need | $10-30 |
| nRF52840 DK (optional) | Safe development board | Consider later | $40 |
| Logic analyzer (optional) | Capture I2C traffic to MAX98390 | Consider later | $10-50 |

## Required Software (all free)

| Tool | Purpose | Install |
|------|---------|---------|
| nRF Connect for Desktop | J-Link interface, flash programmer | https://www.nordicsemi.com/Products/Development-tools/nRF-Connect-for-Desktop |
| nRF Command Line Tools | `nrfjprog` for scripted flash operations | https://www.nordicsemi.com/Products/Development-tools/nRF-Command-Line-Tools |
| Ghidra | ARM firmware disassembly and decompilation | https://ghidra-sre.org/ |
| nRF Connect SDK + Zephyr | Custom firmware development toolchain | https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/ |
| Wireshark | BLE and USB protocol capture | https://www.wireshark.org/ |

---

## Key Resources

| Resource | URL |
|----------|-----|
| Choirama (community teardown) | https://github.com/jetztgradnet/Choirama |
| TE Firmware Releases JSON | https://teenage.engineering/_software/releases.json |
| TE Web Updater JS (contains DFU protocol) | https://teenage.engineering/apps/update/assets/index-0vVGeHxM.js |
| TE Downloads (CH-8) | https://teenage.engineering/downloads |
| nRF52840 Product Page | https://www.nordicsemi.com/Products/nRF52840 |
| nRF52840 Datasheet | https://infocenter.nordicsemi.com/pdf/nRF52840_PS_v1.1.pdf |
| nRF Connect SDK | https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/ |
| MAX98390 Datasheet | https://www.analog.com/en/products/max98390.html |
| TE Firmware RE Blog | https://wmealing.github.io/reverse-engineering-teenage-engineering.html |
| Nordic DFU over Serial | https://infocenter.nordicsemi.com/topic/sdk_nrf5_v16.0.0/lib_dfu_transport_serial.html |

---

## Files

| File | Purpose |
|------|---------|
| `choir-firmware-1.1.3.tfw` | Stock firmware v1.1.3 (485,230 bytes, encrypted) |
| `choir-user-guide.pdf` | Official TE user guide |
| `choir-info.md` | Detailed product research and teardown notes |
| `choir-homepage.md` | TE product page content |
| `choir-custom-firmware-project.md` | This document |

---

## What We Know vs What We Don't

### Known (confirmed)

- Complete .tfw header format (from JS reverse engineering)
- .tfw payload is encrypted on ALL TE products (entropy analysis)
- Decryption happens on-device in the bootloader, not in the updater
- CH-8 uses firmware_type=2 (no inner header, encrypted from byte 64)
- Full TE MIDI SysEx DFU protocol (from JS, but CH-8 uses USB mass storage instead)
- CDC-ACM serial port is unresponsive (exhaustively tested)
- USB mass storage works with full read/write access
- BLE MIDI CC mappings for phoneme control
- Giesela: firmware 1.1.3+0, serial S3DPQ1NT

### Unknown (need SWD dump to determine)

- Flash layout (bootloader size, app region, song data location)
- RTOS (Zephyr, Nordic SDK bare-metal, or something else)
- Synthesis engine type (formant, wavetable, sample-based)
- Song data format (notation structure, timing, phoneme encoding)
- Inter-doll BLE sync protocol details
- Whether APPROTECT is enabled (the #1 risk)
- I2C configuration for MAX98390 amplifier
- Accelerometer model and I2C address
- .tfw decryption algorithm and key

---

## Session Log

### 2026-03-21: Initial Analysis

- Verified Giesela connected: USB mass storage at `/Volumes/GIESELA`, serial at `/dev/cu.usbmodem01`
- Confirmed full read/write access to USB drive
- Analyzed .tfw header: BABE CAFE magic, firmware_type=2, version 1.1.3+0, SKU TE024AS001
- Measured payload entropy: 7.9996 bits/byte (encrypted)
- Downloaded and compared EP-133 and TX-6 firmware: all payloads encrypted regardless of firmware_type
- Reverse-engineered TE web updater JavaScript: found complete Firmware class and DFU protocol
- Decoded .tfw header field layout from JS source (firmware_type, checksum, version, sku bitfield)
- Documented full MIDI SysEx DFU protocol (5 commands, chunk negotiation, 7-bit encoding)
- Confirmed CH-8 is NOT in web updater compatible devices list (uses USB mass storage path)
- Exhaustively probed CDC-ACM serial port: no response at any baud rate or protocol
- Confirmed .tfw cannot be decrypted without SWD access to bootloader
- Ordered J-Link EDU Mini

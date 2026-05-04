---
inclusion: always
---
# Core Development Workflow

## Golden Rules

1. **Never flash without a backup** — Always have a verified flash dump before writing anything to the nRF52840
2. **Git is source of truth** — All code, analysis notes, scripts, and board definitions live in the repo
3. **Document as you go** — Update `TE-Files/choir-custom-firmware-project.md` session log with every discovery
4. **One doll at a time** — Develop and test on a single doll (Giesela) before touching others
5. **Stock firmware is sacred** — Keep `choir-firmware-1.1.3.tfw` and the raw flash dump untouched as golden copies

## J-Link EDU Mini & SWD

### Hardware Setup

- Debug probe: Segger J-Link EDU Mini (USB)
- Target: nRF52840 SWD pads on CH-8 sound module PCB
- Connection: Pogo pins or fine-tip test clips on SWDIO, SWCLK, VCC, GND pads
- The sound module must be removed from the wooden doll body and the speaker lid unscrewed to access the board

### Software Requirements

| Tool | Purpose | Install |
|------|---------|---------|
| nRF Command Line Tools | `nrfjprog` for flash read/write/erase | `brew install --cask nordic-nrf-command-line-tools` or from Nordic website |
| J-Link Software | J-Link drivers and GDB server | Bundled with nRF Command Line Tools, or from Segger |
| nRF Connect for Desktop | GUI for J-Link operations | https://www.nordicsemi.com/Products/Development-tools/nRF-Connect-for-Desktop |

### Critical First Step: APPROTECT Check

**This is the go/no-go gate for the entire project.**

The nRF52840 has hardware flash read-protection (APPROTECT). If TE enabled it:
- SWD reads return 0xFF (all ones)
- Register reads return zero
- Flash cannot be dumped without voltage glitching (major escalation)

```bash
# Check if we can talk to the chip at all
nrfjprog --readregs

# Attempt recovery (will indicate protection status)
nrfjprog --recover
```

If APPROTECT is enabled, `--recover` will erase the entire chip to disable protection — which destroys the firmware. Do NOT run `--recover` unless you understand this tradeoff.

### Flash Dump Procedure

Once SWD access is confirmed:

```bash
# Dump full 1 MB flash (Intel HEX and raw binary)
nrfjprog --readcode --file ch8_flash_dump.hex
nrfjprog --readcode --file ch8_flash_dump.bin --format bin

# Dump UICR (User Information Configuration Registers)
nrfjprog --readuicr --file ch8_uicr.hex

# Optional: RAM snapshot (captures runtime state)
nrfjprog --readram --file ch8_ram_dump.bin
```

**Store all dumps in a `dumps/` directory. These are golden copies — never modify the originals.**

### Restoring Stock Firmware

If something goes wrong, restore from the flash dump:

```bash
# Write back the full flash dump
nrfjprog --program ch8_flash_dump.hex --chiperase
nrfjprog --reset
```

Or use the USB mass storage method (copy .tfw file to mounted drive).

## Git Workflow

Standard git flow. Nothing exotic.

```bash
git add <files>
git commit -m "descriptive message"
git pull --rebase
git push
```

### Commit Message Conventions

- `dump:` — Flash dump related (new dumps, analysis of dump data)
- `analysis:` — Ghidra findings, protocol reverse engineering
- `firmware:` — Custom firmware code changes
- `tools:` — Helper scripts, analysis tools
- `docs:` — Documentation updates
- `app:` — Companion app changes

## Project Directory Structure

```
Choir-Practice/
├── TE-Files/              # Reference materials (read-only after initial setup)
│   ├── choir-custom-firmware-project.md   # Master project doc + session log
│   ├── choir-firmware-1.1.3.tfw           # Stock firmware (encrypted)
│   ├── choir-info.md                      # Hardware research
│   ├── choir-homepage.md                  # TE product page
│   └── choir-user-guide.pdf              # Official guide
├── dumps/                 # Flash dumps from J-Link (golden copies, do not modify)
├── analysis/              # Ghidra project files, annotated disassembly, notes
├── firmware/              # Custom firmware source (nRF Connect SDK / Zephyr)
├── tools/                 # Helper scripts (hex analysis, BLE sniffing, etc.)
├── app/                   # Companion app source
└── .kiro/steering/        # These steering docs
```

Create directories as needed — don't pre-create empty ones.

## Analysis Tools & Workflow

### Ghidra (Firmware Disassembly)

- Processor: ARM Cortex-M4 (little-endian)
- Base address: 0x00000000 (nRF52840 flash origin)
- Look for vector table at 0x00000000 (initial SP + reset handler)
- nRF52840 memory map: flash 0x00000000–0x000FFFFF, RAM 0x20000000–0x2003FFFF

### Useful nrfjprog Commands

```bash
nrfjprog --ids                    # List connected J-Link serial numbers
nrfjprog --deviceversion          # Confirm nRF52840
nrfjprog --memrd 0x00000000 --n 256   # Read first 256 bytes of flash
nrfjprog --memrd 0x10001208 --n 4     # Read APPROTECT register
nrfjprog --readregs               # Dump CPU registers
nrfjprog --pinresetenable         # Enable pin reset (if needed)
```

### Hex/Binary Analysis

```bash
# Quick entropy check on a binary
python3 -c "
import math, sys
data = open(sys.argv[1],'rb').read()
freq = [0]*256
for b in data: freq[b] += 1
ent = -sum((c/len(data))*math.log2(c/len(data)) for c in freq if c)
print(f'{ent:.4f} bits/byte ({len(data)} bytes)')
" <file>

# Hex dump first 256 bytes
xxd -l 256 <file>

# Search for ASCII strings in binary
strings -n 6 <file>
```

## Safety Checklist

Before any write operation to the nRF52840:

- [ ] Flash dump exists and is verified (read back and compare)
- [ ] UICR dump exists
- [ ] Stock .tfw file is backed up
- [ ] Working on the designated test doll (Giesela) only
- [ ] Changes are committed to git before flashing

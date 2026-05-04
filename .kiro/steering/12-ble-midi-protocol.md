---
inclusion: always
---

# BLE & MIDI Protocol Reference

## BLE MIDI Control

Pair PIN: `000000` (six zeros). Connecting one doll pairs the whole ensemble.

### MIDI CC Mappings

| CC | Function | Notes |
|----|----------|-------|
| CC1 | Vibrato | Most noticeable on longer notes |
| CC2 | Consonant selection | Maps CC value to specific consonant phoneme |
| CC3 | Vowel selection | Maps CC value to specific vowel phoneme |
| CC4 | Reverb duration | Controls reverb tail length |

- Voicing changes take effect on the NEXT note only (not mid-note)
- Notes are auto-distributed across active dolls in the ensemble
- Any subset of dolls works (single doll = solo performance)
- Compatible controllers: OP-1 Field, OP-Z, iPad, any BLE MIDI device

### Phoneme System

The CC2 (consonant) and CC3 (vowel) mappings suggest a structured phoneme table in firmware. The full mapping tables are documented in the Choirama repo. This is key to understanding the synthesis engine — the dolls don't play back audio samples, they synthesize speech-like sounds from phoneme parameters.

## Inter-Doll BLE Sync

Dolls communicate via BLE beacons to:
- Discover which ensemble members are in range
- Synchronize tempo and song position
- Distribute voice parts across available dolls

Protocol details are unknown until we can analyze the firmware. Look for:
- Custom BLE advertisement data in the firmware dump
- Beacon payload structure (likely includes doll ID, current song, beat position)
- Sync algorithm (leader election? fixed conductor? round-robin?)

## Known BLE Quirks

- Choir sometimes reverts to built-in repertoire even when MIDI-connected (likely a bug)
- Members occasionally fall out of sync — sometimes self-corrects, sometimes needs power cycle
- These bugs may be fixable in custom firmware once we understand the sync protocol

## USB MIDI (Not Used by CH-8)

The TE web updater uses MIDI SysEx over USB for DFU on other products (EP-133, TX-6, etc.), but the CH-8 uses USB mass storage instead. The SysEx DFU protocol is documented in `TE-Files/choir-custom-firmware-project.md` for reference but is not relevant to CH-8 firmware updates.

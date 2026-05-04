#!/usr/bin/env python3
"""Generate a test MIDI file matching CH-8 song format.

Format (from disk image analysis):
- MIDI format 1, 6 tracks, 192 tpqn
- Track 0: tempo/conductor track (short)
- Tracks 1-5: voice parts with note-on channel 4 (0x94) + lyric events (FF 05)
- Phonemes as MIDI Lyric meta-events before each note
"""
import struct
import os


def var_len(value):
    """Encode a value as MIDI variable-length quantity."""
    result = []
    result.append(value & 0x7F)
    value >>= 7
    while value:
        result.append((value & 0x7F) | 0x80)
        value >>= 7
    result.reverse()
    return bytes(result)


def make_track(events):
    """Build an MTrk chunk from a list of (delta_time, event_bytes) tuples."""
    data = b""
    for delta, event in events:
        data += var_len(delta) + event
    return b"MTrk" + struct.pack(">I", len(data)) + data


def lyric_event(text):
    """Create a MIDI Lyric meta-event (FF 05 len text)."""
    encoded = text.encode("ascii")
    return b"\xff\x05" + var_len(len(encoded)) + encoded


def note_on(channel, note, velocity):
    """MIDI note-on event."""
    return bytes([0x90 | (channel & 0x0F), note & 0x7F, velocity & 0x7F])


def note_off(channel, note, velocity=0):
    """MIDI note-off (note-on with velocity 0)."""
    return bytes([0x90 | (channel & 0x0F), note & 0x7F, velocity & 0x7F])


def end_of_track():
    """MIDI End of Track meta-event."""
    return b"\xff\x2f\x00"


def tempo_event(bpm):
    """MIDI Set Tempo meta-event."""
    uspqn = int(60_000_000 / bpm)
    return b"\xff\x51\x03" + struct.pack(">I", uspqn)[1:]


def main():
    TPQN = 192  # ticks per quarter note
    CHANNEL = 4  # channel 4 (0-indexed), matching 0x94 note-on
    BPM = 100

    # Simple C major scale melody using recovered phonemes
    # Each entry: (phoneme, midi_note, duration_in_quarter_notes)
    # Using notes in a mid range that all dolls can handle
    melody = [
        ("lA", 60, 1.0),  # C4
        ("lA", 62, 1.0),  # D4
        ("lA", 64, 1.0),  # E4
        ("lA", 65, 1.0),  # F4
        ("lA", 67, 2.0),  # G4
        ("lA", 65, 1.0),  # F4
        ("lA", 64, 1.0),  # E4
        ("lA", 62, 1.0),  # D4
        ("lA", 60, 2.0),  # C4
    ]

    # Track 0: conductor (tempo + end)
    track0_events = [
        (0, tempo_event(BPM)),
        (0, end_of_track()),
    ]

    # Track 1: the melody on channel 4 with lyric events
    track1_events = []
    for phoneme, note, dur in melody:
        ticks = int(dur * TPQN)
        track1_events.append((0, lyric_event(phoneme)))
        track1_events.append((0, note_on(CHANNEL, note, 90)))
        track1_events.append((ticks, note_off(CHANNEL, note, 0)))
    track1_events.append((0, end_of_track()))

    # Tracks 2-5: empty voice parts (just end-of-track)
    # The real songs have 6 tracks; we'll keep the structure but leave parts empty
    empty_track_events = [
        (0, end_of_track()),
    ]

    # Build the MIDI file
    # MThd: format 1, 6 tracks, 192 tpqn
    header = b"MThd" + struct.pack(">IHHH", 6, 1, 6, TPQN)

    tracks = [
        make_track(track0_events),
        make_track(track1_events),
        make_track(empty_track_events),
        make_track(empty_track_events),
        make_track(empty_track_events),
        make_track(empty_track_events),
    ]

    midi_data = header + b"".join(tracks)

    os.makedirs("dumps/test_midi", exist_ok=True)
    outpath = "dumps/test_midi/test_song.mid"
    with open(outpath, "wb") as f:
        f.write(midi_data)

    print("Written: {} ({} bytes)".format(outpath, len(midi_data)))
    print("Format: 1, Tracks: 6, TPQN: {}".format(TPQN))
    print("Tempo: {} BPM, Channel: {}".format(BPM, CHANNEL))
    print("Notes: {} melody notes with '{}' phoneme".format(len(melody), melody[0][0]))

    # Verify by hex dumping the header
    print("\nHex header:")
    for i in range(0, min(64, len(midi_data)), 16):
        hex_part = " ".join("{:02x}".format(b) for b in midi_data[i : i + 16])
        ascii_part = "".join(
            chr(b) if 32 <= b < 127 else "." for b in midi_data[i : i + 16]
        )
        print("  {:04X}: {}  {}".format(i, hex_part, ascii_part))


if __name__ == "__main__":
    main()

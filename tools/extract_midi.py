#!/usr/bin/env python3
"""Extract MIDI files from CH-8 USB disk image unallocated space."""
import sys
import os


def extract_midi_files(img_path, output_dir):
    data = open(img_path, "rb").read()
    os.makedirs(output_dir, exist_ok=True)

    # Find all MThd headers
    positions = []
    offset = 0
    while True:
        idx = data.find(b"MThd", offset)
        if idx == -1:
            break
        positions.append(idx)
        offset = idx + 1

    print(f"Found {len(positions)} MIDI file headers")

    for i, start in enumerate(positions):
        # Parse MThd
        if start + 14 > len(data):
            continue
        header_len = int.from_bytes(data[start + 4 : start + 8], "big")
        fmt = int.from_bytes(data[start + 8 : start + 10], "big")
        num_tracks = int.from_bytes(data[start + 10 : start + 12], "big")
        tpqn = int.from_bytes(data[start + 12 : start + 14], "big")

        print(
            f"\nMIDI #{i+1} at 0x{start:06X}: format={fmt}, tracks={num_tracks}, tpqn={tpqn}"
        )

        # Walk through all tracks to find end of file
        pos = start + 8 + header_len
        tracks_found = 0
        lyrics = []

        for t in range(num_tracks):
            if pos + 8 > len(data):
                break
            if data[pos : pos + 4] != b"MTrk":
                print(f"  WARNING: Expected MTrk at 0x{pos:06X}, got {data[pos:pos+4]}")
                break
            track_len = int.from_bytes(data[pos + 4 : pos + 8], "big")

            # Extract lyric events from this track
            track_data = data[pos + 8 : pos + 8 + track_len]
            j = 0
            while j < len(track_data):
                if (
                    j + 2 < len(track_data)
                    and track_data[j] == 0xFF
                    and track_data[j + 1] == 0x05
                ):
                    # Lyric meta-event
                    j += 2
                    length = track_data[j]
                    j += 1
                    lyric = track_data[j : j + length]
                    try:
                        lyrics.append(lyric.decode("ascii", errors="replace"))
                    except:
                        pass
                    j += length
                else:
                    j += 1

            pos = pos + 8 + track_len
            tracks_found += 1

        if tracks_found == num_tracks:
            file_size = pos - start
            midi_data = data[start:pos]
            filename = f"ch8_song_{i+1:02d}.mid"
            filepath = os.path.join(output_dir, filename)
            open(filepath, "wb").write(midi_data)
            print(f"  Extracted: {filename} ({file_size} bytes, {tracks_found} tracks)")
            if lyrics:
                # Show first few unique lyrics
                unique = list(dict.fromkeys(lyrics))[:20]
                print(f"  Lyrics: {' '.join(unique)}")
        else:
            print(f"  INCOMPLETE: only found {tracks_found}/{num_tracks} tracks")


if __name__ == "__main__":
    extract_midi_files("dumps/miki_usb_disk.img", "dumps/extracted_midi")

# splitsmf

`splitsmf` is a Python tool designed to bypass the 16-channel MIDI limitation. It analyzes Standard MIDI Files (SMF) where instruments (Program Changes) switch mid-track within a single channel and automatically splits them into separate files.

## Overview
Most MIDI sound sources and DAWs are restricted to 16 channels per port. To reproduce songs with more than 16 parts, composers often alternate multiple instruments on a single channel (e.g., Violin in the first half, Saxophone in the middle, and returning to Violin in the last half).

`splitsmf.py` automatically detects these "interruption parts" (like the Saxophone in the example) and extracts them into separate `extra` files.

### Output Files
* **Main Output (`*_cleaned.mid`)**: A file that retains only the "initial instrument" for each channel and removes any interrupting parts.
* **Extra Output (`*_extra1.mid`, `*_extra2.mid`, ...)**: One or more files containing only the extracted interrupting parts. If the number of unique interrupting parts exceeds the capacity of a single MIDI file, additional files are created sequentially.

## Features
* **CC Tracking**: The tool analyzes the state of Volume (CC7), Pan (CC10), Expression (CC11), and other controllers immediately before an interrupting part begins. These values are automatically inserted at the beginning of the extracted part, ensuring the musical balance remains intact.
* **SysEx Preservation**: System Exclusive messages are preserved in the main (`_cleaned.mid`) file.
* **Automatic Channel Allocation**:
    * Extracted parts are automatically assigned to available channels in the `extra` files.
    * **Channel 10 is always skipped** to reserve it for drum tracks in standard setups.
    * If the number of extracted parts exceeds 15 (the capacity of one file, skipping Ch10), a new file (`_extra2.mid`, `_extra3.mid`, etc.) is automatically created.

## Execution Results
After running the tool, the following files are generated:

* `your_song_cleaned.mid`: The main part (retaining the original channel structure).
* `your_song_extra1.mid`: The first set of extracted sub-parts.
* `your_song_extra2.mid` (if needed): The next set of extracted sub-parts.
* ...and so on.

## Logic Details
1. **Base Program Identification**: The first `Program Change` encountered on each channel is recognized as the "Base Instrument" for that channel.
2. **Section Extraction**: Any duration where a different `Program Change` is active is marked as an "Extra Section."
3. **Restoration**: When the `Program Change` returns to the Base Instrument, recording to the main part resumes.
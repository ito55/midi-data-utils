# splitsmf

`splitsmf` is a Python tool designed to bypass the 16-channel MIDI limitation. It analyzes Standard MIDI Files (SMF) where instruments (Program Changes) switch mid-track within a single channel and automatically splits them into separate files per instrument.

## Overview
Most MIDI sound sources and DAWs are restricted to 16 channels per port. To reproduce songs with more than 16 parts, composers often alternate multiple instruments on a single channel (e.g., Violin in the first half, Saxophone in the middle, and returning to Violin in the last half).

`splitsmf.py` automatically detects these "interruption parts" (like the Saxophone in the example) and extracts them into a separate file.

### Output Files
* **Main Output (`*_cleaned.mid`)**: A file that retains only the "initial instrument" for each channel and removes any interrupting parts.
* **Extra Output (`*_extra1.mid`)**: A file containing only the extracted interrupting parts, repacked into channels starting from Ch 1.

## Features
* **CC Tracking**: The tool analyzes the state of Volume (CC7), Pan (CC10), Expression (CC11), and other controllers immediately before an interrupting part begins. These values are automatically inserted at the beginning of the extracted file, ensuring the musical balance remains intact.
* **SysEx Preservation**: System Exclusive messages are preserved at the beginning of the master (cleaned) file.
* **Automatic Channel Allocation**: Extracted parts are automatically assigned to available channels (starting from Ch 1) within the new file.

## Execution Results
After running the tool, the following files are generated:

* `your_song_cleaned.mid`: The main part (retaining the original channel structure).
* `your_song_extra1.mid`: The extracted sub-parts (arranged starting from Ch 1).

## Logic Details
1. **Base Program Identification**: The first `Program Change` encountered on each channel is recognized as the "Base Instrument" for that channel.
2. **Section Extraction**: Any duration where a different `Program Change` is active is marked as an "Extra Section."
3. **Restoration**: When the `Program Change` returns to the Base Instrument, recording to the main part resumes.
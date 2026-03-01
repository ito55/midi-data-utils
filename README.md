# midi-data-utils

**Python utilities for MIDI data analysis and format conversion (SMF/MusicXML/XF).**

## Overview
This repository is a consolidated collection of tools designed to analyze, convert, and generate MIDI-related data. By bringing these utilities together, this project aims to provide a unified environment for music data processing and facilitate the sharing of common logic between different MIDI workflows.

## Included Utilities

### 1. midi song note range analyzer
A diagnostic tool that scans MIDI files to determine the pitch range (lowest and highest note numbers). This is useful for verifying if a song fits within the vocal range of a singer or the physical range of a specific instrument.

### 2. smf musicxml to xf converter
A powerful generator that merges Standard MIDI Files (SMF) with MusicXML data. It produces Yamaha XF-format MIDI files that include rich metadata such as lyrics and chord names.

### 3. xf to musicxml converter
A specialized converter that extracts lead-sheet information from Yamaha XF-format MIDI files and outputs it as MusicXML. It allows for the conversion of MIDI-based performance data back into readable sheet music.


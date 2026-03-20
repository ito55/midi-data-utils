import sys
import os
import mido
from mido import MidiFile, MidiTrack, Message

# 追従させる主要なコントロールチェンジ番号
TRACKED_CC = [7, 10, 11, 64, 91, 93] # Volume, Pan, Expression, Sustain, Reverb, Chorus

GM_INSTRUMENTS = [
    "Acoustic Grand Piano", "Bright Acoustic Piano", "Electric Grand Piano", "Honky-tonk Piano",
    "Electric Piano 1", "Electric Piano 2", "Harpsichord", "Clavinet",
    "Celesta", "Glockenspiel", "Music Box", "Vibraphone",
    "Marimba", "Xylophone", "Tubular Bells", "Dulcimer",
    "Drawbar Organ", "Percussive Organ", "Rock Organ", "Church Organ",
    "Reed Organ", "Accordion", "Harmonica", "Tango Accordion",
    "Acoustic Guitar (nylon)", "Acoustic Guitar (steel)", "Electric Guitar (jazz)", "Electric Guitar (clean)",
    "Electric Guitar (muted)", "Overdriven Guitar", "Distortion Guitar", "Guitar Harmonics",
    "Acoustic Bass", "Electric Bass (finger)", "Electric Bass (pick)", "Fretless Bass",
    "Slap Bass 1", "Slap Bass 2", "Synth Bass 1", "Synth Bass 2",
    "Violin", "Viola", "Cello", "Contrabass",
    "Tremolo Strings", "Pizzicato Strings", "Orchestral Harp", "Timpani",
    "String Ensemble 1", "String Ensemble 2", "SynthStrings 1", "SynthStrings 2",
    "Choir Aahs", "Voice Oohs", "Synth Voice", "Orchestra Hit",
    "Trumpet", "Trombone", "Tuba", "Muted Trumpet",
    "French Horn", "Brass Section", "SynthBrass 1", "SynthBrass 2",
    "Soprano Sax", "Alto Sax", "Tenor Sax", "Baritone Sax",
    "Oboe", "English Horn", "Bassoon", "Clarinet",
    "Piccolo", "Flute", "Recorder", "Pan Flute",
    "Blown Bottle", "Shakuhachi", "Whistle", "Ocarina",
    "Lead 1 (square)", "Lead 2 (sawtooth)", "Lead 3 (calliope)", "Lead 4 (chiff)",
    "Lead 5 (charang)", "Lead 6 (voice)", "Lead 7 (fifths)", "Lead 8 (bass + lead)",
    "Pad 1 (new age)", "Pad 2 (warm)", "Pad 3 (polysynth)", "Pad 4 (choir)",
    "Pad 5 (bowed)", "Pad 6 (metallic)", "Pad 7 (halo)", "Pad 8 (sweep)",
    "FX 1 (rain)", "FX 2 (soundtrack)", "FX 3 (crystal)", "FX 4 (atmosphere)",
    "FX 5 (brightness)", "FX 6 (goblins)", "FX 7 (echoes)", "FX 8 (sci-fi)",
    "Sitar", "Banjo", "Shamisen", "Koto",
    "Kalimba", "Bag pipe", "Fiddle", "Shanai",
    "Tinkle Bell", "Agogo", "Steel Drums", "Woodblock",
    "Taiko Drum", "Melodic Tom", "Synth Drum", "Reverse Cymbal",
    "Guitar Fret Noise", "Breath Noise", "Seashore", "Bird Tweet",
    "Telephone Ring", "Helicopter", "Applause", "Gunshot"
]

def get_instrument_name(pc):
    if 0 <= pc < len(GM_INSTRUMENTS):
        return GM_INSTRUMENTS[pc]
    return f"PC#{pc}"

def get_abs_messages(mid):
    """全メッセージを絶対時間(tick)付きのリストで取得"""
    messages = []
    for track in mid.tracks:
        abs_tick = 0
        for msg in track:
            abs_tick += msg.time
            messages.append({'tick': abs_tick, 'msg': msg.copy()})
    return sorted(messages, key=lambda x: x['tick'])

def create_extra_track(messages, base_name, extra_index):
    """抽出されたメッセージから新しいMIDIファイルを作成"""
    new_mid = MidiFile()
    track = MidiTrack()
    new_mid.tracks.append(track)
    
    # 時間順にソートし、デルタタイムに変換
    messages.sort(key=lambda x: x['tick'])
    last_tick = 0
    for m in messages:
        m['msg'].time = m['tick'] - last_tick
        track.append(m['msg'])
        last_tick = m['tick']
        
    out_name = f"{base_name}_extra{extra_index}.mid"
    new_mid.save(out_name)
    print(f"Generated: {out_name}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python splitsmf.py <filename.mid>")
        return

    input_path = sys.argv[1]
    base_name = os.path.splitext(input_path)[0]
    mid = MidiFile(input_path)
    ticks_per_beat = mid.ticks_per_beat

    # 全イベントを絶対時間で取得
    all_events = get_abs_messages(mid)

    # 状態管理
    ch_base_pc = {}     # {ch: initial_program}
    ch_current_cc = {ch: {cc: 0 for cc in TRACKED_CC} for ch in range(16)}
    ch_current_pc = {ch: 0 for ch in range(16)}
    
    # 統計・レポート用
    active_channels = set()
    ch_stats = {ch: {'main': set(), 'extra': set()} for ch in range(16)}

    cleaned_events = []
    extra_events_pool = [] # {tick, msg} のリスト

    # 1. 解析と分類
    for item in all_events:
        msg = item['msg']
        tick = item['tick']

        if msg.is_meta or msg.type == 'sysex':
            cleaned_events.append(item)
            continue

        ch = msg.channel
        active_channels.add(ch)
        
        # CCの状態を常に更新（追従用）
        if msg.type == 'control_change' and msg.control in TRACKED_CC:
            ch_current_cc[ch][msg.control] = msg.value
        
        # Program Change の処理
        if msg.type == 'program_change':
            if ch not in ch_base_pc:
                ch_base_pc[ch] = msg.program # 最初の音色を記録
            ch_current_pc[ch] = msg.program

        # 分類ロジック
        is_extra = (ch in ch_base_pc and ch_current_pc[ch] != ch_base_pc[ch])

        # 統計収集
        if msg.type == 'program_change':
            if is_extra:
                ch_stats[ch]['extra'].add(msg.program)
            else:
                ch_stats[ch]['main'].add(msg.program)

        if not is_extra:
            cleaned_events.append(item)
        else:
            # Extraパート開始時の初期化処理（Note ONの直前にCCとPCを挿入する仕組み）
            if msg.type == 'note_on' and msg.velocity > 0:
                # 直前のCC状態をスナップショットとして挿入
                for cc_num, cc_val in ch_current_cc[ch].items():
                    extra_events_pool.append({'tick': tick, 'msg': Message('control_change', channel=ch, control=cc_num, value=cc_val)})
                extra_events_pool.append({'tick': tick, 'msg': Message('program_change', channel=ch, program=ch_current_pc[ch])})
            
            extra_events_pool.append(item)

    # 2. Cleanedファイルの保存
    cleaned_mid = MidiFile(ticks_per_beat=ticks_per_beat)
    cleaned_track = MidiTrack()
    cleaned_mid.tracks.append(cleaned_track)
    last_tick = 0
    for e in sorted(cleaned_events, key=lambda x: x['tick']):
        e['msg'].time = e['tick'] - last_tick
        cleaned_track.append(e['msg'])
        last_tick = e['tick']
    
    cleaned_out = f"{base_name}_cleaned.mid"
    cleaned_mid.save(cleaned_out)
    print(f"Generated: {cleaned_out}")

    ch_map = {} # {original_ch: new_ch}
    # 3. Extraファイルの生成（ch1から詰める）
    if extra_events_pool:
        # 簡易的に1つのファイルにch1から詰める実装（16chを超える場合は拡張が必要）
        final_extra_events = []
        next_free_ch = 0

        for item in sorted(extra_events_pool, key=lambda x: x['tick']):
            orig_ch = item['msg'].channel
            if orig_ch not in ch_map:
                ch_map[orig_ch] = next_free_ch
                next_free_ch += 1
            
            item['msg'].channel = ch_map[orig_ch]
            final_extra_events.append(item)
            
        create_extra_track(final_extra_events, base_name, 1)

    # レポート出力
    summary_lines = ["--- Split Summary ---"]
    for ch in sorted(active_channels):
        stats = ch_stats[ch]
        has_split = len(stats['extra']) > 0
        
        if not has_split:
            summary_lines.append(f"ch{ch+1}: none")
        else:
            main_names = [get_instrument_name(pc) for pc in sorted(stats['main'])]
            extra_names = [get_instrument_name(pc) for pc in sorted(stats['extra'])]
            main_str = f"main: {', '.join(main_names) if main_names else 'Default'}"
            extra_str = f"extra: {', '.join(extra_names)}"
            
            export_info = ""
            if ch in ch_map:
                mapped_ch = ch_map[ch] + 1
                extra_filename = os.path.basename(f"{base_name}_extra1.mid")
                export_info = f" -> export to {extra_filename} ch{mapped_ch}"
            
            summary_lines.append(f"ch{ch+1}: {main_str}, {extra_str}{export_info}")

    summary_text = "\n".join(summary_lines)
    print("\n" + summary_text)

    summary_path = f"{base_name}_splitsummary.txt"
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary_text)

if __name__ == "__main__":
    main()
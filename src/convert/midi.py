import pandas as pd
from typing import List, Dict
import math
from mido import MidiTrack, Message, MetaMessage, bpm2tempo
import librosa


def df_to_mid(df, label_part, index='s', bpm=60, ppq=1000, program=22) -> MidiTrack:

    track = MidiTrack()

    track.append(
        Message(
            'program_change',
            program=program,
            time=0
        )
    )

    track.append(
        MetaMessage(
            'time_signature',
            time=0
        )
    )

    track.append(
        MetaMessage(
            'set_tempo',
            tempo=bpm2tempo(bpm),
            time=0
        )
    )

    # time_s_last = list(events_chords.keys())[0]

    index_seconds = df.index.get_level_values(1)

    time_s_last = list(index_seconds)[0]

    df.loc[(slice(None), index_seconds[1:]), :]['chord'].tolist()

    df.loc[(slice(None), index_seconds[1:]), :]['chord'].tolist()

    for time_s in list(index_seconds):

        diff_ticks_last_event = s_to_ticks(time_s, bpm=bpm, ppq=ppq) - s_to_ticks(time_s_last, bpm=bpm, ppq=ppq)

        # for index, row in s_timeseries.iterrows():
        #     # print(row['c1'], row['c2'])
        #     if index == index_nearest_s_beat_first_quantized:
        #         passed_first_beat = True
        #
        #     if index == index_nearest_s_beat_last_quantized:
        #         passed_last_beat = True
        #         counter = 0
        #
        #     if passed_first_beat and not passed_last_beat:
        #         counter += 1
        #
        #     key_s_quantized = min(list(beatmap), key=lambda s_beat: abs(s_beat - index))
        #
        #     column_ms_quantized.append(key_s_quantized)
        #     column_beat.append(counter)

        # for index_ms, row in df.iterrows():


        # list(df.index.get_level_values(1))[0]


        # for i_note, note in enumerate(events_chords[time_s_last]):
        for i_note, note in enumerate(df.loc[(slice(None), time_s_last), 'chord'].tolist()[0]):
        # for i_note, note in enumerate(df.loc[time_s_last]):
            if i_note == 0:
                track.append(
                    Message(
                        'note_off',
                        note=note.pitch,
                        velocity=note.velocity,
                        time=diff_ticks_last_event
                    )
                )
            else:
                track.append(
                    Message(
                        'note_off',
                        note=note.pitch,
                        velocity=note.velocity,
                        time=0
                    )
                )

        # for i_note, note in enumerate(events_chords[time_s]):
        for i_note, note in enumerate(df.loc[(slice(None), time_s), 'chord'].tolist()[0]):
            track.append(
                Message(
                    'note_on',
                    note=note.pitch,
                    velocity=note.velocity,
                    time=0
                )
            )

        time_s_last = time_s

    return track


def s_to_ticks(s, bpm=60, ppq=480):

    quarter_notes_per_minute = bpm

    ticks_per_quarter_note = ppq

    ms_per_minute = (60 * 1000)

    ticks_per_minute = ticks_per_quarter_note * quarter_notes_per_minute

    ticks_per_ms = ticks_per_minute / ms_per_minute

    ms_per_second = 1000

    return int(ticks_per_ms * ms_per_second * s)


def mid_to_series(
        track
):

    iter_tick = 0

    tick_last = 0

    ticks = []

    notes_midi = []

    notes_intervals_tick: List[Dict[int, List]] = []

    last_msg_type_note_on = False

    stack_note_sounding = [None]

    for msg in track:
        if msg.type == 'note_on':
            note = int(msg.note)
            # ticks_since_onset_last = int(round(mido.second2tick(msg.time, ppq, mido.bpm2tempo(bpm))))
            ticks_since_onset_last = msg.time
            # track.append(Message('note_on', note=msg.note, velocity=msg.velocity, time=ticks_since_onset_last))
            for tick_empty in range(ticks_since_onset_last):
                # counting ticks during 'note_off' messages
                iter_tick += 1
                ticks.append(tick_last + tick_empty)
                # notes_midi.append(note_current if last_msg_type_note_on else None)
                notes_midi.append(stack_note_sounding[-1])
            # note_current = stack_note_sounding[-1]
            # last_msg_type_note_on = True
            stack_note_sounding.append(note)

        if msg.type == 'note_off':
            note = int(msg.note)
            # if stack_note_sounding[-1] == note:

            # ticks_since_onset_last = int(round(mido.second2tick(msg.time, ppq, mido.bpm2tempo(bpm))))
            ticks_since_onset_last = msg.time
            # track.append(Message('note_off', note=msg.note, velocity=msg.velocity, time=ticks_since_onset_last))
            interval = [iter_tick + 1]
            # interval.append(iter_tick + 1)
            for tick in range(ticks_since_onset_last):
                # counting ticks during 'note_on' messages
                iter_tick += 1
                ticks.append(tick_last + tick)
                notes_midi.append(stack_note_sounding[-1])  # notes_midi.append(note)

            interval.append(iter_tick)
            notes_intervals_tick.append({stack_note_sounding[-1]: interval})
            if stack_note_sounding[-1] == note:
                stack_note_sounding.pop()
            # note_last = note
            # last_msg_type_note_on = False

        tick_last = iter_tick

    # assert stack_note_sounding[-1] is None
    ticks.append(tick_last)
    # notes_midi.append(stack_note_sounding[-1])
    notes_midi.append(None)

    return pd.Series(
        notes_midi,
        index=ticks
    )


def series_to_mid(df, init_velocity):

    iter_tick = 0

    onset_tick = 0

    note_last = 0

    track = MidiTrack()

    while iter_tick < len(df.index) - 1:

        velocity = init_velocity

        tick_next = iter_tick + 1

        pitch_current = df.at[iter_tick]

        pitch_next = df.at[tick_next]

        if pitch_current != pitch_next and not (math.isnan(pitch_current) and math.isnan(pitch_next)):

            note = int(df.at[tick_next]) if df.at[tick_next] > 0 else 0

            if note == 0:
                velocity = 0

            track.append(
                Message(
                    'note_off',
                    note=note_last,
                    velocity=0,
                    time=int(tick_next - onset_tick)
                )
            )

            track.append(
                Message(
                    'note_on',
                    note=note,
                    velocity=int(velocity),
                    time=0
                )
            )

            if velocity > 0:
                note_last = note

            onset_tick = iter_tick + 1

        iter_tick = tick_next

    return track


def hz_to_mid(
        df_hz: pd.DataFrame
) -> pd.DataFrame:
    df_hz['melody'] = df_hz['melody'].apply(librosa.hz_to_midi).round()
    return df_hz


# import numpy as np
# import collections
# import librosa
# from mido import Message, MidiFile, MidiTrack, MetaMessage
# import numpy as np
#
# ms_to_pitch = collections.OrderedDict()
#
# # filename_input = '/Users/elliottevers/Documents/git-repos.nosync/audio_to_midi_melodia/train01.txt'
# #
# # filename_output = 'train01.mid'
#
# filename_input = '/Users/elliottevers/Downloads/out_seg.txt'
#
# filename_output = 'lodi_vocals.mid'
#
# # filename_input = 'lodi_melodia.txt'
#
# # filename_output = 'lodi_melodia.mid'
#
# in_ms = False
#
# samples_per_second = 50.
#
# step_size = 1 / samples_per_second
#
# if in_ms:
#     with open(filename_input, 'r') as file_local:
#         for line in file_local:
#             value_hz = int(float(line.split()[1]))
#             if value_hz > 0:
#                 ms_to_pitch[float(line.split()[0])] = int(float(line.split()[1]))
# else:
#     current_ms = 0
#     with open(filename_input, 'r') as file_local:
#         for line in file_local:
#             ms_to_pitch[float(current_ms)] = int(float(line.split()[1]))
#             current_ms += step_size
#
# bpm = 60
#
# resolution = 1000
#
# mid = MidiFile(ticks_per_beat=resolution)
#
# ms_to_pitch_filtered = collections.OrderedDict()
#
# pitch_last = 0
#
# for time_ms, pitch_hertz in ms_to_pitch.iteritems():
#
#     if pitch_hertz != pitch_last:
#         ms_to_pitch_filtered[time_ms] = pitch_hertz
#
#     pitch_last = pitch_hertz
#
#
# track = MidiTrack()
#
# mid.tracks.append(track)
#
# track.append(MetaMessage('set_tempo', tempo=1000000, time=0))
#
# track.append(Message('note_on', note=0, velocity=127, time=0))
#
# duration_ms_last_note = 0
#
# note_midi_last_note = 0
#
# time_ms_last = 0
#
# for time_ms, pitch_hertz in ms_to_pitch_filtered.iteritems():
#
#     if pitch_hertz == 0:
#         note_midi = 0
#     else:
#         note_midi = librosa.hz_to_midi(pitch_hertz)[0]
#
#     duration_ms_last_note = time_ms - time_ms_last
#
#     track.append(Message('note_off', note=int(note_midi_last_note), velocity=127, time=int(duration_ms_last_note * 1000)))
#
#     track.append(Message('note_on', note=int(note_midi), velocity=127, time=0))
#
#     time_ms_last = time_ms
#
#     note_midi_last_note = note_midi
#
#
# track.append(Message('note_off', note=0, velocity=127, time=0))
#
#
# mid.save(filename_output)
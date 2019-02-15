import pandas as pd
from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
from typing import List, Dict, Any, Optional, Tuple
from music import note
from convert import midi as convert_midi
# class Song, or class Mesh


class MeshSong(object):

    data: pd.DataFrame

    def __init__(self):
        self.data = None

    # def add_chords(self, chords: Dict[Any, List[note.MidiNote]], index_type='s'):
    #     # events_chords: Dict[float, List[note.MidiNote]]
    #     # self.data = pd.merge(self.data, chords, on=index_type)
    #     df_chords = pd.DataFrame(
    #         data={'chords': list(chords.values())}, index=list(chords.keys())
    #     )
    #     df_chords.index.name = index_type

    def add_quantization(self):
        return 0

    @staticmethod
    def chords_to_df(chords: Dict[Any, List[note.MidiNote]], index_type='s'):
        df_chords = pd.DataFrame(
            data={'chord': list(chords.values())}, index=list(chords.keys())
        )

        df_chords.index.name = index_type

        return df_chords

    @staticmethod
    def segments_to_df(data_segments, index_type='s'):

        segments = [
            {
                'timestamp': segment['timestamp'],
                'duration': segment['duration']
            }

            for segment
            in data_segments
        ]

        df_segments = pd.DataFrame(
            data={
                'segment': [
                    note.MidiNote(
                        pitch=60,
                        duration_ticks=convert_midi.s_to_ticks(segment['duration']),  # TODO: make sure defaults (bpm, ppq) don't fuck with this
                        velocity=90,
                        channel=10,
                        program=49
                    )
                    for segment
                    in segments
                ]
            },
            index=[
                segment['timestamp'] for segment in segments
            ]
        )

        df_segments.index.name = index_type

        return df_segments

    @staticmethod
    def melody_to_df(data_melody, index_type='s'):
        list_melody = data_melody[1]

        sample_rate = data_melody[0]

        df_melody_hz = pd.DataFrame(
            data={'melody': list_melody},
            index=[i_sample * sample_rate for i_sample, sample in enumerate(list_melody)]
        )

        df_melody_hz.index.name = index_type

        return df_melody_hz

    @staticmethod
    def quantize(
            s_timeseries: pd.DataFrame,
            beatmap: List[float],
            s_beat_start,
            s_beat_end
    ) -> pd.DataFrame:

        # TODO: add column of beats (NaNs before and after start and end), make it another index
        column_s_quantized = []
        column_beat = []

        s_beat_first_quantized = min(list(beatmap), key=lambda s_beat: abs(s_beat - s_beat_start))

        s_beat_last_quantized = min(list(beatmap), key=lambda s_beat: abs(s_beat - s_beat_end))

        counter = 0
        passed_first_beat = False
        passed_last_beat = False

        index_nearest_s_beat_first_quantized = min(list(s_timeseries.index), key=lambda s_beat: abs(s_beat - s_beat_first_quantized))

        index_nearest_s_beat_last_quantized = min(list(s_timeseries.index), key=lambda s_beat: abs(s_beat - s_beat_last_quantized))

        for index, row in s_timeseries.iterrows():
            if index == index_nearest_s_beat_first_quantized:
                passed_first_beat = True

            if index == index_nearest_s_beat_last_quantized:
                passed_last_beat = True
                counter = 0

            if passed_first_beat and not passed_last_beat:
                counter += 1

            key_s_quantized = min(list(beatmap), key=lambda s_beat: abs(s_beat - index))

            column_s_quantized.append(key_s_quantized)
            column_beat.append(counter)

        s_timeseries['s_quantized'] = column_s_quantized

        s_timeseries['beat'] = column_beat

        return s_timeseries.reset_index(
            drop=True
        ).rename(
            columns={'s_quantized': 's'}
        ).set_index(
            ['beat', 's']
        ).sort_index(
        )

    def fill_legato(self, name_column='chord') -> None:
        col_legato = []
        struct_current = None
        for chord in self.data['chord'].tolist():
            testing = 1


    # TODO: support index type 's' (melodyne) and 'beat' (trascription after source separation)
    def add_melody(self, melody: pd.DataFrame, index_type='s') -> None:
        self.data = pd.merge(
            self.data.reset_index(),
            melody.reset_index(),
            on=[index_type],
            how='outer'
        ).set_index(
            [index_type, 'beat']
        ).sort_index(
            by=index_type
        )

    def add_chords(self, chords: pd.DataFrame, index_type='s') -> None:
        if not self.data:
            self.data = chords
        else:
            self.data = pd.merge(
                self.data.reset_index(),
                chords.reset_index(),
                on=[index_type],
                how='outer'
            ).set_index(
                [index_type, 'beat']
            ).sort_index(
                by=index_type
            )

    def add_segments(self, segments: pd.DataFrame, index_type='s') -> None:
        self.data = pd.merge(
            self.data.reset_index(),
            segments.reset_index(),
            on=[index_type],
            how='outer'
        ).set_index(
            [index_type, 'beat']
        ).sort_index(
            by=index_type
        )

    def add_bass(self, bass: pd.DataFrame, index_type='s') -> None:
        self.data = pd.merge(
            self.data.reset_index(),
            bass.reset_index(),
            on=[index_type, 'beat'],
            how='outer'
        ).set_index(
            [index_type, 'beat']
        ).sort_index(
            by=index_type
        )
    # def add_chords(self, chords: Dict[Any, List[note.MidiNote]], index_type='s'):
    #     # events_chords: Dict[float, List[note.MidiNote]]
    #     # self.data = pd.merge(self.data, chords, on=index_type)
    #     df_chords = pd.DataFrame(
    #         data={'chords': list(chords.values())}, index=list(chords.keys())
    #     )
    #     df_chords.index.name = index_type

    def get_time_aligned(self) -> pd.DataFrame:
        return 0

    def get_fixed_tempo(self) -> pd.DataFrame:
        if not self.tempo:
            raise 'tempo estimate not set'
        return 0

    def render(self, part_to_track: Dict, type='fixed_tempo') -> MidiFile:
        # add chords to tracks
        return MidiFile()

# import mido
# from mido import Message, MidiFile, MidiTrack, MetaMessage
# from music21 import stream as stream21, note as note21, pitch as pitch21, duration as duration21
# import pandas as pd
# import numpy as np
# import seaborn as sns
# import matplotlib.pyplot as plt
# import convert.series_to_mid as series2mid
# import music21
# import os
# import importlib
#
# sns.set(style="darkgrid")
#
# # importlib.import_module(os.path.dirname(os.path.realpath(mido.__file__)) + '/midifiles/midifiles.py')
#
# # mido, midifiles.py
#
# DEFAULT_TEMPO = 500000
#
# filename_input = '/Users/elliottevers/Downloads/ella_dream_vocals_2.mid'
#
# filename_output = '/Users/elliottevers/Downloads/output_midi_to_ticks_timeseries.mid'
#
# program_change = 22  # harmonica
#
# file = MidiFile(filename_input)
#
# ticks_per_beat = file.ticks_per_beat
#
# ppq = ticks_per_beat
#
# mid = MidiFile(ticks_per_beat=ticks_per_beat)
# track = MidiTrack()
# mid.tracks.append(track)
#
# track.append(
#     Message(
#         'program_change',
#         program=program_change,
#         time=0
#     )
# )
#
# iter_tick = 0
#
# tick_last = 0
#
# ticks = []
#
# notes_midi = []
#
# bpm = mido.tempo2bpm(DEFAULT_TEMPO)
#
# track.append(
#     MetaMessage(
#         'time_signature',
#         time=0
#     )
# )
#
# track.append(
#     MetaMessage(
#         'set_tempo',
#         tempo=mido.bpm2tempo(bpm),
#         time=0
#     )
# )
#
# stream = stream21.Stream()
#
# thing = []
#
# for msg in file:
#
#     if msg.type == 'note_on':
#         # assert len(thing) == 0  # monophonic
#
#         ticks_since_onset_last = int(round(mido.second2tick(msg.time, ticks_per_beat, mido.bpm2tempo(bpm))))
#         track.append(Message('note_on', note=msg.note, velocity=msg.velocity, time=ticks_since_onset_last))
#         # quarter note in ticks - ticks_since_onset_last/ticks_per_beat
#         # duration = duration21.Duration()
#         # duration.quarterLength = ticks_since_onset_last/ticks_per_beat
#
#         pitch = pitch21.Pitch()
#         pitch.midi = msg.note
#
#         note = note21.Note()
#         # note.duration = duration
#         note.pitch = pitch
#
#         # stream.append(note)
#         thing.append(note)
#
#         for tick_empty in range(ticks_since_onset_last):
#             iter_tick += 1
#             ticks.append(tick_last + tick_empty)
#             notes_midi.append(None)
#
#     if msg.type == 'note_off':
#         # assert len(thing) == 1  # monophonic
#
#         ticks_since_onset_last = int(round(mido.second2tick(msg.time, ticks_per_beat, mido.bpm2tempo(bpm))))
#         track.append(Message('note_off', note=msg.note, velocity=msg.velocity, time=ticks_since_onset_last))
#
#         duration = duration21.Duration()
#         duration.quarterLength = ticks_since_onset_last / ticks_per_beat
#
#         note = thing.pop()
#
#         note.duration = duration
#
#         stream.append(note)
#
#         # pitch = pitch21.Pitch()
#         # pitch.midi = msg.note
#         #
#         # note = note21.Note()
#         # note.duration = duration
#         # note.pitch = pitch
#         #
#         # stream.append(note)
#
#         for tick in range(ticks_since_onset_last):
#             iter_tick += 1
#             ticks.append(tick_last + tick)
#             notes_midi.append(msg.note)
#
#     tick_last = iter_tick
#
#
# # TODO: we're trying to convert to music21 object here - this also might be the key to making monophonic midi file
#
# df = pd.Series(
#     notes_midi,
#     index=np.array(ticks)
# )
#
#
# mid2 = MidiFile(ticks_per_beat=ticks_per_beat)
#
# track2 = MidiTrack()
#
# mid2.tracks.append(
#     series2mid.timeseries_ticks_to_mid(
#         df,
#         track2,
#         90
#     )
# )
#
# lim = int(round(len(df.index)/4))
#
# sns.relplot(kind="line", data=df[1:lim])
#
#
# plt.show()
#
#
# # df.plot()
#
# # stream.plot()
# mid2.save(filename_output)


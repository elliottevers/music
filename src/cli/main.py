import vamp
import librosa
from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
from typing import List, Dict, Any, Optional, Tuple
import music21
import numpy as np
import pandas as pd
from music import note, song
from convert import midi as midi_convert, vamp as vamp_convert
from filter import vamp as vamp_filter
import jsonpickle
from analysis_discrete import music_xml as analysis_mxl
from information_retrieval import extraction as ir
from postprocess import midi as postp_mid, music_xml as postp_mxl, hz as hz_postp
import music21
from convert import music_xml as mxl_conv
from filter import midi as filter_mid, seconds as s_filt
from preprocess import hz as hz_prep, vamp as prep_vamp, seconds as s_prep
import math

# TODO: endow all structures with music21 instrument

filename_wav = "/Users/elliottevers/Documents/DocumentsSymlinked/git-repos.nosync/audio/youtube/tswift_teardrops.wav"

filename_mid_out = '/Users/elliottevers/Documents/DocumentsSymlinked/git-repos.nosync/audio/ChordTracks/chords_tswift_tears_TEST.mid'

filepath_frozen = '/Users/elliottevers/Downloads/score_frozen.json'

branch = 'vamp'

s_beat_start = 3.436

s_beat_end = 26.9 + 3 * 60

# cadence_beats = 4

durations = [4.1, 3.7, 4.6]

pitches = ['C', 'C#', 'D']

# measure = music21.stream.Measure()

stream = music21.stream.Stream()

for i, duration in enumerate(durations):
    note = music21.note.Note(pitches[i])
    note.duration = music21.duration.Duration(duration)
    stream.append(note)

# note1 = music21.note.Note('C')
#
# note1.duration = music21.duration.Duration(4/3)
#
# note2 = music21.note.Note('C')
#
# note2.duration = music21.duration.Duration(4/3)
#
# note3 = music21.note.Note('C')
#
# note3.duration = music21.duration.Duration(4/3)
#
# measure.append(
#     note1
# )
#
# measure.append(
#     note2
# )
#
# measure.append(
#     note3
# )

stream.quantize((0.25,), inPlace=True)


stream.show()

exit(0)


data_melody = ir.extract_melody(
    filename_wav,
    stub=True
)

data_segments = ir.extract_segments(
    filename_wav,
    stub=True
)

data_chords = ir.extract_chords(
    filename_wav,
    stub=True
)

s_to_label_chords: List[Dict[float, Any]] = data_chords

# data_tempo = ir.extract_tempo(
#     filename_wav,
#     stub=True
# )

data_beats = ir.extract_beats(
    filename_wav,
    stub=True
)

beatmap = [beat['timestamp'] for beat in data_beats]

##### post information extraction #####

# df_melody = prep_vamp.melody_to_df(
#     data_melody,
#     index_type='s'
# )


# def get_name_column_duration(name_column):
#     return name_column + '_duration'
#
#
# def get_name_column_offset(name_column):
#     return name_column + '_offset'
#
#
# def hz_to_mid(hz):
#     if hz == 0:
#         return 0
#     else:
#         return librosa.hz_to_midi(hz)
#
# # TODO: convert to midi before diffing, create rests where pitch is 0
#
#
# def to_mid(df_hz: pd.DataFrame, name_part):
#     df_hz[name_part] = df_hz[name_part].apply(hz_postp._handle_na).apply(hz_to_mid).apply(round)
#     return df_hz
#
#
# def to_diff(df: pd.DataFrame, name_column='melody', sample_rate=0.003) -> pd.DataFrame:
#     offset_diff = []
#     data_diff = []
#     duration_diff = []
#
#     current_val = None
#
#     acc_duration = 0
#
#     for i, val in df[name_column].iteritems():
#         acc_duration = acc_duration + sample_rate
#         if val == current_val:
#             pass
#         else:
#             offset_diff.append(i)
#             data_diff.append(val)
#             duration_diff.append(acc_duration)
#             acc_duration = 0
#             current_val = val
#
#     df_diff = pd.DataFrame(
#         data={
#             name_column: data_diff,
#             get_name_column_duration(name_column): duration_diff
#         },
#         index=offset_diff
#     )
#
#     df_diff.index.name = get_name_column_offset(name_column)
#
#     return df_diff
#
#
# # df of music21 object that know they're duration, and the index knows it's offset
# def to_df_beat_unquantized(df_diff, name_column, beatmap, beat_first, beat_last):
#     # TODO: partmap
#
#     beatmap_trimmed = song.MeshSong.trim_beatmap(beatmap, beat_first, beat_last)
#
#     def find_index_of_nearest_below(array, value):
#         return array.index(max(list(filter(lambda y: y <= 0, [x - value for x in array]))) + value)
#
#     def to_beat_onset(ms, beatmap, index_nearest_below, length_containing_segment):
#         nearest_below = beatmap[index_nearest_below]
#
#         return beatmap.index(nearest_below) + (
#             (ms - beatmap[index_nearest_below])/length_containing_segment
#         )
#
#     index_beat_offset = []
#     data_beat_duration = []
#     data_struct = []
#
#     for row in df_diff.itertuples(index=True, name=True):
#         index_s_offset = row[0]
#         struct = row[1]
#         s_duration = row[2]
#
#         if index_s_offset < beatmap_trimmed[0] or index_s_offset > beatmap_trimmed[-1]:
#             continue
#
#         index_nearest_below = find_index_of_nearest_below(beatmap_trimmed, index_s_offset)
#         length_of_containing_segment = beatmap_trimmed[index_nearest_below + 1] - beatmap_trimmed[index_nearest_below]
#         beat_onset = to_beat_onset(index_s_offset, beatmap_trimmed, index_nearest_below, length_of_containing_segment)
#         beat_duration = s_duration/length_of_containing_segment
#
#         index_beat_offset.append(beat_onset)
#         data_beat_duration.append(beat_duration)
#         data_struct.append(struct)
#
#     df_struct = pd.DataFrame(
#         data={
#             name_column: data_struct,
#             get_name_column_duration(name_column): data_beat_duration
#         },
#         index=index_beat_offset
#     )
#
#     df_struct.index.name = 'beat'
#
#     return df_struct


# vamp branch of pipeline

mesh_song = song.MeshSong()

if branch == 'vamp':

    # MELODY

    # df_melody = prep_vamp.melody_to_df(
    #     data_melody,
    #     index_type='s'
    # )
    #
    # df_melody_diff = to_diff(
    #     to_mid(
    #         df_melody,
    #         'melody'
    #     ),
    #     'melody',
    #     data_melody[0]
    # )
    #
    # # hertz pre-filtering -> discretization -> midi post-filtering -> postprocessing diff series (midi) (but doesn't this happen "automatically" when rendering to score?)
    #
    # tree_melody = song.MeshSong.get_interval_tree(
    #     df_melody_diff
    # )
    #
    # mesh_song.set_tree(
    #     tree_melody,
    #     type='melody'
    # )
    #
    # mesh_song.quantize(
    #     beatmap,
    #     s_beat_start,
    #     s_beat_end,
    #     columns=['melody']
    # )
    #
    # df_data_quantized_diff = to_diff(
    #     mesh_song.data_quantized,
    #     name_column='melody',
    #     sample_rate=1/48
    # )
    #
    # score_melody = postp_mxl.df_grans_quantized_to_score(
    #     df_data_quantized_diff,
    #     parts=['melody']
    # )

    score_melody.show()

    exit(0)

    # CHORDS

    # # TODO: put in preprocessing module
    # non_empty_chords = vamp_filter.vamp_filter_non_chords(
    #     s_to_label_chords
    # )
    #
    # # TODO: put in preprocessing module
    # events_chords: Dict[float, music21.chord.Chord] = vamp_convert.vamp_chord_to_dict(
    #     non_empty_chords
    # )
    #
    # df_chords = prep_vamp.chords_to_df(
    #     events_chords
    # )
    #
    # df_upper_voicings = postp_mxl.extract_upper_voices(
    #     df_chords
    # )
    #
    # chord_tree = song.MeshSong.get_interval_tree(
    #     df_upper_voicings
    # )
    #
    # mesh_song.set_tree(
    #     chord_tree,
    #     type='chord'
    # )

    # BASS

    df_bass = postp_mxl.extract_bass(
        df_chords
    )

    tree_bass = song.MeshSong.get_interval_tree(
        df_bass
    )

    mesh_song.set_tree(
        tree_bass,
        type='bass'
    )

    # SEGMENTS

    df_segments = prep_vamp.segments_to_df(
        data_segments
    )

    tree_segments = song.MeshSong.get_interval_tree(
        df_segments
    )

    mesh_song.set_tree(
        tree_segments,
        type='segment'
    )

    # QUANTIZATION

    # TODO: using the interval trees, this adds the actual data
    # there should not be a multiindex df underneath the hood
    mesh_song.quantize(
        beatmap,
        s_beat_start,
        s_beat_end,
        columns=['melody', 'bass', 'chord', 'segment']
    )

    # SMOOTHING
    # TODO: use quantization at a much higher resolution here
    # mesh_song.data_quantized['chord'] = filter_mid.smooth_chords(
    #     mesh_song.data_quantized['chord'],
    #     cadence_beats=4
    # )
    #
    # mesh_song.data_quantized['bass'] = filter_mid.smooth_bass(
    #     mesh_song.data_quantized['bass'],
    #     cadence_beats=1
    # )
    #
    # mesh_song.data_quantized['segment'] = filter_mid.smooth_segment(
    #     mesh_song.data_quantized['segment'],
    #     cadence_beats=16
    # )

    score_sans_key_centers = postp_mxl.df_grans_to_score(
        mesh_song.data_quantized
    )

    # TODO: filter segments in the same way as chords, except using every *4* measures

    # KEY CENTERS

    stream_chords_and_bass = postp_mxl.extract_parts(
        score_sans_key_centers
    )

    part_key_centers: music21.stream.Part = analysis_mxl.get_key_center_estimates(
        stream_chords_and_bass
    )

    # TODO: since the above is slow to debug, use this as a sort of test stub
    # part_dummy = postp_mxl.extract_parts(
    #     score_sans_key_centers,
    #     parts=['bass']
    # )

    score_with_key_centers = postp_mxl.add_part(
        part_key_centers,
        score=score_sans_key_centers
    )

    # FIXED TEMPO ESTIMATE, FOR FINAL RENDERING

    # tempomap = prep_vamp.extract_tempomap(
    #     data_tempo
    # )
    #
    # # TODO: implement that median filter
    # fixed_tempo_estimate = s_filt.get_fixed_tempo_estimate(
    #     tempomap
    # )

    # stream_score = mesh_song.to_score(
    #
    # )
    #

    stream_score = postp_mxl.set_tempo(
        score_with_key_centers,
        bpm=fixed_tempo_estimate
    )

    stream_score.show()

else:

    # web-based deep learning branch of pipeline

    # # TODO: extract relevant information to merge with other midi file
    # stream_chords: music21.stream.Stream, bpm_chords = prep_mid.load_stream(
    #     filename=''
    # )
    #
    # # TODO: put through series of transformations that will be performed manually in reality
    # stream_melody: music21.stream.Stream, bpm_melody = prep_mid.load_stream(
    #     filename=''
    # )

    stream_chords_bass_melody = postp_mxl.thaw_stream(
        filepath=filepath_frozen
    )

    stream_melody = postp_mxl.extract_parts(
        stream_chords_bass_melody,
        parts=['melody']
    )

    # SEGMENTS
    # TODO: this might work better using chords
    stream_segments: music21.stream.Stream = analysis_mxl.get_segments(
        stream_melody,
        name_part='segments'
    )

    # exit(0)

    # KEY CENTERS
    stream_chords_and_bass: music21.stream.Stream = postp_mxl.extract_parts(
        stream_chords_bass_melody,
        parts=['chord', 'bass']
    )

    # TODO: give this dataframe an index of beats
    stream_key_centers: music21.stream.Stream = analysis_mxl.get_key_center_estimates(
        stream_chords_and_bass
    )

    # TODO: pretty easy, just append to 'parts'
    stream_score = postp_mxl.combine_streams(
        stream_melody,
        stream_chords_and_bass,
        stream_segments,
        stream_key_centers
    )

    # TODO: just search, using the XML element thing, for MetronomeMarker in the first measure
    stream_score = postp_mxl.set_tempo(
        stream_score,
        bpm=postp_mxl.extract_bpm(
            stream_chords_bass_melody
        )
    )


song.MeshSong.render(
    stream_score
)

# TODO: notify Ableton Live that midi file is rendered

# TODO: use parser and encoder to bring parts to and from Ableton Live tracks




# beat_unquantized = to_df_beat_unquantized(
#     to_diff(
#         to_mid(
#             df_melody,
#             'melody'
#         ),
#         'melody',
#         data_melody[0]
#     ),
#     'melody',
#     beatmap,
#     s_beat_start,
#     s_beat_end
# )


location_pickle_beat_unquantized = '/Users/elliottevers/Downloads/beat_unquantized.pickle'

location_pickle_quantized = '/Users/elliottevers/Downloads/quantized.pickle'

# beat_unquantized.to_pickle(location_pickle_beat_unquantized)

# exit(0)

beat_unquantized = pd.read_pickle(location_pickle_beat_unquantized)
quantized = pd.read_pickle(location_pickle_quantized)


# exit(0)

gran_map = song.MeshSong.get_gran_map(
    beatmap=song.MeshSong.trim_beatmap(beatmap, s_beat_start, s_beat_end)
)

grans = list(gran_map.keys())

new = dict()

res = float(1/48)

eps = float(res)/4

then = pd.Timestamp.now()

index_new = []

data_new = []



# for key in grans:
#     less_than = beat_unquantized[beat_unquantized.index <= key + res + eps]
#     sweet_spot = less_than[less_than >= key]
#     index_new.append(key)
#     candidates = sweet_spot.groupby('melody')['melody_duration'].aggregate(np.sum)
#     if len(candidates) == 0:
#         datum = 0
#         data_new.append(datum)
#     else:
#         datum = candidates.idxmax()
#         data_new.append(datum)
#     print(key)
#     print(datum)
#     # data_new.append(thing)

# key = 60.0 + 1/48

# for key in grans:
# less_than = testing[testing.index <= res + eps]
# sweet_spot = less_than[less_than >= key]
# index_new.append(key)
# thing = sweet_spot.groupby('melody')['melody_duration'].aggregate(np.sum).idxmax()
# print(key)
# print(thing)
# data_new.append(thing)

df_quantized = pd.DataFrame(
    data=data_new,
    index=index_new
)

df_quantized.index.name = 'beat_quantized'

df_quantized.to_pickle(location_pickle_quantized)

print(pd.Timestamp.now() - then)

# testing.to_pickle(location_pickle_quantized)

exit(0)

part = music21.stream.Part()

first = testing.iloc[0]

beat_offset_first = first.name

note_first = music21.note.Note(
    pitch=music21.pitch.Pitch(
        midi=first['melody']
    )
)

note_first.duration = music21.duration.Duration(
    first['melody_duration']
)

note_first.offset = music21.duration.Duration(
    beat_offset_first
)

part.append(note_first)

for row in testing.iloc[1:, :].itertuples(index=True, name=True):
    index_beat_offset = row[0]
    struct = row[1]
    beat_duration = row[2]

    if struct == 0:
        note = music21.note.Rest(

        )
    else:
        note = music21.note.Note(
            pitch=music21.pitch.Pitch(
                midi=struct
            )
        )

    note.duration = music21.duration.Duration(beat_duration)

    part.append(note)

part.quantize((8, 12), inPlace=True)

measured = part.makeMeasures()


# gran_map = song.MeshSong.get_gran_map(
#     beatmap=song.MeshSong.trim_beatmap(beatmap, s_beat_start, s_beat_end)
# )
#
# grans = list(gran_map.keys())
#
# new = dict()
#
# for i, key in enumerate(grans):
#     testing[testing.index <= grans[i + 1]][testing.index >= key].groupby('melody')['melody_duration'].aggregate(np.sum)
#     # print(thing[thing.idxmax()])
#     new[key] = testing.idxmax()

exit(0)

# for thing in part:
debugging = 1

# part.show()

exit(0)



# TODO: score quantization testing

# durations = [.27, .54, .01, .6, .9, .01, .07]
#
# pitches = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#']
#
#
# measure = music21.stream.Measure()
#
# for i, duration in enumerate(durations):
#     note = music21.note.Note(pitches[i])
#     note.duration = music21.duration.Duration(duration)
#     measure.append(note)

# note1 = music21.note.Note('C')
#
# note1.duration = music21.duration.Duration(4/3)
#
# note2 = music21.note.Note('C')
#
# note2.duration = music21.duration.Duration(4/3)
#
# note3 = music21.note.Note('C')
#
# note3.duration = music21.duration.Duration(4/3)
#
# measure.append(
#     note1
# )
#
# measure.append(
#     note2
# )
#
# measure.append(
#     note3
# )

# measure.quantize((4,6), inPlace=True)
#
#
# measure.show()
#
# exit(0)
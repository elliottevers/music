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
from analysis_discrete import analysis_midi

filename_wav = "/Users/elliottevers/Documents/DocumentsSymlinked/git-repos.nosync/audio/youtube/tswift_teardrops.wav"

filename_mid_out = '/Users/elliottevers/Documents/DocumentsSymlinked/git-repos.nosync/audio/ChordTracks/chords_tswift_tears_TEST.mid'

data, rate = librosa.load(
    filename_wav
)

with open('test/stubs_pickle/python/melody_tswift_teardrops.json', 'r') as file:
    data_melody = jsonpickle.decode(file.read())

with open('test/stubs_pickle/python/segments_tswift_teardrops.json', 'r') as file:
    data_segments = jsonpickle.decode(file.read())

with open('test/stubs_pickle/python/chords_tswift_teardrops.json', 'r') as file:
    data_chords = jsonpickle.decode(file.read())

s_to_label_chords: List[Dict[float, Any]] = data_chords  # chords['list']

with open('test/stubs_pickle/python/tempo_tswift_teardrops.json', 'r') as file:
    data_tempo = jsonpickle.decode(file.read())

with open('test/stubs_pickle/python/beats_tswift_teardrops.json', 'r') as file:
    data_beats = jsonpickle.decode(file.read())


# vamp branch of pipeline

mesh_song = song.MeshSong()

if branch == 'vamp':

    mesh_song.add_chords(chords)

    mesh_song.add_quantization(beatmap)

    # TODO: shouldn't need to convert, as this will be taken care of in Ableton user assisted processing
    mesh_song.add_melody(
        midi_convert.hz_to_mid( # df
            melody # df
        )
    )

    mesh_song.add_bass(bass)

    mesh_song.add_segments(segments)

    file_chords_and_bass =

    key_centers = analysis_midi.get_key_center_estimates(file_chords_and_bass)

    mesh_song.add_key_centers(key_centers)

    fixed_tempo_estimate = mir.get_fixed_tempo_estimate(tempomap)

else:

    # web-based deep learning branch of pipeline

    # NB: already quantized
    chords = postprocess.load_df(
        filename=''  # chordify download location
    )

    # NB: no conversion from hertz to midi necessary
    melody = postprocess.load_df(
        filename=''  # Ableton transcription download location
    )

    bass = postprocess.extract_bass(chords)

    upper_voicings = postprocess.extract_upper_voicings(chords)

    mesh_song.add_chords(upper_voicings)

    mesh_song.add_bass(bass)

    mesh_song.add_melody(
        melody=melody
    )

    segments = analysis_midi.extract_segments()

    file_chords_and_bass =

    key_centers = analysis_midi.get_key_center_estimates(file_chords_and_bass)

    mesh_song.add_key_centers(key_centers)

    fixed_tempo_estimate = postprocessing.extract_bpm(filename_mid='')


mesh_song.render(
    part_to_track=part_track_map,
    type='fixed_tempo',
    tempo=fixed_tempo_estimate
)



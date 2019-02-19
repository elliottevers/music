import pandas as pd
import music21
import numpy as np
from live import note as nl
from typing import List, Dict, Any, Optional, Tuple
from itertools import groupby


def get_lowest_note(chord):
    return list(chord.pitches)[0]


def get_highest_notes(chord):
    if not chord:
        return None
    else:
        return music21.chord.Chord(
            list(chord.pitches)[1:]
        )


def extract_bass(df_chords) -> pd.DataFrame:
    return df_chords['chord'].apply(get_lowest_note).to_frame(name='bass')


def extract_upper_voices(df_chords) -> pd.DataFrame:
    return df_chords['chord'].apply(get_highest_notes).to_frame(name='chord')


def extract_parts(score: music21.stream.Score, parts=['chord', 'bass']) -> music21.stream.Score:
    score_diminished = music21.stream.Score()

    for i_part, name_part in enumerate(parts):
        score_diminished.insert(i_part, score.getElementById(name_part))

    return score_diminished


def add_part(part: music21.stream.Part, score: music21.stream.Score, id='key_center') -> music21.stream.Score:
    part.id = id
    score.insert(
        len(score.elements),
        part
    )
    return score


def thaw_stream(filepath) -> music21.stream.Stream:
    thawer = music21.freezeThaw.StreamThawer()
    thawer.open(fp=filepath)
    return thawer.stream


def set_tempo(score: music21.stream.Score, bpm: int = 60) -> music21.stream.Score:

    marks_to_remove = []

    # remove current
    for mark in score.flat.getElementsByClass(music21.tempo.MetronomeMark):
        marks_to_remove.append(mark)

    for mark in marks_to_remove:
        score.remove(mark, recurse=True)

    # add new
    for measure in score.parts[0].getElementsByClass(music21.stream.Measure):
        if measure.offset == 0.0:
            tempo = music21.tempo.MetronomeMark(number=bpm)
            tempo.offset = 0.0
            measure.append(tempo)

    return score


def get_struct_score(object, name_part):
    if name_part == 'melody':
        if not object > 0:
            struct_score = music21.note.Rest()
        else:
            struct_score = music21.note.Note(
                pitch=music21.pitch.Pitch(
                    midi=int(object)
                )
            )
    elif name_part == 'chord':
        struct_score = music21.chord.fromIntervalVector(
            object
        )
    elif name_part == 'bass':
        struct_score = music21.note.Note(
            pitch=object
        )
    elif name_part == 'segment':
        struct_score = music21.note.Note(
            pitch=music21.pitch.Pitch(
                midi=60
            )
        )
    else:
        raise 'part ' + name_part + ' not in dataframe to render to score'

    return struct_score


def df_grans_to_score(
        df_grans: pd.DataFrame,
        column_index='beat',
        parts=[
            'melody',
            'chord',
            'bass',
            'segment'
        ]
) -> music21.stream.Score:

    score = music21.stream.Score()

    for i_part, name_part in enumerate(parts):

        part = music21.stream.Part()

        part.id = name_part

        df_grans['event'] = (df_grans[name_part].shift(1) != df_grans[name_part]).astype(int).cumsum()

        df_events = df_grans.reset_index().groupby([name_part, 'event'])[column_index].apply(np.array)

        beat_to_struct_score = dict()

        for i, span in df_events.iteritems():

            struct = i[0]

            beat_start = span[0]

            beat_end = span[-1]

            struct_score = get_struct_score(struct, name_part=name_part)

            struct_score.duration = music21.duration.Duration(
                beat_end - beat_start + 1 / 48
            )

            beat_to_struct_score[beat_start] = struct_score

        counter_measure = 1

        measure = music21.stream.Measure(
            number=counter_measure
        )

        for beat in df_grans.index.get_level_values(0).tolist():
            if int(beat) == beat and int(beat) % 4 == 0:
                part.append(measure)
                counter_measure = counter_measure + 1
                measure = music21.stream.Measure(
                    number=counter_measure
                )

            if beat in beat_to_struct_score:
                struct_score = beat_to_struct_score[beat]
                measure.append(
                    struct_score
                )

        score.insert(i_part, part)

    return score


def live_to_xml(
        notes_live: List[nl.NoteLive],
        mode: str = 'monophonic'
) -> List:
    if mode == 'monophonic':
        notes = []

        for note_live in notes_live:
            note = music21.note.Note(
                pitch=note_live.pitch
            )
            note.duration = music21.duration.Duration(
                note_live.beats_duration
            )

            note.offset = note_live.beat_start

            notes.append(note)

        return notes

    elif mode == 'polyphonic':
        # TODO: this hard a hard requirement that they're sorted by beat beforehand
        groups_notes = []
        unique_onsets_beats = []

        def get_beat_start(note):
            return note.beat_start

        for beat_start, group_note in groupby(notes_live, get_beat_start):
            groups_notes.append(list(group_note))
            unique_onsets_beats.append(beat_start)

        chords = []

        for group in groups_notes:

            chord = music21.chord.Chord([
                music21.note.Note(
                    pitch=music21.pitch.Pitch(
                        midi=note_live.pitch
                    )
                ).name for
                note_live
                in group
            ])

            # TODO: this makes the assumption that all notes in the group have the same offsets and duration

            chord.offset = group[-1].beat_start
            chord.duration = music21.duration.Duration(group[-1].beats_duration)
            chords.append(chord)

        return chords

    else:
        raise 'mode ' + mode + 'not supported'


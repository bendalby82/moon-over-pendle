import time
import rtmidi
from rtmidi.midiconstants import NOTE_ON, NOTE_OFF

def play_note(midi_out, note, velocity=100, duration=0.5, channel=0):
    """Send a note-on then note-off to an open MIDI output port."""
    midi_out.send_message([NOTE_ON + channel, note, velocity])
    time.sleep(duration)
    midi_out.send_message([NOTE_OFF + channel, note, 0])

def map_to_midi(value, value_min, value_max, scale_intervals, root_midi=60, octave_range=0):
    """
    Map a numeric value to a MIDI note within a given scale.

    Args:
        value:           The arbitrary input value.
        value_min:       Minimum of the input range.
        value_max:       Maximum of the input range.
        scale_intervals: List of semitone offsets from root, e.g. [0,2,4,5,7,9,11] for major.
        root_midi:       MIDI note number of the scale root (default C4 = 60).
        octave_range:    Number of octaves above the root to span (default 0 = one octave).

    Returns:
        int: MIDI note number.
    
    Example:
        midi_note = map_to_midi(64, 0, 127, MAJOR, root_midi=60)
    """
    n = len(scale_intervals) * (octave_range + 1)
    # Build the full note list spanning multiple octaves
    notes = [root_midi + i + 12 * (octave_range + 1) // (octave_range + 1) for i in scale_intervals]
    # Simpler: just tile the scale
    notes = [root_midi + scale_intervals[i % len(scale_intervals)] + 12 * (i // len(scale_intervals)) for i in range(n)]

    # Normalize input to [0, 1]
    t = (value - value_min) / (value_max - value_min)
    t = max(0.0, min(1.0, t))  # clamp

    # Map to index
    index = round(t * (n - 1))
    return notes[index]


# --- Scales ---
MAJOR       = [0, 2, 4, 5, 7, 9, 11]
MINOR       = [0, 2, 3, 5, 7, 8, 10]
PENTATONIC  = [0, 2, 4, 7, 9]
BLUES       = [0, 3, 5, 6, 7, 10]

# --- Usage ---
midi_out = rtmidi.MidiOut()
ports = midi_out.get_ports()

if ports:
    midi_out.open_port(0)  # pick your device
else:
    midi_out.open_virtual_port("Python Virtual Output")

# Play the mapped notes in sequence
for v in range(0, 128, 8):
    note = map_to_midi(v, 0, 127, MAJOR, root_midi=60)
    play_note(midi_out, note, duration=0.4)

midi_out.close_port()
from pychord import Chord


def is_chord(value):
    try:
        Chord(value)
        return True
    except ValueError:
        return False
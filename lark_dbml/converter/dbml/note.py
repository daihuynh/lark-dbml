import os

from ...schema import Note
from .base import BaseDBMLConverter
from .utils import quote_value, name_to_str


class NoteConverter(BaseDBMLConverter[Note]):
    def convert(self, node):
        note = node
        note_def = f"Note {name_to_str(note)} {{"
        note_def += os.linesep
        note_def += quote_value(note.note)
        note_def += os.linesep
        note_def += "}"
        return note_def

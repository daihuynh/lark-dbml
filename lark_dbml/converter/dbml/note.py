import os

from ...schema import Note
from .base import BaseDBMLConverter
from .utils import quote_value, name_to_str


class NoteConverter(BaseDBMLConverter[Note]):
    """
    DBML converter for Note objects.

    Converts DBML Note objects to DBML string definitions.
    """

    def convert(self, node):
        """
        Convert a DBML Note object to a DBML string definition.

        Args:
            node: The Note object to convert.

        Returns:
            str: The DBML string representation of the note.
        """
        note = node
        note_def = f"Note {name_to_str(note)} {{"
        note_def += os.linesep
        note_def += quote_value(note.note)
        note_def += os.linesep
        note_def += "}"
        return note_def

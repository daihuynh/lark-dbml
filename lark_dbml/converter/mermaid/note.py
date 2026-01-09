import os
from ...schema import Note
from .base import BaseMermaidConverter


class NoteConverter(BaseMermaidConverter[Note]):
    def convert(self, node: Note) -> str:
        # Convert sticky notes to comments
        return f"%% Note: {node.note.replace(os.linesep, ' ')}"

from ...schema import Note
from .base import BaseDataContractConverter


class NoteConverter(BaseDataContractConverter[Note]):
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
        kv = {note.name: {}}
        try:
            props = self.settings.deserialization_func(note.note)
            kv[note.name].update(props)
        except Exception:
            pass
        return kv

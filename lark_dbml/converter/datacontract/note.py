from ...schema import Note
from .base import BaseDataContractConverter


class NoteConverter(BaseDataContractConverter[Note]):
    """
    Data contract converter for Note objects.

    Converts DBML Note objects to data contract dictionary definitions, using a deserialization
    function to extract properties from the note text if available.
    """

    def convert(self, node):
        """
        Convert a DBML Note object to a data contract dictionary definition.

        Args:
            node: The Note object to convert.

        Returns:
            dict: The data contract dictionary representation of the note.
        """
        note = node
        kv = {note.name: {}}
        try:
            props = self.settings.deserialization_func(note.note)
            kv[note.name].update(props)
        except Exception:
            pass
        return kv

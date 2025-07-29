from ...schema import Enum
from .base import BaseDataContractConverter


class EnumConverter(BaseDataContractConverter[Enum]):
    """
    Data contract converter for Enum objects.

    Converts DBML Enum objects to data contract dictionary definitions, including enum values.
    """

    def convert(self, node):
        """
        Convert a DBML Enum object to a data contract dictionary definition.

        Args:
            node: The Enum object to convert.

        Returns:
            dict: The data contract dictionary representation of the enum.
        """
        enum = node
        kv = {
            "type": "string",
            "enum": list(map(lambda value: value.value, enum.values)),
        }

        return kv

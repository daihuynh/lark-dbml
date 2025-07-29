from ...schema import Enum
from .base import BaseDataContractConverter


class EnumConverter(BaseDataContractConverter[Enum]):
    """
    DBML converter for Enum objects.

    Converts DBML Enum objects to DBML string definitions, including enum values
    and their associated settings.
    """

    def convert(self, node):
        """
        Convert a DBML Enum object to a DBML string definition.

        Args:
            node: The Enum object to convert.

        Returns:
            str: The DBML string representation of the enum.
        """
        enum = node
        kv = {
            "type": "string",
            "enum": list(map(lambda value: value.value, enum.values)),
        }

        return kv

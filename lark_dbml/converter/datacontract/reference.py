from ...schema import Reference
from .base import BaseDataContractConverter


class ReferenceConverter(BaseDataContractConverter[Reference]):
    """
    DBML converter for Reference objects.

    Converts DBML Reference objects to DBML string definitions, including columns,
    relationships, and settings.
    """

    def convert(self, node):
        """
        Convert a DBML Reference object to a DBML string definition.

        Args:
            node: The Reference object to convert.

        Returns:
            str: The DBML string representation of the reference.
        """
        reference = node
        kv = {"fields": {}}
        for idx, column in enumerate(reference.from_columns):
            kv["fields"] = {
                column: {
                    "references": f"{reference.to_table.name}.{reference.to_columns[idx]}"
                }
            }

        return kv

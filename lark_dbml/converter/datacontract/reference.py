from ...schema import Reference
from .base import BaseDataContractConverter


class ReferenceConverter(BaseDataContractConverter[Reference]):
    """
    Data contract converter for Reference objects.

    Converts DBML Reference objects to data contract dictionary definitions,
    including referenced columns and relationships.
    """

    def convert(self, node):
        """
        Convert a DBML Reference object to a data contract dictionary definition.

        Args:
            node: The Reference object to convert.

        Returns:
            dict: The data contract dictionary representation of the reference.
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

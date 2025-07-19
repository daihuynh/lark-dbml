from sqlglot import expressions as exp

from ...schema import Enum
from .base import BaseSQLConverter


class EnumConverter(BaseSQLConverter[Enum]):
    """
    SQL converter for DBML Enum objects.

    Converts DBML enum definitions to SQLGlot expressions for supported SQL dialects.
    """

    def convert(self, node):
        """
        Convert a DBML Enum object to a SQLGlot command for enum type creation.

        Args:
            node: The Enum object to convert.

        Returns:
            exp.Command: The SQLGlot command expression for creating the enum type.
        """
        enum = node
        enum_name = enum.name if not enum.db_schema else f"{enum.db_schema}.{enum.name}"
        values = ",".join(f"'{value.value}'" for value in enum.values)
        return exp.Command(
            this="CREATE", expression=f"TYPE {enum_name} AS ENUM ({values})"
        )

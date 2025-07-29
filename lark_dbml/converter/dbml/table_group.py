import os

from ...schema import TableGroup
from .base import BaseDBMLConverter
from .utils import name_to_str


class TableGroupConverter(BaseDBMLConverter[TableGroup]):
    """
    DBML converter for TableGroup objects.

    Converts DBML TableGroup objects to DBML string definitions, including contained tables.
    """

    def convert(self, node):
        """
        Convert a DBML TableGroup object to a DBML string definition.

        Args:
            node: The TableGroup object to convert.

        Returns:
            str: The DBML string representation of the table group.
        """
        group = node
        group_def = f"TableGroup {name_to_str(group)} {{"
        group_def += os.linesep
        group_def += os.linesep.join(
            self.settings.indent + name_to_str(table_name)
            for table_name in group.tables
        )
        group_def += os.linesep
        group_def += "}"
        return group_def

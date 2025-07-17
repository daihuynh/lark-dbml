import os

from ...schema import TableGroup
from .base import BaseDBMLConverter
from .utils import name_to_str


class TableGroupConverter(BaseDBMLConverter[TableGroup]):
    def convert(self, node):
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

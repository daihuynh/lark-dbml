import os

from ...schema import Table
from .base import BaseMermaidConverter, MermaidConverterSettings
from .column import ColumnConverter


class TableConverter(BaseMermaidConverter[Table]):
    def __init__(
        self,
        settings: MermaidConverterSettings,
        column_converter: ColumnConverter,
    ):
        super().__init__(settings)
        self.column_converter = column_converter

    def convert(self, node: Table) -> str:
        # Mermaid syntax:
        # TableName {
        #     type name PK "comment"
        # }

        lines = []
        table_name = node.name
        if node.alias:
            # Mermaid handles aliases in relationships, but for entity definition
            # usually the main name is used.
            # Or "alias" could be the name displayed?
            # For simplicity, use the name.
            pass

        lines.append(f"{table_name} {{")

        for column in node.columns:
            col_def = self.column_converter.convert(column)
            lines.append(f"{self.settings.indent}{col_def}")

        lines.append("}")
        return os.linesep.join(lines)

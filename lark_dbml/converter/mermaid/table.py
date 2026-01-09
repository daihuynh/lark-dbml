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

        # Handle schema in table name
        table_name = node.name
        if node.db_schema:
            table_name = f'"{node.db_schema}.{node.name}"'

        if node.alias and self.settings.use_alias:
            table_name = (
                f"{table_name}[{node.alias}]"
                if " " not in node.alias
                else f'{table_name}["{node.alias}"]'
            )

        lines.append(f"{table_name} {{")

        for column in node.columns:
            col_def = self.column_converter.convert(column)
            lines.append(f"{self.settings.indent}{col_def}")

        lines.append("}")
        return os.linesep.join(lines)

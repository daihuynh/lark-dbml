from collections import deque
import os

from ...schema import Table, TableSettings
from .base import BaseDBMLConverter, TableType
from .utils import name_to_str, quote_value, quote_identifier
from .column import ColumnConverter
from .index import IndexConverter


class TableConverter(BaseDBMLConverter[TableType]):
    """
    DBML converter for Table and TablePartial objects.

    Converts DBML Table and TablePartial objects to DBML string definitions,
    including columns, indexes, settings, aliases, table partials, and notes.
    """

    def __init__(
        self,
        settings,
        column_converter: ColumnConverter,
        index_converter: IndexConverter,
    ):
        """
        Initialize the table converter.

        Args:
            settings: DBMLConverterSettings object.
            column_converter: Converter for columns.
            index_converter: Converter for indexes.
        """
        super().__init__(settings)
        self.column_converter = column_converter
        self.index_converter = index_converter

    def convert(self, node):
        """
        Convert a DBML Table or TablePartial object to a DBML string definition.

        Args:
            node: The Table or TablePartial object to convert.

        Returns:
            str: The DBML string representation of the Table or TablePartial.
        """
        table = node
        is_table = isinstance(table, Table)
        table_type = "Table" if is_table else "TablePartial"
        alias = ""
        settings = ""
        # Alias
        if is_table and table.alias:
            alias = f" as {quote_identifier(table.alias)}"
        # Settings
        if table.settings:
            settings = f" [{self._convert_table_settings(table.settings)}]"
        # Header
        table_def = f"{table_type} {name_to_str(table)}{alias}{settings} {{"
        table_def += os.linesep
        # Columns + Table Partials
        if is_table and table.table_partials:
            q = deque(table.table_partial_orders.items())
            columns = iter(table.columns)
            for order in range(1, len(table.table_partials) + len(table.columns) + 1):
                # Index of the first item in queue
                if q and order == q[0][1]:
                    table_partial, _ = q.popleft()
                    table_def += f"{self.settings.indent}~{table_partial}"
                    table_def += os.linesep
                else:
                    table_def += self.column_converter.convert(next(columns))
                    table_def += os.linesep
        else:
            table_def += os.linesep.join(
                self.column_converter.convert(column) for column in table.columns
            )
            table_def += os.linesep
        # Index
        if table.indexes:
            table_def += f"{self.settings.indent}indexes {{"
            table_def += os.linesep
            table_def += os.linesep.join(
                self.index_converter.convert(index) for index in table.indexes
            )
            table_def += os.linesep
            table_def += f"{self.settings.indent}}}"
            table_def += os.linesep
        # Note
        if is_table and table.note:
            table_def += os.linesep
            table_def += f"{self.settings.indent}Note: {quote_value(table.note)}"
            table_def += os.linesep
        table_def += "}"
        return table_def

    def _convert_table_settings(self, settings: TableSettings) -> str:
        kv = {}
        for field in TableSettings.model_fields:
            if (value := getattr(settings, field)) is not None:
                match field:
                    case "note":
                        kv[field] = quote_value(value)
                    case "header_color":
                        kv["headercolor"] = value
                    case _:
                        kv[field] = value
        if self.settings.allow_extra:
            for k, v in settings.model_extra.items():
                kv[k] = quote_value(v)
        return ", ".join(f"{k}: {v}" for k, v in kv.items())

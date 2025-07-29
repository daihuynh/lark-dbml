from collections import OrderedDict, defaultdict
from typing import List

from ...schema import Reference, TablePartial
from .base import BaseDataContractConverter, TableType
from .column import ColumnConverter
from .reference import ReferenceConverter


class TableConverter(BaseDataContractConverter[TableType]):
    """
    Data contract converter for Table and TablePartial objects.

    Converts DBML Table and TablePartial objects to data contract dictionary definitions,
    including columns, indexes, references, table partials, and notes.
    """

    def __init__(
        self, settings, table_partials: List[TablePartial], references: List[Reference]
    ):
        """
        Initialize the table converter.

        Args:
            settings: DataContractConverterSettings object.
            table_partials: List of TablePartial objects for column inheritance.
            references: List of Reference objects for foreign key constraints.
        """
        super().__init__(settings)
        self.table_partials = table_partials
        self.references = references
        self.column_converter = ColumnConverter(settings)
        self.reference_converter = ReferenceConverter(settings)

    def convert(self, node):
        """
        Convert a DBML Table or TablePartial object to a data contract dictionary definition.

        Args:
            node: The Table or TablePartial object to convert.

        Returns:
            dict: The data contract dictionary representation of the table or table partial.
        """
        table = node
        kv = {
            "models": {
                table.name: {"type": "table", "fields": defaultdict(OrderedDict)}
            },
            "definitions": {},
        }
        if self.settings.note_as_description and table.settings and table.settings.note:
            kv["models"][table.name]["description"] = table.settings.note
        if self.settings.note_as_fields and table.note:
            fields = self.settings.deserialization_func(table.note)
            kv["models"][table.name].update(fields)
            kv["models"][table.name]["additionalFields"] = True

        # OrderedDict maintains the order of columns
        # this helps overriding settings of columns
        # based on main table's column orders and
        # table partial's column orders
        column_map = OrderedDict()
        indexes = table.indexes or []
        if table.table_partials:
            column_count = len(table.columns)
            last_order_idx = 0
            for (
                table_partial_name,
                table_partial_order,
            ) in table.table_partial_orders.items():
                if (
                    table_partial_order <= column_count
                    and last_order_idx < column_count
                ):
                    # Append columns before this partial order
                    for column in table.columns[
                        last_order_idx : (table_partial_order - 1)
                    ]:
                        column_map[column.name] = column
                # Find the table partials
                table_partial = next(
                    filter(
                        lambda tp: tp.name == table_partial_name, self.table_partials
                    ),
                    None,
                )

                # Append partial's columns
                for column in table_partial.columns:
                    column_map[column.name] = column

                # Append indexes
                indexes += table_partial.indexes or []

                # Store the order index
                last_order_idx = table_partial_order - 1

            if last_order_idx + 1 < column_count:
                for column in table.columns[last_order_idx:]:
                    column_map[column.name] = column
            columns = list(column_map.values())
        else:
            columns = table.columns

        # Columns
        for column in columns:
            column_dict = self.column_converter.convert(column)
            kv["models"][table.name]["fields"].update(column_dict["fields"])
            kv["definitions"].update(column_dict["definitions"])

        # References
        for reference in self.references:
            if (
                reference.from_table.db_schema == table.db_schema
                and reference.from_table.name == table.name
            ):
                ref_def = self.reference_converter.convert(reference)
                for column in ref_def["fields"]:
                    kv["models"][table.name]["fields"][column].update(
                        ref_def["fields"][column]
                    )

        # Primary Key Composite from Index
        if indexes:
            composite_pks = filter(
                lambda index: index.settings and index.settings.is_primary_key,
                table.indexes,
            )
            for composite_pk in composite_pks:
                kv["models"][table.name]["primaryKey"] = composite_pk.columns

        return kv

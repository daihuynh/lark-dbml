from typing import List
from sqlglot import expressions as exp
from ...schema import Column, Enum, Reference, Table, TablePartial
from .base import BaseSQLConverter
from .column import ColumnConverter
from .index import IndexConverter, CompositePKIndexConverter
from .reference import ReferenceConverter


class TableConverter(BaseSQLConverter[Table]):
    def __init__(
        self,
        dialect,
        table_partials: List[TablePartial],
        references: List[Reference],
        enums: List[Enum],
    ):
        super().__init__(dialect)
        self.column_converter = ColumnConverter(dialect, enums)
        self.index_converter = IndexConverter(dialect, self)
        self.composite_pk_converter = CompositePKIndexConverter(dialect)
        self.reference_converter = ReferenceConverter(dialect)
        self.table_partials = table_partials
        self.references = references

    def convert(self, node):
        table = node
        # column name : column object
        column_map: dict[str, Column] = {}
        # Import all columns from table partials
        if table.table_partials:
            assert self.table_partials is not None
            for table_partial in table.table_partials:
                # First or default
                ref_table = next(
                    filter(
                        lambda table: table.name == table_partial, self.table_partials
                    ),
                    None,
                )
                assert ref_table is not None, (
                    f"Reference Table {table_partial} is not found"
                )
                if ref_table:
                    column_map.update(
                        map(lambda column: (column.name, column), ref_table.columns)
                    )
        # Columns in table will be added last
        # to override any overlapped columns
        # in the table partial list
        for column in table.columns:
            column_map.update(map(lambda column: (column.name, column), table.columns))

        # Column definitions
        col_defs = []
        for column_name in column_map:
            column = column_map[column_name]
            col_defs.append(self.column_converter.convert(column))

        # Constraints: Foreign Key
        constraint_defs = []
        for reference in self.references:
            constraint_defs.append(self.reference_converter.convert(reference))

        # Constraints: Primary Key
        if table.indexes:
            composite_pk_indexes = list(
                filter(
                    lambda index: index.settings and index.settings.is_primary_key,
                    table.indexes,
                )
            )
            for composite_pk_index in composite_pk_indexes:
                constraint_defs.append(
                    self.composite_pk_converter.convert(composite_pk_index)
                )

        table_def = exp.Create(
            this=exp.Schema(
                this=exp.Table(
                    this=exp.Identifier(this=table.name, quoted=True),
                    db=exp.Identifier(this=table.db_schema, quoted=True)
                    if table.db_schema
                    else None,
                ),
                expressions=col_defs + constraint_defs,
            ),
            kind="TABLE",
        )
        return table_def

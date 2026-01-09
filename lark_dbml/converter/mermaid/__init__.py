from io import StringIO
import os

from ...schema import Diagram, Reference, ReferenceInline, ColumnSettings
from .base import MermaidConverterSettings
from .column import ColumnConverter
from .enum import EnumConverter
from .note import NoteConverter
from .project import ProjectConverter
from .reference import ReferenceConverter
from .table import TableConverter
from .table_group import TableGroupConverter

__all__ = ["to_mermaid", "MermaidConverterSettings"]


def to_mermaid(diagram: Diagram, settings: MermaidConverterSettings = None) -> str:
    """
    Convert a DBML Diagram object to a Mermaid ER diagram string.

    Args:
        diagram: The DBML Diagram object to convert.
        settings: Optional MermaidConverterSettings for formatting.

    Returns:
        str: The Mermaid string representation of the diagram.
    """
    if not settings:
        settings = MermaidConverterSettings()

    endblock = os.linesep * 2
    project_converter = ProjectConverter(settings)
    enum_converter = EnumConverter(settings)
    reference_converter = ReferenceConverter(settings)
    table_group_converter = TableGroupConverter(settings)
    note_converter = NoteConverter(settings)
    column_converter = ColumnConverter(settings)
    # index_converter = IndexConverter(settings) # Not used directly in main loop but required by TableConverter if we were to use it there

    table_converter = TableConverter(settings, column_converter=column_converter)

    with StringIO() as buffer:
        buffer.write("erDiagram")
        buffer.write(endblock)

        # Project
        if diagram.project:
            project_def = project_converter.convert(diagram.project)
            if project_def:
                buffer.write(project_def)
                buffer.write(endblock)

        # Enum (Comments)
        for enum in diagram.enums:
            enum_def = enum_converter.convert(enum)
            if enum_def:
                buffer.write(enum_def)
                buffer.write(endblock)

        # Tables
        # Combine all inline references and references all together
        references = []
        for table in diagram.tables:
            for column in table.columns:
                if column.settings and column.settings.ref:
                    ref = Reference(**column.settings.ref.model_dump())
                    ref.from_table = table
                    ref.from_columns = [column.name]
                    references.append(ref)

        references.extend(diagram.references)
        # Column map
        ref_map = {}  # Table - Column names
        for reference in references:
            ref_map[str(reference.from_table)] = reference.from_columns

        # Table map: Table name - Table Partials
        table_map = {
            table_partial.name: table_partial
            for table_partial in diagram.table_partials
        }
        for table in diagram.tables:
            reference_columns = ref_map.get(str(table))
            table = table.model_copy()
            # Table Partial
            if table.table_partials:
                for table_partial_name, order in table.table_partial_orders.items():
                    table_partial = table_map[table_partial_name]
                    for idx in range(len(table_partial.columns) - 1, -1, -1):
                        column = table_partial.columns[idx]
                        table.columns.insert(order - 1, column)
            # Index
            if table.indexes:
                # Build column map
                column_map = {column.name: column for column in table.columns}
                for index in table.indexes:
                    if index.settings and (
                        index.settings.is_primary_key or index.settings.is_unique
                    ):
                        for column_name in index.columns:
                            column = column_map[column_name]
                            if not column.settings:
                                column.settings = ColumnSettings.model_construct()
                            if index.settings.is_primary_key:
                                column.settings.is_primary_key = True
                            if index.settings.is_unique:
                                column.settings.is_unique = True
            # Reference
            if reference_columns:
                for column_name in reference_columns:
                    column = next(
                        filter(lambda c: c.name == column_name, table.columns)
                    )
                    if not column.settings:
                        column.settings = ColumnSettings.model_construct()
                    column.settings.ref = ReferenceInline.model_construct()
            # Convert
            table_def = table_converter.convert(table)
            if table_def:
                buffer.write(table_def)
                buffer.write(endblock)

        # Reference
        for reference in references:
            reference_def = reference_converter.convert(reference)
            if reference_def:
                buffer.write(reference_def)
                buffer.write(endblock)

        # Table Groups (Comments)
        for table_group in diagram.table_groups:
            group_def = table_group_converter.convert(table_group)
            if group_def:
                buffer.write(group_def)
                buffer.write(endblock)

        # Sticky notes
        for note in diagram.sticky_notes:
            note_def = note_converter.convert(note)
            if note_def:
                buffer.write(note_def)
                buffer.write(endblock)

        return buffer.getvalue()

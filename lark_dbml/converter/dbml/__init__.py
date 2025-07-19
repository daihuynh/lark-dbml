from io import StringIO
import os

from ...schema import Diagram
from .base import DBMLConverterSettings
from .enum import EnumConverter
from .project import ProjectConverter
from .reference import ReferenceConverter
from .table_group import TableGroupConverter
from .note import NoteConverter
from .column import ColumnConverter
from .index import IndexConverter
from .table import TableConverter

__all__ = ["to_dbml", "DBMLConverterSettings"]


def to_dbml(diagram: Diagram, settings: DBMLConverterSettings = None) -> str:
    """
    Convert a DBML Diagram object to a DBML string.

    This function uses converter classes for each DBML schema type to generate
    the DBML string representation of the diagram, including project, enums,
    table partials, tables, references, table groups, and sticky notes.

    Args:
        diagram: The DBML Diagram object to convert.
        settings: Optional DBMLConverterSettings for formatting.

    Returns:
        str: The DBML string representation of the diagram.
    """
    endblock = os.linesep * 2
    project_converter = ProjectConverter(settings)
    enum_converter = EnumConverter(settings)
    reference_converter = ReferenceConverter(settings)
    table_group_converter = TableGroupConverter(settings)
    note_converter = NoteConverter(settings)
    column_converter = ColumnConverter(settings)
    index_converter = IndexConverter(settings)
    table_converter = TableConverter(
        settings, column_converter=column_converter, index_converter=index_converter
    )

    with StringIO() as buffer:
        # Project
        if diagram.project:
            project_def = project_converter.convert(diagram.project)
            buffer.write(project_def)
            buffer.write(endblock)

        # Enum
        for enum in diagram.enums:
            enum_def = enum_converter.convert(enum)
            buffer.write(enum_def)
            buffer.write(endblock)

        # Table Partials
        for table in diagram.table_partials:
            table_def = table_converter.convert(table)
            buffer.write(table_def)
            buffer.write(endblock)

        # Tables
        for table in diagram.tables:
            table_def = table_converter.convert(table)
            buffer.write(table_def)
            buffer.write(endblock)

        # Reference
        for reference in diagram.references:
            reference_def = reference_converter.convert(reference)
            buffer.write(reference_def)
            buffer.write(endblock)

        # Table Groups
        for table_group in diagram.table_groups:
            group_def = table_group_converter.convert(table_group)
            buffer.write(group_def)
            buffer.write(endblock)

        # Stick notes
        for note in diagram.sticky_notes:
            note_def = note_converter.convert(note)
            buffer.write(note_def)
            buffer.write(endblock)

        return buffer.getvalue()

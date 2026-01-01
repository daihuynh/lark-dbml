from io import StringIO
import os

from ...schema import Diagram
from .base import MermaidConverterSettings
from .column import ColumnConverter
from .enum import EnumConverter
from .index import IndexConverter
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

    table_converter = TableConverter(
        settings,
        column_converter=column_converter
    )

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
        for table in diagram.tables:
            table_def = table_converter.convert(table)
            if table_def:
                buffer.write(table_def)
                buffer.write(endblock)

        # Table Partials (Treat as tables for now, or merge? DBML usually parses them separately)
        # Mermaid doesn't support partial definitions well, so we might just append them as separate entities
        # or we should have merged them before. Assuming Diagram object keeps them separate.
        # If we print them as same name, Mermaid might merge or error.
        # Let's write them out.
        for table in diagram.table_partials:
            table_def = table_converter.convert(table)
            if table_def:
                buffer.write(table_def)
                buffer.write(endblock)

        # Reference
        for reference in diagram.references:
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

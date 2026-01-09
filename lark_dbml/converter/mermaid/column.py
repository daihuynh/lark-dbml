from ...schema import Column
from .base import BaseMermaidConverter


class ColumnConverter(BaseMermaidConverter[Column]):
    def convert(self, node: Column) -> str:
        parts = []

        # node.data_type can be DataType or Name
        if hasattr(node.data_type, "sql_type"):
            parts.append(node.data_type.sql_type)
        # Fallback if it's a Name (e.g. enum reference)
        elif hasattr(node.data_type, "name"):
            parts.append(node.data_type.name)
        else:
            parts.append("unknown")

        # Name
        parts.append(node.name)

        # PK/FK/UK
        keys = []
        if node.settings:
            if node.settings.is_primary_key:
                keys.append("PK")
            if node.settings.ref:
                keys.append("FK")
            if node.settings.is_unique:
                keys.append("UK")

        if keys:
            parts.append(",".join(keys))

        # Comment
        if node.settings and node.settings.note:
            # Escape double quotes
            note = node.settings.note.replace('"', '\\"')
            parts.append(f'"{note}"')

        return " ".join(parts)

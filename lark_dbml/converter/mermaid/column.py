from ...schema import Column
from .base import BaseMermaidConverter


class ColumnConverter(BaseMermaidConverter[Column]):
    def convert(self, node: Column) -> str:
        # Mermaid syntax: <type> <name> [PK|FK] ["comment"]
        # Example: string id PK "Primary Key"

        parts = []

        # Type
        if node.data_type and node.data_type.sql_type:
            parts.append(node.data_type.sql_type)
        else:
            parts.append("unknown")

        # Name
        parts.append(node.name)

        # PK/FK
        keys = []
        if node.settings:
            if node.settings.is_primary_key:
                keys.append("PK")
            # Note: Foreign keys are handled at the table level in DBML usually,
            # or reference level. DBML doesn't strictly mark column as FK in settings
            # unless it's an inline ref, but Mermaid ER allows FK marker.
            # We'll check if we can easily detect FK.
            # For now, let's stick to PK.

        if keys:
            parts.append(",".join(keys))

        # Comment
        if node.settings and node.settings.note:
            # Escape double quotes
            note = node.settings.note.replace('"', '\\"')
            parts.append(f'"{note}"')

        return " ".join(parts)

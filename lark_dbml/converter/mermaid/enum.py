from ...schema import Enum
from .base import BaseMermaidConverter


class EnumConverter(BaseMermaidConverter[Enum]):
    def convert(self, node: Enum) -> str:
        # Mermaid ER doesn't support Enums directly.
        # We can add a comment listing the enum values.
        lines = [f"%% Enum: {node.name}"]
        for item in node.values:
            lines.append(f"%%   - {item.value}")
        return "\n".join(lines)

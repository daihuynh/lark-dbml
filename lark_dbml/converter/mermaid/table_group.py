from ...schema import TableGroup
from .base import BaseMermaidConverter


class TableGroupConverter(BaseMermaidConverter[TableGroup]):
    def convert(self, node: TableGroup) -> str:
        # Mermaid doesn't support grouping tables visually in standard ER syntax
        return f"%% TableGroup: {node.name}"

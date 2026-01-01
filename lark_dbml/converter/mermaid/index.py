from ...schema import Index
from .base import BaseMermaidConverter


class IndexConverter(BaseMermaidConverter[Index]):
    def convert(self, node: Index) -> str:
        # Indexes are not typically shown in Mermaid ER
        return ""

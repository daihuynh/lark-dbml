from ...schema import Project
from .base import BaseMermaidConverter


class ProjectConverter(BaseMermaidConverter[Project]):
    def convert(self, node: Project) -> str:
        # Mermaid doesn't have a specific project metadata section in ER diagram syntax
        # We can add a comment
        return f"%% Project: {node.name}"

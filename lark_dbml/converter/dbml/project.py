import os

from ...schema import Name, Project
from .base import BaseDBMLConverter
from .utils import name_to_str, quote_value


class ProjectConverter(BaseDBMLConverter[Project]):
    """
    DBML converter for Project objects.

    Converts DBML Project objects to DBML string definitions, including settings
    and extra fields.
    """

    def convert(self, node):
        """
        Convert a DBML Project object to a DBML string definition.

        Args:
            node: The Project object to convert.

        Returns:
            str: The DBML string representation of the project.
        """
        project = node
        project_def = f"Project {name_to_str(project)} {{"
        project_def += os.linesep
        project_def += self._convert_project_body(project)
        project_def += os.linesep
        project_def += "}"
        return project_def

    def _convert_project_body(self, project: Project) -> str:
        """
        Convert the body of a DBML Project object to a DBML settings string.

        Args:
            project: The Project object containing settings and extra fields.

        Returns:
            str: The DBML string representation of the project's settings.
        """
        kv = {}
        for field in Project.model_fields:
            if field not in Name.model_fields:
                if (value := getattr(project, field)) is not None:
                    kv[field] = quote_value(value)
        for k, v in project.model_extra.items():
            kv[k] = quote_value(v)

        return os.linesep.join(
            f"{self.settings.indent}{k}: {v}" for k, v in sorted(kv.items())
        )

import os

from ...schema import Name, Project
from .base import BaseDBMLConverter
from .utils import name_to_str, quote_value


class ProjectConverter(BaseDBMLConverter[Project]):
    def convert(self, node):
        project = node
        project_def = f"Project {name_to_str(project)} {{"
        project_def += os.linesep
        project_def += self._convert_project_body(project)
        project_def += os.linesep
        project_def += "}"
        return project_def

    def _convert_project_body(self, project: Project) -> str:
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

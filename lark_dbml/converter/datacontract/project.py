from ...schema import Project
from .base import BaseDataContractConverter


class ProjectConverter(BaseDataContractConverter[Project]):
    """
    DBML converter for Project objects.

    Converts DBML Project objects to DBML string definitions, including settings
    and extra fields.
    """

    def convert(self, node):
        project = node
        kv = {}
        for field in Project.model_fields:
            if (value := getattr(project, field)) is not None:
                if field not in ("note", "name"):
                    kv[field] = value
                elif field == "note":
                    if self.settings.note_as_fields:
                        try:
                            extra = self.settings.deserialization_func(value)
                            kv.update(extra)
                        except Exception:
                            pass
                    elif self.settings.note_as_description:
                        kv["description"] = value
        for k, v in project.model_extra.items():
            kv[k] = v

        return kv

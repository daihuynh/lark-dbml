from ...schema import IndexSettings, Index
from .base import BaseDBMLConverter
from .utils import quote_column, quote_value


class IndexConverter(BaseDBMLConverter[Index]):
    def convert(self, node):
        index = node
        index_def = self.settings.indent * 2
        index_def += f"({','.join(quote_column(column) for column in index.columns)})"
        if index.settings:
            index_def += f" [{self._convert_index_settings(index.settings)}]"
        return index_def

    def _convert_index_settings(self, settings: IndexSettings):
        kv = {}
        for field in IndexSettings.model_fields:
            if (
                IndexSettings.model_fields[field].annotation is not bool
                and (value := getattr(settings, field)) is not None
            ):
                key = IndexSettings.model_fields[field].alias or field
                kv[key] = quote_value(value) if field in ("name", "note") else value
        if self.settings.allow_extra:
            for k, v in settings.model_extra.items():
                kv[k] = quote_value(v)

        flags = []
        if settings.is_primary_key:
            flags.append("pk")
        if settings.is_unique:
            flags.append("unique")

        kv = list(f"{k}: {v}" for k, v in sorted(kv.items()))

        return ", ".join(flags + kv)

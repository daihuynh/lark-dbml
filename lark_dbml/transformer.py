from functools import wraps
from lark import Token, Transformer, v_args
import logging
from .schema import (
    Diagram,
    Project,
    Enum,
    Note,
    Table,
    TableGroup,
    Reference,
    ReferenceSettings,
    TablePartial,
)

logger = logging.getLogger(__name__)


def log_transform(func):
    """
    A decorator to log the entry and exit of a Transformer method.
    """

    @wraps(func)
    def wrapper(self_transformer: Transformer, *args, **kwargs):
        rule_name = func.__name__
        logger.debug(f"Entering '{rule_name}' with args: {args}")

        # Call the original method
        result = func(self_transformer, *args, **kwargs)

        logger.debug(
            f"Exiting '{rule_name}'. Result: {result!r}"
        )  # !r for representation
        return result

    return wrapper


class DBMLTransformer(Transformer[Token, Diagram]):
    def __default__(self, data, children, _):
        return {data.value.strip(): children}

    # 1. Common values
    def IDENTIFIER(self, token):
        return token.value.strip("`")

    def STRING(self, token):
        return token.value[1:-1]

    def MULTILINE_STRING(self, token):
        return token.value[3:-3].strip()

    def NUMBER(self, token):
        if token.value.isnumeric():
            return int(token.value)
        else:
            try:
                return float(token.value)
            except ValueError:
                # If it can't be converted to a number, return as is
                return token.value

    def RELATIONSHIP(self, token):
        return token.value.strip()

    def REFERENTIAL_ACTION(self, token):
        return token.value.strip()

    def FUNC_EXP(self, token):
        return token.value

    def COLOR_HEX(self, token):
        return token.value.strip()

    def true(self, *_):
        return True

    def false(self, *_):
        return False

    def pair(self, kv):
        return kv

    def settings(self, pairs):
        return {"settings": dict(pairs)}

    def name(self, vars):
        if len(vars) == 1:
            return {"name": vars[0]}
        return {"db_schema": vars[0], "name": vars[1]}

    # ====== PROJECT ======
    @v_args(inline=True)
    @log_transform
    def project(self, name, *pairs) -> Project:
        data = name | dict(pairs)
        return Project.model_validate(data)

    # ====== STICKY NOTE & NOTE INLINE ======
    def note_inline(self, vars):
        return {"note": vars[0]}

    @log_transform
    def note(self, vars) -> Note:
        return Note.model_validate(vars[0] | {"note": vars[1]})

    # ====== ENUM ======
    def enum_value(self, vars):
        data = {"value": vars[0]}
        # Settings
        if len(vars) > 1:
            data.update(vars[1])
        return data

    @v_args(inline=True)
    @log_transform
    def enum(self, name, *enum_values) -> Enum:
        data = name | {"values": enum_values}
        return Enum.model_validate(data, by_alias=True)

    # ====== TABLE GROUP ======
    @v_args(inline=True)
    @log_transform
    def group(self, name, *vars) -> TableGroup:
        data = name | {"tables": []}
        for var in vars:
            if "name" in var:
                data["tables"].append(var)
            else:
                data.update(var)
        return TableGroup.model_validate(data)

    # ====== REFERENCE ======
    def ref_col(self, cols):
        return cols

    @v_args(inline=True)
    @log_transform
    def ref(self, name, ref_col, ref_inline):
        ref_inline["ref"]["from_table"] = name
        ref_inline["ref"]["from_columns"] = ref_col
        return ref_inline

    def ref_inline(self, vars):
        return {
            "ref": {"relationship": vars[0], "to_table": vars[1], "to_columns": vars[2]}
        }

    def ref_settings(self, vars):
        settings = {}
        for var in vars:
            if isinstance(var, tuple):
                settings[var[0]] = var[1]
            else:
                settings.update(var)
        return settings

    @log_transform
    def reference(self, vars) -> Reference:
        name_dict = {}
        settings = None
        # Has no name
        if len(vars) == 1:
            relationship = vars[0]
        elif len(vars) == 2:
            if "name" in vars[0]:
                name_dict = vars[0]
                relationship = vars[1]
            else:
                relationship = vars[0]
                settings = ReferenceSettings.model_validate(vars[1]["settings"])
        else:
            name_dict = vars[0]
            relationship = vars[1]
            settings = ReferenceSettings.model_validate(vars[2]["settings"])

        data = {
            "db_schema": name_dict.get("db_schema"),
            "name": name_dict.get("name"),
            "settings": settings,
        } | relationship["ref"]
        return Reference.model_validate(data)

    # ====== TABLE ======
    def is_primary_key(self, *_):
        return "is_primary_key", True

    def is_null(self, *_):
        return "is_null", True

    def is_not_null(self, *_):
        return "is_null", False

    def is_unique(self, *_):
        return "is_unique", True

    def is_increment(self, *_):
        return "is_increment", True

    def alias(self, vars):
        return {"alias": vars[0]}

    @v_args(inline=True)
    @log_transform
    def data_type(self, sql_type, *vars):
        return {
            "data_type": {
                "sql_type": sql_type,
                "length": int(vars[0].value) if len(vars) > 0 else None,
                "scale": int(vars[1].value) if len(vars) > 1 else None,
            }
        }

    def column_setting(self, pairs):
        return pairs[0]

    def column_settings(self, pairs_or_ref):
        settings = {}
        pairs = []
        for pair in pairs_or_ref:
            if isinstance(pair, dict):
                settings.update(pair)
            else:
                pairs.append(pair)
        if pairs:
            settings.update(dict(pairs))
        return {"settings": settings}

    @v_args(inline=True)
    @log_transform
    def column(self, name, column_type, *settings):
        if "data_type" not in column_type:
            column_type = {"data_type": column_type}
        data = {"name": name} | column_type
        if settings:
            data.update(settings[0])
        return {"column": data}

    @v_args(inline=True)
    @log_transform
    def index(self, columns, *settings):
        # index_exp rule
        if isinstance(columns, dict):
            data = {"columns": columns["index_exp"]}
        else:
            data = {"columns": columns}
        if settings:
            data.update(settings[0])
        return data

    @v_args(inline=True)
    @log_transform
    def table_partial(self, name, *vars) -> TablePartial:
        data = name | {"columns": []}
        for var in vars:
            if "column" in var:
                data["columns"].append(var["column"])
            else:
                data.update(var)
        return TablePartial.model_validate(data)

    @v_args(inline=True)
    @log_transform
    def table(self, name, *vars) -> Table:
        data = name | {"columns": []}
        for var in vars:
            if "column" in var:
                data["columns"].append(var["column"])
            elif isinstance(var, str):
                table_partials = data.get("table_partials", [])
                table_partials.append(var)
                data["table_partials"] = table_partials
            else:
                data.update(var)
        return Table.model_validate(data)

    # ====== DIAGRAM ======
    def start(self, items) -> Diagram:
        diagram = Diagram.model_construct()
        for item in items:
            if isinstance(item, Project):
                diagram.project = item
            elif isinstance(item, Enum):
                diagram.enums.append(item)
            elif isinstance(item, Reference):
                diagram.references.append(item)
            elif isinstance(item, TableGroup):
                diagram.table_groups.append(item)
            elif isinstance(item, Note):
                diagram.sticky_notes.append(item)
            elif isinstance(item, Table):
                diagram.tables.append(item)
            elif isinstance(item, TablePartial):
                diagram.table_partials.append(item)

        return diagram

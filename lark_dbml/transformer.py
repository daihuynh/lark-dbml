from functools import wraps

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


def create_dbml_transformer(Transformer, Token, v_args):
    def log_transform(func):
        """
        Decorator for Transformer methods to log entry, arguments, and exit with result.
        Useful for debugging and tracing transformer rule execution.
        """

        @wraps(func)
        def wrapper(self_transformer, *args, **kwargs):
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
        """
        Lark Transformer for converting DBML parse trees into Pydantic schema models.

        This transformer handles all DBML constructs, including projects, tables, enums,
        references, table groups, notes, and settings. It uses Pydantic models for validation
        and construction of the final diagram object.
        """

        def __default__(self, data, children, _):
            """
            Default handler for unmatched rules.
            Returns a dictionary mapping the rule name to its children.
            """
            return {data.value.strip(): children}

        # 1. Common values
        def IDENTIFIER(self, token):
            """
            Returns the identifier string, stripping backticks if present.
            """
            return token.value.strip("`")

        def STRING(self, token):
            """
            Returns the string value, removing surrounding quotes.
            """
            return token.value[1:-1]

        def MULTILINE_STRING(self, token):
            """
            Returns the multiline string value, removing triple quotes and stripping whitespace.
            """
            return token.value[3:-3].strip()

        def NUMBER(self, token):
            """
            Converts the token value to int or float if possible, otherwise returns as string.
            """
            if token.value.isnumeric():
                return int(token.value)
            else:
                try:
                    return float(token.value)
                except ValueError:
                    # If it can't be converted to a number, return as is
                    return token.value

        def INT(self, token):
            return int(token.value)

        def RELATIONSHIP(self, token):
            """
            Returns the relationship operator as a string.
            """
            return token.value.strip()

        def REFERENTIAL_ACTION(self, token):
            """
            Returns the referential action as a string.
            """
            return token.value.strip()

        def FUNC_EXP(self, token):
            """
            Returns the function expression as a string.
            """
            return token.value

        def COLOR_HEX(self, token):
            """
            Returns the color hex string, stripping whitespace.
            """
            return token.value.strip()

        def true(self, *_):
            """
            Returns Python True for DBML 'true' literal.
            """
            return True

        def false(self, *_):
            """
            Returns Python False for DBML 'false' literal.
            """
            return False

        def pair(self, kv):
            """
            Returns a key-value pair dictionary for settings.
            """
            return kv

        def settings(self, pairs):
            """
            Returns a dictionary of settings from key-value pairs.
            """
            return {"settings": dict(pairs)}

        def name(self, vars):
            return {"name": vars[0]}

        def qualified_name(self, vars):
            """
            Returns a dictionary with schema and name, or just name if schema is absent.
            """
            if len(vars) == 1:
                return vars[0]
            return {"db_schema": vars[0]["name"]} | vars[1]

        # ====== PROJECT ======
        @v_args(inline=True)
        @log_transform
        def project(self, name, *pairs) -> Project:
            """
            Constructs a Project model from name and settings pairs.
            """
            data = name | dict(pairs)
            return Project.model_validate(data)

        # ====== STICKY NOTE & NOTE INLINE ======
        def note_inline(self, vars):
            """
            Returns a dictionary for an inline note.
            """
            return {"note": vars[0]}

        @log_transform
        def note(self, vars) -> Note:
            """
            Constructs a Note model from schema/name and note text.
            """
            return Note.model_validate(vars[0] | {"note": vars[1]})

        # ====== ENUM ======
        def enum_value(self, vars):
            """
            Returns a dictionary for an enum value, including settings if present.
            """
            data = {"value": vars[0]}
            # Settings
            if len(vars) > 1:
                data.update(vars[1])
            return data

        @v_args(inline=True)
        @log_transform
        def enum(self, name, *enum_values) -> Enum:
            """
            Constructs an Enum model from name and enum values.
            """
            data = name | {"values": enum_values}
            return Enum.model_validate(data, by_alias=True)

        # ====== TABLE GROUP ======
        @v_args(inline=True)
        @log_transform
        def group(self, name, *vars) -> TableGroup:
            """
            Constructs a TableGroup model from name and contained tables/settings.
            """
            data = name | {"tables": []}
            for var in vars:
                if "name" in var:
                    data["tables"].append(var)
                else:
                    data.update(var)
            return TableGroup.model_validate(data)

        # ====== REFERENCE ======
        @v_args(inline=True)
        @log_transform
        def ref(self, table_ref, ref_inline):
            """
            Constructs a reference dictionary from name, columns, and inline reference details.
            """
            ref_inline["ref"]["from_table"] = table_ref[0]
            ref_inline["ref"]["from_columns"] = table_ref[1]
            return ref_inline

        @v_args(inline=True)
        def ref_inline(self, relationship, table_ref):
            """
            Returns a dictionary for inline reference details (relationship, target table, columns).
            """
            return {
                "ref": {
                    "relationship": relationship,
                    "to_table": table_ref[0],
                    "to_columns": table_ref[1],
                }
            }

        def table_ref(self, vars):
            table_name = {}
            # No schema
            if len(vars) == 2:
                table_name |= vars[0]
            else:
                table_name |= vars[1]
                table_name["db_schema"] = vars[0]["name"]
            if "column_list" in vars[-1]:
                columns = list(map(lambda v: v["name"], vars[-1]["column_list"]))
            else:
                columns = [vars[-1]["name"]]
            return table_name, columns

        @log_transform
        def reference(self, vars) -> Reference:
            """
            Constructs a Reference model from name, relationship, and settings.
            Handles cases with or without name and settings.
            """
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
            """
            Returns a tuple indicating the column is a primary key.
            """
            return "is_primary_key", True

        def is_null(self, *_):
            """
            Returns a tuple indicating the column is nullable.
            """
            return "is_null", True

        def is_not_null(self, *_):
            """
            Returns a tuple indicating the column is not nullable.
            """
            return "is_null", False

        def is_unique(self, *_):
            """
            Returns a tuple indicating the column is unique.
            """
            return "is_unique", True

        def is_increment(self, *_):
            """
            Returns a tuple indicating the column is auto-increment.
            """
            return "is_increment", True

        def alias(self, vars):
            """
            Returns a dictionary for a table alias.
            """
            return {"alias": vars[0]}

        @v_args(inline=True)
        @log_transform
        def data_type(self, sql_type, *vars):
            """
            Returns a dictionary for column data type, including length and scale if present.
            """
            # "schema"."enum" pattern
            # qualified_name rule is processed here due to collision in the EBNF grammar
            if len(vars) == 1 and isinstance(vars[0], str):
                d = {"db_schema": sql_type, "name": vars[0]}
                return d
            return {
                "data_type": {
                    "sql_type": sql_type,
                    "length": vars[0] if len(vars) > 0 else None,
                    "scale": vars[1] if len(vars) > 1 else None,
                }
            }

        def column_setting(self, pairs):
            """
            Returns the first column setting from the list.
            """
            return pairs[0]

        def column_settings(self, pairs_or_ref):
            """
            Returns a dictionary of column settings, merging pairs and references.
            """
            settings = {}
            pairs = []
            for pair in pairs_or_ref:
                if isinstance(pair, dict):
                    settings.update(pair)
                else:
                    if pair[0] == "check":
                        checks = settings.get("checks", [])
                        checks.append(pair[1])
                        settings["checks"] = checks
                    else:
                        pairs.append(pair)
            if pairs:
                settings.update(dict(pairs))
            return {"settings": settings}

        @v_args(inline=True)
        @log_transform
        def column(self, name, column_type, *settings):
            """
            Constructs a column dictionary from name, type, and settings.
            """
            if "data_type" not in column_type:
                column_type = {"data_type": column_type}
            data = name | column_type
            if settings:
                data.update(settings[0])
            return {"column": data}

        @v_args(inline=True)
        @log_transform
        def index(self, columns, *settings):
            """
            Constructs an index dictionary from columns and settings.
            """
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
        def check(self, exp, *settings):
            """
            Constructs an index dictionary from columns and settings.
            """
            data = {"expression": exp}
            if settings:
                data["settings"] = {"name": settings[0]}
            return data

        @v_args(inline=True)
        @log_transform
        def table_partial(self, name, *vars) -> TablePartial:
            """
            Constructs a TablePartial model from name, columns, and settings.
            """
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
            """
            Constructs a Table model from name, columns, partials, and settings.
            Tracks column and partial order.
            """
            data = name | {"columns": []}
            order = 0
            table_partial_orders = {}
            for var in vars:
                if "column" in var:
                    order += 1
                    data["columns"].append(var["column"])
                elif isinstance(var, str):
                    order += 1
                    table_partials = data.get("table_partials", [])
                    table_partials.append(var)
                    table_partial_orders[var] = order
                    data["table_partials"] = table_partials
                else:
                    data.update(var)
            if table_partial_orders:
                data.update({"table_partial_orders": table_partial_orders})
            return Table.model_validate(data)

        # ====== DIAGRAM ======
        def start(self, items) -> Diagram:
            """
            Constructs the final Diagram model from all parsed DBML items.
            """
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

    return DBMLTransformer()

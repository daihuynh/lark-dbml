from io import StringIO
import os
import re
from typing import List

from sqlglot import Dialects, expressions as exp, parse

from ...schema import (
    DataType,
    Diagram,
    Name,
    Reference,
    ReferenceInline,
    ReferenceSettings,
    Table,
    Check,
    CheckSettings,
    Column,
    ColumnSettings,
    Enum,
    EnumValue,
    Index,
    IndexSettings,
)
from .enum import EnumConverter
from .index import IndexConverter
from .table import TableConverter


def to_sql(diagram: Diagram, dialect: Dialects = Dialects.POSTGRES) -> str:
    """
    Convert a DBML Diagram object to SQL statements for the specified dialect.

    This function generates SQL for schemas, enums, tables, and indexes,
    using SQLGlot converters and writes the output to a string buffer.

    Args:
        diagram: The DBML Diagram object to convert.
        dialect: The SQL dialect to use (default: Dialects.POSTGRES).

    Returns:
        str: The generated SQL statements as a string.
    """
    endblock = ";" + os.linesep + os.linesep

    enum_converter = EnumConverter(dialect)
    with StringIO() as buffer:
        # Create schema
        schemas = set(
            map(
                lambda enum: enum.db_schema,
                filter(lambda enum: enum.db_schema is not None, diagram.enums),
            )
        )
        schemas |= set(
            map(
                lambda table: table.db_schema,
                filter(lambda table: table.db_schema is not None, diagram.tables),
            )
        )
        for schema in sorted(schemas):
            schema_def = exp.Create(
                this=exp.Table(db=exp.Identifier(this=schema, quoted=True)),
                kind="SCHEMA",
                exists=True,
            )
            buffer.write(schema_def.sql(dialect=dialect, pretty=True))
            buffer.write(endblock)

        # Only create enum if the dialect supports
        if dialect in [Dialects.POSTGRES, Dialects.DUCKDB]:
            # Create enum
            if diagram.enums:
                for enum in diagram.enums:
                    enum_def = enum_converter.convert(enum)
                    buffer.write(enum_def.sql(dialect=dialect, pretty=True))
                    buffer.write(endblock)

        # Create Table along with Indexes
        for table in diagram.tables:
            # Find any references of this table
            references = list(
                filter(
                    lambda ref: ref.from_table.db_schema == table.db_schema
                    and ref.from_table.name == table.name,
                    diagram.references,
                )
            )

            table_converter = TableConverter(
                dialect,
                table_partials=diagram.table_partials,
                references=references,
                enums=diagram.enums,
            )
            index_converter = IndexConverter(dialect, table)

            table_def = table_converter.convert(table)
            buffer.write(table_def.sql(dialect=dialect, pretty=True))
            buffer.write(endblock)

            if table.indexes:
                # Indexes that are not composite primary keys
                indexes = list(
                    filter(
                        lambda index: not (
                            index.settings and index.settings.is_primary_key
                        ),
                        table.indexes,
                    )
                )
                for index in indexes:
                    index_def = index_converter.convert(index)
                    buffer.write(index_def.sql(dialect=dialect, pretty=True))
                    buffer.write(endblock)

        return buffer.getvalue()


def from_sql(ddl: str | List[str], dialect: Dialects = Dialects.POSTGRES) -> Diagram:
    def parse_enum(text: str) -> Enum | None:
        match = re.search(
            r"CREATE\s+TYPE\s+(?:\"?(\w+)\"?\.)?\"?(\w+)\"?\s+AS\s+ENUM\s*\((.+)\)",
            text,
            re.IGNORECASE | re.DOTALL,
        )
        if match:
            schema = match.group(1)
            name = match.group(2)
            values_str = match.group(3)
            values = []
            for val in values_str.split(","):
                val = val.strip().strip("'")
                values.append(EnumValue(value=val))

            return Enum(name=name, db_schema=schema, values=values)
        return None

    def parse_column(
        exp_col_def: exp.ColumnDef, table_name: str, schema_name: str | None
    ) -> Column:
        def get_param_value(arg):
            if isinstance(arg, exp.DataTypeParam):
                arg = arg.this
            if isinstance(arg, exp.Literal):
                return int(arg.this)
            return None

        sql_type = exp_col_def.kind.sql(dialect=dialect)
        # Try to get cleaner base type if possible to avoid params in string for standard types
        if (
            isinstance(exp_col_def.kind, exp.DataType)
            and exp_col_def.kind.this != exp.DataType.Type.USERDEFINED
        ):
            sql_type = (
                exp_col_def.kind.this.value
                if hasattr(exp_col_def.kind.this, "value")
                else str(exp_col_def.kind.this)
            )
            # If USERDEFINED, we keep the original SQL string (e.g. example.answer)

        col = Column(name=exp_col_def.name, data_type=DataType(sql_type=sql_type))

        # Handle length/precision if present in type definition
        if args := exp_col_def.kind.expressions:
            if len(args) >= 1:
                col.data_type.length = get_param_value(args[0])

            if len(args) == 2:
                col.data_type.scale = get_param_value(args[1])

        # Column Constraint
        exp_constraints = list(exp_col_def.find_all(exp.ColumnConstraint))
        if exp_constraints:
            settings = ColumnSettings()
            for constraint in exp_constraints:
                if isinstance(constraint.kind, exp.PrimaryKeyColumnConstraint):
                    settings.is_primary_key = True
                elif isinstance(constraint.kind, exp.NotNullColumnConstraint):
                    settings.is_null = constraint.kind.args.get("allow_null", False)
                elif isinstance(constraint.kind, exp.UniqueColumnConstraint):
                    settings.is_unique = True
                elif isinstance(
                    constraint.kind, exp.GeneratedAsIdentityColumnConstraint
                ):
                    settings.is_increment = True
                elif isinstance(constraint.kind, exp.DefaultColumnConstraint):
                    # Handle Defaults
                    default_val = constraint.kind.this
                    if isinstance(default_val, exp.Literal):
                        if default_val.is_string:
                            settings.default = default_val.this
                        else:
                            # Numbers or booleans
                            try:
                                settings.default = int(default_val.this)
                            except ValueError:
                                try:
                                    settings.default = float(default_val.this)
                                except ValueError:
                                    settings.default = default_val.this
                    else:
                        # Expressions like CURRENT_TIMESTAMP, NULL, etc.
                        # Wrap in backticks to indicate expression in DBML
                        settings.default = f"`{default_val.sql(dialect=dialect)}`"
                elif isinstance(constraint.kind, exp.Reference):
                    # Inline reference handling
                    res_refs = constraint.kind
                    ref_table = res_refs.find(exp.Table)

                    # Target Columns
                    to_cols = []
                    if isinstance(res_refs.this, exp.Schema):
                        if res_refs.this.expressions:
                            to_cols = [
                                id.name
                                for id in res_refs.this.expressions
                                if isinstance(id, exp.Identifier)
                            ]

                    inline_ref = ReferenceInline(
                        relationship=">",
                        to_table=Name(db_schema=ref_table.db, name=ref_table.name),
                        to_columns=to_cols,
                    )
                    settings.ref = inline_ref

                    # Note: We probably shouldn't add it to diagram.references as well if it's inline in the column.
                    # to_sql likely iterates columns and renders their inline refs.

                elif isinstance(constraint.kind, exp.CheckColumnConstraint):
                    check_expr = constraint.kind.this
                    if check_expr:
                        if settings.checks is None:
                            settings.checks = []
                        # Wrap in backticks to indicate expression in DBML, similar to default values
                        settings.checks.append(f"`{check_expr.sql(dialect=dialect)}`")

            col.settings = settings
        return col

    def parse_foreign_keys(tree: exp.Create, table_name: Name) -> List[exp.Expression]:
        constraint_exps = []
        # Find table level foreign keys
        # They are usually in exp.ForeignKey (if parsed inline) or part of Create Table args

        # Iterate over all constraints in the Create statement
        for constraint in tree.find_all(exp.Constraint):
            # Foreign Key
            for fk in constraint.find_all(exp.ForeignKey):
                res_refs = constraint.find(exp.Reference)
                if not res_refs:
                    continue
                ref_table = res_refs.find(exp.Table)

                # Column names in the current table
                # fk.expressions contains the source columns
                from_cols = []
                if fk.expressions:
                    from_cols = [
                        id.name
                        for id in fk.expressions
                        if isinstance(id, exp.Identifier)
                    ]

                # Column names in the referenced table
                # res_refs.this is usually exp.Schema which has the table in .this and columns in .expressions
                to_cols = []
                if isinstance(res_refs.this, exp.Schema):
                    if res_refs.this.expressions:
                        to_cols = [
                            id.name
                            for id in res_refs.this.expressions
                            if isinstance(id, exp.Identifier)
                        ]

                # Parse Actions (ON DELETE, ON UPDATE)
                delete_action = None
                update_action = None
                # sqlglot stores these in actions
                if res_refs.args.get("options"):
                    for option in res_refs.args.get("options"):
                        opt_str = str(option).upper()
                        if "ON DELETE" in opt_str:
                            delete_action = (
                                opt_str.replace("ON DELETE", "").strip().lower()
                            )
                        if "ON UPDATE" in opt_str:
                            update_action = (
                                opt_str.replace("ON UPDATE", "").strip().lower()
                            )

                ref_settings = ReferenceSettings()
                if delete_action:
                    ref_settings.delete = delete_action
                if update_action:
                    ref_settings.update = update_action

                ref = Reference(
                    name=constraint.name,
                    relationship=">",
                    from_table=table_name,
                    from_columns=from_cols,
                    to_table=Name(db_schema=ref_table.db, name=ref_table.name),
                    to_columns=to_cols,
                    settings=ref_settings if (delete_action or update_action) else None,
                )

                constraint_exps.append(ref)
        return constraint_exps

    def parse_index(tree: exp.Create, table_map: dict):
        # tree.this is the index name (usually Identifier)
        # tree.find(exp.Table) is the table
        tbl_exp = tree.find(exp.Table)
        if not tbl_exp:
            return None

        schema = tbl_exp.db if tbl_exp.db else None
        table_name = tbl_exp.name

        target_table = None
        # Try to find the table in our map
        # We need a robust way to match tables.
        # For now assume schema is present if it was created with one.
        for tbl in table_map.values():
            if tbl.name == table_name and tbl.db_schema == schema:
                target_table = tbl
                break

        if target_table:
            index = Index(columns=[])
            settings = IndexSettings()

            # Name
            # tree.this is exp.Index. tree.this.this is the Identifier for name.
            if isinstance(tree.this, exp.Index) and isinstance(
                tree.this.this, exp.Identifier
            ):
                idx_name = tree.this.this.name
            else:
                idx_name = (
                    tree.this.name
                    if isinstance(tree.this, exp.Identifier)
                    else str(tree.this)
                )

            settings.name = idx_name

            # Properties
            if tree.args.get("unique"):
                settings.is_unique = True

            # Columns
            index_expr = tree.this if isinstance(tree.this, exp.Index) else tree
            params_node = index_expr.args.get("params")

            cols = []
            if params_node:
                cols = [id.name for id in params_node.find_all(exp.Identifier)]
            else:
                # Fallback: find all identifiers in the index expression excluding name/table
                all_ids = list(tree.find_all(exp.Identifier))
                for id_node in all_ids:
                    if id_node.name not in [table_name, schema, idx_name]:
                        cols.append(id_node.name)

            if cols:
                index.columns = cols
                index.settings = settings
                target_table.indexes = target_table.indexes or []
                target_table.indexes.append(index)

    if isinstance(ddl, List):
        ddl = ";".join(ddl)

    diagram = Diagram()
    trees = parse(ddl, dialect=dialect)

    # Store tables in a map for easy access
    table_map = {}

    # First pass: Tables and Enums
    for tree in trees:
        if isinstance(tree, exp.Command):
            # Check for Enum
            enum = parse_enum(tree.sql(dialect=dialect))
            if enum:
                diagram.enums.append(enum)
            continue

        if not isinstance(tree, exp.Create):
            continue

        if tree.kind == "TABLE":
            table_this = tree.this
            if isinstance(table_this, exp.Schema):
                table_this = table_this.this

            tbl = Table(
                db_schema=table_this.db if table_this.db else None,
                name=table_this.name,
                columns=[],
            )

            # Columns
            for col_def in tree.find_all(exp.ColumnDef):
                col = parse_column(col_def, tbl.name, tbl.db_schema)
                tbl.columns.append(col)

            diagram.tables.append(tbl)
            table_map[f"{tbl.db_schema}.{tbl.name}"] = tbl

            # Table constraint
            for constraint_exp in tree.find_all(exp.Constraint):
                if chk_exp := constraint_exp.find(exp.CheckColumnConstraint):
                    chk = Check(expression=f"`{chk_exp.this.sql(dialect=dialect)}`")
                    if constraint_exp.this:
                        chk.settings = CheckSettings(name=constraint_exp.this.this)
                    if not tbl.checks:
                        tbl.checks = []
                    tbl.checks.append(chk)

            # Check for inline or table properties that indicate Primary Key (composite)
            for pk in tree.find_all(exp.PrimaryKey):
                # Ensure it's a table-level PK (has columns)
                if not pk.expressions:
                    continue

                pk_cols_names = [id.name for id in pk.find_all(exp.Identifier)]

                if len(pk_cols_names) > 1:
                    # Composite PK -> Create Index with is_primary_key=True
                    pk_index = Index(
                        columns=pk_cols_names,
                        settings=IndexSettings(is_primary_key=True),
                    )
                    # Use existing indexes list or create new
                    if tbl.indexes is None:
                        tbl.indexes = []
                    tbl.indexes.append(pk_index)

                    # Ensure columns DO NOT have is_primary_key set (if they were set by inline constraint)
                    for col in tbl.columns:
                        if col.name in pk_cols_names and col.settings:
                            col.settings.is_primary_key = False
                else:
                    # Single Column PK -> Set column setting
                    for col in tbl.columns:
                        if col.name in pk_cols_names:
                            if not col.settings:
                                col.settings = ColumnSettings()
                            col.settings.is_primary_key = True

    # Second pass: Foreign Keys and Indexes (and separate ALTER statements if any)
    for tree in trees:
        if isinstance(tree, exp.Create):
            if tree.kind == "TABLE":
                # Extract FKs defined in CREATE TABLE
                table_this = tree.this
                if isinstance(table_this, exp.Schema):
                    table_this = table_this.this

                fks = parse_foreign_keys(
                    tree, Name(db_schema=table_this.db, name=table_this.name)
                )
                diagram.references.extend(fks)

            elif tree.kind == "INDEX":
                parse_index(tree, table_map)

    return diagram

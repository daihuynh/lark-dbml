import re
from ...schema import Name

NON_WORD_PATTERN = re.compile(r"\W")
ESCAPED_SINGLE_QUOTE = re.compile(r"'|\\")


def name_to_str(namable: Name) -> str:
    name_need_quote = len(NON_WORD_PATTERN.findall(namable.name)) > 0
    if namable.db_schema:
        schema_need_quote = len(NON_WORD_PATTERN.findall(namable.db_schema)) > 0
        name = (
            f'"{namable.name}"'
            if name_need_quote or schema_need_quote
            else namable.name
        )
        schema = (
            f'"{namable.db_schema}"'
            if name_need_quote or schema_need_quote
            else namable.db_schema
        )
        return f"{schema}.{name}"
    name = f'"{namable.name}"' if name_need_quote else namable.name
    return name


def quote_value(value: str) -> str:
    is_multiline = "\n" in value
    if not is_multiline:
        value = ESCAPED_SINGLE_QUOTE.sub(r"\'", value)
    # Escape the single quote if the value is not a multiline string
    return f"'{value}'" if not is_multiline else f"'''{value}'''"


def quote_identifier(id: str) -> str:
    if len(NON_WORD_PATTERN.findall(id)) > 0:
        return f'"{id}"'
    else:
        return id


def quote_column(column: str) -> str:
    # Function expression
    if "`" in column:
        return column
    return quote_identifier(column)

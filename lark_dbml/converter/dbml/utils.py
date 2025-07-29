import re
from ...schema import Name

NON_WORD_PATTERN = re.compile(r"\W")
ESCAPED_SINGLE_QUOTE = re.compile(r"'|\\")


def name_to_str(namable: Name) -> str:
    """
    Format a DBML Name object as a string, quoting schema and name if needed.

    Args:
        namable: The Name object to format.

    Returns:
        str: The formatted name, with schema if present.
    """
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
    """
    Quote a string value for DBML output, using single or triple quotes as needed.

    Args:
        value: The string value to quote.

    Returns:
        str: The quoted value.
    """
    is_multiline = "\n" in value
    if not is_multiline:
        value = ESCAPED_SINGLE_QUOTE.sub(r"\'", value)
    # Escape the single quote if the value is not a multiline string
    return f"'{value}'" if not is_multiline else f"'''{value}'''"


def quote_identifier(id: str) -> str:
    """
    Quote an identifier for DBML output if it contains non-word characters.

    Args:
        id: The identifier string.

    Returns:
        str: The quoted identifier if needed.
    """
    if len(NON_WORD_PATTERN.findall(id)) > 0:
        return f'"{id}"'
    else:
        return id


def quote_column(column: str) -> str:
    """
    Quote a column name for DBML output, handling function expressions and identifiers.

    Args:
        column: The column name string.

    Returns:
        str: The quoted column name.
    """
    # Function expression
    if "`" in column:
        return column
    return quote_identifier(column)

import importlib.resources as pkg_resources
import logging
from pathlib import Path
from io import TextIOBase
from typing import Literal

from .converter.dbml import to_dbml, DBMLConverterSettings
from .schema import (
    Diagram,
)
from .transformer import create_dbml_transformer

__all__ = ["load", "loads", "dump", "dumps", "Diagram", "DBMLConverterSettings"]

GRAMMAR_FILE_CONTENT = (
    pkg_resources.files("lark_dbml").joinpath("dbml.lark").read_text(encoding="utf-8")
)

logger = logging.getLogger(__name__)


def load(
    file: str | Path | TextIOBase,
    standalone_mode=True,
    parser: Literal["earley", "lalr"] = "lalr",
    **lark_options,
) -> Diagram:
    """
    Load and parse a DBML diagram from a file path, file-like object, or string path.

    This function reads the DBML source from the given file or file-like object,
    then parses it into a Diagram object using the specified parser and options.

    Args:
        file: Path to the DBML file, a file-like object, or a string.
        standalone_mode: Whether to use the standalone parser implementation.
        parser: The parser algorithm to use ("earley" or "lalr").
        **lark_options: Additional options to pass to the Lark parser.

    Returns:
        Diagram: The parsed DBML diagram as a Diagram object.
    """
    if isinstance(file, TextIOBase):
        dbml_diagram = file.read()
    else:
        with open(file, encoding="utf-8", mode="r") as f:
            dbml_diagram = f.read()

    return loads(dbml_diagram, standalone_mode, parser, **lark_options)


def loads(
    dbml_diagram: str,
    standalone_mode=True,
    parser: Literal["earley", "lalr"] = "lalr",
    **lark_options,
) -> Diagram:
    """
    Parse a DBML diagram from a string and return a Diagram object.

    This function parses the provided DBML source string using either the standalone
    or Lark parser, and transforms the parse tree into a Diagram object.

    Args:
        dbml_diagram: DBML source as a string.
        standalone_mode: Whether to use the standalone parser implementation.
        parser: The parser algorithm to use ("earley" or "lalr").
        **lark_options: Additional options to pass to the Lark parser.

    Returns:
        Diagram: The parsed DBML diagram as a Diagram object.
    """
    if standalone_mode:
        from .lark_dbml_standalone import Lark_StandAlone, Transformer, Token, v_args

        parser = Lark_StandAlone(**lark_options)
        transformer = create_dbml_transformer(Transformer, Token, v_args)
        logger.debug("lark-dbml is parsing using standalone mode")
    else:
        try:
            from lark import Lark, Transformer, Token, v_args

            parser = Lark(GRAMMAR_FILE_CONTENT, parser=parser, **lark_options)
            transformer = create_dbml_transformer(Transformer, Token, v_args)
            logger.debug("lark-dbml is parsing using lark mode")
        except ImportError:
            raise RuntimeError(
                'Lark package is not found. Please run `pip install "lark-dbml[lark]"` or set standalone = False'
            )

    tree = parser.parse(dbml_diagram)

    return transformer.transform(tree)


def dump(
    diagram: Diagram,
    file: str | Path | TextIOBase,
    settings: DBMLConverterSettings = None,
):
    """
    Write a Diagram object to a file in DBML format.

    Args:
        diagram: The Diagram object to serialize.
        file: Path to the output file or a file-like object.
        settings: Optional DBML converter settings.

    Returns:
        None
    """
    dbml = dumps(diagram, settings)
    if isinstance(file, TextIOBase):
        file.write(dbml)
    else:
        with open(file, encoding="utf-8", mode="w") as f:
            f.write(dbml)


def dumps(diagram: Diagram, settings: DBMLConverterSettings = None) -> str:
    """
    Serialize a Diagram object to a DBML string.

    Args:
        diagram: The Diagram object to serialize.
        settings: Optional DBML converter settings.

    Returns:
        str: The DBML string representation of the diagram.
    """
    return to_dbml(diagram, settings)

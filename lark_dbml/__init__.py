import importlib.resources as pkg_resources
from pathlib import Path
from io import TextIOBase

from lark import Lark

from .converter.dbml import to_dbml, DBMLConverterSettings
from .schema import (
    Diagram,
)
from .transformer import DBMLTransformer

__all__ = ["load", "loads", "dump", "dumps", "Diagram", "DBMLConverterSettings"]

GRAMMAR_FILE_CONTENT = (
    pkg_resources.files("lark_dbml").joinpath("dbml.lark").read_text(encoding="utf-8")
)


def load(file: str | Path | TextIOBase):
    """
    Load a DBML diagram from a file path, file-like object, or string path.

    Args:
        file: Path to the DBML file, a file-like object, or a string.

    Returns:
        Diagram: Parsed DBML diagram as a Diagram object.
    """
    if isinstance(file, TextIOBase):
        dbml_diagram = file.read()
    else:
        with open(file, encoding="utf-8", mode="r") as f:
            dbml_diagram = f.read()

    return loads(dbml_diagram)


def loads(dbml_diagram: str) -> Diagram:
    """
    Parse a DBML diagram from a string and return a Diagram object.

    Args:
        dbml_diagram: DBML source as a string.

    Returns:
        Diagram: Parsed DBML diagram as a Diagram object.
    """
    parser = Lark(GRAMMAR_FILE_CONTENT)

    tree = parser.parse(dbml_diagram)

    transformer = DBMLTransformer()

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

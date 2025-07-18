import importlib.resources as pkg_resources
from io import TextIOWrapper
from pathlib import Path

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


def load(file: str | Path | TextIOWrapper):
    if isinstance(file, TextIOWrapper):
        dbml_diagram = file.read()
    else:
        with open(file, encoding="utf-8", mode="r") as f:
            dbml_diagram = f.read()

    return loads(dbml_diagram)


def loads(dbml_diagram: str) -> Diagram:
    parser = Lark(GRAMMAR_FILE_CONTENT)

    tree = parser.parse(dbml_diagram)

    transformer = DBMLTransformer()

    return transformer.transform(tree)


def dump(
    diagram: Diagram,
    file: str | Path | TextIOWrapper,
    settings: DBMLConverterSettings = None,
):
    dbml = dumps(diagram, settings)
    if isinstance(file, TextIOWrapper):
        file.write(dbml)
    else:
        with open(file, encoding="utf-8", mode="w") as f:
            f.write(dbml)


def dumps(diagram: Diagram, settings: DBMLConverterSettings = None) -> str:
    return to_dbml(diagram, settings)

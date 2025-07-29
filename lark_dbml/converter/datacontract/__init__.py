import yaml
from collections import OrderedDict, defaultdict

from ...schema import Diagram
from .base import DataContractConverterSettings
from .enum import EnumConverter
from .note import NoteConverter
from .project import ProjectConverter
from .table import TableConverter


def represent_ordereddict(dumper, data):
    pairs = ((k, v) for (k, v) in data.items() if v)
    return dumper.represent_mapping("tag:yaml.org,2002:map", pairs)


def represent_multiline_string(dumper, data):
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


# Register the representers with the YAML dumper
yaml.add_representer(defaultdict, represent_ordereddict)
yaml.add_representer(OrderedDict, represent_ordereddict)
yaml.add_representer(str, represent_multiline_string)


def to_data_contract(
    diagram: Diagram, settings: DataContractConverterSettings = None
) -> str:
    """
    Convert a DBML Diagram object to a data contract YAML string.

    This function uses converter classes for each DBML schema type to generate
    the data contract YAML representation of the diagram, including enums, tables,
    models, definitions, and sticky notes.

    Args:
        diagram: The DBML Diagram object to convert.
        settings: Optional DataContractConverterSettings for formatting and options.

    Returns:
        str: The data contract YAML string representation of the diagram.
    """
    if not settings:
        settings = DataContractConverterSettings()
    project_convert = ProjectConverter(settings)
    enum_converter = EnumConverter(settings)
    note_converter = NoteConverter(settings)
    table_converter = TableConverter(
        settings, diagram.table_partials, diagram.references
    )

    contract = defaultdict(OrderedDict)
    contract["dataContractSpecification"] = "1.2.0"
    contract["id"] = diagram.project.name if diagram.project else "unknown"
    contract["info"] = OrderedDict()
    contract["servers"] = None
    contract["terms"] = None

    if settings.project_as_info and diagram.project:
        info = project_convert.convert(diagram.project)
        contract["info"].update(info)
    else:
        contract["info"] = {"title": "Untitled", "version": "0.0.1"}

    contract["models"] = {}
    contract["definitions"] = {}

    for enum in diagram.enums:
        enum_def = enum_converter.convert(enum)
        contract["definitions"][enum.name] = enum_def

    for table in diagram.tables:
        table_def = table_converter.convert(table)
        contract["models"].update(table_def["models"])
        for column, definition in table_def["definitions"].items():
            contract["definitions"][column] = definition

    if settings.note_as_fields:
        for note in diagram.sticky_notes:
            note_def = note_converter.convert(note)
            contract.update(note_def)

    return yaml.dump(contract)

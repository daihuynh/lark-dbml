import json
from lark_dbml import load
from lark_dbml.converter import to_data_contract
from lark_dbml.converter.datacontract import DataContractConverterSettings


def test_datacontract(example_path, expectation_path):
    diagram = load(example_path / "complex_datacontract.dbml")

    datacontract = to_data_contract(diagram)

    with open(expectation_path / "complex_datacontract.yml") as f:
        expectation = f.read()

    assert datacontract == expectation


def test_datacontract_note_as_desc_settings(example_path, expectation_path):
    diagram = load(example_path / "complex_datacontract.dbml")

    datacontract = to_data_contract(
        diagram,
        DataContractConverterSettings(
            project_as_info=True,
            note_as_description=True,
        ),
    )

    with open(expectation_path / "complex_datacontract_desc.yml") as f:
        expectation = f.read()

    assert datacontract == expectation


def test_datacontract_full_settings(example_path, expectation_path):
    diagram = load(example_path / "complex_datacontract.dbml")

    datacontract = to_data_contract(
        diagram,
        DataContractConverterSettings(
            project_as_info=True,
            note_as_description=True,
            note_as_fields=True,
            deserialization_func=json.loads,
        ),
    )

    with open(expectation_path / "complex_datacontract_full.yml") as f:
        expectation = f.read()

    assert datacontract == expectation

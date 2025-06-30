from pathlib import Path
from pytest import fixture


@fixture(scope="session")
def mock_path() -> str:
    return Path(__file__).resolve().parent / "mock"

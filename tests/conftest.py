import pathlib

import pytest
from datadog_api_client_generator.openapi.openapi_model import OpenAPI

from datadog_api_client_generator.openapi.utils import load_yaml


ROOT_PATH = pathlib.Path(__file__).parent.parent


@pytest.fixture(scope="session")
def openapi_basic():
    f = load_yaml(ROOT_PATH / "tests/examples/openapi.yaml")

    return OpenAPI.model_validate(f, context={})

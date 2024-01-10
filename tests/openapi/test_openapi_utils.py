import pathlib

from datadog_api_client_generator.openapi.utils import get_name_and_path_from_ref, load_yaml


def test_load_yaml():
    fp = pathlib.Path("tests/examples/openapi.yaml")
    f = load_yaml(fp)
    
    assert f is not None
    
def test_get_name_and_path_from_ref():
    assert get_name_and_path_from_ref("#/components/schemas/Response") == ["schemas", "Response"]
    assert get_name_and_path_from_ref("#/components/parameters/Error") == ["parameters", "Error"]
    assert len(get_name_and_path_from_ref("#/components/parameters/Error")) == 2

import pytest
from pydantic_core import ValidationError

from datadog_api_client_generator.openapi.openapi_model import OpenAPI


class TestOpenAPISchemas:
    invalid_schema = {
        "foo": "bar"
    }
    
    def test_missing_context_invalid_schema(self):
        with pytest.raises(AttributeError):
            OpenAPI.model_validate(self.invalid_schema)

    def test_invalid_schema(self):
        with pytest.raises(ValidationError):
            OpenAPI.model_validate(self.invalid_schema, context={})
    
    def test_schemas_by_name(self, openapi_basic: OpenAPI):
        s = openapi_basic.schemas_by_name()
        
        assert set(s.keys()) == {'Pet', 'NewPet', 'Error'}

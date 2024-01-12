import pytest
from pydantic_core import ValidationError

from datadog_api_client_generator.openapi.openapi_model import OpenAPI
from datadog_api_client_generator.openapi.schema_model import ArraySchema, AnyOfSchema, AllOfSchema, EnumSchema, OneOfSchema, ObjectSchema, Schema
from datadog_api_client_generator.openapi.shared_model import RefObject


class TestOpenAPISchemas:
    def test_all_of_schema(self, openapi_basic: OpenAPI):
        all_of_schema = openapi_basic.components.schemas["Pet"]

        assert hasattr(all_of_schema, "allOf")
        assert type(all_of_schema) == AllOfSchema
        assert type(all_of_schema.allOf[0]) == RefObject
        assert type(all_of_schema.allOf[1]) == ObjectSchema

    def test_object_schema(self, openapi_basic: OpenAPI):
        object_schema = openapi_basic.components.schemas["Error"]

        assert hasattr(object_schema, "properties")
        assert type(object_schema) == ObjectSchema
        assert set(object_schema.properties.keys()) == {"code", "message",}

    def test_one_of_schema(self, openapi_basic: OpenAPI):
        one_of_schema = openapi_basic.components.schemas["OneOfPet"]

        assert hasattr(one_of_schema, "oneOf")
        assert type(one_of_schema) == OneOfSchema
        assert type(one_of_schema.oneOf[0]) == RefObject
        assert one_of_schema.oneOf[0].name == "Dog"

    def test_array_schema(self, openapi_basic: OpenAPI):
        array_schema = openapi_basic.components.schemas["Pets"]

        assert hasattr(array_schema, "items")
        assert type(array_schema) == ArraySchema

    def test_array_schema(self, openapi_basic: OpenAPI):
        array_schema = openapi_basic.components.schemas["PetType"]

        assert hasattr(array_schema, "enum")
        assert type(array_schema) == EnumSchema


class TestEnumSchema:
    valid_schema = {
        "description": "enum schema",
        "enum": ["foo", "BAR"],
        "x-enum-varnames": ["FOO", "BAR"]
    }
    invalid_schema = {
        "description": "enum schema",
        "x-enum-varnames": ["FOO", "BAR"]
    }

    def test_schema(self):
        m = EnumSchema.model_validate(self.valid_schema)

        assert m.enum[0] == "foo"
        assert m.extensions["x-enum-varnames"][0] == "FOO"
    
    def test_invalid_schema(self):
        with pytest.raises(ValidationError):
            EnumSchema.model_validate(self.invalid_schema)


class TestOneOfSchema:
    valid_schema = {
        "description": "oneof schema",
        "oneOf": [{"$ref": '#/components/schemas/Dog'}]
    }
    invalid_schema = {
        "description": "oneof schema",
        "type": "object",
    }

    def test_schema(self):
        m = OneOfSchema.model_validate(self.valid_schema)

        assert type(m.oneOf[0]) == RefObject
    
    def test_invalid_enum_schema(self):
        with pytest.raises(ValidationError):
            OneOfSchema.model_validate(self.invalid_schema)


class TestOneOfSchema:
    valid_schema = {
        "description": "array schema",
        "items": {"$ref": '#/components/schemas/Dog'}
    }
    invalid_schema = {
        "description": "oneof schema",
        "type": "object",
    }

    def test_schema(self):
        m = ArraySchema.model_validate(self.valid_schema)

        assert type(m.items) == RefObject
    
    def test_invalid_enum_schema(self):
        with pytest.raises(ValidationError):
            ArraySchema.model_validate(self.invalid_schema)

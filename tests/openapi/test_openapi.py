from datadog_api_client_generator.openapi.schema_model import AllOfSchema, ObjectSchema, OneOfSchema
from datadog_api_client_generator.openapi.shared_model import RefObject


def test_openapi_basic_schemas(openapi_basic):
    # AllOfSchema
    assert type(openapi_basic.components.schemas["Pet"]) == AllOfSchema
    assert type(openapi_basic.components.schemas["Pet"].allOf[0]) == RefObject
    assert type(openapi_basic.components.schemas["Pet"].allOf[0]) == RefObject

    # ObjectSchema
    assert type(openapi_basic.components.schemas["Error"]) == ObjectSchema
    assert openapi_basic.components.schemas["Error"].properties.keys() == ["code", "message"]

    # OneOfSchema
    assert type(openapi_basic.components.schemas["OneOfPet"]) == OneOfSchema
    assert type(openapi_basic.components.schemas["OneOfPet"].oneOf[0]) == RefObject
    assert openapi_basic.components.schemas["OneOfPet"].oneOf[0].name == "Dog"

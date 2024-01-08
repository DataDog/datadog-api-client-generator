import keyword
from typing import Any, Dict, Optional, Union

import m2r2

from datadog_api_client_generator.codegen.shared.templates_env import snake_case
from datadog_api_client_generator.codegen.shared.utils import camel_case
from datadog_api_client_generator.openapi.operation_model import OperationObject
from datadog_api_client_generator.openapi.parameter_model import Parameter
from datadog_api_client_generator.openapi.schema_model import (
    ArraySchema,
    EnumSchema,
    ObjectSchema,
    OneOfSchema,
    Schema,
    SchemaType,
)
from datadog_api_client_generator.openapi.shared_model import RefObject


KEYWORDS = set(keyword.kwlist)
KEYWORDS.add("property")
KEYWORDS.add("cls")

EDGE_CASES = {"IdP": "Idp", "AuthNMapping": "AuthnMapping", "AuthN ": "Authn ", "IoT": "Iot", "SLOs": "Slos"}

WHITELISTED_LIST_MODELS = {
    "v1": (
        "AgentCheck",
        "AzureAccountListResponse",
        "DashboardBulkActionDataList",
        "DistributionPoint",
        "GCPAccountListResponse",
        "HTTPLog",
        "LogsPipelineList",
        "MonitorSearchCount",
        "Point",
        "ServiceChecks",
        "SharedDashboardInvitesDataList",
        "SlackIntegrationChannels",
        "SyntheticsRestrictedRoles",
        "UsageAttributionAggregates",
    ),
    "v2": (
        "CIAppAggregateBucketValueTimeseries",
        "EventsQueryGroupBys",
        "GroupTags",
        "HTTPLog",
        "IncidentTodoAssigneeArray",
        "LogsAggregateBucketValueTimeseries",
        "MetricBulkTagConfigEmailList",
        "MetricBulkTagConfigTagNameList",
        "MetricCustomAggregations",
        "MetricSuggestedAggregations",
        "RUMAggregateBucketValueTimeseries",
        "ScalarFormulaRequestQueries",
        "SecurityMonitoringSignalIncidentIds",
        "SensitiveDataScannerGetConfigIncludedArray",
        "SensitiveDataScannerStandardPatternsResponse",
        "TagsEventAttribute",
        "TeamPermissionSettingValues",
        "TimeseriesFormulaRequestQueries",
        "TimeseriesResponseSeriesList",
        "TimeseriesResponseTimes",
        "TimeseriesResponseValues",
        "TimeseriesResponseValuesList",
    ),
}

PRIMITIVE_TYPES = ["string", "number", "boolean", "integer"]


def safe_snake_case(value: str) -> str:
    for token, replacement in EDGE_CASES.items():
        value = value.replace(token, replacement)
    return snake_case(value)


def escape_reserved_keyword(word: str) -> str:
    """
    Escape reserved language keywords like openapi generator does it
    :param word: Word to escape
    :return: The escaped word if it was a reserved keyword, the word unchanged otherwise
    """
    if word in KEYWORDS:
        return f"_{word}"
    return word


def attribute_name(attribute: str) -> str:
    return escape_reserved_keyword(snake_case(attribute))


class CustomRenderer(m2r2.RestRenderer):
    def double_emphasis(self, text: Any) -> Any:
        if "``" in text:
            text = text.replace("\\ ``", "").replace("``\\ ", "")
        if "`_" in text:
            return text
        return "\\ **{}**\\ ".format(text)

    def header(self, text, level, raw=None) -> str:
        return "\n{}\n".format(self.double_emphasis(text))


def docstring(text) -> Any:
    return (
        m2r2.convert(text.replace("\\n", "\\\\n"), renderer=CustomRenderer())[1:-1]
        .replace("\\ ", " ")
        .replace("\\`", "\\\\`")
        .replace("\n\n\n", "\n\n")
    )


def set_api_version(version):
    global API_VERSION
    API_VERSION = version


def is_list_model_whitelisted(name):
    return name in WHITELISTED_LIST_MODELS[API_VERSION]


def basic_type_to_python(type_: Optional[str], schema: SchemaType, typing: bool = False):
    schema = schema()
    if not type_:
        if typing:
            return "Any"
        return "bool, date, datetime, dict, float, int, list, str, UUID, none_type"
    if type_ == "integer":
        return "int"
    elif type_ == "number":
        return "float"
    elif type_ == "string":
        format_ = schema.format
        if format_ in {"date", "date-time"}:
            return "datetime"
        elif format_ == "binary":
            return "file_type"
        elif format_ == "uuid":
            return "UUID"
        return "str"
    elif type_ == "boolean":
        return "bool"
    elif type_ == "array":
        subtype = type_to_python(schema.items(), typing=typing)
        if typing:
            return "List[{}]".format(subtype)
        if schema.items().nullable:
            subtype += ", none_type"
        return "[{}]".format(subtype)
    elif type_ == "object":
        if "additionalProperties" in schema:
            nested_schema = schema["additionalProperties"]
            nested_name = type_to_python(nested_schema, typing=typing)
            if nested_schema.get("nullable"):
                if typing:
                    nested_name = f"Union[{nested_name}, none_type]"
                else:
                    nested_name += ", none_type"
            if typing:
                return f"Dict[str, {nested_name}]"
            return "{{str: ({},)}}".format(nested_name)
        return "dict"
    else:
        raise ValueError(f"Unknown type {type_}")


def get_oneof_types(model: OneOfSchema, typing=False):
    for schema in model().oneOf:
        type_ = schema().type or "object"
        if type_ == "object" or is_list_model_whitelisted(schema().name):
            yield schema().name
        else:
            yield basic_type_to_python(type_, schema(), typing=typing)


def type_to_python(schema: SchemaType, typing: bool = False):
    """Return Python type name for the type."""
    schema = schema()
    if type(schema) == OneOfSchema:
        types = list(get_oneof_types(schema, typing=typing))

        if schema().name and typing:
            types.insert(0, schema().name)
        type_ = ", ".join(types)
        if typing:
            return f"Union[{type_}]"
        elif schema.name:
            return schema.name
        return type_

    if type(schema) == EnumSchema:
        return schema.name

    if schema.name and (schema.type == "object" or is_list_model_whitelisted(schema.name)):
        return schema.name

    return basic_type_to_python(schema.type, schema, typing=typing)


def return_type(operation: OperationObject):
    for response in operation.responses.values():
        for content in response.content.values():
            if content.schema:
                return type_to_python(content.schema)
        return


def get_type_for_parameter(parameter: Parameter, typing: bool = False):
    """Return Python type name for the parameter."""
    # if "content" in parameter:
    #     assert "in" not in parameter
    #     for content in parameter["content"].values():
    #         return type_to_python(content["schema"], typing=typing)
    return type_to_python(parameter().schema(), typing=typing)


def get_default(operation: OperationObject, attribute_path: str):
    attrs = attribute_path.split(".")
    for name, parameter in operation.get_parameters():
        if name == attrs[0]:
            break
    if name == attribute_path:
        # We found a top level attribute matching the full path, let's use the default
        return parameter().schema().default

    if name == "body":
        parameter = parameter().schema()
    for attr in attrs[1:]:
        parameter = parameter().properties[attr]()

    return parameter().default


def attribute_path(attribute):
    return ".".join(attribute_name(a) for a in attribute.split("."))


def get_type_for_items(schema: ArraySchema):
    return schema.items.name


def get_type_at_path(operation: OperationObject, attribute_path: str):
    content = None
    for code, response in operation.responses.items():
        if int(code) >= 300:
            continue
        for content in response.content.values():
            if content.schema():
                break
    if content is None:
        raise RuntimeError("Default response not found")
    content = content.schema()
    if not attribute_path:
        return get_type_for_items(content)
    for attr in attribute_path.split("."):
        content = content.properties[attr]()

    return get_type_for_items(content)


def filter_models(models: Dict[str, SchemaType]) -> Dict[str, None]:
    for name in list(models.keys()):
        if isinstance(models[name], ArraySchema):
            if is_list_model_whitelisted(name):
                continue
        if isinstance(models[name], EnumSchema):
            continue
        if isinstance(models[name], ObjectSchema):
            continue
        if isinstance(models[name], OneOfSchema):
            continue
        if isinstance(models[name], Schema):
            if models[name].additionalProperties:
                continue

        del models[name]

    return models


def find_non_primitive_type(schema: SchemaType):
    if isinstance(schema(), EnumSchema):
        return True
    return schema().type not in PRIMITIVE_TYPES


def get_references_for_model(model: SchemaType, model_name: str):
    result = {}
    top_name = model().name or model_name
    if isinstance(model(), ObjectSchema):
        for key, definition in model().properties.items():
            if (
                definition().type == "object"
                or isinstance(definition(), EnumSchema)
                or isinstance(definition(), OneOfSchema)
            ):
                name = definition().name
                if name:
                    result[name] = None
                elif isinstance(definition(), ObjectSchema) and top_name:
                    result[top_name + camel_case(key)] = None
                elif isinstance(definition().additionalProperties, SchemaType):
                    name = definition().additionalProperties().name
                    if name:
                        result[name] = None
            elif isinstance(definition(), ArraySchema):
                name = definition().name
                if name and is_list_model_whitelisted(name):
                    result[name] = None
                else:
                    items_name = definition().items().name
                    if items_name:
                        if is_list_model_whitelisted(items_name):
                            result[items_name] = None
                        elif isinstance(definition().items(), ArraySchema):
                            result[definition().items().name] = None
                        elif find_non_primitive_type(definition().items()):
                            result[items_name] = None
            elif isinstance(definition(), ObjectSchema) and top_name:
                result[top_name + camel_case(key)] = None
    if isinstance(model().additionalProperties, SchemaType):
        definition = model().additionalProperties()
        if definition.name:
            result[definition.name] = None
        elif isinstance(definition(), ArraySchema):
            name = definition().items().name
            if name:
                result[name] = None
    result.pop(model_name, None)
    return list(result)


def get_oneof_references_for_model(model: SchemaType, model_name: str, seen: Dict[str, str] = None):
    result = {}
    if seen is None:
        seen = set()
    name = model().name
    if name:
        if name in seen:
            return []
        seen.add(name)

    if isinstance(model(), OneOfSchema):
        for schema in model().oneOf:
            type_ = schema().type or "object"

            oneof_name = schema().name
            if type_ == "object" or is_list_model_whitelisted(oneof_name):
                result[oneof_name] = None
            elif isinstance(schema(), ArraySchema):
                sub_name = schema().items().name
                if sub_name:
                    result[sub_name] = None

    if isinstance(model(), ObjectSchema):
        for key, definition in model().properties.items():
            result.update({k: None for k in get_oneof_references_for_model(definition(), model_name, seen)})
            if isinstance(definition(), ArraySchema):
                result.update({k: None for k in get_oneof_references_for_model(definition().items(), model_name, seen)})
            if isinstance(definition().additionalProperties, SchemaType):
                result.update(
                    {
                        k: None
                        for k in get_oneof_references_for_model(definition().additionalProperties(), model_name, seen)
                    }
                )
    result.pop(model_name, None)
    return list(result)


def get_type_for_attribute(schema: SchemaType, attribute: str, current_name: Optional[str] = None):
    """Return Python type name for the attribute."""
    if isinstance(schema(), SchemaType):
        child_schema = schema().properties.get(attribute)
        return type_to_python(child_schema)


def get_typing_for_attribute(
    schema: SchemaType, attribute: str, current_name: Optional[str] = None, optional: Optional[str] = False
):
    if isinstance(schema(), SchemaType):
        child_schema = schema().properties.get(attribute)()
        attr_type = type_to_python(child_schema, typing=True)
        if child_schema.nullable:
            attr_type = f"Union[{attr_type}, none_type]"
        if optional:
            if attr_type.startswith("Union"):
                return attr_type[:-1] + ", UnsetType]"
            return f"Union[{attr_type}, UnsetType]"
        return attr_type


def get_types_for_attribute(schema: SchemaType, attribute: str, current_name: Optional[str] = None):
    if isinstance(schema(), SchemaType):
        child_schema = schema().properties.get(attribute)()
        base_type = get_type_for_attribute(schema, attribute, current_name)
        if child_schema.nullable and not child_schema.name:
            return f"({base_type}, none_type)"
        return f"({base_type},)"


def format_value(value: Any, quotes: str = '"'):
    if isinstance(value, str):
        return f"{quotes}{value}{quotes}"
    elif isinstance(value, bool):
        return "true" if value else "false"
    return value


def get_enum_default(model: EnumSchema):
    return model().enum[0] if len(model.enum) == 1 else model().default


def get_enum_type(schema: EnumSchema):
    if schema().type == "integer":
        return "int"
    elif schema().type == "string":
        return "str"

    raise ValueError(f"Unknown type {schema().type}")


def get_oneof_models(model: OneOfSchema):
    result = []
    for schema in model.oneOf:
        type_ = schema().type or "object"
        if type_ == "object" or is_list_model_whitelisted(schema().name):
            result.append(schema().name)
        elif type_ == "array":
            name = schema().items().name
            if name:
                result.append(name)
    return result


def get_oneof_parameters(model: OneOfSchema):
    seen = set()
    for schema in model.oneOf:
        if isinstance(schema(), ObjectSchema):
            for attr, definition in schema().properties.items():
                if attr not in seen:
                    seen.add(attr)
                    yield attr, definition(), schema

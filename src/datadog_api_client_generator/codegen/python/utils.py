# Unless explicitly stated otherwise all files in this repository are licensed under the Apache 2.0 License.
#
# This product includes software developed at Datadog (https://www.datadoghq.com/  Copyright 2025 Datadog, Inc.
from __future__ import annotations

import keyword
from typing import TYPE_CHECKING, Any

import m2r2

from datadog_api_client_generator.codegen.shared.templates_env import snake_case
from datadog_api_client_generator.codegen.shared.utils import camel_case
from datadog_api_client_generator.openapi.schema_model import (
    ArraySchema,
    EnumSchema,
    ObjectSchema,
    OneOfSchema,
    Schema,
    SchemaType,
)
from datadog_api_client_generator.openapi.utils import Empty

if TYPE_CHECKING:
    from datadog_api_client_generator.openapi.operation_model import OperationObject
    from datadog_api_client_generator.openapi.parameter_model import Parameter

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
ERROR_STATUS_START = 300


def safe_snake_case(value: str) -> str:
    for token, replacement in EDGE_CASES.items():
        value = value.replace(token, replacement)
    return snake_case(value)


def escape_reserved_keyword(word: str) -> str:
    """Escape reserved language keywords like openapi generator does it.

    :param word: Word to escape
    :return: The escaped word if it was a reserved keyword, the word unchanged otherwise
    """
    if word in KEYWORDS:
        return f"_{word}"
    return word


def attribute_name(attribute: str) -> str:
    return escape_reserved_keyword(snake_case(attribute))


class CustomRenderer(m2r2.RestRenderer):
    def double_emphasis(self, text: object) -> object:  # noqa: PLR6301
        if "``" in text:
            text = text.replace("\\ ``", "").replace("``\\ ", "")
        if "`_" in text:
            return text
        return f"\\ **{text}**\\ "

    def header(self, text, _level, _raw=None) -> str:
        return f"\n{self.double_emphasis(text)}\n"


def docstring(text) -> Any:
    return (
        m2r2.convert(text.replace("\\n", "\\\\n"), renderer=CustomRenderer())[1:-1]
        .replace("\\ ", " ")
        .replace("\\`", "\\\\`")
        .replace("\n\n\n", "\n\n")
    )


def set_api_version(version):
    global API_VERSION  # noqa: PLW0603
    API_VERSION = version


def is_list_model_whitelisted(name):
    return name in WHITELISTED_LIST_MODELS[API_VERSION]


def basic_type_to_python(type_: str | None, schema: SchemaType, *, typing: bool = False):
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
            return f"List[{subtype}]"
        if schema.items().nullable:
            subtype += ", none_type"
        return f"[{subtype}]"
    elif type_ == "object":
        if not isinstance(schema.additionalProperties, Empty):
            nested_schema = schema.additionalProperties
            nested_name = type_to_python(nested_schema, typing=typing)
            if nested_schema().nullable:
                if typing:
                    nested_name = f"Union[{nested_name}, none_type]"
                else:
                    nested_name += ", none_type"
            if typing:
                return f"dict[str, {nested_name}]"
            return f"{{str: ({nested_name},)}}"
        return "dict"
    else:
        msg = f"Unknown type {type_}"
        raise ValueError(msg)


def get_oneof_types(model: OneOfSchema, *, typing=False):
    for schema in model().oneOf:
        type_ = schema().type or "object"
        if type_ == "object" or is_list_model_whitelisted(schema().name):
            yield schema().name
        else:
            yield basic_type_to_python(type_, schema(), typing=typing)


def type_to_python(schema: SchemaType, *, typing: bool = False):
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
        for content in response().content.values():
            if content.schema:
                return type_to_python(content.schema)
        return
    return


def get_type_for_parameter(parameter: Parameter, *, typing: bool = False):
    """Return Python type name for the parameter."""
    # if "content" in parameter:
    #     assert "in" not in parameter
    #     for content in parameter["content"].values():
    #         return type_to_python(content["schema"], typing=typing)
    return type_to_python(parameter().schema(), typing=typing)


def get_default(operation: OperationObject, attribute_path: str):
    attrs = attribute_path.split(".")
    for name, _parameter in operation.get_parameters():
        if name == attrs[0]:
            break
    if name == attribute_path:
        # We found a top level attribute matching the full path, let's use the default
        return _parameter().schema().default

    if name == "body":
        _parameter = _parameter().schema()
    for attr in attrs[1:]:
        _parameter = _parameter().properties[attr]()

    return _parameter().default


def attribute_path(attribute):
    return ".".join(attribute_name(a) for a in attribute.split("."))


def get_type_for_items(schema: ArraySchema):
    return schema.items.name


def get_type_at_path(operation: OperationObject, attribute_path: str):
    content = None
    for code, response in operation.responses.items():
        if int(code) >= ERROR_STATUS_START:
            continue
        for content in response().content.values():
            if content.schema():
                break
    if content is None:
        msg = "Default response not found"
        raise RuntimeError(msg)
    content = content.schema()
    if not attribute_path:
        return get_type_for_items(content)
    for attr in attribute_path.split("."):
        content = content.properties[attr]()

    return get_type_for_items(content)


def filter_models(models: dict[str, SchemaType]) -> dict[str, None]:
    for name in list(models.keys()):
        if isinstance(models[name], ArraySchema) and is_list_model_whitelisted(name):
            continue
        if isinstance(models[name], EnumSchema):
            continue
        if isinstance(models[name], ObjectSchema):
            continue
        if isinstance(models[name], OneOfSchema):
            continue
        if isinstance(models[name], Schema) and models[name].additionalProperties:
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
            if isinstance(definition(), (EnumSchema, OneOfSchema)):
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
                            result[definition().items().items().name] = None
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


def get_oneof_references_for_model(model: SchemaType, model_name: str, seen: dict[str, str] | None = None) -> list[str] | None:
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
        for definition in model().properties.values():
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


def get_type_for_attribute(schema: SchemaType, attribute: str, _current_name: str | None = None) -> str | None:
    """Return Python type name for the attribute."""
    if isinstance(schema(), SchemaType):
        child_schema = schema().properties.get(attribute)
        return type_to_python(child_schema)

    return


def get_typing_for_attribute(
    schema: SchemaType, attribute: str, _current_name: str | None = None, *, optional: str | None = False
) -> str | None:
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
    return


def get_types_for_attribute(schema: SchemaType, attribute: str, current_name: str | None = None) -> str | None:
    if isinstance(schema(), SchemaType):
        child_schema = schema().properties.get(attribute)()
        base_type = get_type_for_attribute(schema, attribute, _current_name=current_name)
        if child_schema.nullable and not child_schema.name:
            return f"({base_type}, none_type)"
        return f"({base_type},)"

    return


def format_value(value: Any, quotes: str = '"'):
    if isinstance(value, str):
        return f"{quotes}{value}{quotes}"
    elif isinstance(value, bool):
        return "true" if value else "false"
    return value


def get_enum_default(model: EnumSchema):
    return model().enum[0] if len(model.enum) == 1 else model().default


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

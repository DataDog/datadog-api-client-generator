import keyword
from typing import Any, Optional, Union

import m2r2

from datadog_api_client_generator.codegen.shared.templates_env import snake_case
from datadog_api_client_generator.openapi.operation_model import OperationObject
from datadog_api_client_generator.openapi.parameter_model import Parameter
from datadog_api_client_generator.openapi.schema_model import EnumSchema, OneOfSchema, Schema


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


def basic_type_to_python(type_: Optional[str], schema: Schema, typing: bool = False):
    if type_ is None:
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
        subtype = type_to_python(schema.items, typing=typing)
        if typing:
            return "List[{}]".format(subtype)
        if schema.items.nullable:
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
    for schema in model["oneOf"]:
        type_ = schema.get("type", "object")
        if type_ == "object" or is_list_model_whitelisted(schema.name):
            yield schema.name
        else:
            yield basic_type_to_python(type_, schema, typing=typing)


def type_to_python(schema: Schema, typing: bool = False):
    """Return Python type name for the type."""

    if type(schema) == OneOfSchema:
        types = list(get_oneof_types(schema, typing=typing))
        if schema.name and typing:
            types.insert(0, schema.name)
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


def get_type_for_parameter(parameter: Parameter, typing: bool =False):
    """Return Python type name for the parameter."""
    # if "content" in parameter:
    #     assert "in" not in parameter
    #     for content in parameter["content"].values():
    #         return type_to_python(content["schema"], typing=typing)
    return type_to_python(parameter.schema, typing=typing)

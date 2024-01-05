from __future__ import annotations
from typing import Any, Dict, Iterator, List, Optional, TypeAlias, Union

from datadog_api_client_generator.openapi.schema_model import SchemaType
from datadog_api_client_generator.openapi.parameter_model import Parameter, ParameterType
from datadog_api_client_generator.openapi.utils import Empty, HEADER_ANY_TYPE, OptionalEmpty, StrBool
from datadog_api_client_generator.openapi.shared_model import _Base, ExternalDocs, RefObject, Server


class MediaObject(_Base):
    schema: OptionalEmpty[SchemaType] = Empty()
    example: OptionalEmpty[Any] = Empty()


class RequestBody(_Base):
    content: Dict[str, MediaObject]
    description: OptionalEmpty[str] = Empty()
    required: OptionalEmpty[StrBool] = Empty()


class ResponseObject(_Base):
    content: OptionalEmpty[Dict[str, MediaObject]] = dict()
    description: OptionalEmpty[str] = None


ResponseType: TypeAlias = Union[RefObject, ResponseObject]


class OperationObject(_Base):
    tags: OptionalEmpty[List[str]] = list()
    summary: OptionalEmpty[str] = Empty()
    description: OptionalEmpty[str] = Empty()
    operationId: OptionalEmpty[str] = Empty()
    parameters: OptionalEmpty[List[ParameterType]] = list()
    deprecated: OptionalEmpty[StrBool] = Empty()
    externalDocs: OptionalEmpty[ExternalDocs] = Empty()
    requestBody: OptionalEmpty[RequestBody] = Empty()
    responses: OptionalEmpty[Dict[str, ResponseType]] = dict()
    servers: OptionalEmpty[List[Server]] = list()
    security: OptionalEmpty[List[Dict[str, List[str]]]] = Empty()

    def get_parameters(self) -> Iterator[str, ParameterType]:
        if self.parameters:
            for parameter in self.parameters:
                if parameter().schema():
                    yield parameter().name, parameter()

        if self.requestBody:
            if "multipart/form-data" in self.requestBody.content:
                parent = self.requestBody.content["multipart/form-data"].schema()
                for name, schema in parent.properties.items():
                    yield name, Parameter(
                        **{
                            "in": "form",
                            "schema": schema(),
                            "name": name,
                            "description": self.requestBody.description
                            if self.requestBody.description
                            else schema().description,
                            "required": name in parent.required,
                        }
                    )
            else:
                for content in self.requestBody.content.values():
                    schema = content.schema()
                    if schema:
                        yield "body", Parameter(
                            **{
                                "in": None,
                                "schema": schema,
                                "name": "body",
                                "description": self.requestBody.description
                                if self.requestBody.description
                                else schema.description,
                                "required": self.requestBody.required,
                            }
                        )
                    break

    def get_accept_headers(self) -> List[str]:
        seen = []
        for response in self.responses.values():
            if getattr(response(), "content"):
                for media_type in response().content.keys():
                    if media_type not in seen:
                        seen.append(media_type)
            else:
                return [HEADER_ANY_TYPE]

        return seen

    def get_return_schema(self) -> Optional[SchemaType]:
        for response in self.responses.values():
            for content in response.content.values():
                if content.schema:
                    return content.schema
            return None

    def schemas_by_name(self, mapping: Dict[str, SchemaType] = {}) -> Dict[str, SchemaType]:
        for _, parameter in self.get_parameters():
            if parameter():
                mapping.update(parameter().schemas_by_name(mapping=mapping))

        if self.requestBody:
            for content in self.requestBody.content.values():
                if content.schema():
                    mapping.update(content.schema().schemas_by_name(mapping=mapping))

        if self.responses:
            for response in self.responses.values():
                if response().content:
                    for content in response().content.values():
                        if content.schema:
                            mapping.update(content.schema.schemas_by_name(mapping=mapping))

        return mapping


class PathsItemObject(_Base):
    summary: OptionalEmpty[str] = Empty()
    description: OptionalEmpty[str] = Empty()
    servers: OptionalEmpty[List[Server]] = list()
    parameters: OptionalEmpty[List[ParameterType]] = list()
    get: OptionalEmpty[OperationObject] = Empty()
    put: OptionalEmpty[OperationObject] = Empty()
    post: OptionalEmpty[OperationObject] = Empty()
    delete: OptionalEmpty[OperationObject] = Empty()
    options: OptionalEmpty[OperationObject] = Empty()
    head: OptionalEmpty[OperationObject] = Empty()
    patch: OptionalEmpty[OperationObject] = Empty()
    trace: OptionalEmpty[OperationObject] = Empty()

    def schemas_by_name(self, mapping: Dict[str, SchemaType] = {}) -> Dict[str, SchemaType]:
        if self.get:
            mapping.update(self.get.schemas_by_name(mapping=mapping))
        if self.put:
            mapping.update(self.put.schemas_by_name(mapping=mapping))
        if self.post:
            mapping.update(self.post.schemas_by_name(mapping=mapping))
        if self.delete:
            mapping.update(self.delete.schemas_by_name(mapping=mapping))
        if self.options:
            mapping.update(self.options.schemas_by_name(mapping=mapping))
        if self.head:
            mapping.update(self.head.schemas_by_name(mapping=mapping))
        if self.patch:
            mapping.update(self.patch.schemas_by_name(mapping=mapping))
        if self.trace:
            mapping.update(self.trace.schemas_by_name(mapping=mapping))

        return mapping

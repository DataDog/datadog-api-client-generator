from __future__ import annotations
from typing import Any, Dict, Iterator, List, Optional, Union

from datadog_api_client_generator.openapi.schema_model import Schema
from datadog_api_client_generator.openapi.parameter_model import Parameter
from datadog_api_client_generator.openapi.utils import HEADER_ANY_TYPE, StrBool
from datadog_api_client_generator.openapi.shared_model import _Base, ExternalDocs, Server


class MediaObject(_Base):
    schema: Optional[Schema] = None
    example: Optional[Any] = None


class RequestBody(_Base):
    content: Dict[str, MediaObject]
    description: Optional[str] = None
    required: Optional[StrBool] = None


class ResponseObject(_Base):
    content: Optional[Dict[str, MediaObject]] = dict()
    description: Optional[str] = None


class OperationObject(_Base):
    tags: Optional[List[str]] = list()
    summary: Optional[str] = None
    description: Optional[str] = None
    operationId: Optional[str] = None
    parameters: Optional[List[Parameter]] = list()
    deprecated: Optional[StrBool] = None
    externalDocs: Optional[ExternalDocs] = None
    requestBody: Optional[RequestBody] = None
    responses: Optional[Dict[str, ResponseObject]] = dict()
    servers: Optional[List[Server]] = list()
    security: Optional[List[Dict[str, List[str]]]] = None

    def get_parameters(self) -> Iterator[str, Parameter]:
        if self.parameters:
            for parameter in self.parameters:
                if parameter.schema:
                    yield parameter.name, parameter

        if self.requestBody:
            if "multipart/form-data" in self.requestBody.content:
                parent = self.requestBody.content["multipart/form-data"].schema
                for name, schema in parent.properties.items():
                    yield name, Parameter(
                        **{
                            "in": "form",
                            "schema": schema,
                            "name": name,
                            "description": self.requestBody.description
                            if self.requestBody.description
                            else schema.description,
                            "required": name in parent.required,
                        }
                    )
            else:
                for content in self.requestBody.content.values():
                    if content.schema:
                        yield "body", Parameter(
                            **{
                                "in": None,
                                "schema": content.schema,
                                "name": "body",
                                "description": self.requestBody.description
                                if self.requestBody.description
                                else content.schema.description,
                                "required": self.requestBody.required,
                            }
                        )
                    break

    def get_accept_headers(self) -> List[str]:
        seen = []
        for response in self.responses.values():
            if response.content:
                for media_type in response.content.keys():
                    if media_type not in seen:
                        seen.append(media_type)
            else:
                return [HEADER_ANY_TYPE]
        return seen

    def get_return_schema(self) -> Optional[Schema]:
        for response in self.responses.values():
            for content in response.content.values():
                if content.schema:
                    return content.schema
            return None

    def schemas_by_name(self) -> Dict[str, Schema]:
        schemas_by_name = {}

        if self.requestBody:
            for content in self.requestBody.content.values():
                if content.schema:
                    schemas_by_name.update(content.schema.schemas_by_name())

        if self.responses:
            for response in self.responses.values():
                if response.content:
                    for content in response.content.values():
                        if content.schema:
                            schemas_by_name.update(content.schema.schemas_by_name())

        return schemas_by_name


class PathsItemObject(_Base):
    summary: Optional[str] = None
    description: Optional[str] = None
    servers: Optional[List[Server]] = list()
    parameters: Optional[List[Parameter]] = list()
    get: Optional[OperationObject] = None
    put: Optional[OperationObject] = None
    post: Optional[OperationObject] = None
    delete: Optional[OperationObject] = None
    options: Optional[OperationObject] = None
    head: Optional[OperationObject] = None
    patch: Optional[OperationObject] = None
    trace: Optional[OperationObject] = None

    def schemas_by_name(self) -> Dict[str, Schema]:
        schemas_by_name = {}

        if self.get:
            schemas_by_name.update(self.get.schemas_by_name())
        if self.put:
            schemas_by_name.update(self.put.schemas_by_name())
        if self.post:
            schemas_by_name.update(self.post.schemas_by_name())
        if self.delete:
            schemas_by_name.update(self.delete.schemas_by_name())
        if self.options:
            schemas_by_name.update(self.options.schemas_by_name())
        if self.head:
            schemas_by_name.update(self.head.schemas_by_name())
        if self.patch:
            schemas_by_name.update(self.patch.schemas_by_name())
        if self.trace:
            schemas_by_name.update(self.trace.schemas_by_name())

        return schemas_by_name

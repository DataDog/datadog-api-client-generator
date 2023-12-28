from __future__ import annotations
from typing import Any, Dict, Iterator, List, Optional, Union

from pydantic import BaseModel

from datadog_api_client_generator.openapi.schema_model import (
    AllOfSchema,
    AnyOfSchema,
    BaseSchema,
    EnumSchema,
    ObjectSchema,
    OneOfSchema,
)
from datadog_api_client_generator.openapi.parameter_model import Parameter
from datadog_api_client_generator.openapi.utils import HEADER_ANY_TYPE, StrBool
from datadog_api_client_generator.openapi.shared_model import ExternalDocs, Server


class MediaObject(BaseModel):
    schema: Optional[Union[AnyOfSchema, AllOfSchema, EnumSchema, OneOfSchema, ObjectSchema, BaseSchema]] = None
    example: Optional[Any] = None


class RequestBody(BaseModel):
    content: Dict[str, MediaObject]
    description: Optional[str] = None
    required: Optional[StrBool] = None


class ResponseObject(BaseModel):
    content: Optional[Dict[str, MediaObject]] = None
    description: Optional[str] = None


class OperationObject(BaseModel):
    tags: Optional[List[str]] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    operationId: Optional[str] = None
    parameters: Optional[List[Parameter]] = None
    deprecated: Optional[StrBool] = None
    externalDocs: Optional[ExternalDocs] = None
    requestBody: Optional[RequestBody] = None
    responses: Optional[Dict[str, ResponseObject]] = None
    servers: Optional[List[Server]] = None
    security: Optional[List[Dict[str, List[str]]]] = None

    def get_parameters(self) -> Iterator[str, Union[Parameter, RequestBody]]:
        if self.parameters:
            for content in self.parameters:
                if "schema" in content:
                    yield content["name"], content

        if self.requestBody:
            if "multipart/form-data" in self.requestBody.content:
                parent = self.requestBody.content["multipart/form-data"].schema
                for name, schema in parent.properties.items():
                    yield name, Parameter(
                        **{
                            "in": "form",
                            "schema": schema,
                            "name": name,
                            "description": schema.description,
                            "required": name in parent.get("required", []),
                        }
                    )
            else:
                yield "body", self.requestBody

    def accept_headers(self) -> List[str]:
        seen = []
        for response in self.responses.values():
            if response.content:
                for media_type in response.content.keys():
                    if media_type not in seen:
                        seen.append(media_type)
            else:
                return [HEADER_ANY_TYPE]
        return seen


class PathsItemObject(BaseModel):
    summary: Optional[str] = None
    description: Optional[str] = None
    servers: Optional[List[Server]] = None
    parameters: Optional[List[Parameter]] = None
    get: Optional[OperationObject] = None
    put: Optional[OperationObject] = None
    post: Optional[OperationObject] = None
    delete: Optional[OperationObject] = None
    options: Optional[OperationObject] = None
    head: Optional[OperationObject] = None
    patch: Optional[OperationObject] = None
    trace: Optional[OperationObject] = None

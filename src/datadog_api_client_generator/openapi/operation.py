from __future__ import annotations
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from .schema import AllOfSchema, AnyOfSchema, BaseSchema, EnumSchema, ObjectSchema, OneOfSchema
from .parameter import Parameter
from .utils import StrBool
from .shared import ExternalDocs, Server

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
    responses: Optional[Dict[str, ResponseObject]]
    servers: Optional[List[Server]] = None
    security: Optional[List[Dict[str, List[str]]]] = None


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

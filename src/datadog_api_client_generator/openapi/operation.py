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


class _PathsItemObjectBase(BaseModel):
    summary: Optional[str] = None
    description: Optional[str] = None
    servers: Optional[List[Server]] = None
    parameters: Optional[List[Parameter]] = None


class GetPath(_PathsItemObjectBase):
    get: OperationObject


class PutPath(_PathsItemObjectBase):
    put: OperationObject


class PostPath(_PathsItemObjectBase):
    post: OperationObject


class DeletePath(_PathsItemObjectBase):
    delete: OperationObject


class OptionsPath(_PathsItemObjectBase):
    options: OperationObject


class HeadPath(_PathsItemObjectBase):
    head: OperationObject


class PatchPath(_PathsItemObjectBase):
    patch: OperationObject


class TracePath(_PathsItemObjectBase):
    trace: OperationObject

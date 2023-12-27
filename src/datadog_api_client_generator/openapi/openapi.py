from __future__ import annotations

from typing import Annotated, Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, PlainValidator, model_validator

from .utils import get_name_from_json_ref, StrBool


class BaseSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    required: Optional[List[str]] = None
    type: Optional[Literal["string", "number", "integer", "boolean", "array", "object"]] = None
    format: Optional[
        Literal["int32", "int64", "float", "double", "byte", "binary", "date", "date-time", "password", "email", "uuid"]
    ] = None
    deprecated: Optional[StrBool] = None
    example: Optional[Any] = None
    nullable: Optional[StrBool] = None
    additionalProperties: Optional[Any] = None
    extensions: Optional[Dict[str, Any]] = None

    @model_validator(mode="before")
    def _enrich_schema(cls, v):
        # inject name from $ref
        if not v.get("name"):
            name = get_name_from_json_ref(v)
            if name:
                v["name"] = name

        extensions = {}
        for k in list(v.keys()):
            if k.startswith("x-"):
                extensions[k] = v[k]
                del v[k]
        if extensions:
            v["extensions"] = extensions

        # Remap extensions
        return v


class OneOfSchema(BaseSchema):
    oneOf: List[BaseSchema]


class EnumSchema(BaseSchema):
    enum: List[Union[str, int, float]]


class AllOfSchema(BaseSchema):
    allOf: List[BaseSchema]


class AnyOfSchema(BaseSchema):
    anyOf: List[BaseSchema]


class ObjectSchema(BaseSchema):
    properties: Dict[str, BaseSchema]


class Parameter(BaseModel):
    in_: Literal["query", "header", "path", "cookie"] = Field(alias="in")
    name: str
    description: Optional[str] = None
    required: Optional[StrBool] = None
    deprecated: Optional[StrBool] = None
    schema: Optional[Union[AnyOfSchema, AllOfSchema, EnumSchema, OneOfSchema, ObjectSchema, BaseSchema]] = None
    style: Optional[str] = None
    explode: Optional[StrBool] = None
    example: Optional[Any] = None


class OpenAPIContact(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    email: Optional[str] = None


class OpenAPIInfo(BaseModel):
    title: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    contact: Optional[OpenAPIContact] = None


class Components(BaseModel):
    schemas: Optional[
        Dict[str, Union[AnyOfSchema, AllOfSchema, EnumSchema, OneOfSchema, ObjectSchema, BaseSchema]]
    ] = None
    parameters: Optional[Dict[str, Parameter]] = None


class ExternalDocs(BaseModel):
    url: str
    description: Optional[str] = None


class ServerVariable(BaseModel):
    default: str
    description: Optional[str] = None
    enum: Optional[List[str]] = None


class Server(BaseModel):
    url: str
    description: Optional[str] = None
    variables: Optional[Dict[str, ServerVariable]] = None


class Tag(BaseModel):
    name: str
    description: Optional[str] = None


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


class OpenAPI(BaseModel):
    openapi: str
    info: OpenAPIInfo
    paths: Dict[str, Union[GetPath, PutPath, PostPath, DeletePath, OptionsPath, HeadPath, PatchPath, TracePath]]
    components: Optional[Components] = None
    servers: Optional[List[Server]] = None
    tags: Optional[List[Tag]] = None
    externalDocs: Optional[ExternalDocs] = None
    security: Optional[List[Dict[str, List[str]]]] = None

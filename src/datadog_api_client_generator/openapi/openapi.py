from __future__ import annotations
from typing import Dict, List, Optional, Union

from pydantic import BaseModel

from .operation import PathsItemObject
from .shared import ExternalDocs, Server
from .schema import AllOfSchema, AnyOfSchema, BaseSchema, EnumSchema, ObjectSchema, OneOfSchema
from .parameter import Parameter


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


class Tag(BaseModel):
    name: str
    description: Optional[str] = None


class OpenAPI(BaseModel):
    openapi: str
    info: OpenAPIInfo
    paths: Dict[str, PathsItemObject]
    components: Optional[Components] = None
    servers: Optional[List[Server]] = None
    tags: Optional[List[Tag]] = None
    externalDocs: Optional[ExternalDocs] = None
    security: Optional[List[Dict[str, List[str]]]] = None

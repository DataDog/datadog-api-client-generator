from __future__ import annotations
from typing import Dict, List, Optional

from pydantic import BaseModel
from datadog_api_client_generator.codegen.shared.templates_env import camel_case

from datadog_api_client_generator.openapi.operation_model import OperationObject, PathsItemObject
from datadog_api_client_generator.openapi.shared_model import ExternalDocs, Server
from datadog_api_client_generator.openapi.schema_model import ArraySchema, EnumSchema, ObjectSchema, OneOfSchema, Schema
from datadog_api_client_generator.openapi.parameter_model import Parameter


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
    schemas: Optional[Dict[str, Schema]] = dict()
    parameters: Optional[Dict[str, Parameter]] = dict()


class Tag(BaseModel):
    name: str
    description: Optional[str] = None


class OpenAPI(BaseModel):
    openapi: str
    info: OpenAPIInfo
    paths: Dict[str, PathsItemObject]
    components: Optional[Components] = None
    servers: Optional[List[Server]] = list()
    tags: Optional[List[Tag]] = list()
    externalDocs: Optional[ExternalDocs] = None
    security: Optional[List[Dict[str, List[str]]]] = None

    def tags_by_name(self) -> Dict[str, Tag]:
        return {tag.name: tag for tag in self.tags}

    def group_apis_by_tag(self) -> Dict[str, List[str, str, OperationObject]]:
        operations = {}

        for path in self.paths:
            for k, v in self.paths[path]:
                if type(v) == OperationObject:
                    tag = v.tags[0] if v.tags else None
                    operations.setdefault(tag, []).append((path, k, v))

        return operations

    def schemas_by_name(self) -> Dict[str, Schema]:
        schemas_by_name = {}
        for path in self.paths.values():
            schemas_by_name.update(path.schemas_by_name())

        return schemas_by_name

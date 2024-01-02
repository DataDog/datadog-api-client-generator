from __future__ import annotations
from typing import Dict, List, Union

from datadog_api_client_generator.openapi.operation_model import OperationObject, PathsItemObject
from datadog_api_client_generator.openapi.shared_model import _Base, ExternalDocs, Server
from datadog_api_client_generator.openapi.schema_model import Schema
from datadog_api_client_generator.openapi.parameter_model import Parameter
from datadog_api_client_generator.openapi.utils import Empty, OptionalEmpty


class OpenAPIContact(_Base):
    name: OptionalEmpty[str] = Empty()
    url: OptionalEmpty[str] = Empty()
    email: OptionalEmpty[str] = Empty()


class OpenAPIInfo(_Base):
    title: OptionalEmpty[str] = Empty()
    version: OptionalEmpty[str] = Empty()
    description: OptionalEmpty[str] = Empty()
    contact: OptionalEmpty[OpenAPIContact] = Empty()


class Components(_Base):
    schemas: OptionalEmpty[Dict[str, Schema]] = dict()
    parameters: OptionalEmpty[Dict[str, Parameter]] = dict()


class Tag(_Base):
    name: str
    description: OptionalEmpty[str] = Empty()


class OpenAPI(_Base):
    openapi: str
    info: OpenAPIInfo
    paths: Dict[str, PathsItemObject]
    components: OptionalEmpty[Components] = Empty()
    servers: OptionalEmpty[List[Server]] = list()
    tags: OptionalEmpty[List[Tag]] = list()
    externalDocs: OptionalEmpty[ExternalDocs] = Empty()
    security: OptionalEmpty[List[Dict[str, List[str]]]] = Empty()

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

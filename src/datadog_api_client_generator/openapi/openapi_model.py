from __future__ import annotations
from contextvars import ContextVar
from typing import Dict, List, Optional, TypeAlias, Union

from pydantic import ValidationInfo, model_validator

from datadog_api_client_generator.openapi.operation_model import OperationObject, PathsItemObject, ResponseType
from datadog_api_client_generator.openapi.shared_model import _Base, ExternalDocs, SecuritySchemeType, Server
from datadog_api_client_generator.openapi.schema_model import SchemaType, Schema
from datadog_api_client_generator.openapi.parameter_model import ParameterType, Parameter
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
    schemas: OptionalEmpty[Dict[str, SchemaType]] = dict()
    parameters: OptionalEmpty[Dict[str, ParameterType]] = dict()
    responses: OptionalEmpty[Dict[str, ResponseType]] = dict()
    securitySchemes: OptionalEmpty[Dict[str, SecuritySchemeType]] = dict()

    @model_validator(mode="before")
    def _inject_schema_names(cls, v: Dict, info: ValidationInfo) -> Dict:
        if "schemas" in v:
            for k, schema in v["schemas"].items():
                schema["name"] = k
        return v


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

    @model_validator(mode="before")
    def _inject_ctx(cls, v: Dict, info: ValidationInfo) -> Dict:
        if info.context is None:
            raise AttributeError("context cannot be None when initializing")
        info.context["openapi"] = ContextVar(str(id(v)))
        return v

    @model_validator(mode="after")
    def _inject_ctx_after(self, info: ValidationInfo) -> Dict:
        info.context["openapi"].set(self)
        return self

    def tags_by_name(self) -> Dict[str, Tag]:
        return {tag.name: tag for tag in self.tags}

    def group_apis_by_tag(self) -> Dict[str, List[str, str, OperationObject]]:
        operations = {}

        for path in self.paths:
            for k, v in self.paths[path]:
                if isinstance(v, OperationObject):
                    tag = v.tags[0] if v.tags else None
                    operations.setdefault(tag, []).append((path, k, v))

        return operations

    def schemas_by_name(
        self, mapping: Optional[Dict[str, SchemaType]] = None, recursive: bool = True, include_self: bool = True
    ) -> Dict[str, SchemaType]:
        if mapping is None:
            mapping = {}

        for path in self.paths.values():
            mapping.update(path.schemas_by_name(mapping=mapping, recursive=recursive, include_self=include_self))

        return mapping

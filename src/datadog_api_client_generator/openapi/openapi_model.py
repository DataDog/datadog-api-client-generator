# Unless explicitly stated otherwise all files in this repository are licensed under the Apache 2.0 License.
#
# This product includes software developed at Datadog (https://www.datadoghq.com/  Copyright 2025 Datadog, Inc.
from __future__ import annotations

from contextvars import ContextVar
from typing import TYPE_CHECKING

from pydantic import ValidationInfo, model_validator

from datadog_api_client_generator.openapi.operation_model import OperationObject, PathsItemObject, ResponseType
from datadog_api_client_generator.openapi.shared_model import ExternalDocs, SecuritySchemeType, Server, _Base
from datadog_api_client_generator.openapi.utils import Empty, OptionalEmpty

if TYPE_CHECKING:
    from datadog_api_client_generator.openapi.parameter_model import ParameterType
    from datadog_api_client_generator.openapi.schema_model import SchemaType


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
    schemas: OptionalEmpty[dict[str, SchemaType]] = None
    parameters: OptionalEmpty[dict[str, ParameterType]] = None
    responses: OptionalEmpty[dict[str, ResponseType]] = None
    securitySchemes: OptionalEmpty[dict[str, SecuritySchemeType]] = None

    @classmethod
    @model_validator(mode="before")
    def _inject_schema_names(cls, v: dict, _info: ValidationInfo) -> dict:
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
    paths: dict[str, PathsItemObject]
    components: OptionalEmpty[Components] = Empty()
    servers: OptionalEmpty[list[Server]] = None
    tags: OptionalEmpty[list[Tag]] = None
    externalDocs: OptionalEmpty[ExternalDocs] = Empty()
    security: OptionalEmpty[list[dict[str, list[str]]]] = Empty()

    @classmethod
    @model_validator(mode="before")
    def _inject_ctx(cls, v: dict, info: ValidationInfo) -> dict:
        if info.context is None:
            msg = "context cannot be None when initializing"
            raise AttributeError(msg)
        info.context["openapi"] = ContextVar(str(id(v)))
        return v

    @model_validator(mode="after")
    def _inject_ctx_after(self, info: ValidationInfo) -> dict:
        info.context["openapi"].set(self)
        return self

    def tags_by_name(self) -> dict[str, Tag]:
        return {tag.name: tag for tag in self.tags}

    def group_apis_by_tag(self) -> dict[str, list[str, str, OperationObject]]:
        operations = {}

        for path in self.paths:
            for k, v in self.paths[path]:
                if isinstance(v, OperationObject):
                    tag = v.tags[0] if v.tags else None
                    operations.setdefault(tag, []).append((path, k, v))

        return operations

    def schemas_by_name(
        self, mapping: dict[str, SchemaType] | None = None, *, recursive: bool = True, include_self: bool = True
    ) -> dict[str, SchemaType]:
        if mapping is None:
            mapping = {}

        for path in self.paths.values():
            mapping.update(path.schemas_by_name(mapping=mapping, recursive=recursive, include_self=include_self))

        return mapping

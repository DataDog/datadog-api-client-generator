# Unless explicitly stated otherwise all files in this repository are licensed under the Apache 2.0 License.
#
# This product includes software developed at Datadog (https://www.datadoghq.com/  Copyright 2025 Datadog, Inc.

from __future__ import annotations

from typing import Any, Literal, TypeAlias, Union

from pydantic import Field

from datadog_api_client_generator.openapi.schema_model import ArraySchema, SchemaType
from datadog_api_client_generator.openapi.shared_model import RefObject, _Base
from datadog_api_client_generator.openapi.utils import Empty, OptionalEmpty, StrBool


class Parameter(_Base):
    in_: Literal[None, "query", "header", "path", "cookie", "body", "form"] = Field(alias="in")
    name: str
    description: OptionalEmpty[str] = Empty()
    required: OptionalEmpty[StrBool] = Empty()
    deprecated: OptionalEmpty[StrBool] = Empty()
    schema: OptionalEmpty[SchemaType] = Empty()
    style: OptionalEmpty[str] = Empty()
    explode: OptionalEmpty[StrBool] = Empty()
    example: OptionalEmpty[Any] = Empty()

    def get_collection_format(self) -> str:
        in_to_style = {
            "query": "form",
            "path": "simple",
            "header": "simple",
            "cookie": "form",
        }
        matrix = {
            ("form", False): "csv",
            ("form", True): "multi",
        }
        if isinstance(self.schema, ArraySchema):
            in_ = self.in_ or "query"
            style = self.style if self.style else in_to_style[in_]
            explode = self.explode
            if self.explode is None:
                explode = style == "form"

            return matrix.get((style, explode), "multi")

        return ""

    def schemas_by_name(
        self, mapping: dict[str, SchemaType] | None = None, *, recursive: bool = True, include_self: bool = True
    ) -> dict[str, SchemaType]:
        if mapping is None:
            mapping = {}

        if self.schema:
            mapping.update(self.schema.schemas_by_name(mapping=mapping, recursive=recursive, include_self=include_self))

        return mapping


class ParamRef(RefObject):
    _resolved_ref: Parameter = None

    def __call__(self) -> Parameter:
        return self._resolve_ref()

    def _resolve_ref(self) -> Parameter:
        if self._resolved_ref is None:
            self._resolved_ref = getattr(self._root_openapi.get().components, self.ref_components_path).get(self.name)

        return self._resolved_ref


ParameterType: TypeAlias = Union[Parameter, ParamRef]

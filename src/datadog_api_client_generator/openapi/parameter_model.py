from __future__ import annotations
from typing import Any, Dict, Literal, TypeAlias, Union

from pydantic import Field

from datadog_api_client_generator.openapi.schema_model import ArraySchema, SchemaType
from datadog_api_client_generator.openapi.shared_model import _Base, _RefObject
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
            # TODO add more cases from https://swagger.io/specification/#parameter-style
        }
        if isinstance(self.schema, ArraySchema):
            in_ = self.in_ or "query"
            style = self.style if self.style else in_to_style[in_]
            explode = self.explode if self.explode is not None else True if style == "form" else False

            return matrix.get((style, explode), "multi")

    def schemas_by_name(self, mapping: Dict[str, SchemaType] = {}) -> Dict[str, SchemaType]:
        if self.schema:
            mapping.update(self.schema.schemas_by_name(mapping=mapping))

        return mapping


class ParameterRefObject(_RefObject):
    _ref_path: Literal["parameters"]

    def get_collection_format(self) -> str:
        return self.resolve_ref().get_collection_format()

    def schemas_by_name(self, mapping: Dict[str, SchemaType] = {}) -> Dict[str, SchemaType]:
        param = self.resolve_ref()
        if param.schema and param.schema.name not in mapping:
            mapping.update(param.schema.schemas_by_name(mapping=mapping))

        return mapping

    def resolve_ref(self) -> Parameter:
        return self._root_openapi.get().components.parameters.get(self.name)


ParameterType: TypeAlias = Union[Parameter, ParameterRefObject]

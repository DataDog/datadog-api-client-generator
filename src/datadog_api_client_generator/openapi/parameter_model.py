from __future__ import annotations
from typing import Any, Dict, Literal, Optional

from pydantic import Field

from datadog_api_client_generator.openapi.schema_model import ArraySchema, Schema
from datadog_api_client_generator.openapi.shared_model import _Base
from datadog_api_client_generator.openapi.utils import StrBool


class Parameter(_Base):
    in_: Literal[None, "query", "header", "path", "cookie", "body", "form"] = Field(alias="in")
    name: str
    description: Optional[str] = None
    required: Optional[StrBool] = None
    deprecated: Optional[StrBool] = None
    schema: Optional[Schema] = None
    style: Optional[str] = None
    explode: Optional[StrBool] = None
    example: Optional[Any] = None

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
        if type(self.schema) == ArraySchema:
            in_ = self.in_ or "query"
            style = self.style if self.style else in_to_style[in_]
            explode = self.explode if self.explode is not None else True if style == "form" else False

            return matrix.get((style, explode), "multi")

    def schemas_by_name(self) -> Dict[str, Schema]:
        schemas_by_name = {}
        if self.schema:
            schemas_by_name.update(self.schema.schemas_by_name())

        return schemas_by_name

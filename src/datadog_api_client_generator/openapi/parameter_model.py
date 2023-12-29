from __future__ import annotations
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field

from datadog_api_client_generator.openapi.schema_model import ArraySchema, Schema
from datadog_api_client_generator.openapi.utils import StrBool


class Parameter(BaseModel):
    in_: Literal["query", "header", "path", "cookie"] = Field(alias="in")
    name: str
    description: Optional[str] = None
    required: Optional[StrBool] = None
    deprecated: Optional[StrBool] = None
    schema: Optional[Schema] = None
    style: Optional[str] = None
    explode: Optional[StrBool] = None
    example: Optional[Any] = None

    def collection_format(self) -> str:
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
        if self.schema.type == "array" or type(self.schema) == ArraySchema:
            in_ = self.get("in_", "query")
            style = self.get("style", in_to_style[in_])
            explode = self.get("explode", True if style == "form" else False)
            return matrix.get((style, explode), "multi")

    def schemas_by_name(self) -> Dict[str, Schema]:
        schemas_by_name = {}
        if self.schema:
            schemas_by_name.update(self.schema.schemas_by_name())

        return schemas_by_name

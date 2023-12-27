from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, model_validator

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

        # Remap extensions
        extensions = {}
        for k in list(v.keys()):
            if k.startswith("x-"):
                extensions[k] = v[k]
                del v[k]
        if extensions:
            v["extensions"] = extensions

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

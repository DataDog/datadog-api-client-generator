from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional, Union, TypeAlias

from jsonref import JsonRef
from pydantic import BaseModel, model_validator

from datadog_api_client_generator.openapi.utils import get_name_from_json_ref, StrBool


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
    additionalProperties: Optional[Union[bool, Schema]] = None
    extensions: Optional[Dict[str, Any]] = None

    @model_validator(mode="before")
    def _enrich_schema(cls, v: Dict) -> Dict:
        if type(v) == JsonRef:
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

    def schemas_by_name(self) -> Dict[str, Schema]:
        schemas_by_name = {}
        if self.name:
            schemas_by_name[self.name] = self

        if type(self.additionalProperties) == Schema:
            schemas_by_name.update(self.additionalProperties.schemas_by_name())

        return schemas_by_name


class OneOfSchema(BaseSchema):
    oneOf: List[Schema]

    def schemas_by_name(self) -> Dict[str, Schema]:
        schemas_by_name = {}
        if self.name:
            schemas_by_name[self.name] = self

        for oneOf in self.oneOf:
            schemas_by_name.update(oneOf.schemas_by_name())

        return schemas_by_name


class EnumSchema(BaseSchema):
    enum: List[Union[str, int, float]]

    def schemas_by_name(self) -> Dict[str, Schema]:
        schemas_by_name = {}
        if self.name:
            schemas_by_name[self.name] = self

        return schemas_by_name


class AllOfSchema(BaseSchema):
    allOf: List[Schema]

    def schemas_by_name(self) -> Dict[str, Schema]:
        schemas_by_name = {}
        if self.name:
            schemas_by_name[self.name] = self

        for allOf in self.allOf:
            schemas_by_name.update(allOf.schemas_by_name())

        return schemas_by_name


class AnyOfSchema(BaseSchema):
    anyOf: List[Schema]

    def schemas_by_name(self) -> Dict[str, Schema]:
        schemas_by_name = {}
        if self.name:
            schemas_by_name[self.name] = self

        for anyOf in self.anyOf:
            schemas_by_name.update(anyOf.schemas_by_name())

        return schemas_by_name


class ArraySchema(BaseSchema):
    items: Schema

    def schemas_by_name(self) -> Dict[str, Schema]:
        schemas_by_name = {}
        if self.name:
            schemas_by_name[self.name] = self

        schemas_by_name.update(self.items.schemas_by_name())

        return schemas_by_name


class ObjectSchema(BaseSchema):
    properties: Dict[str, Schema]

    def schemas_by_name(self) -> Dict[str, Schema]:
        schemas_by_name = {}
        if self.name:
            schemas_by_name[self.name] = self

        for k, p in self.properties.items():
            schemas_by_name.update(p.schemas_by_name())

        return schemas_by_name


Schema: TypeAlias = Union[ArraySchema, AnyOfSchema, AllOfSchema, EnumSchema, OneOfSchema, ObjectSchema, BaseSchema]

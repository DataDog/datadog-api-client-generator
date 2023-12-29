from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional, Union, TypeAlias

from jsonref import JsonRef
from pydantic import model_validator

from datadog_api_client_generator.openapi.shared_model import _Base
from datadog_api_client_generator.openapi.utils import get_name_from_json_ref, StrBool


class BaseSchema(_Base):
    name: Optional[str] = None
    description: Optional[str] = None
    required: Optional[List[str]] = None
    type: Optional[Literal["string", "number", "integer", "boolean", "array", "object"]] = None
    format: Optional[
        Literal["int32", "int64", "float", "double", "byte", "binary", "date", "date-time", "password", "email", "uuid"]
    ] = None
    deprecated: Optional[StrBool] = None
    example: Optional[Any] = None
    default: Optional[Any] = None
    nullable: Optional[StrBool] = None
    additionalProperties: Optional[Union[bool, Schema]] = None
    maxLength: Optional[int] = None
    minLength: Optional[int] = None
    maximum: Optional[int] = None
    minimum: Optional[int] = None
    pattern: Optional[str] = None
    maxItems: Optional[int] = None
    minItems: Optional[int] = None

    @model_validator(mode="before")
    def _enrich_schema(cls, v: Dict) -> Dict:
        if type(v) == JsonRef:
            # inject name from $ref
            if not v.get("name"):
                name = get_name_from_json_ref(v)
                if name:
                    v["name"] = name
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

from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional, Union, TypeAlias

from datadog_api_client_generator.openapi.shared_model import _Base, _RefObject
from datadog_api_client_generator.openapi.utils import Empty, OptionalEmpty, StrBool


class Schema(_Base):
    name: OptionalEmpty[str] = Empty()
    description: OptionalEmpty[str] = Empty()
    required: Optional[List[str]] = list()
    type: OptionalEmpty[Literal["string", "number", "integer", "boolean", "array", "object"]] = Empty()
    format: OptionalEmpty[
        Literal["int32", "int64", "float", "double", "byte", "binary", "date", "date-time", "password", "email", "uuid"]
    ] = Empty()
    deprecated: OptionalEmpty[StrBool] = Empty()
    example: OptionalEmpty[Any] = Empty()
    default: OptionalEmpty[Any] = Empty()
    nullable: OptionalEmpty[StrBool] = Empty()
    additionalProperties: OptionalEmpty[Union[bool, SchemaType]] = Empty()
    maxLength: OptionalEmpty[int] = Empty()
    minLength: OptionalEmpty[int] = Empty()
    maximum: OptionalEmpty[int] = Empty()
    minimum: OptionalEmpty[int] = Empty()
    pattern: OptionalEmpty[str] = Empty()
    maxItems: OptionalEmpty[int] = Empty()
    minItems: OptionalEmpty[int] = Empty()
    exclusiveMinimum: OptionalEmpty[StrBool] = Empty()
    exclusiveMaximum: OptionalEmpty[StrBool] = Empty()

    def schemas_by_name(self) -> Dict[str, SchemaType]:
        schemas_by_name = {}
        if self.name:
            schemas_by_name[self.name] = self

        if type(self.additionalProperties) == SchemaType:
            schemas_by_name.update(self.additionalProperties.schemas_by_name())

        return schemas_by_name


class OneOfSchema(Schema):
    oneOf: List[SchemaType]

    def schemas_by_name(self) -> Dict[str, SchemaType]:
        schemas_by_name = {}
        if self.name:
            schemas_by_name[self.name] = self

        for oneOf in self.oneOf:
            schemas_by_name.update(oneOf.schemas_by_name())

        return schemas_by_name


class EnumSchema(Schema):
    enum: List[Union[str, int, float]]

    def schemas_by_name(self) -> Dict[str, SchemaType]:
        schemas_by_name = {}
        if self.name:
            schemas_by_name[self.name] = self

        return schemas_by_name


class AllOfSchema(Schema):
    allOf: List[SchemaType]

    def schemas_by_name(self) -> Dict[str, SchemaType]:
        schemas_by_name = {}
        if self.name:
            schemas_by_name[self.name] = self

        for allOf in self.allOf:
            schemas_by_name.update(allOf.schemas_by_name())

        return schemas_by_name


class AnyOfSchema(Schema):
    anyOf: List[SchemaType]

    def schemas_by_name(self) -> Dict[str, SchemaType]:
        schemas_by_name = {}
        if self.name:
            schemas_by_name[self.name] = self

        for anyOf in self.anyOf:
            schemas_by_name.update(anyOf.schemas_by_name())

        return schemas_by_name


class ArraySchema(Schema):
    items: SchemaType

    def schemas_by_name(self) -> Dict[str, SchemaType]:
        schemas_by_name = {}
        if self.name:
            schemas_by_name[self.name] = self

        schemas_by_name.update(self.items.schemas_by_name())

        return schemas_by_name


class ObjectSchema(Schema):
    properties: Dict[str, SchemaType]

    def schemas_by_name(self) -> Dict[str, SchemaType]:
        schemas_by_name = {}
        if self.name:
            schemas_by_name[self.name] = self

        for k, p in self.properties.items():
            schemas_by_name.update(p.schemas_by_name())

        return schemas_by_name


class SchemasRefObject(_RefObject):
    _ref_path: Literal["schemas"]

    def schemas_by_name(self) -> Dict[str, SchemaType]:
        return self.resolve_ref().schemas_by_name()

    def resolve_ref(self) -> SchemaType:
        return self._root_openapi.get().components.schemas.get(self.name)


SchemaType: TypeAlias = Union[
    SchemasRefObject, ArraySchema, AnyOfSchema, AllOfSchema, EnumSchema, OneOfSchema, ObjectSchema, Schema
]

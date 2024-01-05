from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional, Union, TypeAlias

from datadog_api_client_generator.openapi.shared_model import _Base, RefObject
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

    def schemas_by_name(self, mapping: Optional[Dict[str, SchemaType]] = None) -> Dict[str, SchemaType]:
        if mapping is None:
            mapping = {}

        if self.name:
            mapping[self.name] = self

        if isinstance(self.additionalProperties, SchemaType):
            mapping.update(self.additionalProperties.schemas_by_name(mapping=mapping))

        return mapping


class OneOfSchema(Schema):
    oneOf: List[SchemaType]

    def schemas_by_name(self, mapping: Optional[Dict[str, SchemaType]] = None) -> Dict[str, SchemaType]:
        if mapping is None:
            mapping = {}

        if self.name:
            mapping[self.name] = self

        for oneOf in self.oneOf:
            mapping.update(oneOf.schemas_by_name(mapping=mapping))

        return mapping


class EnumSchema(Schema):
    enum: List[Union[str, int, float]]

    def schemas_by_name(self, mapping: Optional[Dict[str, SchemaType]] = None) -> Dict[str, SchemaType]:
        if mapping is None:
            mapping = {}

        if self.name:
            mapping[self.name] = self

        return mapping


class AllOfSchema(Schema):
    allOf: List[SchemaType]

    def schemas_by_name(self, mapping: Optional[Dict[str, SchemaType]] = None) -> Dict[str, SchemaType]:
        if mapping is None:
            mapping = {}

        if self.name:
            mapping[self.name] = self

        for allOf in self.allOf:
            mapping.update(allOf.schemas_by_name(mapping=mapping))

        return mapping


class AnyOfSchema(Schema):
    anyOf: List[SchemaType]

    def schemas_by_name(self, mapping: Optional[Dict[str, SchemaType]] = None) -> Dict[str, SchemaType]:
        if mapping is None:
            mapping = {}

        if self.name:
            mapping[self.name] = self

        for anyOf in self.anyOf:
            mapping.update(anyOf.schemas_by_name(mapping=mapping))

        return mapping


class ArraySchema(Schema):
    items: SchemaType

    def schemas_by_name(self, mapping: Optional[Dict[str, SchemaType]] = None) -> Dict[str, SchemaType]:
        if mapping is None:
            mapping = {}

        if self.name:
            mapping[self.name] = self

        mapping.update(self.items.schemas_by_name(mapping=mapping))

        return mapping


class ObjectSchema(Schema):
    properties: Dict[str, SchemaType]

    def schemas_by_name(self, mapping: Optional[Dict[str, SchemaType]] = None) -> Dict[str, SchemaType]:
        if mapping is None:
            mapping = {}

        if self.name:
            mapping[self.name] = self

        for k, p in self.properties.items():
            mapping.update(p.schemas_by_name(mapping=mapping))

        return mapping


SchemaType: TypeAlias = Union[
    RefObject, ArraySchema, AnyOfSchema, AllOfSchema, EnumSchema, OneOfSchema, ObjectSchema, Schema
]

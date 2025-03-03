# Unless explicitly stated otherwise all files in this repository are licensed under the Apache 2.0 License.
#
# This product includes software developed at Datadog (https://www.datadoghq.com/  Copyright 2025 Datadog, Inc.
from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, TypeAlias, Union

from datadog_api_client_generator.openapi.shared_model import RefObject, _Base
from datadog_api_client_generator.openapi.utils import Empty, OptionalEmpty, StrBool


class Schema(_Base):
    name: OptionalEmpty[str] = Empty()
    description: OptionalEmpty[str] = Empty()
    required: Optional[List[str]] = []
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
    readOnly: OptionalEmpty[StrBool] = Empty()
    writeOnly: OptionalEmpty[StrBool] = Empty()

    def schemas_by_name(
        self, mapping: Optional[Dict[str, SchemaType]] = None, recursive: bool = True, include_self: bool = True
    ) -> Dict[str, SchemaType]:
        if mapping is None:
            mapping = {}

        if isinstance(self.additionalProperties, SchemaType):
            if self.additionalProperties().name:
                if self.additionalProperties().name in mapping:
                    return mapping
                mapping[self.additionalProperties().name] = self.additionalProperties()

                if recursive:
                    mapping.update(self.additionalProperties().schemas_by_name(mapping=mapping, recursive=recursive))

        if self.name and include_self:
            mapping[self.name] = self

        return mapping


class OneOfSchema(Schema):
    oneOf: List[SchemaType]

    def schemas_by_name(
        self, mapping: Optional[Dict[str, SchemaType]] = None, recursive: bool = True, include_self: bool = True
    ) -> Dict[str, SchemaType]:
        if mapping is None:
            mapping = {}

        for oneOf in self.oneOf:
            if oneOf().name:
                if oneOf().name in mapping:
                    continue
                mapping[oneOf().name] = oneOf()

                if recursive:
                    mapping.update(oneOf().schemas_by_name(mapping=mapping))

        if self.name and include_self:
            mapping[self.name] = self

        return mapping


class EnumSchema(Schema):
    enum: List[Union[str, int, float]]

    def schemas_by_name(
        self, mapping: Optional[Dict[str, SchemaType]] = None, recursive: bool = True, include_self: bool = True
    ) -> Dict[str, SchemaType]:
        if mapping is None:
            mapping = {}

        if self.name and include_self:
            mapping[self.name] = self

        return mapping


class AllOfSchema(Schema):
    allOf: List[SchemaType]

    def schemas_by_name(
        self, mapping: Optional[Dict[str, SchemaType]] = None, recursive: bool = True, include_self: bool = True
    ) -> Dict[str, SchemaType]:
        if mapping is None:
            mapping = {}

        for allOf in self.allOf:
            if allOf().name:
                if allOf().name in mapping:
                    continue
                mapping[allOf().name] = allOf()

            if recursive:
                mapping.update(allOf().schemas_by_name(mapping=mapping))

        if self.name and include_self:
            mapping[self.name] = self

        return mapping


class AnyOfSchema(Schema):
    anyOf: List[SchemaType]

    def schemas_by_name(
        self, mapping: Optional[Dict[str, SchemaType]] = None, recursive: bool = True, include_self: bool = True
    ) -> Dict[str, SchemaType]:
        if mapping is None:
            mapping = {}

        for anyOf in self.anyOf:
            if anyOf().name:
                if anyOf().name in mapping:
                    continue
                mapping[anyOf().name] = anyOf()
            if recursive:
                mapping.update(anyOf().schemas_by_name(mapping=mapping))

        if self.name and include_self:
            mapping[self.name] = self

        return mapping


class ArraySchema(Schema):
    items: SchemaType

    def schemas_by_name(
        self, mapping: Optional[Dict[str, SchemaType]] = None, recursive: bool = True, include_self: bool = True
    ) -> Dict[str, SchemaType]:
        if mapping is None:
            mapping = {}

        if isinstance(self.items, SchemaType):
            if self.items().name:
                if self.items().name in mapping:
                    return mapping
                mapping[self.items().name] = self.items()

            if recursive:
                mapping.update(self.items().schemas_by_name(mapping=mapping))

        if self.name and include_self:
            mapping[self.name] = self

        return mapping


class ObjectSchema(Schema):
    properties: Dict[str, SchemaType]

    def schemas_by_name(
        self, mapping: Optional[Dict[str, SchemaType]] = None, recursive: bool = True, include_self: bool = True
    ) -> Dict[str, SchemaType]:
        if mapping is None:
            mapping = {}

        for _, p in self.properties.items():
            if p().name:
                if p().name in mapping:
                    continue
                mapping[p().name] = p()

            if recursive:
                mapping.update(p().schemas_by_name(mapping=mapping))

        if self.name and include_self:
            mapping[self.name] = self

        return mapping


class SchemaRef(RefObject):
    _resolved_ref: Schema = None

    def __call__(self) -> Schema:
        return self._resolve_ref()

    def _resolve_ref(self) -> Schema:
        if self._resolved_ref is None:
            self._resolved_ref = getattr(self._root_openapi.get().components, self.ref_components_path).get(self.name)

        return self._resolved_ref


SchemaType: TypeAlias = Union[
    SchemaRef, ArraySchema, AnyOfSchema, AllOfSchema, EnumSchema, OneOfSchema, ObjectSchema, Schema
]

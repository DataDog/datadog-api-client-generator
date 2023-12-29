from __future__ import annotations
from typing import Dict, List, Optional

from pydantic import BaseModel
from datadog_api_client_generator.codegen.shared.templates_env import camel_case

from datadog_api_client_generator.openapi.operation_model import OperationObject, PathsItemObject
from datadog_api_client_generator.openapi.shared_model import ExternalDocs, Server
from datadog_api_client_generator.openapi.schema_model import ArraySchema, EnumSchema, ObjectSchema, OneOfSchema, Schema
from datadog_api_client_generator.openapi.parameter_model import Parameter


class OpenAPIContact(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    email: Optional[str] = None


class OpenAPIInfo(BaseModel):
    title: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    contact: Optional[OpenAPIContact] = None


class Components(BaseModel):
    schemas: Optional[Dict[str, Schema]] = None
    parameters: Optional[Dict[str, Parameter]] = None


class Tag(BaseModel):
    name: str
    description: Optional[str] = None


class OpenAPI(BaseModel):
    openapi: str
    info: OpenAPIInfo
    paths: Dict[str, PathsItemObject]
    components: Optional[Components] = None
    servers: Optional[List[Server]] = None
    tags: Optional[List[Tag]] = None
    externalDocs: Optional[ExternalDocs] = None
    security: Optional[List[Dict[str, List[str]]]] = None

    def child_models(self, schema: Schema, alternative_name: str = None, seen: Optional[bool] = None):
        seen = seen or set()
        name = schema.name or alternative_name
        schema_type = type(schema)

        if name in seen:
            return

        has_sub_models = False
        if schema_type == OneOfSchema:
            for child in schema.oneOf:
                sub_models = list(self.child_models(child, seen=seen))
                if sub_models:
                    has_sub_models = True
                    yield from sub_models
            if not has_sub_models:
                return

        if has_sub_models:
            seen.add(name)
            yield name, schema

        if schema_type == ArraySchema:
            yield from self.child_models(schema.items, seen=seen)

        if schema_type == ObjectSchema:
            if name is None:
                # this is a basic map object so we don't need a type
                return

            if schema.properties:
                seen.add(name)
                yield name, schema

            if schema.additionalProperties and name:
                seen.add(name)
                yield name, schema

            for key, child in schema.properties.items():
                yield from self.child_models(child, alternative_name=name + camel_case(key), seen=seen)

        if schema.name and schema_type == ArraySchema:
            seen.add(name)
            yield name, schema

        if schema_type == EnumSchema:
            if name is None:
                raise ValueError(f"Schema {schema} has no name")

            seen.add(name)
            yield name, schema

        if schema.additionalProperties:
            yield from self.child_models(
                schema.additionalProperties,
                alternative_name=name,
                seen=seen,
            )

    def models(self):
        name_to_schema = {}

        for path in self.paths:
            for k, v in self.paths[path]:
                if type(v) == OperationObject:
                    if v.parameters:
                        for content in v.parameters:
                            if content.schema:
                                name_to_schema.update(dict(self.child_models(content.schema)))

                    if v.requestBody:
                        for content in v.requestBody.content.values():
                            if content.schema:
                                name_to_schema.update(dict(self.child_models(content.schema)))
                    if v.responses:
                        for response in v.responses.values():
                            if response.content:
                                for content in response.content.values():
                                    if content.schema:
                                        name_to_schema.update(dict(self.child_models(content.schema)))

        return name_to_schema

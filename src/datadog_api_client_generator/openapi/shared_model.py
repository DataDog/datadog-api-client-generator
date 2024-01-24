from __future__ import annotations
from contextvars import ContextVar
from typing import TYPE_CHECKING, Any, Dict, List, Optional, TypeAlias, Union
from typing_extensions import Unpack

from pydantic import BaseModel, Field, model_validator

from datadog_api_client_generator.openapi.utils import Empty, OptionalEmpty, get_name_and_path_from_ref


if TYPE_CHECKING:
    from datadog_api_client_generator.openapi.openapi_model import OpenAPI
    from datadog_api_client_generator.openapi.parameter_model import Parameter
    from datadog_api_client_generator.openapi.schema_model import Schema


class _Base(BaseModel):
    extensions: Dict[str, Any] = dict()
    _root_openapi: Optional[ContextVar[OpenAPI]] = None

    @model_validator(mode="before")
    def _remap_extensions(cls, v: Any) -> Dict:
        if not isinstance(v, BaseModel) and callable(getattr(v, "keys")):
            # Remap extensions
            extensions = v.get("extensions", {})
            for k in list(v.keys()):
                if k.startswith("x-"):
                    extensions[k] = v[k]
                    del v[k]
            v["extensions"] = extensions

        return v

    @model_validator(mode="after")
    def _inject_ctx_after(self, v: Any) -> Dict:
        if v.context:
            self._root_openapi = v.context.get("openapi")

        return self

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self


class RefObject(_Base):
    ref: str = Field(alias="$ref")
    name: str
    ref_components_path: str
    _resolved_ref: Any = None

    @model_validator(mode="before")
    def _inject_ref_properties(cls, v: Any) -> Dict:
        if "$ref" in v:
            path, name = get_name_and_path_from_ref(v["$ref"])
            v["ref_components_path"] = path
            v["name"] = name
        return v

    def __call__(self) -> Any:
        return self._resolve_ref()

    def _resolve_ref(self) -> Any:
        if not self._resolved_ref:
            self._resolved_ref = getattr(self._root_openapi.get().components, self.ref_components_path).get(self.name)
        return self._resolved_ref

    def schemas_by_name(
        self, mapping: Optional[Dict[str, Any]] = None, recursive: bool = True, include_self: bool = True
    ) -> Dict[str, Any]:
        if mapping is None:
            mapping = {}

        if recursive:
            mapping.update(self().schemas_by_name(mapping=mapping))

        if self.name and include_self:
            mapping[self.name] = self

        return mapping


class ExternalDocs(_Base):
    url: str
    description: OptionalEmpty[str] = Empty()


class ServerVariable(_Base):
    default: str
    description: OptionalEmpty[str] = Empty()
    enum: Optional[List[str]] = list()


class Server(_Base):
    url: str
    description: OptionalEmpty[str] = Empty()
    variables: Optional[Dict[str, ServerVariable]] = dict()


class SecurityScheme(_Base):
    type: str
    name: str
    scheme: str
    in_: Optional[str] = Field(alias="in")
    description: OptionalEmpty[str] = Empty()
    bearerFormat: OptionalEmpty[str] = Empty()
    flows: OptionalEmpty[Dict] = Empty()
    openIdConnectUrl: OptionalEmpty[str] = Empty()


SecuritySchemeType: TypeAlias = Union[SecurityScheme, RefObject]

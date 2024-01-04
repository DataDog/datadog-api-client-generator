from __future__ import annotations
from contextvars import ContextVar
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pydantic import BaseModel, Field, model_validator

from datadog_api_client_generator.openapi.utils import get_name_and_path_from_ref


if TYPE_CHECKING:
    from datadog_api_client_generator.openapi.openapi_model import OpenAPI


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


class _RefObject(_Base):
    ref: str = Field(alias="$ref")
    name: str

    @model_validator(mode="before")
    def _inject_ref_properties(cls, v: Any) -> Dict:
        if "$ref" in v:
            path, name = get_name_and_path_from_ref(v["$ref"])
            v["_ref_path"] = path
            v["name"] = name
        return v


class ExternalDocs(_Base):
    url: str
    description: Optional[str] = None


class ServerVariable(_Base):
    default: str
    description: Optional[str] = None
    enum: Optional[List[str]] = list()


class Server(_Base):
    url: str
    description: Optional[str] = None
    variables: Optional[Dict[str, ServerVariable]] = dict()

from __future__ import annotations
from contextvars import ContextVar
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, model_validator


class _Base(BaseModel):
    extensions: Dict[str, Any] = dict()
    _root_openapi: Optional[ContextVar] = None

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

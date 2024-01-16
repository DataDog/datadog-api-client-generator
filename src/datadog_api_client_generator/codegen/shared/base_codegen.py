from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import PosixPath
from typing import Any, Dict, List, Optional

from jinja2 import Environment

from datadog_api_client_generator.codegen.shared.templates_env import build_default_jinja2_env
from datadog_api_client_generator.openapi.openapi_model import OpenAPI


@dataclass
class GeneratorConfig:
    additional_filters: Optional[Dict[str, Any]] = None
    additional_globals: Optional[Dict[str, Any]] = None


class BaseCodegen(ABC):
    generator_config: GeneratorConfig

    def __init__(self) -> None:
        self.env: Environment = build_default_jinja2_env()

        if self.generator_config.additional_filters:
            self.env.filters.update(self.generator_config.additional_filters)
        if self.generator_config.additional_globals:
            self.env.globals.update(self.generator_config.additional_globals)

    @abstractmethod
    def generate(self, specs: List[OpenAPI], output: PosixPath):
        ...

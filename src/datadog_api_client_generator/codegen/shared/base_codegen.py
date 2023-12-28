from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import PosixPath
from typing import Any, Dict, List, Set

from jinja2 import Environment

from datadog_api_client_generator.codegen.shared.templates_env import build_default_jinja2_env
from datadog_api_client_generator.openapi.openapi_model import OpenAPI


@dataclass
class GeneratorConfig:
    pass


class BaseCodegen(ABC):
    lanugage_config: GeneratorConfig

    def __init__(self, specs: List[OpenAPI], output: PosixPath) -> None:
        self.specs: List[OpenAPI] = specs
        self.output: PosixPath = output
        self.env: Environment = build_default_jinja2_env()

        self.env.filters.update(self.additional_filters())
        self.env.globals.update(self.additional_globals())

    @abstractmethod
    def generate(self):
        pass

    @abstractmethod
    def additional_filters(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def additional_globals(self) -> Dict[str, Any]:
        pass

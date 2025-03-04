# Unless explicitly stated otherwise all files in this repository are licensed under the Apache 2.0 License.
#
# This product includes software developed at Datadog (https://www.datadoghq.com/  Copyright 2025 Datadog, Inc.
from __future__ import annotations

from typing import TYPE_CHECKING

from datadog_api_client_generator.codegen.python import utils
from datadog_api_client_generator.codegen.shared.base_codegen import BaseCodegen, GeneratorConfig

if TYPE_CHECKING:
    from pathlib import PosixPath

    from datadog_api_client_generator.openapi.openapi_model import OpenAPI

PACKAGE_NAME = "datadog_api_client"


class PythonGenerator(BaseCodegen):
    generator_config = GeneratorConfig(
        additional_filters={
            "safe_snake_case": utils.safe_snake_case,
            "docstring": utils.docstring,
            "attribute_name": utils.attribute_name,
            "return_type": utils.return_type,
            "attribute_path": utils.attribute_path,
            "format_value": utils.format_value,
        },
        additional_globals={
            "package": PACKAGE_NAME,
            "get_type_for_parameter": utils.get_type_for_parameter,
            "get_type_at_path": utils.get_type_at_path,
            "get_default": utils.get_default,
            "get_references_for_model": utils.get_references_for_model,
            "get_oneof_references_for_model": utils.get_oneof_references_for_model,
            "get_types_for_attribute": utils.get_types_for_attribute,
            "get_typing_for_attribute": utils.get_typing_for_attribute,
            "get_type_for_attribute": utils.get_type_for_attribute,
            "type_to_python": utils.type_to_python,
            "get_enum_default": utils.get_enum_default,
            "get_oneof_models": utils.get_oneof_models,
            "get_oneof_parameters": utils.get_oneof_parameters,
            "get_oneof_types": utils.get_oneof_types,
            "basic_type_to_python": utils.basic_type_to_python,
        },
    )

    def generate(self, specs: list[OpenAPI], output: PosixPath) -> None:
        api_j2 = self.env.get_template("api.j2")
        apis_j2 = self.env.get_template("apis.j2")
        model_j2 = self.env.get_template("model.j2")
        models_j2 = self.env.get_template("models.j2")
        init_j2 = self.env.get_template("init.j2")
        configuration_j2 = self.env.get_template("configuration.j2")

        extra_files = {
            "api_client.py": self.env.get_template("api_client.j2"),
            "exceptions.py": self.env.get_template("exceptions.j2"),
            "model_utils.py": self.env.get_template("model_utils.j2"),
            "rest.py": self.env.get_template("rest.j2"),
        }

        top_package = output / PACKAGE_NAME
        top_package.mkdir(parents=True, exist_ok=True)

        for name, template in extra_files.items():
            filename = top_package / name
            with filename.open("w") as fp:
                fp.write(template.render())

        all_apis = {}
        for version, spec in specs.items():
            package = top_package / version
            package.mkdir(exist_ok=True)

            self.env.globals["openapi"] = spec
            self.env.globals["version"] = version
            utils.set_api_version(version)

            apis = spec.group_apis_by_tag()
            all_apis[version] = apis
            models = spec.schemas_by_name()
            utils.filter_models(models)
            tags_by_name = spec.tags_by_name()

            for name, model in models.items():
                filename = utils.safe_snake_case(name) + ".py"
                model_path = package / "model" / filename
                model_path.parent.mkdir(parents=True, exist_ok=True)
                with model_path.open("w") as fp:
                    fp.write(model_j2.render(name=name, model=model))

            model_init_path = package / "model" / "__init__.py"
            with model_init_path.open("w") as fp:
                fp.write("")

            models_path = package / "models" / "__init__.py"
            models_path.parent.mkdir(parents=True, exist_ok=True)
            with models_path.open("w") as fp:
                fp.write(models_j2.render(models=sorted(models)))

            for name, operations in apis.items():
                filename = utils.safe_snake_case(name) + "_api.py"
                api_path = package / "api" / filename
                api_path.parent.mkdir(parents=True, exist_ok=True)
                with api_path.open("w") as fp:
                    fp.write(
                        api_j2.render(name=name, operations=operations, description=tags_by_name[name].description)
                    )

            api_init_path = package / "api" / "__init__.py"
            with api_init_path.open("w") as fp:
                fp.write("")

            apis_path = package / "apis" / "__init__.py"
            apis_path.parent.mkdir(parents=True, exist_ok=True)
            with apis_path.open("w") as fp:
                fp.write(apis_j2.render(apis=sorted(apis)))

            init_path = package / "__init__.py"
            with init_path.open("w") as fp:
                fp.write(init_j2.render())

        filename = top_package / "configuration.py"
        with filename.open("w") as fp:
            fp.write(configuration_j2.render(specs=specs, apis=all_apis))

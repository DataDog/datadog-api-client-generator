from datadog_api_client_generator.codegen.python import utils
from datadog_api_client_generator.codegen.shared.base_codegen import BaseCodegen, GeneratorConfig


PACKAGE_NAME = "datadog_api_client"


class PythonGenerator(BaseCodegen):
    generator_config = GeneratorConfig(
        additional_filters={
            "safe_snake_case": utils.safe_snake_case,
            "docstring": utils.docstring,
            "attribute_name": utils.attribute_name,
            "return_type": utils.return_type,
            "attribute_path": utils.attribute_path,
        },
        additional_globals={
            "package": PACKAGE_NAME,
            "get_type_for_parameter": utils.get_type_for_parameter,
            "get_type_at_path": utils.get_type_at_path,
            "get_default": utils.get_default,
        },
    )

    def generate(self) -> None:
        api_j2 = self.env.get_template("api.j2")
        # apis_j2 = self.env.get_template("apis.j2")
        # model_j2 = self.env.get_template("model.j2")
        models_j2 = self.env.get_template("models.j2")
        # init_j2 = self.env.get_template("init.j2")
        # configuration_j2 = self.env.get_template("configuration.j2")

        # extra_files = {
        #     "api_client.py": self.env.get_template("api_client.j2"),
        #     "exceptions.py": self.env.get_template("exceptions.j2"),
        #     "model_utils.py": self.env.get_template("model_utils.j2"),
        #     "rest.py": self.env.get_template("rest.j2"),
        # }

        # for name, template in extra_files.items():
        #     filename = top_package / name
        #     with filename.open("w") as fp:
        #         fp.write(template.render())

        top_package = self.output / PACKAGE_NAME
        top_package.mkdir(parents=True, exist_ok=True)

        for version, spec in self.specs.items():
            self.env.globals["version"] = version
            utils.set_api_version(version)

            apis = spec.group_apis_by_tag()
            models = spec.schemas_by_name()

            package = top_package / version
            package.mkdir(exist_ok=True)

            tags_by_name = spec.tags_by_name()

            for name, operations in apis.items():
                filename = utils.safe_snake_case(name) + "_api.py"
                api_path = package / "api" / filename
                api_path.parent.mkdir(parents=True, exist_ok=True)
                with api_path.open("w") as fp:
                    fp.write(
                        api_j2.render(name=name, operations=operations, description=tags_by_name[name].description)
                    )

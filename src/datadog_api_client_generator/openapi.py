# Unless explicitly stated otherwise all files in this repository are licensed under the Apache 2.0 License.
#
# This product includes software developed at Datadog (https://www.datadoghq.com/  Copyright 2025 Datadog, Inc.
import pathlib

import yaml
from jsonref import JsonRef
from yaml import CSafeLoader


def load(filename):
    path = pathlib.Path(filename)
    with path.open() as fp:
        return JsonRef.replace_refs(yaml.load(fp, Loader=CSafeLoader))


def apis(spec):
    operations = {}

    for path, endpoints in spec["paths"].items():
        for method, operation in endpoints.items():
            tag = operation["tags"][0]
            operations.setdefault(tag, []).append((path, method, operation))

    return operations

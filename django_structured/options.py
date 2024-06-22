from collections import namedtuple
from dataclasses import dataclass, field
from functools import wraps

import click
from click_option_group import optgroup


@dataclass
class ProjectOptions:
    django: str = field(
        default="5",
        metadata={
            "help": "Django version to use",
            "choices": ["3", "4", "5"],
        },
    )

    # Dependency management
    poetry: bool = field(
        default=True,
        metadata={
            "help": "Genrate poetry configuration with pyproject.toml",
            "group": "Dependency management",
        },
    )
    pipenv: bool = field(
        default=False,
        metadata={
            "help": "Generate pipenv configuration with Pipfile",
            "group": "Dependency management",
        },
    )
    pip: bool = field(
        default=False,
        metadata={
            "help": "Generate requirements.txt",
            "group": "Dependency management",
        },
    )

    # Containerization
    docker: bool = field(
        default=True,
        metadata={
            "help": "Generate Dockerfile and docker-compose.yaml",
            "group": "Containerization",
        },
    )

    # Editors
    vscode: bool = field(
        default=True,
        metadata={
            "help": "Generate .vscode configuration",
            "group": "Editors",
        },
    )

    # Testing
    pytest: bool = field(
        default=True,
        metadata={
            "help": "Generate pytest configuration",
            "group": "Testing",
        },
    )


@dataclass
class AppOptions:
    migrations: bool = field(
        default=True,
        metadata={"help": "Generate migrations for the app"},
    )


def click_options(options_dataclass):
    groups = {}
    decorators = []

    for field in options_dataclass.__dataclass_fields__.values():
        option_kwargs = {
            "default": field.default,
            "show_default": True,
            "type": field.type,
        }

        if field.type == bool:
            option_arg = f"--{field.name} / --no-{field.name}"
        else:
            option_arg = f"--{field.name}"

        if "choices" in field.metadata:
            option_kwargs["type"] = click.Choice(
                field.metadata["choices"],
            )
        else:
            option_kwargs["type"] = field.type

        if "help" in field.metadata:
            option_kwargs["help"] = field.metadata["help"]

        if "group" in field.metadata:
            group_name = field.metadata["group"]
            if group_name not in groups:
                group = groups.setdefault(group_name, [optgroup.group(group_name)])
                decorators.append(group)
            else:
                group = groups[group_name]
            group.append(optgroup.option(option_arg, **option_kwargs))
        else:
            decorators.append(click.option(option_arg, **option_kwargs))

    def _click_options(fn):
        for decorator in reversed(decorators):
            if isinstance(decorator, list):
                for group_decorator in reversed(decorator):
                    fn = group_decorator(fn)
            else:
                fn = decorator(fn)

        return fn

    return _click_options

import inspect
from collections.abc import Callable
from typing import Any, TypedDict, cast, get_type_hints

from pydantic import BaseModel, create_model

from llm_gamebook.schema.validators import is_normalized_snake_case
from llm_gamebook.story.entity import BaseStoryEntity, EntityProperty

TraitRegistryEntry = TypedDict(
    "TraitRegistryEntry",
    {
        # Trait class
        "class": type,
        # Trait parameters model
        "param_model": type[BaseModel] | None,
        # Instance props model
        "props_model": type[BaseModel] | None,
    },
)


trait_registry: dict[str, TraitRegistryEntry] = {}
"""Maps trait ID to entry."""


def model_from_constructor_annotations(cls: type) -> type[BaseModel] | None:
    """Constructs a model from class constructor arguments."""
    init = cls.__dict__.get("__init__", None)
    if init is object.__init__:
        return None  # no custom constructor

    args: dict[str, tuple[str, Any]] = {}
    for name, param in inspect.signature(init).parameters.items():
        if name == "self" or param.kind in {param.VAR_POSITIONAL, param.VAR_KEYWORD}:
            # skip `self`, `*args` and `**kwargs`
            continue
        default = param.default if param.default is not param.empty else ...
        args[name] = get_type_hints(init)[name], default

    field_definitions = cast("dict[str, Any]", args)
    return create_model(f"{cls.__name__}PropsModel", **field_definitions)


def trait(name: str, params_model: type[BaseModel] | None = None) -> Callable[[type], type]:
    """Class decorator that registers story entity traits."""

    if not is_normalized_snake_case(name):
        msg = f"Trait name must be normalized snake_case {name}"
        raise ValueError(msg)

    def wrapper(cls: type) -> type:
        # Register trait
        trait_registry[name] = {
            "class": cls,
            "param_model": params_model,
            "props_model": model_from_constructor_annotations(cls),
        }

        return cls

    return wrapper

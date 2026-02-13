import pytest
from pydantic import BaseModel

from llm_gamebook.story.entity import BaseEntity
from llm_gamebook.story.trait_registry import TraitRegistryEntry, trait_registry


class DummyOptions(BaseModel):
    value: str


@trait_registry.register("test_trait")
class DummyTrait(BaseEntity):
    pass


@trait_registry.register("test_trait_with_options", options_model=DummyOptions)
class DummyTraitWithOptions(BaseEntity):
    pass


def test_trait_registry_register() -> None:
    """Test registering a trait without options."""
    entry = trait_registry["test_trait"]

    assert isinstance(entry, TraitRegistryEntry)
    assert entry.cls is DummyTrait
    assert entry.options_model is None


def test_trait_registry_register_with_options() -> None:
    """Test registering a trait with options model."""
    entry = trait_registry["test_trait_with_options"]

    assert isinstance(entry, TraitRegistryEntry)
    assert entry.cls is DummyTraitWithOptions
    assert entry.options_model is DummyOptions


def test_trait_registry_register_invalid_name() -> None:
    """Test that invalid trait names raise ValueError."""
    with pytest.raises(ValueError, match="Invalid normalized snake_case format"):
        trait_registry.register("InvalidName")

    with pytest.raises(ValueError, match="Invalid normalized snake_case format"):
        trait_registry.register("invalid-name")

    with pytest.raises(ValueError, match="Invalid normalized snake_case format"):
        trait_registry.register("Invalid_Name")


def test_trait_registry_getitem_missing() -> None:
    """Test that KeyError is raised for missing trait."""
    with pytest.raises(KeyError):
        trait_registry["nonexistent_trait"]


def test_trait_registry_iter() -> None:
    """Test iterating over registry."""
    keys = list(trait_registry)

    assert "test_trait" in keys
    assert "test_trait_with_options" in keys


def test_trait_registry_len() -> None:
    """Test getting registry length."""
    assert len(trait_registry) >= 2

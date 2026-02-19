import pytest
from pydantic import BaseModel

from llm_gamebook.story.actions import Action
from llm_gamebook.story.entity import BaseEntity
from llm_gamebook.story.session_state import SessionState
from llm_gamebook.story.store import Store
from llm_gamebook.story.trait_registry import TraitRegistryEntry, reducer, trait_registry
from llm_gamebook.story.traits.graph import GraphTransitionPayload


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


def test_trait_registry_reducer_decorator() -> None:
    @trait_registry.register("test")
    class TestTrait(BaseEntity):
        @staticmethod
        @reducer("test/action")
        def graph_transition_reducer(
            state: SessionState, action: Action[BaseModel]
        ) -> SessionState:
            return state

    all_reducers = trait_registry.get_all_reducers()
    assert "test/action" in all_reducers


def test_trait_registry_reducer_decorator_fails_with_non_staticmethod() -> None:
    with pytest.raises(TypeError, match="is not a staticmethod"):

        @trait_registry.register("test")
        class TestTrait(BaseEntity):
            @reducer("test/action")
            def graph_transition_reducer(
                self, state: SessionState, action: Action[BaseModel]
            ) -> SessionState:
                return state


def test_trait_registry_register_with_reducers() -> None:
    entry = trait_registry["graph"]
    assert entry.reducers is not None
    assert "graph/transition" in entry.reducers


def test_trait_registry_get_all_reducers() -> None:
    all_reducers = trait_registry.get_all_reducers()
    assert "graph/transition" in all_reducers


def test_store_load_trait_reducers() -> None:
    store = Store()
    action = Action[GraphTransitionPayload](
        name="graph/transition",
        payload=GraphTransitionPayload(entity_id="test_entity", to="new_node"),
    )
    new_state = store.dispatch(action)

    assert new_state.get_field("test_entity", "current_node_id") == "new_node"

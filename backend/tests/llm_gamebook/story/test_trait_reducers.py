from llm_gamebook.story.actions import Action
from llm_gamebook.story.store import Store
from llm_gamebook.story.trait_registry import trait_registry
from llm_gamebook.story.traits.graph import GraphTransitionPayload


def test_trait_registry_register_with_reducers() -> None:
    entry = trait_registry["graph"]
    assert entry.reducers is not None
    assert "graph/transition" in entry.reducers


def test_trait_registry_get_all_reducers() -> None:
    all_reducers = trait_registry.get_all_reducers()
    assert "graph/transition" in all_reducers


def test_store_load_trait_reducers() -> None:
    store = Store(load_trait_reducers=True)
    action = Action[GraphTransitionPayload](
        name="graph/transition",
        payload=GraphTransitionPayload(entity_id="test_entity", to="new_node"),
    )
    new_state = store.dispatch(action)

    assert new_state.get_field("test_entity", "current_node_id") == "new_node"

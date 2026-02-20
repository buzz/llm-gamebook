from llm_gamebook.story.errors import (
    EntityFieldNotFoundError,
    EntityNotFoundError,
    EntityTypeNotFoundError,
    ProjectError,
    ProjectExistsError,
    ProjectNotFoundError,
    StateAccessError,
    TraitNotFoundError,
)


def test_project_error_is_exception() -> None:
    assert issubclass(ProjectError, Exception)


def test_project_not_found_error_inherits_from_project_error() -> None:
    assert issubclass(ProjectNotFoundError, ProjectError)


def test_project_exists_error_inherits_from_project_error() -> None:
    assert issubclass(ProjectExistsError, ProjectError)


def test_project_not_found_error_message() -> None:
    error = ProjectNotFoundError("my_project")
    assert "my_project" in str(error)


def test_project_exists_error_message() -> None:
    error = ProjectExistsError("existing_project")
    assert "existing_project" in str(error)


def test_state_access_error_is_exception() -> None:
    assert issubclass(StateAccessError, Exception)


def test_entity_type_not_found_error_inherits_from_state_access_error() -> None:
    assert issubclass(EntityTypeNotFoundError, StateAccessError)


def test_trait_not_found_error_inherits_from_state_access_error() -> None:
    assert issubclass(TraitNotFoundError, StateAccessError)


def test_entity_not_found_error_inherits_from_state_access_error() -> None:
    assert issubclass(EntityNotFoundError, StateAccessError)


def test_entity_field_not_found_error_inherits_from_state_access_error() -> None:
    assert issubclass(EntityFieldNotFoundError, StateAccessError)

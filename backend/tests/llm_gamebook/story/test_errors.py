from llm_gamebook.story.errors import (
    DynamicFieldEvalError,
    DynamicFieldReadOnlyError,
    EntityFieldNotFoundError,
    EntityNotFoundError,
    EntityTypeNotFoundError,
    ExpressionEvalError,
    ProjectError,
    ProjectExistsError,
    ProjectNotFoundError,
    StateAccessError,
    TraitNotFoundError,
)


def test_expression_eval_error_is_exception() -> None:
    assert issubclass(ExpressionEvalError, Exception)


def test_dynamic_field_eval_error_inherits_from_expression_eval_error() -> None:
    assert issubclass(DynamicFieldEvalError, ExpressionEvalError)


def test_dynamic_field_eval_error_with_field_and_source() -> None:
    error = DynamicFieldEvalError("bad operand", field="player.health", source="=player.a * 2")
    assert error.field == "player.health"
    assert error.source == "=player.a * 2"
    message = str(error)
    assert "player.health" in message
    assert "=player.a * 2" in message
    assert "bad operand" in message


def test_dynamic_field_eval_error_without_field() -> None:
    error = DynamicFieldEvalError("Maximum expression evaluation depth (32) exceeded")
    assert error.field is None
    assert error.source is None
    assert str(error) == "Maximum expression evaluation depth (32) exceeded"


def test_dynamic_field_read_only_error_is_exception() -> None:
    assert issubclass(DynamicFieldReadOnlyError, Exception)


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

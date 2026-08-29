class ProjectError(Exception):
    pass


class ProjectNotFoundError(ProjectError):
    """Raised when a project could not be found."""


class ProjectExistsError(ProjectError):
    """Raised when a project already exists."""


class StateAccessError(Exception):
    """Raised when an unknown state was accessed."""


class EntityTypeNotFoundError(StateAccessError):
    """Raised when an unknown entity type was accessed."""


class TraitNotFoundError(StateAccessError):
    """Raised when an unknown trait was accessed."""


class EntityNotFoundError(StateAccessError):
    """Raised when an unknown entity was accessed."""


class EntityFieldNotFoundError(StateAccessError):
    """Raised when an unknown entity field was accessed."""


class ExpressionEvalError(Exception):
    """Raised when evaluation of an expression failed."""


class DynamicFieldEvalError(ExpressionEvalError):
    """Raised when evaluation of a dynamic field's expression failed.

    Attributes:
        field: The `entity_id.field_name` of the dynamic field, if known.
        source: The expression source string of the dynamic field, if known.
    """

    def __init__(self, message: str, field: str | None = None, source: str | None = None) -> None:
        self.field = field
        self.source = source
        if field is not None:
            expression = f" (expression: {source})" if source is not None else ""
            message = f"Failed to evaluate dynamic field '{field}'{expression}: {message}"
        super().__init__(message)


class DynamicFieldReadOnlyError(Exception):
    """Raised when a read-only dynamic field is written."""


class CoreActionError(Exception):
    """Raised when a core action cannot be executed."""


class InvalidStepError(CoreActionError):
    """Raised when a core action targets an invalid history step."""


class NoStateError(CoreActionError):
    """Raised when a core action requires a state snapshot but none exists."""


class SessionEndedError(Exception):
    """Raised when an operation is attempted on an ended session."""

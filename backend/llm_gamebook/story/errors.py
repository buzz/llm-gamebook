class StateAccessError(Exception):
    """Raised when an unknown state was accessed."""


class EntityTypeNotFoundError(StateAccessError):
    """Raised when an unknown entity type was accessed."""


class TraitNotFoundError(StateAccessError):
    """Raised when an unknown trait was accessed."""


class EntityNotFoundError(StateAccessError):
    """Raised when an unknown entity was accessed."""

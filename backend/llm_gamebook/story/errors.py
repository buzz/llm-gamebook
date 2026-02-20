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

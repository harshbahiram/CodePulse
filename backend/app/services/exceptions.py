class RepositoryServiceError(Exception):
    """Base exception for repository service errors."""

    pass


class PrivateRepositoryError(RepositoryServiceError):
    """Raised when a private repository is submitted."""

    pass


class InvalidRepositoryDataError(RepositoryServiceError):
    """Raised when repository data is invalid or incomplete."""

    pass


class BranchNotFoundError(RepositoryServiceError):
    """Raised when the requested branch does not exist."""

    pass


class InvalidBranchNameError(RepositoryServiceError):
    """Raised when a branch name is invalid."""

    pass


class InvalidRepositoryTreeError(RepositoryServiceError):
    """Raised when repository tree data is invalid."""

    pass
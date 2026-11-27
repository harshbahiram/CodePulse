class RepositoryServiceError(Exception):
    """Base exception for repository service errors."""

    pass


class PrivateRepositoryError(RepositoryServiceError):
    """Raised when a private repository is submitted."""

    pass


class InvalidRepositoryDataError(RepositoryServiceError):
    """Raised when repository data is invalid or incomplete."""

    pass
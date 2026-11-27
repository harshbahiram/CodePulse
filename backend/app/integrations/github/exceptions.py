class GitHubAPIError(Exception):
    """Base exception for GitHub API errors."""

    pass


class GitHubAuthenticationError(GitHubAPIError):
    """Raised when GitHub authentication fails."""

    pass


class GitHubRateLimitError(GitHubAPIError):
    """Raised when GitHub API rate limit is exceeded."""

    pass


class GitHubNotFoundError(GitHubAPIError):
    """Raised when a GitHub resource cannot be found."""

    pass


class GitHubPermissionError(GitHubAPIError):
    """Raised when access to a resource is forbidden."""

    pass


class GitHubConnectionError(GitHubAPIError):
    """Raised when GitHub cannot be reached."""

    pass        
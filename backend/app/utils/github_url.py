import re

from dataclasses import dataclass
from urllib.parse import urlsplit


OWNER_PATTERN = re.compile(
    r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*"
)

REPOSITORY_PATTERN = re.compile(
    r"[A-Za-z0-9_.-]+"
)


class InvalidGitHubURLError(ValueError):
    """Raised when a GitHub repository URL is invalid."""

    pass


@dataclass(frozen=True)
class GitHubRepositoryURL:
    owner: str
    repository: str

    @property
    def full_name(self) -> str:
        return f"{self.owner}/{self.repository}"

    @property
    def normalized_url(self) -> str:
        return f"https://github.com/{self.full_name}"


def parse_github_url(url: str) -> GitHubRepositoryURL:

    url = url.strip()

    if not url or any(
        char.isspace() or ord(char) < 32
        for char in url
    ):
        raise InvalidGitHubURLError(
            "Invalid characters in repository URL"
        )

    if "\\" in url or "?" in url or "#" in url:
        raise InvalidGitHubURLError(
            "Unsupported characters in repository URL"
        )

    try:
        parsed = urlsplit(url)

        if parsed.scheme != "https":
            raise InvalidGitHubURLError(
                "Repository URL must use HTTPS"
            )

        if parsed.netloc.lower() != "github.com":
            raise InvalidGitHubURLError(
                "Only github.com repository URLs are supported"
            )

    except ValueError as exc:
        raise InvalidGitHubURLError(
            "Invalid or unsupported GitHub URL"
        ) from exc

    path = parsed.path.removesuffix("/")

    parts = path.split("/")

    if len(parts) != 3 or parts[0] != "":
        raise InvalidGitHubURLError(
            "URL must contain a repository owner and name"
        )

    owner = parts[1]
    repository = parts[2].removesuffix(".git")

    if (
        len(owner) > 39
        or not OWNER_PATTERN.fullmatch(owner)
    ):
        raise InvalidGitHubURLError(
            "Invalid GitHub repository owner"
        )

    if (
        len(repository) > 100
        or repository in (".", "..")
        or not REPOSITORY_PATTERN.fullmatch(repository)
    ):
        raise InvalidGitHubURLError(
            "Invalid GitHub repository name"
        )

    return GitHubRepositoryURL(
        owner=owner,
        repository=repository
    )
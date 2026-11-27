from typing import Any

from app.integrations.github.client import GitHubClient
from app.utils.github_url import (GitHubRepositoryURL, parse_github_url)
from app.services.exceptions import (PrivateRepositoryError, InvalidRepositoryDataError)


class RepositoryService:

    def __init__(self, github_client: GitHubClient):
        self.github_client = github_client

    def parse_repository_url(self, repository_url: str) -> GitHubRepositoryURL:
        return parse_github_url(repository_url)

    def get_raw_repository(self, repository_url: str) -> dict[str, Any]:
        repository = self.parse_repository_url(repository_url)

        endpoint = (
            f"/repos/{repository.owner}/"
            f"{repository.repository}"
        )

        data = self.github_client.get(endpoint)

        if not isinstance(data, dict):
            raise InvalidRepositoryDataError(
                "GitHub returned invalid repository data"
            )

        if data.get("private") is True:
            raise PrivateRepositoryError(
                "Private repositories are not supported"
            )

        if data.get("private") is not False:
            raise InvalidRepositoryDataError(
                "Repository visibility could not be verified"
            )

        return data
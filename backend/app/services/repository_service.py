from typing import Any
from pydantic import ValidationError

from app.integrations.github.client import GitHubClient
from app.utils.github_url import (GitHubRepositoryURL, parse_github_url)
from app.services.exceptions import (PrivateRepositoryError, InvalidRepositoryDataError)
from app.schemas.repository import (RepositoryMetadata, RepositoryLanguages, RepositoryResponse)


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

    def get_repository_metadata(self, repository_url: str) -> RepositoryMetadata:
        data = self.get_raw_repository(repository_url)
        try:
            return RepositoryMetadata.model_validate(data)
        except ValidationError as exc:
            raise InvalidRepositoryDataError(
                "GitHub returned invalid repository metadata"
            ) from exc

    def _get_repository_languages(
    self,
    repository: RepositoryMetadata
    ) -> RepositoryLanguages:

        endpoint = (
            f"/repos/{repository.owner.login}/"
            f"{repository.name}/languages"
        )

        data = self.github_client.get(endpoint)

        if not isinstance(data, dict):
            raise InvalidRepositoryDataError(
                "GitHub returned invalid language data"
            )

        if any(
            not isinstance(language, str)
            or not language.strip()
            or type(byte_count) is not int
            or byte_count < 0
            for language, byte_count in data.items()
        ):
            raise InvalidRepositoryDataError(
                "Invalid programming language byte counts"
            )

        try:
            return RepositoryLanguages(
                languages=data,
                total_bytes=sum(data.values())
            )

        except ValidationError as exc:
            raise InvalidRepositoryDataError(
                "Unable to validate repository languages"
            ) from exc

    def get_repository_details(
    self,
    repository_url: str
    ) -> RepositoryResponse:

        metadata = self.get_repository_metadata(
            repository_url
        )

        languages = self._get_repository_languages(
            metadata
        )

        return RepositoryResponse(
            repository=metadata,
            languages=languages
        )
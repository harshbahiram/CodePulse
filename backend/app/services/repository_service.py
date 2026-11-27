from typing import Any
from pydantic import ValidationError
from urllib.parse import quote

from app.integrations.github.client import GitHubClient
from app.utils.github_url import (GitHubRepositoryURL, parse_github_url)
from app.services.exceptions import (PrivateRepositoryError, InvalidRepositoryDataError, BranchNotFoundError, InvalidBranchNameError)
from app.schemas.repository import (
    RepositoryMetadata, 
    RepositoryLanguages, 
    RepositoryResponse, 
    RepositoryBranch, 
    RepositoryBranches, 
    RepositoryCommit, 
    RepositorySnapshot
)
from app.integrations.github.exceptions import (GitHubNotFoundError)

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

    def _map_branch(
        self,
        data: dict
    ) -> RepositoryBranch:

        try:
            return RepositoryBranch(
                name=data["name"],
                commit_sha=data["commit"]["sha"],
                protected=data["protected"]
            )

        except (
            KeyError,
            TypeError,
            ValidationError
        ) as exc:

            raise InvalidRepositoryDataError(
                "GitHub returned invalid branch data"
            ) from exc

    def get_repository_branches(
        self,
        repository_url: str
    ) -> RepositoryBranches:

        repository = self.get_repository_metadata(
            repository_url
        )

        endpoint = (
            f"/repos/{repository.owner.login}/"
            f"{repository.name}/branches"
        )

        branches = []

        per_page = 100
        max_pages = 10

        for page in range(1, max_pages + 1):

            data = self.github_client.get(
                endpoint,
                params={
                    "per_page": per_page,
                    "page": page
                }
            )

            if not isinstance(data, list):
                raise InvalidRepositoryDataError(
                    "GitHub returned invalid branches data"
                )

            for item in data:
                branches.append(
                    self._map_branch(item)
                )

            if len(data) < per_page:

                return RepositoryBranches(
                    branches=branches,
                    total_branches=len(branches),
                    truncated=False
                )

        return RepositoryBranches(
            branches=branches,
            total_branches=len(branches),
            truncated=True
        )

    def _get_repository_branch(
        self,
        repository: RepositoryMetadata,
        branch: str | None = None
    ) -> RepositoryBranch:

        branch_name = (
            branch
            if branch is not None
            else repository.default_branch
        )

        if (
            not branch_name
            or len(branch_name) > 255
            or branch_name in (".", "..")
            or any(
                char.isspace() or ord(char) < 32
                for char in branch_name
            )
        ):
            raise InvalidBranchNameError(
                "Invalid repository branch name"
            )

        encoded_branch = quote(branch_name, safe="")

        endpoint = (
            f"/repos/{repository.owner.login}/"
            f"{repository.name}/branches/"
            f"{encoded_branch}"
        )

        try:
            data = self.github_client.get(endpoint)

        except GitHubNotFoundError as exc:

            raise BranchNotFoundError(
                f"Branch '{branch_name}' was not found"
            ) from exc

        return self._map_branch(data)

    def _get_repository_commit(
        self,
        repository: RepositoryMetadata,
        branch: RepositoryBranch
    ) -> RepositoryCommit:

        endpoint = (
            f"/repos/{repository.owner.login}/"
            f"{repository.name}/commits/"
            f"{branch.commit_sha}"
        )

        data = self.github_client.get(endpoint)

        try:
            commit_data = data["commit"]

            author = commit_data.get("author") or {}
            committer = commit_data.get("committer") or {}

            return RepositoryCommit(
                sha=data["sha"],
                message=commit_data["message"],
                author_name=author.get("name"),
                author_email=author.get("email"),
                committed_at=committer.get("date"),
                html_url=data["html_url"]
            )

        except (
            KeyError,
            TypeError,
            AttributeError,
            ValidationError
        ) as exc:

            raise InvalidRepositoryDataError(
                "GitHub returned invalid commit data"
            ) from exc

    def get_repository_snapshot(
        self,
        repository_url: str,
        branch: str | None = None
    ) -> RepositorySnapshot:

        repository = self.get_repository_metadata(
            repository_url
        )

        selected_branch = self._get_repository_branch(
            repository,
            branch
        )

        commit = self._get_repository_commit(
            repository,
            selected_branch
        )

        try:
            return RepositorySnapshot(
                repository=repository,
                branch=selected_branch,
                commit=commit
            )

        except ValidationError as exc:

            raise InvalidRepositoryDataError(
                "Repository snapshot validation failed"
            ) from exc
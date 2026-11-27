from unittest.mock import Mock
import pytest

from app.integrations.github.client import GitHubClient
from app.integrations.github.exceptions import (GitHubNotFoundError)
from app.services.repository_service import (RepositoryService)
from app.services.exceptions import (PrivateRepositoryError,InvalidRepositoryDataError)
from app.utils.github_url import InvalidGitHubURLError


@pytest.fixture
def github_client():
    return Mock(spec=GitHubClient)


@pytest.fixture
def repository_service(github_client):
    return RepositoryService(github_client)


def test_parse_repository_url(repository_service):

    result = repository_service.parse_repository_url(
        "https://github.com/fastapi/fastapi.git"
    )

    assert result.owner == "fastapi"
    assert result.repository == "fastapi"


def test_get_public_repository(repository_service, github_client):

    github_client.get.return_value = {
        "id": 123,
        "name": "fastapi",
        "full_name": "fastapi/fastapi",
        "private": False
    }

    result = repository_service.get_raw_repository(
        "https://github.com/fastapi/fastapi"
    )

    assert result["full_name"] == "fastapi/fastapi"
    assert result["private"] is False

    github_client.get.assert_called_once_with(
        "/repos/fastapi/fastapi"
    )


def test_reject_private_repository(
    repository_service,
    github_client
):

    github_client.get.return_value = {
        "name": "private-repo",
        "private": True
    }

    with pytest.raises(PrivateRepositoryError):

        repository_service.get_raw_repository(
            "https://github.com/user/private-repo"
        )


@pytest.mark.parametrize(
    "invalid_data",
    [
        None,
        [],
        "invalid-response",
        123,
        {},
        {"private": None},
        {"private": "false"}
    ]
)
def test_invalid_repository_data(
    repository_service,
    github_client,
    invalid_data
):

    github_client.get.return_value = invalid_data

    with pytest.raises(InvalidRepositoryDataError):

        repository_service.get_raw_repository(
            "https://github.com/user/repo"
        )


def test_invalid_repository_url(
    repository_service,
    github_client
):

    with pytest.raises(InvalidGitHubURLError):

        repository_service.get_raw_repository(
            "https://example.com/user/repo"
        )

    github_client.get.assert_not_called()


def test_repository_not_found(
    repository_service,
    github_client
):

    github_client.get.side_effect = GitHubNotFoundError(
        "Repository not found"
    )

    with pytest.raises(GitHubNotFoundError):

        repository_service.get_raw_repository(
            "https://github.com/user/nonexistent-repo"
        )
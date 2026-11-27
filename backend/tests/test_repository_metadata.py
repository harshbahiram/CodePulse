from unittest.mock import Mock

import pytest

from app.integrations.github.client import GitHubClient
from app.services.repository_service import RepositoryService
from app.services.exceptions import InvalidRepositoryDataError

from app.schemas.repository import (
    RepositoryMetadata,
    RepositoryResponse
)


REPOSITORY_URL = "https://github.com/test/demo"


@pytest.fixture
def github_client():
    return Mock(spec=GitHubClient)


@pytest.fixture
def repository_service(github_client):
    return RepositoryService(github_client)


@pytest.fixture
def repository_data():
    return {
        "id": 12345,
        "name": "demo",
        "full_name": "test/demo",
        "description": "Demo repository",

        "owner": {
            "login": "test",
            "avatar_url": "https://github.com/test.png",
            "html_url": "https://github.com/test",
            "type": "User"
        },

        "html_url": REPOSITORY_URL,
        "clone_url": f"{REPOSITORY_URL}.git",

        "private": False,
        "fork": False,
        "archived": False,

        "default_branch": "main",
        "language": "Python",

        "size": 1024,
        "stargazers_count": 100,
        "forks_count": 20,
        "open_issues_count": 5,

        "created_at": "2025-01-01T10:00:00Z",
        "updated_at": "2025-02-01T10:00:00Z",
        "pushed_at": "2025-02-01T10:00:00Z"
    }


def test_repository_metadata(
    repository_service,
    github_client,
    repository_data
):

    github_client.get.return_value = repository_data

    result = repository_service.get_repository_metadata(
        REPOSITORY_URL
    )

    assert isinstance(result, RepositoryMetadata)
    assert result.full_name == "test/demo"
    assert result.language == "Python"
    assert result.owner.login == "test"


def test_invalid_metadata(
    repository_service,
    github_client,
    repository_data
):

    del repository_data["id"]

    github_client.get.return_value = repository_data

    with pytest.raises(InvalidRepositoryDataError):
        repository_service.get_repository_metadata(
            REPOSITORY_URL
        )


def test_repository_details(
    repository_service,
    github_client,
    repository_data
):

    github_client.get.side_effect = [
        repository_data,
        {
            "Python": 8000,
            "JavaScript": 2000
        }
    ]

    result = repository_service.get_repository_details(
        REPOSITORY_URL
    )

    assert isinstance(result, RepositoryResponse)
    assert result.repository.full_name == "test/demo"
    assert result.languages.total_bytes == 10000
    assert result.languages.languages["Python"] == 8000

    assert github_client.get.call_count == 2

    github_client.get.assert_any_call(
        "/repos/test/demo"
    )

    github_client.get.assert_any_call(
        "/repos/test/demo/languages"
    )


def test_empty_repository_languages(
    repository_service,
    github_client,
    repository_data
):

    github_client.get.side_effect = [
        repository_data,
        {}
    ]

    result = repository_service.get_repository_details(
        REPOSITORY_URL
    )

    assert result.languages.languages == {}
    assert result.languages.total_bytes == 0


@pytest.mark.parametrize(
    "invalid_languages",
    [
        None,
        [],
        "invalid-response",
        {"Python": -100},
        {"Python": "1000"},
        {"Python": True},
        {"Python": 10.5},
        {"": 100}
    ]
)
def test_invalid_language_data(
    repository_service,
    github_client,
    repository_data,
    invalid_languages
):

    github_client.get.side_effect = [
        repository_data,
        invalid_languages
    ]

    with pytest.raises(InvalidRepositoryDataError):
        repository_service.get_repository_details(
            REPOSITORY_URL
        )
from unittest.mock import Mock, call

import pytest

from app.integrations.github.client import GitHubClient

from app.integrations.github.exceptions import (
    GitHubNotFoundError
)

from app.services.repository_service import RepositoryService

from app.services.exceptions import (
    BranchNotFoundError,
    InvalidBranchNameError,
    InvalidRepositoryDataError
)

from app.schemas.repository import RepositoryMetadata


REPOSITORY_URL = "https://github.com/test/demo"

COMMIT_SHA = "a" * 40


@pytest.fixture
def github_client():
    return Mock(spec=GitHubClient)


@pytest.fixture
def repository_metadata():

    return RepositoryMetadata(
        id=123,
        name="demo",
        full_name="test/demo",
        description="Test repository",

        owner={
            "login": "test",
            "avatar_url": "https://github.com/test.png",
            "html_url": "https://github.com/test",
            "type": "User"
        },

        html_url=REPOSITORY_URL,
        clone_url=f"{REPOSITORY_URL}.git",

        private=False,
        fork=False,
        archived=False,

        default_branch="main",
        language="Python",

        size=100,
        stargazers_count=10,
        forks_count=2,
        open_issues_count=1,

        created_at="2025-01-01T10:00:00Z",
        updated_at="2025-01-01T10:00:00Z"
    )


@pytest.fixture
def repository_service(
    github_client,
    repository_metadata
):

    service = RepositoryService(github_client)

    service.get_repository_metadata = Mock(
        return_value=repository_metadata
    )

    return service


@pytest.fixture
def branch_data():

    return {
        "name": "main",
        "commit": {
            "sha": COMMIT_SHA
        },
        "protected": False
    }


@pytest.fixture
def commit_data():

    return {
        "sha": COMMIT_SHA,

        "commit": {
            "message": "Initial commit",

            "author": {
                "name": "Developer",
                "email": "developer@example.com"
            },

            "committer": {
                "date": "2025-01-01T10:00:00Z"
            }
        },

        "html_url": (
            f"{REPOSITORY_URL}/commit/{COMMIT_SHA}"
        )
    }


def test_get_repository_branches(
    repository_service,
    github_client,
    branch_data
):

    github_client.get.return_value = [branch_data]

    result = repository_service.get_repository_branches(
        REPOSITORY_URL
    )

    assert result.total_branches == 1
    assert result.branches[0].name == "main"
    assert result.truncated is False


def test_branch_pagination(
    repository_service,
    github_client,
    branch_data
):

    first_page = [
        {**branch_data, "name": f"branch-{i}"}
        for i in range(100)
    ]

    second_page = [branch_data]

    github_client.get.side_effect = [
        first_page,
        second_page
    ]

    result = repository_service.get_repository_branches(
        REPOSITORY_URL
    )

    assert result.total_branches == 101
    assert result.truncated is False

    assert github_client.get.call_args_list == [
        call(
            "/repos/test/demo/branches",
            params={"per_page": 100, "page": 1}
        ),
        call(
            "/repos/test/demo/branches",
            params={"per_page": 100, "page": 2}
        )
    ]


def test_branch_pagination_limit(
    repository_service,
    github_client,
    branch_data
):

    github_client.get.side_effect = [
        [
            {**branch_data, "name": f"branch-{p}-{i}"}
            for i in range(100)
        ]
        for p in range(10)
    ]

    result = repository_service.get_repository_branches(
        REPOSITORY_URL
    )

    assert result.total_branches == 1000
    assert result.truncated is True
    assert github_client.get.call_count == 10


def test_default_branch_snapshot(
    repository_service,
    github_client,
    branch_data,
    commit_data
):

    github_client.get.side_effect = [
        branch_data,
        commit_data
    ]

    result = repository_service.get_repository_snapshot(
        REPOSITORY_URL
    )

    assert result.branch.name == "main"
    assert result.commit.sha == COMMIT_SHA

    github_client.get.assert_any_call(
        "/repos/test/demo/branches/main"
    )

    github_client.get.assert_any_call(
        f"/repos/test/demo/commits/{COMMIT_SHA}"
    )


def test_custom_branch_snapshot(
    repository_service,
    github_client,
    branch_data,
    commit_data
):

    branch_data["name"] = "develop"

    github_client.get.side_effect = [
        branch_data,
        commit_data
    ]

    result = repository_service.get_repository_snapshot(
        REPOSITORY_URL,
        branch="develop"
    )

    assert result.branch.name == "develop"

    github_client.get.assert_any_call(
        "/repos/test/demo/branches/develop"
    )


def test_branch_with_slash(
    repository_service,
    github_client,
    branch_data,
    commit_data
):

    branch_data["name"] = "feature/auth"

    github_client.get.side_effect = [
        branch_data,
        commit_data
    ]

    result = repository_service.get_repository_snapshot(
        REPOSITORY_URL,
        branch="feature/auth"
    )

    assert result.branch.name == "feature/auth"

    github_client.get.assert_any_call(
        "/repos/test/demo/branches/feature%2Fauth"
    )


def test_branch_not_found(
    repository_service,
    github_client
):

    github_client.get.side_effect = GitHubNotFoundError(
        "Branch not found"
    )

    with pytest.raises(BranchNotFoundError):

        repository_service.get_repository_snapshot(
            REPOSITORY_URL,
            branch="nonexistent"
        )


def test_invalid_branch_name(
    repository_service,
    github_client
):

    with pytest.raises(InvalidBranchNameError):

        repository_service.get_repository_snapshot(
            REPOSITORY_URL,
            branch="invalid branch"
        )

    github_client.get.assert_not_called()


def test_invalid_branch_data(
    repository_service,
    github_client
):

    github_client.get.return_value = {
        "name": "main"
    }

    with pytest.raises(InvalidRepositoryDataError):

        repository_service.get_repository_snapshot(
            REPOSITORY_URL
        )


def test_invalid_commit_data(
    repository_service,
    github_client,
    branch_data
):

    github_client.get.side_effect = [
        branch_data,
        {}
    ]

    with pytest.raises(InvalidRepositoryDataError):

        repository_service.get_repository_snapshot(
            REPOSITORY_URL
        )


def test_commit_sha_mismatch(
    repository_service,
    github_client,
    branch_data,
    commit_data
):

    commit_data["sha"] = "b" * 40

    github_client.get.side_effect = [
        branch_data,
        commit_data
    ]

    with pytest.raises(InvalidRepositoryDataError):

        repository_service.get_repository_snapshot(
            REPOSITORY_URL
        )
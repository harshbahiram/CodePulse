from unittest.mock import Mock

import pytest

from app.integrations.github.client import GitHubClient

from app.schemas.repository import RepositorySnapshot

from app.services.repository_tree_service import (
    RepositoryTreeService
)

from app.services.exceptions import (
    InvalidRepositoryTreeError
)


COMMIT_SHA = "a" * 40
TREE_SHA = "b" * 40
BLOB_SHA = "c" * 40

REPOSITORY_URL = "https://github.com/test/demo"


@pytest.fixture
def github_client():
    return Mock(spec=GitHubClient)


@pytest.fixture
def tree_service(github_client):
    return RepositoryTreeService(github_client)


@pytest.fixture
def snapshot():

    return RepositorySnapshot(
        repository={
            "id": 123,
            "name": "demo",
            "full_name": "test/demo",

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

            "size": 100,
            "stargazers_count": 10,
            "forks_count": 2,
            "open_issues_count": 1,

            "created_at": "2025-01-01T10:00:00Z",
            "updated_at": "2025-01-01T10:00:00Z"
        },

        branch={
            "name": "main",
            "commit_sha": COMMIT_SHA,
            "protected": False
        },

        commit={
            "sha": COMMIT_SHA,
            "tree_sha": TREE_SHA,
            "message": "Initial commit",
            "html_url": (
                f"{REPOSITORY_URL}/commit/{COMMIT_SHA}"
            )
        }
    )


@pytest.fixture
def tree_data():

    return {
        "sha": TREE_SHA,

        "truncated": False,

        "tree": [
            {
                "path": "src",
                "mode": "040000",
                "type": "tree",
                "sha": TREE_SHA
            },
            {
                "path": "src/main.py",
                "mode": "100644",
                "type": "blob",
                "sha": BLOB_SHA,
                "size": 1000
            },
            {
                "path": "run.sh",
                "mode": "100755",
                "type": "blob",
                "sha": BLOB_SHA,
                "size": 500
            },
            {
                "path": "shortcut",
                "mode": "120000",
                "type": "blob",
                "sha": BLOB_SHA,
                "size": 10
            },
            {
                "path": "external",
                "mode": "160000",
                "type": "commit",
                "sha": COMMIT_SHA
            }
        ]
    }


def test_repository_tree(
    tree_service,
    github_client,
    snapshot,
    tree_data
):

    github_client.get.return_value = tree_data

    result = tree_service.get_repository_tree(snapshot)

    assert result.commit_sha == COMMIT_SHA
    assert result.tree_sha == TREE_SHA
    assert len(result.entries) == 5
    assert result.truncated is False

    github_client.get.assert_called_once_with(
        f"/repos/test/demo/git/trees/{TREE_SHA}",
        params={"recursive": 1}
    )


def test_tree_statistics(
    tree_service,
    github_client,
    snapshot,
    tree_data
):

    github_client.get.return_value = tree_data

    result = tree_service.get_repository_tree(snapshot)

    stats = result.statistics

    assert stats.total_entries == 5
    assert stats.total_files == 2
    assert stats.total_directories == 1
    assert stats.total_symlinks == 1
    assert stats.total_submodules == 1
    assert stats.total_file_bytes == 1500


def test_github_truncated_tree(
    tree_service,
    github_client,
    snapshot,
    tree_data
):

    tree_data["truncated"] = True

    github_client.get.return_value = tree_data

    result = tree_service.get_repository_tree(snapshot)

    assert result.truncated is True


def test_local_tree_limit(
    tree_service,
    github_client,
    snapshot,
    tree_data
):

    tree_service.MAX_TREE_ENTRIES = 2

    github_client.get.return_value = tree_data

    result = tree_service.get_repository_tree(snapshot)

    assert len(result.entries) == 2
    assert result.truncated is True


def test_tree_sha_mismatch(
    tree_service,
    github_client,
    snapshot,
    tree_data
):

    tree_data["sha"] = "d" * 40

    github_client.get.return_value = tree_data

    with pytest.raises(InvalidRepositoryTreeError):
        tree_service.get_repository_tree(snapshot)


def test_invalid_tree_response(
    tree_service,
    github_client,
    snapshot
):

    github_client.get.return_value = []

    with pytest.raises(InvalidRepositoryTreeError):
        tree_service.get_repository_tree(snapshot)


def test_invalid_tree_entry(
    tree_service,
    github_client,
    snapshot,
    tree_data
):

    tree_data["tree"][0]["mode"] = "invalid"

    github_client.get.return_value = tree_data

    with pytest.raises(InvalidRepositoryTreeError):
        tree_service.get_repository_tree(snapshot)


def test_invalid_mode_type_combination(
    tree_service,
    github_client,
    snapshot,
    tree_data
):

    tree_data["tree"][0]["type"] = "blob"

    github_client.get.return_value = tree_data

    with pytest.raises(InvalidRepositoryTreeError):
        tree_service.get_repository_tree(snapshot)


@pytest.mark.parametrize(
    "path",
    [
        "../secret.txt",
        "/etc/passwd",
        "src/../../secret.txt",
        "src\\main.py",
        "src//main.py"
    ]
)
def test_invalid_file_path(
    tree_service,
    github_client,
    snapshot,
    tree_data,
    path
):

    tree_data["tree"][1]["path"] = path

    github_client.get.return_value = tree_data

    with pytest.raises(InvalidRepositoryTreeError):
        tree_service.get_repository_tree(snapshot)


def test_missing_file_size(
    tree_service,
    github_client,
    snapshot,
    tree_data
):

    del tree_data["tree"][1]["size"]

    github_client.get.return_value = tree_data

    with pytest.raises(InvalidRepositoryTreeError):
        tree_service.get_repository_tree(snapshot)


def test_empty_tree(
    tree_service,
    github_client,
    snapshot,
    tree_data
):

    tree_data["tree"] = []

    github_client.get.return_value = tree_data

    result = tree_service.get_repository_tree(snapshot)

    assert result.entries == []
    assert result.statistics.total_entries == 0
    assert result.statistics.total_file_bytes == 0


def test_invalid_truncation_status(
    tree_service,
    github_client,
    snapshot,
    tree_data
):

    tree_data["truncated"] = "false"

    github_client.get.return_value = tree_data

    with pytest.raises(InvalidRepositoryTreeError):
        tree_service.get_repository_tree(snapshot)
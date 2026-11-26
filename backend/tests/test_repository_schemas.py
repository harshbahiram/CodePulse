import pytest

from pydantic import ValidationError

from app.schemas.repository import (
    RepositoryRequest,
    RepositoryBranch,
    RepositoryLanguages
)


def test_valid_repository_request():
    request = RepositoryRequest(
        repository_url="https://github.com/fastapi/fastapi"
    )

    assert str(request.repository_url) == (
        "https://github.com/fastapi/fastapi"
    )

    assert request.branch is None


def test_repository_request_with_branch():
    request = RepositoryRequest(
        repository_url="https://github.com/fastapi/fastapi",
        branch="master"
    )

    assert request.branch == "master"


def test_invalid_repository_url():
    with pytest.raises(ValidationError):
        RepositoryRequest(
            repository_url="invalid-url"
        )


def test_empty_branch():
    with pytest.raises(ValidationError):
        RepositoryRequest(
            repository_url="https://github.com/fastapi/fastapi",
            branch=""
        )


def test_repository_branch():
    branch = RepositoryBranch(
        name="main",
        commit_sha="a" * 40,
        protected=False
    )

    assert branch.name == "main"
    assert branch.protected is False


def test_repository_languages():
    languages = RepositoryLanguages(
        languages={
            "Python": 850000,
            "HTML": 100000,
            "JavaScript": 50000
        },
        total_bytes=1000000
    )

    assert languages.total_bytes == 1000000
    assert languages.languages["Python"] == 850000


def test_negative_total_bytes():
    with pytest.raises(ValidationError):
        RepositoryLanguages(
            languages={},
            total_bytes=-100
        )
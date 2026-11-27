import pytest

from pydantic import ValidationError

from app.utils.github_url import (
    parse_github_url,
    InvalidGitHubURLError
)

from app.schemas.repository import RepositoryRequest


@pytest.mark.parametrize(
    "url",
    [
        "https://github.com/fastapi/fastapi",
        "https://github.com/fastapi/fastapi.git",
        "https://github.com/fastapi/fastapi/",
        "https://github.com/fastapi/fastapi.git/"
    ]
)
def test_valid_github_urls(url):

    result = parse_github_url(url)

    assert result.owner == "fastapi"
    assert result.repository == "fastapi"
    assert result.full_name == "fastapi/fastapi"

    assert result.normalized_url == (
        "https://github.com/fastapi/fastapi"
    )


@pytest.mark.parametrize(
    "url",
    [
        "",
        "invalid-url",
        "http://github.com/user/repo",
        "https://gitlab.com/user/repo",
        "https://github.com.evil.com/user/repo",
        "https://github.com/user",
        "https://github.com/user/repo/issues",
        "https://github.com/user/repo?token=123",
        "https://github.com/user/repo#readme",
        "https://github.com:443/user/repo",
        "https://user@github.com/user/repo",
        "https://github.com/user/..",
        "https://github.com/user/%2e%2e",
        "https://github.com//repo",
        "https://github.com/user/my repo",
        "https://github.com/user/repo\\file",
        "http://localhost:8000"
    ]
)
def test_invalid_github_urls(url):

    with pytest.raises(InvalidGitHubURLError):
        parse_github_url(url)


def test_repository_schema_normalization():

    request = RepositoryRequest(
        repository_url=(
            "https://github.com/fastapi/fastapi.git"
        )
    )

    assert str(request.repository_url) == (
        "https://github.com/fastapi/fastapi"
    )


def test_repository_schema_rejects_non_github_url():

    with pytest.raises(ValidationError):

        RepositoryRequest(
            repository_url="https://example.com/user/repo"
        )
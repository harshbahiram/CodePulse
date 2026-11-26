from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl, field_validator
from app.utils.github_url import parse_github_url


class RepositoryRequest(BaseModel):

    repository_url: HttpUrl = Field(
        ...,
        description="Public GitHub repository URL",
        examples=["https://github.com/fastapi/fastapi"]
    )

    branch: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Repository branch to analyze"
    )

    @field_validator("repository_url", mode="before")
    @classmethod
    def validate_repository_url(cls, value):

        if not isinstance(value, str):
            raise ValueError(
                "Repository URL must be a string"
            )

        repository = parse_github_url(value)

        return repository.normalized_url


class RepositoryOwner(BaseModel):
    login: str
    avatar_url: HttpUrl
    html_url: HttpUrl
    type: str


class RepositoryMetadata(BaseModel):
    id: int
    name: str
    full_name: str
    description: str | None = None

    owner: RepositoryOwner

    html_url: HttpUrl
    clone_url: HttpUrl

    private: bool
    fork: bool
    archived: bool

    default_branch: str
    language: str | None = None

    size: int = Field(ge=0)
    stargazers_count: int = Field(ge=0)
    forks_count: int = Field(ge=0)
    open_issues_count: int = Field(ge=0)

    created_at: datetime
    updated_at: datetime
    pushed_at: datetime | None = None


class RepositoryBranch(BaseModel):
    name: str
    commit_sha: str
    protected: bool


class RepositoryCommit(BaseModel):
    sha: str
    message: str

    author_name: str | None = None
    author_email: str | None = None
    committed_at: datetime | None = None

    html_url: HttpUrl


class RepositoryLanguages(BaseModel):
    languages: dict[str, int]
    total_bytes: int = Field(ge=0)


class RepositoryResponse(BaseModel):
    repository: RepositoryMetadata
    languages: RepositoryLanguages
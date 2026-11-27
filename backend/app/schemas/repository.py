from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator

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
    name: str = Field(min_length=1)
    commit_sha: str = Field( pattern=r"^[a-fA-F0-9]{40}$")
    protected: bool


class RepositoryCommit(BaseModel):
    sha: str = Field( pattern=r"^[a-fA-F0-9]{40}$")
    tree_sha: str = Field( pattern=r"^[a-fA-F0-9]{40}$")
    message: str

    author_name: str | None = None
    author_email: str | None = None
    committed_at: datetime | None = None

    html_url: HttpUrl


class RepositoryLanguages(BaseModel):
    languages: dict[str, Annotated[int, Field(ge=0, strict=True)]]
    total_bytes: int = Field(ge=0, strict=True)

    @model_validator(mode="after")
    def validate_total_bytes(self):

        if self.total_bytes != sum(self.languages.values()):
            raise ValueError(
                "Total bytes must match the sum of language bytes"
            )

        return self


class RepositoryResponse(BaseModel):
    repository: RepositoryMetadata
    languages: RepositoryLanguages


class RepositoryBranches(BaseModel):

    branches: list[RepositoryBranch]

    total_branches: int = Field(ge=0)

    truncated: bool = False


class RepositorySnapshot(BaseModel):

    repository: RepositoryMetadata

    branch: RepositoryBranch

    commit: RepositoryCommit

    @model_validator(mode="after")
    def validate_commit_consistency(self):

        if self.branch.commit_sha != self.commit.sha:
            raise ValueError(
                "Branch and commit SHA must match"
            )

        return self
from typing import Literal

from pydantic import BaseModel, Field


class RepositoryTreeEntry(BaseModel):

    path: str = Field(min_length=1)

    mode: Literal[
        "040000",
        "100644",
        "100755",
        "120000",
        "160000"
    ]

    type: Literal["blob", "tree", "commit"]

    sha: str = Field(
        pattern=r"^[a-fA-F0-9]{40}$"
    )

    size: int | None = Field(
        default=None,
        ge=0,
        strict=True
    )

    @property
    def is_file(self) -> bool:
        return self.mode in ("100644", "100755")

    @property
    def is_directory(self) -> bool:
        return self.mode == "040000"

    @property
    def is_symlink(self) -> bool:
        return self.mode == "120000"

    @property
    def is_submodule(self) -> bool:
        return self.mode == "160000"


class RepositoryTreeStatistics(BaseModel):

    total_entries: int = Field(ge=0)

    total_files: int = Field(ge=0)

    total_directories: int = Field(ge=0)

    total_symlinks: int = Field(ge=0)

    total_submodules: int = Field(ge=0)

    total_file_bytes: int = Field(ge=0)


class RepositoryTreeResponse(BaseModel):

    repository_full_name: str

    branch: str

    commit_sha: str = Field(
        pattern=r"^[a-fA-F0-9]{40}$"
    )

    tree_sha: str = Field(
        pattern=r"^[a-fA-F0-9]{40}$"
    )

    entries: list[RepositoryTreeEntry]

    statistics: RepositoryTreeStatistics

    truncated: bool
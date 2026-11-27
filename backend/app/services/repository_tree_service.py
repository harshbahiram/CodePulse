from pydantic import ValidationError

from app.integrations.github.client import GitHubClient

from app.schemas.repository import RepositorySnapshot

from app.schemas.repository_tree import (
    RepositoryTreeEntry,
    RepositoryTreeStatistics,
    RepositoryTreeResponse
)

from app.services.exceptions import (
    InvalidRepositoryTreeError
)


class RepositoryTreeService:

    MAX_TREE_ENTRIES = 50000

    def __init__(self, github_client: GitHubClient):
        self.github_client = github_client

    def _map_tree_entry(
        self,
        data: dict
    ) -> RepositoryTreeEntry:

        try:
            entry = RepositoryTreeEntry.model_validate(data)

        except ValidationError as exc:
            raise InvalidRepositoryTreeError(
                "GitHub returned an invalid tree entry"
            ) from exc

        expected_types = {
            "040000": "tree",
            "100644": "blob",
            "100755": "blob",
            "120000": "blob",
            "160000": "commit"
        }

        if expected_types[entry.mode] != entry.type:
            raise InvalidRepositoryTreeError(
                "Git tree mode and type do not match"
            )

        if entry.is_file and entry.size is None:
            raise InvalidRepositoryTreeError(
                "Regular file size is missing"
            )

        path_parts = entry.path.split("/")

        if (
            "\\" in entry.path
            or "\x00" in entry.path
            or any(
                part in ("", ".", "..")
                for part in path_parts
            )
        ):
            raise InvalidRepositoryTreeError(
                "Invalid repository file path"
            )

        return entry

    def _calculate_statistics(
        self,
        entries: list[RepositoryTreeEntry]
    ) -> RepositoryTreeStatistics:

        files = [
            entry
            for entry in entries
            if entry.is_file
        ]

        return RepositoryTreeStatistics(
            total_entries=len(entries),

            total_files=len(files),

            total_directories=sum(
                entry.is_directory
                for entry in entries
            ),

            total_symlinks=sum(
                entry.is_symlink
                for entry in entries
            ),

            total_submodules=sum(
                entry.is_submodule
                for entry in entries
            ),

            total_file_bytes=sum(
                entry.size or 0
                for entry in files
            )
        )

    def get_repository_tree(
        self,
        snapshot: RepositorySnapshot
    ) -> RepositoryTreeResponse:

        if snapshot.repository.private:
            raise InvalidRepositoryTreeError(
                "Private repositories are not supported"
            )

        repository = snapshot.repository

        tree_sha = snapshot.commit.tree_sha

        endpoint = (
            f"/repos/{repository.owner.login}/"
            f"{repository.name}/git/trees/{tree_sha}"
        )

        data = self.github_client.get(
            endpoint,
            params={"recursive": 1}
        )

        if not isinstance(data, dict):
            raise InvalidRepositoryTreeError(
                "Invalid GitHub tree response"
            )

        if data.get("sha") != tree_sha:
            raise InvalidRepositoryTreeError(
                "Repository tree SHA mismatch"
            )

        raw_entries = data.get("tree")

        if not isinstance(raw_entries, list):
            raise InvalidRepositoryTreeError(
                "Repository tree entries are invalid"
            )

        github_truncated = data.get("truncated")

        if type(github_truncated) is not bool:
            raise InvalidRepositoryTreeError(
                "Invalid repository truncation status"
            )

        local_truncated = (
            len(raw_entries) > self.MAX_TREE_ENTRIES
        )

        entries = [
            self._map_tree_entry(entry)
            for entry in raw_entries[:self.MAX_TREE_ENTRIES]
        ]

        statistics = self._calculate_statistics(entries)

        return RepositoryTreeResponse(
            repository_full_name=repository.full_name,
            branch=snapshot.branch.name,
            commit_sha=snapshot.commit.sha,
            tree_sha=tree_sha,
            entries=entries,
            statistics=statistics,
            truncated=(
                github_truncated or local_truncated
            )
        )
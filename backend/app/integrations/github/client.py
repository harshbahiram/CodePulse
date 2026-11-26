import logging
from typing import Any

import httpx

from app.core.config import settings

from app.integrations.github.exceptions import (
    GitHubAPIError,
    GitHubAuthenticationError,
    GitHubRateLimitError,
    GitHubNotFoundError,
    GitHubPermissionError,
    GitHubConnectionError
)


logger = logging.getLogger(__name__)


class GitHubClient:

    def __init__(self):
        self.client = httpx.Client(
            base_url=settings.GITHUB_API_BASE_URL,
            timeout=settings.GITHUB_API_TIMEOUT,
            follow_redirects=False,
            headers={
                "Authorization": (
                    f"Bearer {settings.GITHUB_TOKEN.get_secret_value()}"
                ),
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": settings.GITHUB_API_VERSION,
                "User-Agent": "CodePulse"
            }
        )

    def get(self, endpoint: str, params: dict | None = None) -> Any:

        if (
            not endpoint.startswith("/")
            or endpoint.startswith("//")
            or "\\" in endpoint
        ):
            raise ValueError("Invalid GitHub API endpoint")

        try:
            response = self.client.get(
                endpoint,
                params=params
            )

        except httpx.RequestError as exc:
            logger.warning("GitHub API connection failed")

            raise GitHubConnectionError(
                "Unable to connect to GitHub API"
            ) from exc

        self._handle_response(response)

        try:
            return response.json()

        except ValueError as exc:
            raise GitHubAPIError(
                "GitHub returned an invalid JSON response"
            ) from exc

    def _handle_response(self, response: httpx.Response) -> None:

        status = response.status_code

        if status == 401:
            raise GitHubAuthenticationError("Invalid or expired GitHub token")

        if status in (403, 429):

            if (
                status == 429
                or response.headers.get(
                    "X-RateLimit-Remaining"
                ) == "0"
                or "Retry-After" in response.headers
                or "rate limit" in response.text.lower()
            ):
                raise GitHubRateLimitError(
                    "GitHub API rate limit exceeded"
                )

            raise GitHubPermissionError(
                "Access to GitHub resource is forbidden"
            )

        if status == 404:
            raise GitHubNotFoundError(
                "GitHub resource not found or inaccessible"
            )

        if not response.is_success:
            raise GitHubAPIError(
                f"GitHub API returned status code {status}"
            )

    def close(self):
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback
    ):
        self.close()
"""GitHub client factory."""

from __future__ import annotations

from githubkit import AppInstallationAuthStrategy, GitHub  # type: ignore[reportMissingImports]

__all__ = ("create_github_client",)


def create_github_client(
    app_id: int,
    private_key: str,
    installation_id: int,
    client_id: str,
    client_secret: str,
) -> GitHub:
    """Create a GitHub client for an app installation.

    This factory function creates a GitHub client authenticated as a GitHub App installation.
    Unlike the hardcoded client in the monolith, this allows for dynamic installation IDs
    so different guilds can use different GitHub App installations.

    Args:
        app_id: GitHub App ID.
        private_key: GitHub App private key (PEM format).
        installation_id: GitHub App installation ID.
        client_id: GitHub App client ID.
        client_secret: GitHub App client secret.

    Returns:
        Configured GitHub client instance.

    Example:
        ```python
        from byte_common.clients import create_github_client

        client = create_github_client(
            app_id=480575,
            private_key=settings.github.APP_PRIVATE_KEY,
            installation_id=guild_installation_id,
            client_id=settings.github.APP_CLIENT_ID,
            client_secret=settings.github.APP_CLIENT_SECRET,
        )

        # Use the client
        repo = await client.rest.repos.async_get("owner", "repo")
        ```
    """
    return GitHub(
        AppInstallationAuthStrategy(
            app_id=app_id,
            private_key=private_key,
            installation_id=installation_id,
            client_id=client_id,
            client_secret=client_secret,
        )
    )

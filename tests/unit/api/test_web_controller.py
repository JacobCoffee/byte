"""Tests for web controller endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from litestar.status_codes import HTTP_200_OK

if TYPE_CHECKING:
    from litestar.testing import AsyncTestClient

__all__ = [
    "TestWebAboutEndpoint",
    "TestWebContactEndpoint",
    "TestWebCookiesEndpoint",
    "TestWebDashboardEndpoint",
    "TestWebIndexEndpoint",
    "TestWebPrivacyEndpoint",
    "TestWebTermsEndpoint",
]


@pytest.mark.asyncio
class TestWebIndexEndpoint:
    """Tests for GET / endpoint."""

    async def test_index_renders_successfully(self, api_client: AsyncTestClient) -> None:
        """Test index page renders without errors."""
        response = await api_client.get("/")

        # Should return 200 with HTML content
        assert response.status_code == HTTP_200_OK
        assert "text/html" in response.headers.get("content-type", "")

    async def test_index_contains_expected_content(self, api_client: AsyncTestClient) -> None:
        """Test index page contains server status information."""
        response = await api_client.get("/")

        assert response.status_code == HTTP_200_OK
        content = response.text

        # Page should contain some basic HTML structure
        assert "<html" in content.lower() or "<!doctype html>" in content.lower()


@pytest.mark.asyncio
class TestWebDashboardEndpoint:
    """Tests for GET /dashboard endpoint."""

    async def test_dashboard_renders_successfully(self, api_client: AsyncTestClient) -> None:
        """Test dashboard page renders without errors."""
        response = await api_client.get("/dashboard")

        assert response.status_code == HTTP_200_OK
        assert "text/html" in response.headers.get("content-type", "")

    async def test_dashboard_html_structure(self, api_client: AsyncTestClient) -> None:
        """Test dashboard returns valid HTML."""
        response = await api_client.get("/dashboard")

        assert response.status_code == HTTP_200_OK
        content = response.text
        assert "<html" in content.lower() or "<!doctype html>" in content.lower()


@pytest.mark.asyncio
class TestWebAboutEndpoint:
    """Tests for GET /about endpoint."""

    async def test_about_page_loads(self, api_client: AsyncTestClient) -> None:
        """Test about page renders successfully."""
        response = await api_client.get("/about")

        assert response.status_code == HTTP_200_OK
        assert "text/html" in response.headers.get("content-type", "")


@pytest.mark.asyncio
class TestWebContactEndpoint:
    """Tests for GET /contact endpoint."""

    async def test_contact_page_loads(self, api_client: AsyncTestClient) -> None:
        """Test contact page renders successfully."""
        response = await api_client.get("/contact")

        assert response.status_code == HTTP_200_OK
        assert "text/html" in response.headers.get("content-type", "")


@pytest.mark.asyncio
class TestWebPrivacyEndpoint:
    """Tests for GET /privacy endpoint."""

    async def test_privacy_page_loads(self, api_client: AsyncTestClient) -> None:
        """Test privacy page renders successfully."""
        response = await api_client.get("/privacy")

        assert response.status_code == HTTP_200_OK
        assert "text/html" in response.headers.get("content-type", "")


@pytest.mark.asyncio
class TestWebTermsEndpoint:
    """Tests for GET /terms endpoint."""

    async def test_terms_page_loads(self, api_client: AsyncTestClient) -> None:
        """Test terms page renders successfully."""
        response = await api_client.get("/terms")

        assert response.status_code == HTTP_200_OK
        assert "text/html" in response.headers.get("content-type", "")


@pytest.mark.asyncio
class TestWebCookiesEndpoint:
    """Tests for GET /cookies endpoint."""

    async def test_cookies_page_loads(self, api_client: AsyncTestClient) -> None:
        """Test cookies page renders successfully."""
        response = await api_client.get("/cookies")

        assert response.status_code == HTTP_200_OK
        assert "text/html" in response.headers.get("content-type", "")

"""Web Controller."""

from __future__ import annotations

from litestar import Controller, get
from litestar.response import Template
from litestar.status_codes import HTTP_200_OK

from server.domain import urls

__all__ = ["WebController"]


class WebController(Controller):
    """Web Controller."""

    opt = {"exclude_from_auth": True}

    @get(
        [urls.INDEX, urls.SITE_ROOT],
        operation_id="WebIndex",
        name="frontend:index",
        status_code=HTTP_200_OK,
        include_in_schema=False,
        opt={"exclude_from_auth": True},
    )
    async def index(self) -> Template:
        """Serve site root."""
        return Template(template_name="index.html")

    # add dashboard
    @get(
        path="/dashboard",
        operation_id="WebDashboard",
        name="frontend:dashboard",
        status_code=HTTP_200_OK,
        include_in_schema=False,
        opt={"exclude_from_auth": True},
    )
    async def dashboard(self) -> Template:
        """Serve dashboard."""
        return Template(template_name="dashboard.html")

    @get(
        path="/about",
        operation_id="WebAbout",
        name="frontend:about",
        status_code=HTTP_200_OK,
        include_in_schema=False,
        opt={"exclude_from_auth": True},
    )
    async def about(self) -> Template:
        """Serve about page."""
        return Template(template_name="about.html")

    @get(
        path="/contact",
        operation_id="WebContact",
        name="frontend:contact",
        status_code=HTTP_200_OK,
        include_in_schema=False,
        opt={"exclude_from_auth": True},
    )
    async def contact(self) -> Template:
        """Serve contact page."""
        return Template(template_name="contact.html")

    @get(
        path="/privacy",
        operation_id="WebPrivacy",
        name="frontend:privacy",
        status_code=HTTP_200_OK,
        include_in_schema=False,
        opt={"exclude_from_auth": True},
    )
    async def privacy(self) -> Template:
        """Serve privacy page."""
        return Template(template_name="privacy.html")

    @get(
        path="/terms",
        operation_id="WebTerms",
        name="frontend:terms",
        status_code=HTTP_200_OK,
        include_in_schema=False,
        opt={"exclude_from_auth": True},
    )
    async def terms(self) -> Template:
        """Serve terms page."""
        return Template(template_name="terms.html")

    @get(
        path="/cookies",
        operation_id="WebCookies",
        name="frontend:cookies",
        status_code=HTTP_200_OK,
        include_in_schema=False,
        opt={"exclude_from_auth": True},
    )
    async def cookies(self) -> Template:
        """Serve cookies page."""
        return Template(template_name="cookies.html")

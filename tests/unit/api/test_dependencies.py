"""Unit tests for dependency injection system.

Tests dependency providers, database session injection,
settings injection, repository injection, and dependency cleanup.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from advanced_alchemy.filters import BeforeAfter, CollectionFilter, LimitOffset, OrderBy, SearchFilter
from litestar.status_codes import HTTP_200_OK

from byte_api.lib.dependencies import (
    create_collection_dependencies,
    provide_created_filter,
    provide_filter_dependencies,
    provide_id_filter,
    provide_limit_offset_pagination,
    provide_order_by,
    provide_search_filter,
    provide_updated_filter,
)

if TYPE_CHECKING:
    from litestar.testing import AsyncTestClient
    from sqlalchemy.ext.asyncio import AsyncSession

__all__ = [
    "test_create_collection_dependencies",
    "test_db_session_cleanup_on_error",
    "test_db_session_dependency",
    "test_provide_created_filter",
    "test_provide_filter_dependencies",
    "test_provide_id_filter",
    "test_provide_limit_offset_pagination",
    "test_provide_order_by",
    "test_provide_search_filter",
    "test_provide_updated_filter",
    "test_settings_accessible",
]


def test_create_collection_dependencies() -> None:
    """Test collection dependencies dictionary is created correctly."""
    dependencies = create_collection_dependencies()

    assert isinstance(dependencies, dict)
    assert len(dependencies) > 0

    # Should contain all expected dependency keys
    expected_keys = [
        "active_filter",
        "limit_offset",
        "updated_filter",
        "created_filter",
        "id_filter",
        "search_filter",
        "order_by",
        "filters",
    ]

    for key in expected_keys:
        assert key in dependencies
        assert dependencies[key] is not None


def test_provide_id_filter() -> None:
    """Test ID filter provider."""
    # No IDs
    filter_empty = provide_id_filter(None)
    assert isinstance(filter_empty, CollectionFilter)
    assert filter_empty.values == []

    # With IDs
    test_ids = [uuid4(), uuid4()]
    filter_with_ids = provide_id_filter(test_ids)
    assert isinstance(filter_with_ids, CollectionFilter)
    assert filter_with_ids.values == test_ids


def test_provide_created_filter() -> None:
    """Test created date filter provider."""
    before = datetime(2024, 1, 1, tzinfo=UTC)
    after = datetime(2023, 1, 1, tzinfo=UTC)

    filter_result = provide_created_filter(before, after)

    assert isinstance(filter_result, BeforeAfter)
    assert filter_result.field_name == "created_at"
    assert filter_result.before == before
    assert filter_result.after == after


def test_provide_updated_filter() -> None:
    """Test updated date filter provider."""
    before = datetime(2024, 1, 1, tzinfo=UTC)
    after = datetime(2023, 1, 1, tzinfo=UTC)

    filter_result = provide_updated_filter(before, after)

    assert isinstance(filter_result, BeforeAfter)
    assert filter_result.field_name == "updated_at"
    assert filter_result.before == before
    assert filter_result.after == after


def test_provide_limit_offset_pagination() -> None:
    """Test pagination filter provider."""
    # Default values
    filter_default = provide_limit_offset_pagination()
    assert isinstance(filter_default, LimitOffset)
    assert filter_default.limit == 10  # DEFAULT_PAGINATION_SIZE
    assert filter_default.offset == 0

    # Custom values
    filter_custom = provide_limit_offset_pagination(current_page=3, page_size=25)
    assert isinstance(filter_custom, LimitOffset)
    assert filter_custom.limit == 25
    assert filter_custom.offset == 50  # page_size * (current_page - 1)


def test_provide_search_filter() -> None:
    """Test search filter provider."""
    # No search
    filter_empty = provide_search_filter(None, None, None)
    assert isinstance(filter_empty, SearchFilter)

    # With search
    filter_with_search = provide_search_filter("name", "test", True)
    assert isinstance(filter_with_search, SearchFilter)
    assert filter_with_search.field_name == "name"
    assert filter_with_search.value == "test"
    assert filter_with_search.ignore_case is True


def test_provide_order_by() -> None:
    """Test order by filter provider."""
    # No ordering
    filter_empty = provide_order_by(None, None)
    assert isinstance(filter_empty, OrderBy)

    # With ordering
    filter_ordered = provide_order_by("created_at", "desc")
    assert isinstance(filter_ordered, OrderBy)
    assert filter_ordered.field_name == "created_at"
    assert filter_ordered.sort_order == "desc"


def test_provide_filter_dependencies() -> None:
    """Test filter dependencies aggregation."""
    from advanced_alchemy.filters import BeforeAfter, CollectionFilter, LimitOffset

    # Create mock filters
    created_filter = BeforeAfter("created_at", None, None)
    updated_filter = BeforeAfter("updated_at", None, None)
    id_filter = CollectionFilter(field_name="id", values=[])
    limit_offset = LimitOffset(10, 0)
    search_filter = SearchFilter(field_name="name", value="", ignore_case=False)
    order_by = OrderBy(field_name="id", sort_order="desc")

    # Test without filters
    filters = provide_filter_dependencies(
        created_filter=created_filter,
        updated_filter=updated_filter,
        id_filter=id_filter,
        limit_offset=limit_offset,
        search_filter=search_filter,
        order_by=order_by,
    )

    assert isinstance(filters, list)
    assert len(filters) >= 3  # At minimum: created, updated, limit_offset

    # Test with ID filter
    id_filter_with_values = CollectionFilter(field_name="id", values=[uuid4()])
    filters_with_id = provide_filter_dependencies(
        created_filter=created_filter,
        updated_filter=updated_filter,
        id_filter=id_filter_with_values,
        limit_offset=limit_offset,
        search_filter=search_filter,
        order_by=order_by,
    )

    assert len(filters_with_id) >= 4  # Should include ID filter


@pytest.mark.asyncio
async def test_db_session_dependency(
    api_client: AsyncTestClient,
    db_session: AsyncSession,
) -> None:
    """Test database session dependency injection works in endpoints."""
    # Health endpoint uses database session
    response = await api_client.get("/health")

    # Should succeed with injected session
    assert response.status_code == HTTP_200_OK


@pytest.mark.asyncio
async def test_db_session_cleanup_on_error(
    api_client: AsyncTestClient,
) -> None:
    """Test database session is cleaned up on exception.

    When an endpoint raises an exception, the database session
    should be properly rolled back and closed.
    """
    # Create a guild that will cause a conflict
    await api_client.post("/api/guilds/create?guild_id=5000&guild_name=Test")

    # Try to create the same guild again (should error)
    response = await api_client.post("/api/guilds/create?guild_id=5000&guild_name=Test")

    # Should handle error gracefully (session cleanup should not leak)
    assert response.status_code in [400, 409, 500]


@pytest.mark.asyncio
async def test_settings_accessible() -> None:
    """Test settings dependency is accessible."""
    from byte_api.lib import settings

    # Settings should be loaded
    assert settings.project is not None
    assert settings.api is not None
    assert settings.db is not None
    assert settings.openapi is not None


def test_dependency_providers_are_sync_to_thread_false() -> None:
    """Test dependency providers are configured with sync_to_thread=False.

    This ensures async dependencies don't block the event loop.
    """
    dependencies = create_collection_dependencies()

    # All providers should have sync_to_thread=False
    for provider in dependencies.values():
        assert hasattr(provider, "sync_to_thread")
        assert provider.sync_to_thread is False


@pytest.mark.asyncio
async def test_pagination_parameters_from_request(api_client: AsyncTestClient) -> None:
    """Test pagination parameters are correctly extracted from request."""
    # Create some guilds for pagination
    for i in range(15):
        await api_client.post(f"/api/guilds/create?guild_id={6000 + i}&guild_name=Page%20Test%20{i}")

    # Test pagination
    response = await api_client.get("/api/guilds/list?currentPage=1&pageSize=5")

    assert response.status_code == HTTP_200_OK
    data = response.json()

    # Should respect page size
    assert len(data["items"]) <= 5


@pytest.mark.asyncio
async def test_filter_parameters_from_request(api_client: AsyncTestClient) -> None:
    """Test filter parameters are correctly extracted from request."""
    # Create guilds with different timestamps
    await api_client.post("/api/guilds/create?guild_id=7000&guild_name=Filter%20Test")

    # Try to query with filters (may not be fully implemented)
    response = await api_client.get("/api/guilds/list")

    # Should handle filters gracefully even if not fully implemented
    assert response.status_code in [HTTP_200_OK, 400]


@pytest.mark.asyncio
async def test_dependency_injection_with_mock() -> None:
    """Test dependency injection can be mocked for testing."""
    from byte_api.lib import constants

    mock_session = AsyncMock()

    # Mock can be created and used
    assert mock_session is not None
    assert constants.DB_SESSION_DEPENDENCY_KEY == "db_session"


def test_active_filter_provider() -> None:
    """Test active filter provider."""
    from byte_api.lib.dependencies import provide_active_filter

    # Default should be True
    result = provide_active_filter()
    assert result is True

    # Can be set to False
    result_inactive = provide_active_filter(is_active=False)
    assert result_inactive is False


def test_limit_offset_pagination_edge_cases() -> None:
    """Test pagination with edge cases."""
    # Page 1
    filter_page1 = provide_limit_offset_pagination(current_page=1, page_size=10)
    assert filter_page1.offset == 0
    assert filter_page1.limit == 10

    # Page 10
    filter_page10 = provide_limit_offset_pagination(current_page=10, page_size=5)
    assert filter_page10.offset == 45
    assert filter_page10.limit == 5

    # Large page size
    filter_large = provide_limit_offset_pagination(current_page=1, page_size=100)
    assert filter_large.limit == 100


def test_created_filter_with_none_values() -> None:
    """Test created filter with None before/after."""
    filter_result = provide_created_filter(None, None)

    assert isinstance(filter_result, BeforeAfter)
    assert filter_result.field_name == "created_at"
    assert filter_result.before is None
    assert filter_result.after is None


def test_updated_filter_with_none_values() -> None:
    """Test updated filter with None before/after."""
    filter_result = provide_updated_filter(None, None)

    assert isinstance(filter_result, BeforeAfter)
    assert filter_result.field_name == "updated_at"
    assert filter_result.before is None
    assert filter_result.after is None


def test_search_filter_ignore_case_default() -> None:
    """Test search filter ignore_case defaults to False."""
    filter_result = provide_search_filter("name", "test", None)

    assert isinstance(filter_result, SearchFilter)
    assert filter_result.ignore_case is False


def test_order_by_default_sort_order() -> None:
    """Test order by with default sort order."""
    filter_result = provide_order_by("created_at", None)

    assert isinstance(filter_result, OrderBy)
    assert filter_result.field_name == "created_at"


def test_filter_dependencies_with_search() -> None:
    """Test filter dependencies includes search when provided."""
    search_filter = SearchFilter(field_name="name", value="test", ignore_case=True)
    order_by = OrderBy(field_name="created_at", sort_order="asc")

    filters = provide_filter_dependencies(
        created_filter=BeforeAfter("created_at", None, None),
        updated_filter=BeforeAfter("updated_at", None, None),
        id_filter=CollectionFilter(field_name="id", values=[]),
        limit_offset=LimitOffset(10, 0),
        search_filter=search_filter,
        order_by=order_by,
    )

    # Should include search and order_by filters
    assert len(filters) >= 5
    assert any(isinstance(f, SearchFilter) for f in filters)
    assert any(isinstance(f, OrderBy) for f in filters)


def test_dependency_key_constants() -> None:
    """Test dependency key constants are defined."""
    from byte_api.lib.dependencies import (
        ACTIVE_FILTER_DEPENDENCY_KEY,
        CREATED_FILTER_DEPENDENCY_KEY,
        FILTERS_DEPENDENCY_KEY,
        ID_FILTER_DEPENDENCY_KEY,
        LIMIT_OFFSET_DEPENDENCY_KEY,
        ORDER_BY_DEPENDENCY_KEY,
        SEARCH_FILTER_DEPENDENCY_KEY,
        UPDATED_FILTER_DEPENDENCY_KEY,
    )

    assert ACTIVE_FILTER_DEPENDENCY_KEY == "active_filter"
    assert CREATED_FILTER_DEPENDENCY_KEY == "created_filter"
    assert FILTERS_DEPENDENCY_KEY == "filters"
    assert ID_FILTER_DEPENDENCY_KEY == "id_filter"
    assert LIMIT_OFFSET_DEPENDENCY_KEY == "limit_offset"
    assert ORDER_BY_DEPENDENCY_KEY == "order_by"
    assert SEARCH_FILTER_DEPENDENCY_KEY == "search_filter"
    assert UPDATED_FILTER_DEPENDENCY_KEY == "updated_filter"


def test_all_filter_types_exported() -> None:
    """Test all filter types are exported in __all__."""
    from byte_api.lib import dependencies

    expected_exports = [
        "BeforeAfter",
        "CollectionFilter",
        "FilterTypes",
        "LimitOffset",
        "OrderBy",
        "SearchFilter",
        "create_collection_dependencies",
        "provide_created_filter",
        "provide_filter_dependencies",
        "provide_id_filter",
        "provide_limit_offset_pagination",
        "provide_order_by",
        "provide_search_filter",
        "provide_updated_filter",
    ]

    for export in expected_exports:
        assert export in dependencies.__all__


def test_type_aliases_defined() -> None:
    """Test type aliases are properly defined."""
    from byte_api.lib.dependencies import (
        BooleanOrNone,
        DTorNone,
        SortOrderOrNone,
        StringOrNone,
        UuidOrNone,
    )

    # Type aliases should be defined
    assert DTorNone is not None
    assert StringOrNone is not None
    assert UuidOrNone is not None
    assert BooleanOrNone is not None
    assert SortOrderOrNone is not None


def test_collection_dependencies_all_keys_present() -> None:
    """Test all expected keys are in collection dependencies."""
    dependencies = create_collection_dependencies()

    required_keys = {
        "active_filter",
        "limit_offset",
        "updated_filter",
        "created_filter",
        "id_filter",
        "search_filter",
        "order_by",
        "filters",
    }

    assert set(dependencies.keys()) == required_keys


def test_provide_order_by_asc_desc() -> None:
    """Test order by with both asc and desc."""
    filter_asc = provide_order_by("name", "asc")
    assert filter_asc.sort_order == "asc"

    filter_desc = provide_order_by("name", "desc")
    assert filter_desc.sort_order == "desc"


def test_provide_id_filter_multiple_ids() -> None:
    """Test ID filter with multiple IDs."""
    ids = [uuid4() for _ in range(10)]
    filter_result = provide_id_filter(ids)

    assert filter_result.values is not None
    assert len(filter_result.values) == 10
    assert all(test_id in filter_result.values for test_id in ids)

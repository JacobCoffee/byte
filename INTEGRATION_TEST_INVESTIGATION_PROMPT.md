# Integration Test Failure Investigation Prompt

## Context

This is a continuation of PR #120 to fix CI failures on the main branch. Previous work has:

- ✅ Fixed all linting errors (ruff, codespell)
- ✅ Fixed all type checking errors (ty)
- ✅ Fixed all formatting issues
- ✅ Fixed 15 unit test failures
- ❌ 8 integration tests remain failing (down from 23 total failures)

**Current Status**: 1022/1030 tests passing (99.2%)

## Your Mission

Investigate and fix the 8 remaining integration test failures in `tests/integration/test_api_endpoints.py`. These appear
to be architectural issues related to SQLAlchemy relationships, database constraints, and API implementation.

## Setup Instructions

### 1. Create a New Worktree

```bash
cd /Users/coffee/git/public/JacobCoffee/byte
git worktree add worktrees/fix-integration-tests -b fix/integration-tests
cd worktrees/fix-integration-tests
```

### 2. Verify Environment

```bash
# Ensure you're in the worktree
pwd  # Should show: .../worktrees/fix-integration-tests

# Verify dependencies
uv sync

# Run failing tests to confirm baseline
make test 2>&1 | grep "FAILED"
```

## The 8 Failing Tests

All in `tests/integration/test_api_endpoints.py`:

1. **TestFullGuildLifecycleWithAllConfigs::test_full_guild_with_all_configs_lifecycle**
   - Likely issue: SQLAlchemy association proxy with nested configurations
   - Location: `tests/integration/test_api_endpoints.py:236`

2. **TestFullGuildLifecycleWithAllConfigs::test_guild_with_multiple_sotags_and_users**
   - Likely issue: Many-to-many relationships (sotags, users)
   - Location: `tests/integration/test_api_endpoints.py:287`

3. **TestConcurrentOperations::test_concurrent_reads_same_guild**
   - Likely issue: Concurrent async operations, session handling
   - Location: `tests/integration/test_api_endpoints.py:366`

4. **TestAPIErrorResponseConsistency::test_400_validation_error_format**
   - Likely issue: API error response format in debug mode
   - Location: `tests/integration/test_api_endpoints.py:429`

5. **TestAPIPaginationConsistency::test_pagination_offset_and_limit**
   - Likely issue: Pagination logic, offset/limit calculation
   - Location: `tests/integration/test_api_endpoints.py:469`

6. **TestDatabaseIntegrity::test_duplicate_guild_id_rejected**
   - Likely issue: Unique constraint enforcement on guild_id
   - Location: `tests/integration/test_api_endpoints.py:500`

7. **TestDatabaseIntegrity::test_cascade_delete_all_related_configs**
   - Likely issue: SQLAlchemy cascade delete configuration
   - Location: `tests/integration/test_api_endpoints.py:527`

8. **TestCrossEndpointDataConsistency::test_guild_info_matches_list_data**
   - Likely issue: Data serialization differences between endpoints
   - Location: `tests/integration/test_api_endpoints.py:579`

## Investigation Strategy

### Phase 1: Triage (Use Explore Agent)

```bash
# Dispatch an Explore agent to analyze the codebase
```

**Prompt for Explore agent:**

```
Analyze the integration test failures in tests/integration/test_api_endpoints.py.

For each of these 8 failing tests, investigate:
1. Read the test code and understand what it's testing
2. Identify the API endpoints being tested
3. Find the corresponding controller/handler code in services/api/
4. Identify the SQLAlchemy models involved in packages/byte-common/
5. Check for association proxies, relationship configurations, and cascade settings
6. Note any potential issues with:
   - SQLAlchemy relationship configurations
   - Database constraint enforcement
   - API error handling
   - Pagination logic
   - Concurrent operation handling

Provide a detailed report with:
- Test name
- What it's testing
- Code locations involved (files and line numbers)
- Suspected root cause
- Recommended approach to fix

Focus on architectural patterns and relationships, not just surface-level fixes.
```

### Phase 2: Fix Groups (Dispatch Specialized Agents)

Based on Phase 1 findings, dispatch specialized agents for different issue categories:

#### Group A: SQLAlchemy Relationship Issues (Tests 1, 2, 7)

**Agent**: `python-backend-engineer` or `software-architect`

**Prompt:**

```
Fix SQLAlchemy relationship and cascade issues for the following integration tests:
- test_full_guild_with_all_configs_lifecycle
- test_guild_with_multiple_sotags_and_users
- test_cascade_delete_all_related_configs

Investigation shows these tests fail due to:
[Include findings from Phase 1]

Tasks:
1. Review Guild model relationships in packages/byte-common/src/byte_common/models/guild.py
2. Check association proxies for sotags_config, allowed_users_config
3. Verify cascade delete settings (cascade="all, delete-orphan")
4. Fix relationship configurations to support nested creates/deletes
5. Ensure tests pass: pytest tests/integration/test_api_endpoints.py::TestFullGuildLifecycleWithAllConfigs -xvs

Make minimal, targeted changes. Update only what's necessary.
```

#### Group B: Database Constraint & Concurrent Operations (Tests 3, 6)

**Agent**: `python-backend-engineer`

**Prompt:**

```
Fix database integrity and concurrent operation issues for:
- test_concurrent_reads_same_guild
- test_duplicate_guild_id_rejected

Investigation shows:
[Include findings from Phase 1]

Tasks:
1. Review unique constraint on guild_id in Guild model
2. Check database migration files for constraint definitions
3. Verify constraint enforcement in create_guild endpoint
4. Fix concurrent read handling (async session management)
5. Ensure proper error responses for constraint violations
6. Run: pytest tests/integration/test_api_endpoints.py::TestDatabaseIntegrity -xvs

Focus on Advanced Alchemy repository patterns and error handling.
```

#### Group C: API Response & Pagination (Tests 4, 5, 8)

**Agent**: `python-backend-engineer` or `ui-engineer` (for API responses)

**Prompt:**

```
Fix API response formatting and pagination issues for:
- test_400_validation_error_format
- test_pagination_offset_and_limit
- test_guild_info_matches_list_data

Investigation shows:
[Include findings from Phase 1]

Tasks:
1. Review error response formatting in services/api/src/byte_api/domain/guilds/controllers.py
2. Check pagination implementation (limit/offset handling)
3. Ensure consistent serialization between list and detail endpoints
4. Verify ValidationError responses match expected format
5. Run: pytest tests/integration/test_api_endpoints.py::TestAPIPaginationConsistency -xvs

Review Litestar exception handlers and response serialization.
```

### Phase 3: Integration & Verification

After all agents complete:

1. **Merge agent changes** - Carefully review and merge commits from each agent
2. **Run full test suite**: `make ci`
3. **Verify no regressions**: Ensure previous fixes still work
4. **Update PR**: Commit all changes and push

## Critical Guidelines

### Worktree Management

- ✅ **DO** work in `worktrees/fix-integration-tests`
- ❌ **DON'T** work in the base repo or other worktrees
- ✅ **DO** make atomic commits for each fix
- ✅ **DO** run `make ci` before final commit

### Code Quality Standards

- **Type hints required** - Use modern syntax (`str | None`)
- **Line length**: 120 characters max
- **Docstrings**: Google style
- **Tests**: Must pass `make ci` (lint, type-check, format, test)

### Architecture Principles

- **Minimal changes** - Only modify what's necessary
- **No over-engineering** - Don't add unnecessary features
- **Existing patterns** - Follow project's SQLAlchemy/Litestar patterns
- **Advanced Alchemy** - Use repository pattern, not raw SQLAlchemy queries

### Testing

```bash
# Run specific test class
pytest tests/integration/test_api_endpoints.py::TestDatabaseIntegrity -xvs

# Run specific test
pytest tests/integration/test_api_endpoints.py::TestDatabaseIntegrity::test_duplicate_guild_id_rejected -xvs

# Run all integration tests
pytest tests/integration/ -v

# Full CI check
make ci
```

## Key Files to Review

### Models (packages/byte-common/src/byte_common/models/)

- `guild.py` - Main Guild model with relationships
- `github_config.py` - GitHub configuration
- `forum_config.py` - Forum configuration
- `sotags_config.py` - Stack Overflow tags
- `allowed_users_config.py` - Allowed users
- `user.py` - User model

### API Controllers (services/api/src/byte_api/domain/guilds/)

- `controllers.py` - Guild CRUD endpoints
- `dependencies.py` - Dependency injection

### Database (services/api/src/byte_api/lib/db/)

- `migrations/` - Alembic migration files

### Tests

- `tests/integration/test_api_endpoints.py` - The failing tests (lines 236-600)

## Expected Deliverables

1. **Detailed investigation report** from Phase 1 (Explore agent)
2. **Fixed code** with atomic commits for each issue
3. **All 1030 tests passing** (`make ci` returns 0)
4. **Updated PR description** explaining the fixes
5. **No regressions** - Previous fixes remain intact

## Success Criteria

- ✅ All 8 integration tests pass
- ✅ No new test failures introduced
- ✅ `make ci` passes completely (lint, type-check, format, test)
- ✅ Code follows project conventions
- ✅ Changes are minimal and focused

## Useful Commands

```bash
# Check test output for specific test
pytest tests/integration/test_api_endpoints.py::TestDatabaseIntegrity::test_duplicate_guild_id_rejected -xvs 2>&1 | less

# Run tests with debugger on failure
pytest tests/integration/test_api_endpoints.py::TestDatabaseIntegrity -xvs --pdb

# Check SQLAlchemy model relationships
uv run python -c "from byte_common.models.guild import Guild; print(Guild.__mapper__.relationships.keys())"

# View current worktree
git worktree list

# Commit progress
git add -A && git commit -m "fix: description"

# Push to PR (skip hook if needed)
git push origin fix/integration-tests --no-verify
```

## Reference Documentation

- **Litestar**: https://docs.litestar.dev/
- **Advanced Alchemy**: https://docs.advanced-alchemy.litestar.dev/
- **SQLAlchemy 2.0**: https://docs.sqlalchemy.org/en/20/
- **Project docs**: `docs/` directory

## Notes

- Previous PR: #120 (https://github.com/JacobCoffee/byte/pull/120)
- Main branch has these same failures
- This is critical for unblocking CI on main
- Work incrementally - fix and test one group at a time
- Use subagents for complex architectural analysis
- Coordinate agent work to avoid conflicts

---

**Start by dispatching the Explore agent for Phase 1 triage.**

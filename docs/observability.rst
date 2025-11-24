==============
Observability
==============

This document describes the observability features of Byte Bot, including structured logging,
correlation IDs for request tracing, and Prometheus metrics for monitoring.

Structured Logging
==================

All services use structured logging with the following features:

- **JSON output in production**: Logs are formatted as JSON for easy parsing by log aggregation systems
- **Pretty console output in development**: Human-readable colored output when running in TTY mode
- **Correlation IDs**: Every HTTP request is tagged with a unique correlation ID
- **Contextual information**: Logs include timestamp, log level, logger name, and structured context

Log Fields
----------

Every log entry includes:

- ``timestamp``: ISO 8601 timestamp (UTC)
- ``level``: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- ``logger``: Name of the logger that created the entry
- ``correlation_id``: Request correlation ID (for HTTP requests)
- ``event``: Log message
- Additional context fields specific to the event

Example log entry:

.. code-block:: json

   {
     "timestamp": "2025-11-23T10:30:45.123456Z",
     "level": "info",
     "logger": "byte_api.domain.guilds.controllers",
     "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
     "event": "Guild fetched successfully",
     "guild_id": 123456789,
     "guild_name": "My Discord Server"
   }

Correlation IDs
===============

Every HTTP request processed by the API service is assigned a correlation ID, which enables
tracing requests across services and through the entire request lifecycle.

How It Works
------------

1. **Request Ingress**: When a request arrives at the API:

   - If the request includes an ``X-Correlation-ID`` header, that value is used
   - Otherwise, a new UUID v4 is generated

2. **Log Context**: The correlation ID is bound to the structured logging context
   for the duration of the request

3. **Response Headers**: The correlation ID is included in the ``X-Correlation-ID``
   response header

4. **Service Propagation**: When the bot service calls the API service, it includes
   its generated correlation ID in the request headers

Example Usage
-------------

**API Request**:

.. code-block:: bash

   curl -H "X-Correlation-ID: my-custom-id-123" http://localhost:8000/api/guilds/123

**Response Headers**:

.. code-block:: text

   HTTP/1.1 200 OK
   X-Correlation-ID: my-custom-id-123
   Content-Type: application/json

**Logs**:

All logs generated during this request will include ``"correlation_id": "my-custom-id-123"``,
making it easy to trace the entire request flow.

Bot Service Integration
-----------------------

The bot service automatically generates correlation IDs for all API requests:

.. code-block:: python

   # In byte_bot/api_client.py
   async def _request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
       correlation_id = str(uuid.uuid4())
       headers = {"X-Correlation-ID": correlation_id}

       logger.info(
           "API request",
           extra={
               "method": method,
               "endpoint": endpoint,
               "correlation_id": correlation_id,
           },
       )

       response = await self.client.request(method, endpoint, headers=headers, **kwargs)
       # ... response logged with same correlation_id

This creates an end-to-end trace from Discord event → bot service → API service.

Prometheus Metrics
==================

The API service exposes Prometheus metrics at ``/metrics`` for monitoring and alerting.

Available Metrics
-----------------

HTTP Metrics
~~~~~~~~~~~~

**http_requests_total** (Counter)
    Total number of HTTP requests, labeled by:

    - ``method``: HTTP method (GET, POST, etc.)
    - ``endpoint``: Request path
    - ``status``: HTTP status code (200, 404, 500, etc.)

    Example:

    .. code-block:: text

       http_requests_total{method="GET",endpoint="/api/guilds/123",status="200"} 42

**http_request_duration_seconds** (Histogram)
    HTTP request latency distribution, labeled by:

    - ``method``: HTTP method
    - ``endpoint``: Request path

    Includes buckets for:

    - ``_sum``: Total time spent
    - ``_count``: Total number of requests
    - Histogram buckets for percentile calculations

    Example:

    .. code-block:: text

       http_request_duration_seconds_sum{method="GET",endpoint="/api/guilds/123"} 1.234
       http_request_duration_seconds_count{method="GET",endpoint="/api/guilds/123"} 42

Database Metrics
~~~~~~~~~~~~~~~~

**db_queries_total** (Counter)
    Total number of database queries, labeled by:

    - ``operation``: Query type (SELECT, INSERT, UPDATE, DELETE)

    Example:

    .. code-block:: text

       db_queries_total{operation="SELECT"} 150

Business Metrics
~~~~~~~~~~~~~~~~

**guild_operations_total** (Counter)
    Total guild operations, labeled by:

    - ``operation``: Operation type (create, update, delete, fetch)
    - ``status``: Operation status (success, error)

    Example:

    .. code-block:: text

       guild_operations_total{operation="create",status="success"} 10
       guild_operations_total{operation="create",status="error"} 2

Accessing Metrics
-----------------

The metrics endpoint is available at:

.. code-block:: text

   http://localhost:8000/metrics

Example output:

.. code-block:: text

   # HELP http_requests_total Total HTTP requests
   # TYPE http_requests_total counter
   http_requests_total{method="GET",endpoint="/health",status="200"} 1234.0
   http_requests_total{method="GET",endpoint="/api/guilds/123",status="200"} 42.0
   http_requests_total{method="POST",endpoint="/api/guilds",status="201"} 10.0

   # HELP http_request_duration_seconds HTTP request latency
   # TYPE http_request_duration_seconds histogram
   http_request_duration_seconds_bucket{le="0.005",method="GET",endpoint="/health"} 1200.0
   http_request_duration_seconds_bucket{le="0.01",method="GET",endpoint="/health"} 1234.0
   http_request_duration_seconds_sum{method="GET",endpoint="/health"} 1.234
   http_request_duration_seconds_count{method="GET",endpoint="/health"} 1234.0

Prometheus Configuration
------------------------

To scrape these metrics with Prometheus, add to your ``prometheus.yml``:

.. code-block:: yaml

   scrape_configs:
     - job_name: 'byte-api'
       scrape_interval: 15s
       static_configs:
         - targets: ['localhost:8000']
       metrics_path: /metrics

Grafana Dashboards
-------------------

Recommended panels for Grafana:

1. **Request Rate**:

   .. code-block:: promql

      rate(http_requests_total[5m])

2. **Error Rate**:

   .. code-block:: promql

      rate(http_requests_total{status=~"5.."}[5m])

3. **Request Latency (p95)**:

   .. code-block:: promql

      histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

4. **Guild Operations**:

   .. code-block:: promql

      rate(guild_operations_total[5m])

Implementation Details
======================

Middleware Stack
----------------

The observability features are implemented as Litestar middleware in this order:

1. **Correlation ID Middleware** (``byte_api.lib.middleware.correlation``)
   - Extracts or generates correlation ID
   - Binds to structlog context
   - Adds to response headers

2. **Metrics Middleware** (``byte_api.lib.middleware.metrics``)
   - Tracks HTTP request count and latency
   - Records to Prometheus registry

3. **Logging Middleware** (``byte_api.lib.log.controller``)
   - Handles request/response logging

Middleware Configuration
~~~~~~~~~~~~~~~~~~~~~~~~

In ``byte_api/app.py``:

.. code-block:: python

   from byte_api.lib.middleware import correlation_middleware, metrics_middleware

   app = Litestar(
       middleware=[
           correlation_middleware,
           metrics_middleware,
           log.controller.middleware_factory,
       ],
       # ...
   )

Custom Metrics
--------------

To add custom business metrics, update ``byte_api/domain/system/controllers/metrics.py``:

.. code-block:: python

   from prometheus_client import Counter

   # Add to registry
   custom_metric = Counter(
       "custom_operations_total",
       "Total custom operations",
       ["operation_type", "status"],
       registry=registry,
   )

   # Use in your code
   custom_metric.labels(operation_type="foo", status="success").inc()

Testing
=======

Correlation ID Tests
--------------------

Location: ``tests/unit/api/lib/test_correlation_middleware.py``

Tests verify:

- Correlation IDs are generated when not provided
- Provided correlation IDs are propagated
- Each request gets a unique ID
- IDs are included in response headers

Metrics Tests
-------------

Location: ``tests/unit/api/domain/system/controllers/test_metrics.py``

Tests verify:

- ``/metrics`` endpoint returns Prometheus format
- HTTP requests are tracked
- Metrics include method and status labels
- Endpoint is excluded from OpenAPI schema

Running Tests
-------------

.. code-block:: bash

   # Run all observability tests
   uv run pytest tests/unit/api/lib/test_correlation_middleware.py -v
   uv run pytest tests/unit/api/domain/system/controllers/test_metrics.py -v

   # Or run all tests
   make test

Best Practices
==============

1. **Always include correlation IDs**: When making HTTP requests between services,
   propagate correlation IDs to enable end-to-end tracing

2. **Log at appropriate levels**:

   - ``DEBUG``: Detailed information for debugging
   - ``INFO``: General informational messages
   - ``WARNING``: Warning messages for unexpected but handled situations
   - ``ERROR``: Error messages for failures
   - ``CRITICAL``: Critical failures that require immediate attention

3. **Include context in logs**: Use structured logging with relevant context:

   .. code-block:: python

      logger.info("Guild created", guild_id=guild.id, guild_name=guild.name)

4. **Monitor key metrics**: Set up alerts for:

   - High error rates (5xx responses)
   - High latency (p95 > threshold)
   - Unusual request patterns

5. **Use correlation IDs for debugging**: When investigating issues, search logs
   by correlation ID to see the complete request flow

Troubleshooting
===============

Missing Correlation IDs
-----------------------

**Symptom**: Logs don't include correlation IDs

**Solution**: Ensure the correlation middleware is registered before the logging middleware
in ``byte_api/app.py``:

.. code-block:: python

   middleware = [
       correlation_middleware,  # Must come first
       metrics_middleware,
       log.controller.middleware_factory,
   ]

Metrics Not Updating
--------------------

**Symptom**: Prometheus metrics always show 0 or don't update

**Solution**: Verify the metrics middleware is registered and placed correctly in
the middleware stack. Check that you're accessing the correct registry:

.. code-block:: python

   from byte_api.domain.system.controllers.metrics import registry

High Memory Usage
-----------------

**Symptom**: High memory usage from metrics

**Solution**: Prometheus metrics store time series data in memory. Consider:

- Using fewer labels (high cardinality = more memory)
- Aggregating similar endpoints (e.g., ``/api/guilds/{id}`` → ``/api/guilds/*``)
- Increasing Prometheus scrape interval

References
==========

- `Prometheus Best Practices <https://prometheus.io/docs/practices/naming/>`_
- `Structured Logging with structlog <https://www.structlog.org/>`_
- `Litestar Middleware Documentation <https://docs.litestar.dev/latest/usage/middleware/>`_

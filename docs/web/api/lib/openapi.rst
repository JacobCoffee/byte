=======
openapi
=======

OpenAPI config

The Byte Bot API uses `Scalar <https://scalar.com/>`_ as the default OpenAPI documentation UI,
with Swagger UI available as a fallback option.

Accessing the API Documentation
--------------------------------

* **Scalar UI (Default)**: http://localhost:8000/api/scalar
* **Swagger UI (Fallback)**: http://localhost:8000/api/swagger
* **OpenAPI Schema**: http://localhost:8000/api/openapi.json

Custom Theme
------------

The Scalar UI uses a custom theme with Byte brand colors:

* Primary: ``#42b1a8`` (Byte Teal)
* Secondary: ``#7bcebc`` (Byte Blue)
* Accent: ``#abe6d2`` (Byte Light Blue)

The theme supports both light and dark modes with automatic detection.

Configuration
-------------

.. automodule:: byte_api.lib.openapi
     :members:

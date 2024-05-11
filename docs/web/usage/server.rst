================
About the Server
================

The server side of Byte is utilizing the `Litestar <https://litestar.dev>`_ framework.
It is an immensely powerful, fast, and easy to use framework that is perfect for Byte.

The server is responsible for handling all of the requests to and from the database,
as well as serving the frontend to the user; it utilizes the `Jinja2 <https://jinja.palletsprojects.com/en/3.0.x/>`_
templating engine to do so.

There are a few key components to the server, structured like so:

* ``app.py``: The main entry point for the server where the application factory is defined.
* ``cli.py``: The command line interface for the server.
* ``__main__.py``: The entry point for the server when running it via the command line.
* ``lib/``: A directory containing all of the server's logic, settings, and configuration.
* ``domain/``: A directory containing all of the server's domain logic, including the database models and routes.

The domain is further broken down into logical components, such as:

* ``db/``: The database models

  .. note:: These once were houses inside the respective domain components, but were moved to a separate directory to
    make it easier to manage and maintain the database models (but also because circular imports are bad).
* ``github/``: The GitHub domain logic, including connectivity to GitHub via the
  `githubkit <https://github.com/yanyongyu/githubkit>`_ library.
* ``guilds/``: The guilds domain logic, including the guilds routes and any helper functions used to perform CRUD
  operations on guilds.
* ``system/``: The system domain logic, mainly for dealing with tasks and healthchecks for the core system.
* ``web/``: The web domain logic, including the web routes, frontend resources, and templates

This structure allows for a clear separation of concerns and makes it easy to find and maintain the server's logic.

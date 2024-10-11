==========
About Byte
==========

The Discord side of Byte is utilizing the `discord.py <https://discordpy.readthedocs.io/en/latest/>`_. framework.

The structure of Byte is not too complex. There exists a ``bot.py`` file containing the main
:ref:`Byte` bot class, which includes some on-start utilities like loading cogs and ingesting
new guilds as they join into the database. The class is called via the :func:`run_bot` function
to start the bot.

The structure of Byte is not dissimilar to the structure of the server side; it has a ``lib/``
directory for common backend functionality like utilities, logging, and settings, a ``plugings/``
directory for the cogs, and a ``views/`` directory for the UI components inside of Discord.

For example, any functionality related to `Astral <https://astral.sh/>`_ is located in the
``plugins/astral/`` directory, such as ``ruff`` embeds, and it's related views are located in
``views/astral/``.

# Byte Bot

> [!WARNING]\
> This repository holds very broken code.
> It is not recommended to use this code in any way.
> It is currently being used to learn the creation of a Discord bot, used by developers
> to enhance their community/guild experience with features like
>
> - GitHub integration
> - Upload Threads/Forum Posts to GitHub discussions
> - Sync commit contributions for a repo or organization to a Discord role (Commit Club type gamification)
> - Create GitHub issue from thread, forum post, or comment
> and whatever else is found to be useful.

All of this may go down in flames, though... so... yeah - good luck 😅

## Bot

The Discord bot is built on the [Discord.py v2][discordpy] library.

## Web

The web service is a [Litestar][litestar] application. It is utilizing Jinja2[jinja] templating, TailwindCSS[tailwind],
[DaisyUI[daisy], and [Feather icons][feather] for the front end, and the backend is using the Litestar-provided 
utilities for routing, middleware, and more.

### UI Examples

![Home](docs/images/home.png)
![Dark Home](docs/images/dark-home.png)
![Dashboard](docs/images/dashboard.png)
![API - Elements](docs/images/api-elements.png)

[litestar]: https://litestar.dev
[discordpy]: https://discordpy.readthedocs.io/en/stable/
[jinja]: https://jinja.palletsprojects.com/en/3.0.x/
[tailwind]: https://tailwindcss.com/
[daisy]: https://daisyui.com/
[feather]: https://feathericons.com/

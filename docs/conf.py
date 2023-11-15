"""Sphinx configuration."""
from __future__ import annotations

import importlib.metadata
import os
import sys
from pathlib import Path

import urllib3
from dotenv import load_dotenv

from src.__metadata__ import __project__

# -- Environmental Data ------------------------------------------------------
path = Path("..").resolve()
tls_verify = False
urllib3.disable_warnings()
sys.path.insert(0, path.as_posix())
load_dotenv()

# -- Project information -----------------------------------------------------
project = __project__
copyright = "2023, Jacob Coffee"
author = "Jacob Coffee"
release = os.getenv("_BYTE_BOT_DOCS_BUILD_VERSION", importlib.metadata.version("byte-bot").rsplit(".")[0])

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinxcontrib.mermaid",
    "sphinx_copybutton",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx_click",
    "sphinx_toolbox.collapse",
    # "sphinx_design",  # not available in 7.0
    # Pending https://github.com/mansenfranzen/autodoc_pydantic/pull/162
    # "sphinxcontrib.autodoc_pydantic",
]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "anyio": ("https://anyio.readthedocs.io/en/stable/", None),
    "click": ("https://click.palletsprojects.com/en/8.1.x/", None),
    "structlog": ("https://www.structlog.org/en/stable/", None),
    "opentelemetry": ("https://opentelemetry-python.readthedocs.io/en/latest/", None),
    "litestar": ("https://docs.litestar.dev/2/", None),
    "msgspec": ("https://jcristharif.com/msgspec/", None),
}

napoleon_google_docstring = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = False
napoleon_attr_annotations = True

autoclass_content = "both"
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "exclude-members": "__weakref__",
    "show-inheritance": True,
    "class-signature": "separated",
    "typehints-format": "short",
}

nitpicky = False  # This is too much of a headache right now
nitpick_ignore = []
nitpick_ignore_regex = []

# with Path("nitpick-exceptions").open() as file:
#     for line in file:
#         if line.strip() == "" or line.startswith("#"):
#             continue
#         dtype, target = line.split(None, 1)
#         target = target.strip()
#         nitpick_ignore.append((dtype, target))
#
# with Path("nitpick-exceptions-regex").open() as file:
#     for line in file:
#         if line.strip() == "" or line.startswith("#"):
#             continue
#         dtype, target = line.split(None, 1)
#         target = target.strip()
#         nitpick_ignore_regex.append((dtype, target))

autosectionlabel_prefix_document = True
suppress_warnings = [
    "autosectionlabel.*",
    "ref.python",  # TODO: remove when https://github.com/sphinx-doc/sphinx/issues/4961 is fixed
]
todo_include_todos = True

# -- Style configuration -----------------------------------------------------
html_theme = "shibuya"
html_static_path = ["_static"]
html_css_files = [
    "custom.css",
]
html_show_sourcelink = True
html_title = "Docs"
html_favicon = "_static/badge.svg"
html_logo = "_static/badge.svg"
html_context = {
    "source_type": "github",
    "source_user": "JacobCoffee",
    "source_repo": "byte-bot",
}

brand_colors = {
    "--brand-main": {"rgb": "66, 177, 168", "hex": "#42B1A8"},
    "--byte-blue": {"rgb": "123, 206, 188", "hex": "#7BCEBC"},
    "--byte-light-blue": {"rgb": "171, 230, 210", "hex": "#ABE6D2"},
    "--byte-orange": {"rgb": "212, 163, 90", "hex": "#D4A35A"},
    "--byte-red": {"rgb": "173, 42, 19", "hex": "#AD2A13"},
    "--byte-dark": {"rgb": "12, 12, 12", "hex": "#0C0C0C"},
    "--byte-white": {"rgb": "235, 235, 233", "hex": "#EBEBE9"},
}


html_theme_options = {
    "logo_target": "/",
    "announcement": "This documentation is currently under development.",
    "github_url": "https://github.com/JacobCoffee/byte-bot",
    "discord_url": "https://discord.gg/ZVG8hN6RrJ/",
    "twitter_url": "https://twitter.com/_scriptr",
    "youtube_url": "https://youtube.com/@monorepo",
    "nav_links": [
        {"title": "Dashboard", "url": "https://byte-bot.app/"},
        {
            "title": "Sponsor me",
            "url": "https://github.com/sponsors/JacobCoffee",
            "icon": "accessibility",
        },
    ],
    # TODO: commented sections appear to not work?
    "light_css_variables": {
        # RGB
        "--sy-rc-theme": brand_colors["--brand-main"]["rgb"],
        "--sy-rc-text": brand_colors["--brand-main"]["rgb"],
        "--sy-rc-invert": brand_colors["--brand-main"]["rgb"],
        # "--sy-rc-bg": brand_colors["--byte-orange"]["rgb"],
        # Hex
        "--sy-c-link": brand_colors["--byte-orange"]["hex"],
        # "--sy-c-foot-bg": "#191919",
        "--sy-c-foot-divider": brand_colors["--brand-main"]["hex"],
        "--sy-c-foot-text": brand_colors["--byte-dark"]["hex"],
        "--sy-c-bold": brand_colors["--brand-main"]["hex"],
        "--sy-c-heading": brand_colors["--brand-main"]["hex"],
        "--sy-c-text-weak": brand_colors["--brand-main"]["hex"],
        "--sy-c-text": brand_colors["--byte-dark"]["hex"],
        "--sy-c-bg-weak": brand_colors["--byte-dark"]["rgb"],
    },
    "dark_css_variables": {
        # RGB
        "--sy-rc-theme": brand_colors["--brand-main"]["rgb"],
        "--sy-rc-text": brand_colors["--brand-main"]["rgb"],
        "--sy-rc-invert": brand_colors["--brand-main"]["rgb"],
        "--sy-rc-bg": brand_colors["--byte-dark"]["rgb"],
        # Hex
        "--sy-c-link": brand_colors["--brand-main"]["hex"],
        "--sy-c-foot-bg": brand_colors["--byte-dark"]["hex"],
        "--sy-c-foot-divider": brand_colors["--brand-main"]["hex"],
        "--sy-c-foot-text": brand_colors["--byte-white"]["hex"],
        "--sy-c-bold": brand_colors["--brand-main"]["hex"],
        "--sy-c-heading": brand_colors["--brand-main"]["hex"],
        "--sy-c-text-weak": brand_colors["--brand-main"]["hex"],
        "--sy-c-text": brand_colors["--byte-white"]["hex"],
        "--sy-c-bg-weak": brand_colors["--byte-dark"]["hex"],
        "--sy-c-bg": brand_colors["--brand-main"]["hex"],
    },
}

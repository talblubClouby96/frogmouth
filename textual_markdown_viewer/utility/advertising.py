"""Provides the 'branding' for the application."""

from typing_extensions import Final

from .. import __version__

ORGANISATION_NAME: Final[str] = "textualize"
"""The organisation name to use when creating namespaced resources."""

PACKAGE_NAME: Final[str] = "textual-markdown-viewer"
"""The name of the package."""

APPLICATION_TITLE: Final[str] = "Textual Markdown Viewer"
"""The title of the application."""

USER_AGENT: Final[str] = f"{PACKAGE_NAME} v{__version__}"
"""The user agent to use when making web requests."""

DISCORD: Final[str] = "https://discord.gg/Enf6Z3qhVr"
"""The link to the Textualize Discord server."""

TEXTUAL_URL: Final[str] = "https://textual.textualize.io/"
"""The URL people should visit to find out more about Textual."""

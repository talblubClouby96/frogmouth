"""The main screen for the application."""

from __future__ import annotations

from pathlib import Path
from webbrowser import open as open_url

from httpx import URL
from textual import __version__ as textual_version  # pylint: disable=no-name-in-module
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.events import Paste
from textual.screen import Screen
from textual.widgets import Footer, Header, Markdown

from .. import __version__
from ..data import load_history, save_history
from ..dialogs import ErrorDialog, InformationDialog
from ..utility import maybe_markdown
from ..widgets import Navigation, Omnibox, Viewer
from ..widgets.navigation_panes import History, LocalFiles


class Main(Screen):  # pylint:disable=too-many-public-methods
    """The main screen for the application."""

    BINDINGS = [
        Binding("escape", "escape", "Escpae", show=False),
        Binding("/", "omnibox", "Omnibox", show=False),
        Binding("ctrl+t", "table_of_contents", "Contents"),
        Binding("ctrl+b", "bookmarks", "Bookmarks"),
        Binding("ctrl+y", "history", "History"),
        Binding("ctrl+l", "local_files", "Local Files"),
        Binding("ctrl+left", "backward", "Back"),
        Binding("ctrl+right", "forward", "Forward"),
        Binding("f2", "about", "About"),
    ]
    """The keyboard bindings for the main screen."""

    def __init__(self, initial_location: str | None = None) -> None:
        """Initialise the main screen.

        Args:
            initial_location: The initial location to view.
        """
        super().__init__()
        self._initial_location = initial_location

    def compose(self) -> ComposeResult:
        """Compose the main screen.."""
        yield Header()
        yield Omnibox()
        with Horizontal():
            yield Navigation()
            yield Viewer()
        yield Footer()

    async def visit(self, location: Path | URL, remember: bool = True) -> None:
        """Visit the given location.

        Args:
            location: The location to visit.
            remember: Should the visit be added to the history?
        """
        if maybe_markdown(location):
            await self.query_one(Viewer).visit(location, remember)
            self.query_one(Viewer).focus()
        else:
            open_url(str(location))

    async def on_mount(self) -> None:
        """Set up the main screen once the DOM is ready."""

        # Load up any history that might be saved.
        if history := load_history():
            self.query_one(Viewer).load_history(history)

        # If we've not been tasked to start up looking at a very specific
        # location (in other words if no location was passed on the command
        # line), and if there is some history...
        if self._initial_location is None and history:
            # ...start up revisiting the last location the user was looking
            # at.
            await self.query_one(Viewer).visit(history[-1], remember=False)
        elif self._initial_location is not None:
            # Seems there is an initial location; so let's start up looking
            # at that.
            (omnibox := self.query_one(Omnibox)).value = self._initial_location
            await omnibox.action_submit()

    async def on_omnibox_local_view_command(
        self, event: Omnibox.LocalViewCommand
    ) -> None:
        """Handle the omnibox asking us to view a particular file.

        Args:
            event: The local view command event.
        """
        await self.visit(event.path)

    async def on_omnibox_remote_view_command(
        self, event: Omnibox.RemoteViewCommand
    ) -> None:
        """Handle the omnibox asking us to view a particular URL.

        Args:
            event: The remote view command event.
        """
        await self.visit(event.url)

    def on_omnibox_contents_command(self) -> None:
        """Handle being asked to show the table of contents."""
        self.action_table_of_contents()

    async def on_omnibox_local_files_command(self) -> None:
        """Handle being asked to view the local files picker."""
        await self.action_local_files()

    async def on_omnibox_local_chdir_command(
        self, event: Omnibox.LocalChdirCommand
    ) -> None:
        """Handle being asked to view a new directory in the local files picker."""
        if not event.target.exists():
            self.app.push_screen(
                ErrorDialog("No such directory", f"{event.target} does not exist.")
            )
        elif not event.target.is_dir():
            self.app.push_screen(
                ErrorDialog("Not a directory", f"{event.target} is not a directory.")
            )
        await self.query_one(Navigation).jump_to_local_files(event.target)

    def on_omnibox_history_command(self) -> None:
        """Handle being asked to view the history."""
        self.action_history()

    def on_omnibox_about_command(self) -> None:
        """Handle being asked to show the about dialog."""
        self.action_about()

    def on_omnibox_quit_command(self) -> None:
        """Handle being asked to quit."""
        self.app.exit()

    async def on_local_files_goto(self, event: LocalFiles.Goto) -> None:
        """Visit a local file in the viewer.

        Args:
            event: The local file visit request event.
        """
        await self.visit(event.location)

    async def on_history_goto(self, event: History.Goto) -> None:
        """Handle a request to go to a location from history.

        Args:
            event: The event to handle.
        """
        await self.visit(
            event.location, remember=event.location != self.query_one(Viewer).location
        )

    def on_viewer_location_changed(self, event: Viewer.LocationChanged) -> None:
        """Update for the location being changed.

        Args:
            event: The location change event.
        """
        self.query_one(Omnibox).visiting = (
            str(event.viewer.location) if event.viewer.location is not None else ""
        )

    def on_viewer_history_updated(self, event: Viewer.HistoryUpdated) -> None:
        """Handle the viewer updating the history.

        Args:
            event: The history update event.
        """
        self.query_one(Navigation).history.update_from(event.viewer.history.locations)
        save_history(event.viewer.history.locations)

    def on_markdown_table_of_contents_updated(
        self, event: Markdown.TableOfContentsUpdated
    ) -> None:
        """Handle the table of contents of the document being updated.

        Args:
            event: The table of contents update event to handle.
        """
        # We don't handle this, the navigation pane does. Bounce the event
        # over there.
        self.query_one(Navigation).table_of_contents.on_table_of_contents_updated(event)

    def on_markdown_table_of_contents_selected(
        self, event: Markdown.TableOfContentsSelected
    ) -> None:
        """Handle the user selecting something from the table of contents.

        Args:
            event: The table of contents selection event to handle.
        """
        self.query_one(Viewer).scroll_to_block(event.block_id)

    async def on_markdown_link_clicked(self, event: Markdown.LinkClicked) -> None:
        """Handle a link being clicked in the Markdown document.

        Args:
            event: The Markdown link click event to handle.
        """
        self.query_one(Omnibox).value = event.href
        await self.query_one(Omnibox).action_submit()

    async def on_paste(self, event: Paste) -> None:
        """Handle a paste event.

        Args:
            event: The paste event.

        This method is here to capture paste events that look like the name
        of a local file (later I may add URL support too).
        """
        if (candidate_file := Path(event.text)).exists():
            await self.visit(candidate_file)

    def action_escape(self) -> None:
        """Process the escape key."""
        if self.query_one(Omnibox).has_focus:
            self.app.exit()
        else:
            self.query_one(Omnibox).focus()

    def action_omnibox(self) -> None:
        """Jump to the omnibox."""
        self.query_one(Omnibox).focus()

    def action_table_of_contents(self) -> None:
        """Display and focus the table of contents pane."""
        self.query_one(Navigation).jump_to_contents()

    async def action_local_files(self) -> None:
        """Display and focus the local files selection pane."""
        await self.query_one(Navigation).jump_to_local_files()

    def action_bookmarks(self) -> None:
        """Display and focus the bookmarks selection pane."""
        self.query_one(Navigation).jump_to_bookmarks()

    def action_history(self) -> None:
        """Display and focus the history pane."""
        self.query_one(Navigation).jump_to_history()

    async def action_backward(self) -> None:
        """Go backward in the history."""
        await self.query_one(Viewer).back()

    async def action_forward(self) -> None:
        """Go forward in the history."""
        await self.query_one(Viewer).forward()

    def action_about(self) -> None:
        """Show the about dialog."""
        self.app.push_screen(
            InformationDialog(
                "About textual-markdown-viewer",
                f"Version {__version__}.\n\n"
                f"Built with [link=https://textual.textualize.io/]Textual[/] v{textual_version}.\n\n"
                "[link]https://github.com/Textualize/textual-markdown-viewer[/]",
            )
        )

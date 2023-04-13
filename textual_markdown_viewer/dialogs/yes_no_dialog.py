"""Provides a dialog for getting a yes/no response from the user."""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Horizontal, Vertical
from textual.message import Message
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import Button, Static


class YesNoDialog(ModalScreen):
    """A dialog for asking a user a yes/no question."""

    DEFAULT_CSS = """
    YesNoDialog {
        align: center middle;
    }

    YesNoDialog > Vertical {
        background: $panel;
        height: auto;
        width: auto;
        border: thick $primary;
    }

    YesNoDialog > Vertical > * {
        width: auto;
        height: auto;
    }

    YesNoDialog Static {
        width: auto;
    }

    YesNoDialog .spaced {
        padding: 1;
    }

    YesNoDialog #question {
        min-width: 100%;
        border-top: solid $primary;
        border-bottom: solid $primary;
    }

    YesNoDialog Button {
        margin-right: 1;
    }

    YesNoDialog #buttons {
        width: 100%;
        align-horizontal: right;
        padding-right: 1;
    }
    """
    """The default CSS for the yes/no dialog."""

    BINDINGS = [
        Binding("left,up", "focus_previous", "", show=False),
        Binding("right,down", "focus_next", "", show=False),
        Binding("escape", "app.pop_screen", "", show=False),
    ]
    """Bindings for the yes/no dialog."""

    def __init__(  # pylint:disable=redefined-builtin,too-many-arguments
        self,
        requester: Widget,
        title: str,
        question: str,
        yes_label: str = "Yes",
        no_label: str = "No",
        yes_first: bool = True,
        cargo: Any = None,
        id: str | None = None,
    ) -> None:
        """Initialise the yes/no dialog.

        Args:
            requester: The widget requesting the input.
            title: The title for the dialog.
            question: The question to ask.
            yes_label: The optional label for the yes button.
            no_label: The optional label for the no button.
            yes_first: Should the yes button come first?
            cargo: Any cargo value for the question.
            id: The ID for the dialog.
        """
        super().__init__(id=id)
        self._requester = requester
        """A reference to the widget asking the question."""
        self._title = title
        """The title for the dialog."""
        self._question = question
        """The question to ask the user."""
        self._aye = yes_label
        """The label for the yes button."""
        self._naw = no_label
        """The label for the no button."""
        self._aye_first = yes_first
        """Should the positive button come first?"""
        self._cargo = cargo
        """Any cargo data for the reply."""

    def compose(self) -> ComposeResult:
        """Compose the content of the dialog."""
        with Vertical():
            with Center():
                yield Static(self._title, classes="spaced")
            yield Static(self._question, id="question", classes="spaced")
            with Horizontal(id="buttons"):
                aye = Button(self._aye, id="yes")
                naw = Button(self._naw, id="no")
                if self._aye_first:
                    aye.variant = "primary"
                    yield aye
                    yield naw
                else:
                    naw.variant = "primary"
                    yield naw
                    yield aye

    def on_mount(self) -> None:
        """Configure the dialog once the DOM is ready."""
        self.query(Button).first().focus()

    class Reply(Message):
        """Base class for replies from the yes/no dialog."""

        def __init__(self, sender_id: str | None, cargo: Any = None) -> None:
            """Initialise the reply message.

            Args:
                sender_id: The ID of the dialog sending the message.
                cargo: Any cargo data for the result.
            """
            super().__init__()
            self.sender_id: str | None = sender_id
            """The ID of the sending dialog."""
            self.cargo: Any = cargo
            """Cargo data for the result."""

    class PositiveReply(Reply):
        """A positive reply from the yes/no dialog."""

    class NegativeReply(Reply):
        """A negative reply from the yes/no dialog."""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle a button being pressed on the dialog.

        Args:
            event: The event to handle.
        """
        self._requester.post_message(
            (self.PositiveReply if event.button.id == "yes" else self.NegativeReply)(
                self.id, self._cargo
            )
        )
        self.app.pop_screen()

from typing import ClassVar

from textual.app import App, ComposeResult, ScreenStackError
from textual.binding import Binding, BindingType
from textual.screen import Screen
from textual.widgets import Footer, Header, LoadingIndicator

from graph_viewer import GraphViewer, make_nodes


class LoadingScreen(Screen):
    def compose(self) -> ComposeResult:
        yield LoadingIndicator()


class NotebookApp(App[None]):
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("q", "quit", "Quit app", show=True),
    ]
    CSS_PATH: ClassVar[str] = "main.css"
    SCREENS = {"loading_screen": LoadingScreen()}

    def compose(self) -> ComposeResult:
        self._setup()

        yield Header(show_clock=True)
        yield GraphViewer(nodes=make_nodes())
        yield Footer()

    def action_toggledark(self) -> None:
        self.dark = not self.dark

    def on_loadable_widget_loading(self):
        self.push_screen("loading_screen")

    def on_loadable_widget_loaded(self):
        try:
            self.pop_screen()
        except ScreenStackError:
            pass

    def _setup(self):
        ...


if __name__ == "__main__":
    app = NotebookApp()
    app.run()

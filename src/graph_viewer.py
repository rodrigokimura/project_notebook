from __future__ import annotations

from rich.console import RenderableType
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label, Static


class GraphViewer(Widget):
    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        nodes: list[Node] | None = None,
        connectors: list[Connector] | None = None,
    ) -> None:
        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled
        )
        self.nodes = nodes
        self.connectors = connectors

    def compose(self) -> ComposeResult:
        if self.nodes:
            for node in self.nodes:
                yield node
        if self.connectors:
            for conn in self.connectors:
                yield conn


class Node(Widget):
    DEFAULT_CSS = """
    Node {
        height: auto;
        width: auto;
        padding: 0;
        align: center middle;
        text-align: center;
        border: round white;
    }
    """

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        position: tuple[int, int] = (0, 0),
    ) -> None:
        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled
        )
        self.position = position

    def render(self):
        x, y = self.position
        w, h = self.outer_size
        x *= 2
        w /= 4
        h /= 2
        self.styles.offset = int(x - w), int(y - h)
        return self.name


class VerticalLine(Widget):
    DEFAULT_CSS = """
    VerticalLine {
        height: 1;
        width: 3;
        border: none;
    }
    """

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        position: tuple[int, int] = (0, 0),
    ) -> None:
        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled
        )
        self.position = position

    def render(self):
        self.styles.width = 1
        return "|"


class Connector(Static):
    DEFAULT_CSS = """
    Connector {
        height: auto;
        width: auto;
        border: none;
    }
    """

    def __init__(
        self,
        renderable: RenderableType = "",
        *,
        expand: bool = False,
        shrink: bool = False,
        markup: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        start: tuple[int, int] = (0, 0),
        end: tuple[int, int] = (0, 0),
    ) -> None:
        super().__init__(
            renderable,
            expand=expand,
            shrink=shrink,
            markup=markup,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.start = start
        self.end = end

    def compose(self) -> ComposeResult:
        x, y = self.start
        x *= 2
        self.styles.offset = x, y

        x, y_start = self.start
        _, y_end = self.end
        for y in range(y_start, y_end + 1):
            yield VerticalLine(position=(x, y))


def make_nodes():
    node_1 = Node(name="test 1", position=(0, 0))
    node_2 = Node(name="test2", position=(8, 8))
    node_3 = Node(name="test3", position=(10, 10))
    node_4 = Node(name="test4", position=(12, 12))
    return list(locals().values())


def make_connectors():
    conn = Connector(start=(10, 2), end=(10, 10))
    return list(locals().values())

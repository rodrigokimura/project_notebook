from __future__ import annotations

from textual.app import ComposeResult
from textual.layouts.horizontal import HorizontalLayout
from textual.layouts.vertical import VerticalLayout
from textual.widget import Widget

from connectors import Connector, Point
from layouts import FreeLayout


class GraphViewer(Widget):
    DEFAULT_CSS = """
    GraphViewer {
        layers: connectors nodes;
    }
    """

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
        self._default_layout = FreeLayout()
        self.nodes = nodes
        self.connectors = connectors

    def compose(self) -> ComposeResult:
        if self.connectors:
            for conn in self.connectors:
                yield conn
        if self.nodes:
            for node in self.nodes:
                yield node


class Node(Widget):
    DEFAULT_CSS = """
    Node {
        height: auto;
        width: auto;
        padding: 0;
        border: round white;
        layer: nodes;
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
        # x *= 2
        w /= 2
        h /= 2
        self.styles.offset = int(x - w), int(y - h)
        return self.name


def make_nodes():
    node_1 = Node(name="test 1", position=(2, 0))
    # node_2 = Node(name="test2", position=(0, 3))
    # node_3 = Node(name="test3", position=(10, 10))
    # node_4 = Node(name="test4", position=(12, 11))
    return list(locals().values())


def make_connectors():
    conn1 = Connector(start=Point(5, 5), end=Point(15, 15))
    conn2 = Connector(start=Point(20, 30), end=Point(10, 23), classes="test")
    return list(locals().values())

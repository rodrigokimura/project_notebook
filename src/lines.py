from textual.widget import Widget

from geometry import Point


class Line(Widget):
    DEFAULT_CSS = """
    Line {
        height: 1;
        width: 1;
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
        position: Point = Point(0, 0),
        length: int = 1,
    ) -> None:
        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled
        )
        self.position = position
        self.length = length


class VerticalLine(Line):
    def render(self):
        self.styles.offset = self.position.x, self.position.y
        self.styles.width = 1
        self.styles.height = self.length
        return "│" * self.length
        # return ":" * self.length


class HorizontalLine(Line):
    def render(self):
        self.styles.offset = self.position.x, self.position.y
        self.styles.height = 1
        self.styles.width = self.length
        return "─" * self.length
        # return "." * self.length

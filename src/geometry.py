import enum
from dataclasses import dataclass

from textual.geometry import Offset
from textual.widget import Widget
from textual.widgets import Static

Point = Offset


class _Line(Widget):
    DEFAULT_CSS = """
    _Line {
        height: 1;
        width: 1;
        border: none;
        background: white 0%;
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
        sign: bool = True,
    ) -> None:
        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled
        )
        self.position = position
        self.length = length
        self.sign = sign


class _Char(Widget):
    DEFAULT_CSS = """
    _Char {
        height: 1;
        width: 1;
        border: none;
        background: white 0%;
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
        char: str = ".",
    ) -> None:
        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled
        )
        self.position = position
        self.char = char

    def render(self):
        self.styles.offset = self.position.x, self.position.y
        return self.char


class VerticalLine(_Line):
    def render(self):
        x, y = self.position.x, self.position.y
        if not self.sign:
            y -= self.length - 1
        self.styles.offset = x, y
        self.styles.width = 1
        self.styles.height = self.length
        return "│" * self.length
        # return ":" * self.length


class HorizontalLine(_Line):
    def render(self):
        x, y = self.position.x, self.position.y
        if not self.sign:
            x -= self.length - 1
        self.styles.offset = x, y
        self.styles.height = 1
        self.styles.width = self.length
        return "─" * self.length
        # return "." * self.length


def comparison_map(a: int, b: int):
    if a > b:
        return 1
    if a < b:
        return -1
    return 0


class Direction(enum.Enum):
    V = enum.auto()
    H = enum.auto()

    def other(self):
        if self == Direction.H:
            return Direction.V
        return Direction.H


class TerminalType(enum.Enum):
    START = enum.auto()
    END = enum.auto()


class Orientation(enum.Enum):
    NE = enum.auto()
    NW = enum.auto()
    SE = enum.auto()
    SW = enum.auto()


@dataclass
class Segment:
    @property
    def widget(self):
        return Widget()


@dataclass
class Terminal(Segment):
    char_map = {
        TerminalType.START: "+",
        TerminalType.END: "*",
    }

    point: Point
    terminal_type: TerminalType

    @property
    def widget(self):
        return _Char(position=self.point, char=self.char_map[self.terminal_type])


@dataclass
class Line(Segment):
    widget_map = {
        Direction.V: VerticalLine,
        Direction.H: HorizontalLine,
    }

    point: Point
    direction: Direction
    length: int
    sign: bool

    @property
    def widget(self):
        return self.widget_map[self.direction](
            position=self.point, length=self.length, sign=self.sign
        )


@dataclass
class Elbow(Segment):
    char_map = {
        Orientation.NE: "╮",
        Orientation.NW: "╭",
        Orientation.SE: "╯",
        Orientation.SW: "╰",
    }
    point: Point
    orientation: Orientation

    @property
    def widget(self):
        return _Char(position=self.point, char=self.char_map[self.orientation])


class Connector:
    def __init__(self, start: Point, end: Point) -> None:
        self.start = start
        self.end = end
        self.direction = (
            Direction.H if abs(end.x - start.x) >= abs(end.y - start.y) else Direction.V
        )
        self.steps = 1
        self.segments: list[Segment] = []
        self.rightwards = comparison_map(end.x, start.x)
        self.downwards = comparison_map(end.y, start.y)
        self._build()

    def _build(self):
        add_segment = self.segments.append
        is_null = self.start.get_distance_to(self.end) == 0
        if is_null:
            return

        add_segment(Terminal(self.start, TerminalType.START))

        point = self.start
        start = self.start
        if self.direction == Direction.H:
            start += Point(self.rightwards, 0)
        else:
            start += Point(0, self.downwards)

        is_straight = not self.downwards or not self.rightwards
        if is_straight:
            end = self.end
            # end -= Point(self.rightwards, self.downwards)

            length = int(start.get_distance_to(end))
            if length >= 1:
                if self.direction == Direction.H:
                    sign = self.rightwards == 1
                else:
                    sign = self.downwards == 1
                add_segment(Line(start, self.direction, length, sign))
            add_segment(Terminal(self.end, TerminalType.END))
            return

        end = self.end
        if self.direction == Direction.H:
            length = abs((end.x - start.x) // 2)
            sign = self.rightwards == 1
        else:
            length = abs((end.y - start.y) // 2)
            sign = self.downwards == 1
        add_segment(Line(start, self.direction, length, sign))

        if self.direction == Direction.H:
            start += Point(self.rightwards * length, 0)
        else:
            start += Point(0, self.downwards * length)
        add_segment(Elbow(start, Orientation.SW))

        if self.direction.other() == Direction.H:
            step_length = abs(end.x - start.x) - 1
            start += Point(self.rightwards, 0)
            sign = self.rightwards == 1
        else:
            step_length = abs(end.y - start.y) - 1
            start += Point(0, self.downwards)
            sign = self.downwards == 1
        add_segment(Line(start, self.direction.other(), step_length, sign))

        if self.direction.other() == Direction.H:
            start += Point(self.rightwards * step_length, 0)
        else:
            start += Point(0, self.downwards * step_length)
        add_segment(Elbow(start, Orientation.NE))

        if self.direction == Direction.H:
            length = end.x - start.x - 1
            sign = self.rightwards == 1
            start += Point(self.rightwards, 0)
        else:
            length = end.y - start.y - 1
            sign = self.downwards == 1
            start += Point(0, self.downwards)

        add_segment(Line(start, self.direction, length, sign))

        add_segment(Terminal(self.end, TerminalType.END))

    def _inc(self, point: Point):
        x, y = point
        if self.direction == Direction.H:
            x += self.rightwards
        else:
            y += self.downwards
        return Point(x, y)

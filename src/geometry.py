import enum
from dataclasses import dataclass

from textual.geometry import Offset
from textual.widget import Widget

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


class HorizontalLine(_Line):
    def render(self):
        x, y = self.position.x, self.position.y
        if not self.sign:
            x -= self.length - 1
        self.styles.offset = x, y
        self.styles.height = 1
        self.styles.width = self.length
        return "─" * self.length


def comparison_map(a: int, b: int):
    if a > b:
        return 1
    if a < b:
        return -1
    return 0


class Direction(enum.Enum):
    V = enum.auto()
    H = enum.auto()

    def shift(self):
        if self == Direction.H:
            return Direction.V
        return Direction.H


class TerminalType(enum.Enum):
    START = enum.auto()
    UP = enum.auto()
    DOWN = enum.auto()
    LEFT = enum.auto()
    RIGHT = enum.auto()


class Orientation(enum.Enum):
    NE = enum.auto()
    NW = enum.auto()
    SE = enum.auto()
    SW = enum.auto()

    def flip(self, direction: Direction):
        map = {
            Direction.V: {
                Orientation.NE: Orientation.SE,
                Orientation.NW: Orientation.SW,
                Orientation.SE: Orientation.NE,
                Orientation.SW: Orientation.NW,
            },
            Direction.H: {
                Orientation.NE: Orientation.NW,
                Orientation.NW: Orientation.NE,
                Orientation.SE: Orientation.SW,
                Orientation.SW: Orientation.SE,
            },
        }
        return map[direction][self]


@dataclass
class Segment:
    @property
    def widget(self):
        return Widget()


@dataclass
class Terminal(Segment):
    char_map = {
        TerminalType.START: "⭘",
        TerminalType.UP: "▲",
        TerminalType.DOWN: "▼",
        TerminalType.LEFT: "◀",
        TerminalType.RIGHT: "▶",
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
        is_null = self.start.get_distance_to(self.end) == 0
        if is_null:
            return

        cursor = self.start
        cursor = self._add_start_terminal(cursor)

        is_straight = not self.downwards or not self.rightwards
        if is_straight:
            cursor = self._add_straight_body(cursor)
        else:
            cursor = self._add_first_body_half(cursor)

            cursor = self._add_first_elbow(cursor)
            cursor = self._add_step(cursor)
            cursor = self._add_second_elbow(cursor)

            cursor = self._add_second_body_half(cursor)

        assert self.end == cursor
        cursor = self._add_end_terminal(cursor)

    def _add_segment(self, segment: Segment):
        self.segments.append(segment)

    def _add_start_terminal(self, cursor: Point):
        self._add_segment(Terminal(cursor, TerminalType.START))
        if self.direction == Direction.H:
            cursor += Point(self.rightwards, 0)
        else:
            cursor += Point(0, self.downwards)
        return cursor

    def _add_straight_body(self, cursor: Point):
        end = self.end
        length = int(cursor.get_distance_to(end))
        if self.direction == Direction.H:
            sign = self.rightwards == 1
        else:
            sign = self.downwards == 1
        if length >= 1:
            self._add_segment(Line(cursor, self.direction, length, sign))
        if self.direction == Direction.H:
            cursor += Point(self.rightwards * length, 0)
        else:
            cursor += Point(0, self.downwards * length)
        return cursor

    def _add_first_body_half(self, cursor: Point):
        end = self.end
        if self.direction == Direction.H:
            length = abs((end.x - cursor.x) // 2)
            sign = self.rightwards == 1
        else:
            length = abs((end.y - cursor.y) // 2)
            sign = self.downwards == 1
        self._add_segment(Line(cursor, self.direction, length, sign))
        if self.direction == Direction.H:
            cursor += Point(self.rightwards * length, 0)
        else:
            cursor += Point(0, self.downwards * length)
        return cursor

    def _add_first_elbow(self, cursor: Point):
        orientation = Orientation.NE
        if self.rightwards == 1:
            orientation = orientation.flip(Direction.H)
            if self.downwards == 1:
                orientation = orientation.flip(Direction.V)
        self._add_segment(Elbow(cursor, orientation))
        if self.direction.shift() == Direction.H:
            cursor += Point(self.rightwards, 0)
        else:
            cursor += Point(0, self.downwards)
        return cursor

    def _add_step(self, cursor: Point):
        end = self.end
        if self.direction.shift() == Direction.H:
            length = abs(end.x - cursor.x)
            sign = self.rightwards == 1
        else:
            length = abs(end.y - cursor.y)
            sign = self.downwards == 1
        self._add_segment(Line(cursor, self.direction.shift(), length, sign))

        if self.direction.shift() == Direction.H:
            cursor += Point(self.rightwards * length, 0)
        else:
            cursor += Point(0, self.downwards * length)
        return cursor

    def _add_second_elbow(self, cursor: Point):
        orientation = Orientation.SW
        if self.rightwards == 1:
            orientation = orientation.flip(Direction.H)
            if self.downwards == 1:
                orientation = orientation.flip(Direction.V)
        self._add_segment(Elbow(cursor, orientation))
        if self.direction == Direction.H:
            cursor += Point(self.rightwards, 0)
        else:
            cursor += Point(0, self.downwards)
        return cursor

    def _add_second_body_half(self, cursor: Point):
        end = self.end
        if self.direction == Direction.H:
            length = end.x - cursor.x
            sign = self.rightwards == 1
        else:
            length = end.y - cursor.y
            sign = self.downwards == 1
        self._add_segment(Line(cursor, self.direction, length, sign))
        if self.direction == Direction.H:
            cursor += Point(self.rightwards * length, 0)
        else:
            cursor += Point(0, self.downwards * length)
        return cursor

    def _add_end_terminal(self, cursor: Point):
        if self.direction == Direction.H:
            sign = self.rightwards == 1
            terminal_type = TerminalType.RIGHT if sign else TerminalType.LEFT
        else:
            sign = self.downwards == 1
            terminal_type = TerminalType.DOWN if sign else TerminalType.UP
        self._add_segment(Terminal(cursor, terminal_type))
        if self.direction == Direction.H:
            cursor += Point(self.rightwards, 0)
        else:
            cursor += Point(0, self.downwards)
        return cursor

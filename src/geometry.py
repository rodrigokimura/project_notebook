import enum
from dataclasses import dataclass

from textual.geometry import Offset

Point = Offset


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
    ...


@dataclass
class Terminal(Segment):
    char_map = {
        TerminalType.START: "+",
        TerminalType.END: "*",
    }

    point: Point
    terminal_type: TerminalType


@dataclass
class Line(Segment):
    char_map = {
        Direction.V: "|",
        Direction.H: "─",
    }

    point: Point
    direction: Direction
    length: int
    sign: bool


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

        is_straight = not self.downwards or not self.rightwards
        if is_straight:
            start = self.start
            start += Point(self.rightwards, self.downwards)
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

        add_segment(Line(self.start + Point(), self.direction, 1, True))

        point = self._inc(self.start)
        add_segment(Elbow(point, Orientation.SW))

        add_segment(Line(self.start, self.direction.other(), 1, True))
        add_segment(Elbow(self.start, Orientation.SW))
        add_segment(Line(self.start, self.direction, 1, True))

        add_segment(Terminal(self.end, TerminalType.END))

    def _inc(self, point: Point):
        x, y = point
        if self.direction == Direction.H:
            x += self.rightwards
        else:
            y += self.downwards
        return Point(x, y)

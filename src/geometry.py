from textual.geometry import Offset

Point = Offset


class Terminal:
    def __init__(self, point: Point) -> None:
        self.point = point


class Segment:
    def __init__(self) -> None:
        ...


class Conn:
    def __init__(self, start: Point, end: Point) -> None:
        ...

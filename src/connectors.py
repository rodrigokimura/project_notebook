import enum

from textual.app import ComposeResult
from textual.geometry import Region
from textual.widget import Widget

from geometry import Point
from layouts import FreeLayout
from lines import HorizontalLine, VerticalLine


class Direction(str, enum.Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class _Connector(Widget):
    DEFAULT_CSS = """
    Connector {
        height: auto;
        width: auto;
        border: none;
        layer: connectors;
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
        start: Point = Point(0, 0),
        end: Point = Point(0, 0),
    ) -> None:
        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled
        )
        self._default_layout = FreeLayout()
        self.start = start
        self.end = end

    def compose(self) -> ComposeResult:
        steps = 2
        segments = steps + 1

        top = min(self.start.y, self.end.y)
        left = min(self.start.x, self.end.y)
        width = abs(self.end.x - self.start.x)
        height = abs(self.end.y - self.start.y)

        region = Region(
            left,
            top,
            width,
            height,
        )
        self.styles.offset = (region.x, region.y)
        self.styles.width = region.width + steps
        self.styles.height = region.height + steps
        self.styles.opacity = 0.7

        direction: Direction = Direction.VERTICAL
        # direction: Direction = Direction.HORIZONTAL

        is_vertical = direction == Direction.VERTICAL

        spans = (region.line_span, region.column_span)
        self.line_types = (HorizontalLine, VerticalLine)

        segment_span = spans[is_vertical]
        step_span = spans[not is_vertical]
        segment_line_type = self.line_types[is_vertical]
        step_line_type = self.line_types[not is_vertical]

        start, end = segment_span
        total_length = end - start
        segment_lengths = [total_length // segments] * segments
        if remainder := total_length % segments:
            segment_lengths[segments // 2] += remainder

        start, end = step_span
        total_length = end - start
        step_lengths = [total_length // steps] * steps
        if remainder := total_length % steps:
            step_lengths[steps // 2] += remainder
        step_lengths.append(0)

        segment_acc = 0
        step_acc = 0
        for segment, step in zip(segment_lengths, step_lengths):
            if is_vertical:
                if segment:
                    point = Point(step_acc, segment_acc)
                    yield segment_line_type(position=point, length=segment)
                segment_acc += segment - 1

                if step:
                    point = Point(step_acc, segment_acc)
                    yield step_line_type(position=point, length=step)
                step_acc += step - 1
            else:
                if segment:
                    point = Point(step_acc, segment_acc)
                    yield segment_line_type(position=point, length=segment)
                step_acc += step - 1

                if step:
                    point = Point(step_acc, segment_acc)
                    yield step_line_type(position=point, length=step)
                segment_acc += segment + 1

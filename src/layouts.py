from fractions import Fraction

from textual._layout import ArrangeResult, Layout, WidgetPlacement
from textual.geometry import Region, Size, Spacing
from textual.widget import Widget


class FreeLayout(Layout):
    """Used to layout Widgets freelly on screen."""

    name = "free"

    def arrange(
        self, parent: Widget, children: list[Widget], size: Size
    ) -> ArrangeResult:
        placements: list[WidgetPlacement] = []
        add_placement = placements.append

        for widget in children:
            overlay = widget.styles.overlay == "screen"

            box_model = widget._get_box_model(parent.size, size, Fraction(), Fraction())

            region = Region(0, 0, int(box_model.width), int(box_model.height))
            add_placement(WidgetPlacement(region, Spacing(), widget, 0, False, overlay))

        return placements

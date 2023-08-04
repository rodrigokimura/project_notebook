from geometry import Connector, Direction, Elbow, Line, Point, Terminal, TerminalType


def test_line_build():
    """
    ⭘──╮
       |
       ╰──▶
    """
    conn = Connector(Point(0, 0), Point(6, 2))

    assert len(conn.segments) == 7

    seg = conn.segments[0]
    assert isinstance(seg, Terminal)
    assert seg.point == Point(0, 0)

    seg = conn.segments[1]
    assert isinstance(seg, Line)
    assert seg == Line(Point(1, 0), Direction.H, 2, True)

    seg = conn.segments[2]
    assert isinstance(seg, Elbow)
    assert seg.point == Point(3, 0)

    assert isinstance(conn.segments[3], Line)
    assert conn.segments[3].direction == Direction.V
    assert isinstance(conn.segments[4], Elbow)
    assert isinstance(conn.segments[5], Line)
    assert isinstance(conn.segments[6], Terminal)


def test_comp():
    assert Point(0, 1) == Point(0, 1)
    assert Point(0, 0) != Point(0, 1)


def test_null_connectors():
    conn = Connector(Point(0, 0), Point(0, 0))
    assert conn.segments == []

    conn = Connector(Point(1, 2), Point(1, 2))
    assert conn.segments == []


def test_straight_connectors_without_body():
    conn = Connector(Point(0, 0), Point(1, 0))
    assert len(conn.segments) == 2
    assert conn.segments[0] == Terminal(Point(0, 0), TerminalType.START)
    assert conn.segments[1] == Terminal(Point(1, 0), TerminalType.RIGHT)

    conn = Connector(Point(0, 0), Point(0, 1))
    assert len(conn.segments) == 2
    assert conn.segments[0] == Terminal(Point(0, 0), TerminalType.START)
    assert conn.segments[1] == Terminal(Point(0, 1), TerminalType.DOWN)

    conn = Connector(Point(1, 0), Point(0, 0))
    assert len(conn.segments) == 2
    assert conn.segments[0] == Terminal(Point(1, 0), TerminalType.START)
    assert conn.segments[1] == Terminal(Point(0, 0), TerminalType.LEFT)

    conn = Connector(Point(0, 1), Point(0, 0))
    assert len(conn.segments) == 2
    assert conn.segments[0] == Terminal(Point(0, 1), TerminalType.START)
    assert conn.segments[1] == Terminal(Point(0, 0), TerminalType.UP)


def test_straight_connectors_with_body():
    conn = Connector(Point(0, 0), Point(2, 0))
    assert len(conn.segments) == 3
    assert conn.segments[0] == Terminal(Point(0, 0), TerminalType.START)
    assert conn.segments[1] == Line(Point(1, 0), Direction.H, 1, True)
    assert conn.segments[2] == Terminal(Point(2, 0), TerminalType.RIGHT)

    # inverted
    conn = Connector(Point(2, 0), Point(0, 0))
    assert len(conn.segments) == 3
    assert conn.segments[0] == Terminal(Point(2, 0), TerminalType.START)
    assert conn.segments[1] == Line(Point(1, 0), Direction.H, 1, False)
    assert conn.segments[2] == Terminal(Point(0, 0), TerminalType.LEFT)

    conn = Connector(Point(0, 0), Point(5, 0))
    assert len(conn.segments) == 3
    assert conn.segments[0] == Terminal(Point(0, 0), TerminalType.START)
    assert conn.segments[1] == Line(Point(1, 0), Direction.H, 4, True)
    assert conn.segments[2] == Terminal(Point(5, 0), TerminalType.RIGHT)

    # inverted
    conn = Connector(Point(5, 0), Point(0, 0))
    assert len(conn.segments) == 3
    assert conn.segments[0] == Terminal(Point(5, 0), TerminalType.START)
    assert conn.segments[1] == Line(Point(4, 0), Direction.H, 4, False)
    assert conn.segments[2] == Terminal(Point(0, 0), TerminalType.LEFT)

    conn = Connector(Point(0, 0), Point(0, 2))
    assert len(conn.segments) == 3
    assert conn.segments[0] == Terminal(Point(0, 0), TerminalType.START)
    assert conn.segments[1] == Line(Point(0, 1), Direction.V, 1, True)
    assert conn.segments[2] == Terminal(Point(0, 2), TerminalType.DOWN)

    conn = Connector(Point(0, 0), Point(0, 5))
    assert len(conn.segments) == 3
    assert conn.segments[0] == Terminal(Point(0, 0), TerminalType.START)
    assert conn.segments[1] == Line(Point(0, 1), Direction.V, 4, True)
    assert conn.segments[2] == Terminal(Point(0, 5), TerminalType.DOWN)

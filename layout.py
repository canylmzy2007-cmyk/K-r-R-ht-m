"""Özgün yük terminali planı. Mesafeler oyun dünyası birimindedir."""

from dataclasses import dataclass
from collections import deque
from math import ceil, hypot

LIMIT_X, LIMIT_Y = 15.0, 21.0
START = (0.0, -15.4)
EXIT = (0.0, 19.15)
PORTALS = ((0, 17.7), (-12.7, 15.0), (12.6, 17.2), (-12.8, -11), (12.7, -9.5))
WAVES = (5, 8, 11)


@dataclass(frozen=True)
class Prop:
    kind: str
    x: float
    y: float
    w: float
    d: float
    h: float
    tone: int = 0

    def bounds(self, margin=0):
        return (
            self.x - self.w / 2 - margin,
            self.x + self.w / 2 + margin,
            self.y - self.d / 2 - margin,
            self.y + self.d / 2 + margin,
        )


PROPS = (
    Prop("container", -8.4, -7.5, 3, 8.3, 3.0, 0),
    Prop("container", 8.4, -6, 3, 8.3, 3.0, 1),
    Prop("container", -7.5, 6, 8, 2.9, 2.95, 2),
    Prop("container", 8.6, 7.4, 3, 8.1, 2.95, 0),
    Prop("container", -9.0, 15.8, 4.7, 2.6, 2.7, 1),
    Prop("crate", 3.8, -2.3, 2.1, 2.1, 1.9),
    Prop("crate", 3.5, -0.15, 1.4, 1.7, 1.15),
    Prop("crate", -3.5, -1.8, 1.8, 1.8, 1.55),
    Prop("barrier", 2.9, 11.7, 4.0, 0.85, 1.16),
    Prop("barrier", -3.5, -13.5, 3.7, 0.9, 1.12),
    Prop("crate", -12.8, 2.4, 1.3, 1.4, 1.2),
    Prop("cache", -1.65, -18.8, 1.54, 0.83, 0.74),
    Prop("crate", 12.7, -14, 1.7, 1.7, 1.5),
)


def clear(x, y, radius=0.32, feet=0):
    if abs(x) > LIMIT_X - radius or abs(y) > LIMIT_Y - radius:
        return False
    for p in PROPS:
        if feet >= p.h - 0.003:
            continue
        a, b, c, d = p.bounds()
        dx = x - min(b, max(a, x))
        dy = y - min(d, max(c, y))
        if dx * dx + dy * dy < radius * radius:
            return False
    return True


def slide(x, y, dx, dy, radius=0.32, feet=0):
    for _ in range(steps := max(1, ceil(hypot(dx, dy) / 0.18))):
        if clear(x + dx / steps, y, radius, feet):
            x += dx / steps
        if clear(x, y + dy / steps, radius, feet):
            y += dy / steps
    return x, y


def support(x, y, feet, rad=0.3):
    highest = 0.0
    for p in PROPS:
        a, b, c, d = p.bounds(rad * 0.70)
        if a < x < b and c < y < d and p.h <= feet + 0.004:
            highest = max(highest, p.h)
    return highest


class Navigation:
    """One shared shortest-path field for every infected in the yard."""

    def __init__(self):
        self.cells = {
            (x, y) for x in range(-14, 15) for y in range(-20, 21) if clear(x, y, 0.51)
        }
        self.edges = {}
        for x, y in self.cells:
            self.edges[x, y] = [
                (x + dx, y + dy)
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                if (x + dx, y + dy) in self.cells
                and clear(x + dx * 0.5, y + dy * 0.5, 0.4)
            ]
        self.goal = None
        self.next = {}

    def nearest(self, x, y):
        p = (round(x), round(y))
        if p in self.cells:
            return p
        return min(self.cells, key=lambda c: (c[0] - x) ** 2 + (c[1] - y) ** 2)

    def aim(self, x, y):
        goal = self.nearest(x, y)
        if self.goal == goal:
            return
        self.goal = goal
        self.next = {goal: goal}
        queue = deque([goal])
        while queue:
            here = queue.popleft()
            for adj in self.edges[here]:
                if adj not in self.next:
                    self.next[adj] = here
                    queue.append(adj)

    def waypoint(self, x, y, px, py):
        a = self.nearest(x, y)
        b = self.next.get(a, a)
        if a == self.goal:
            return px, py
        # Aim at the middle of the cell before turning a tight corner.
        if not clear((x + b[0]) * 0.5, (y + b[1]) * 0.5, 0.37):
            return a
        return b


def wall_distance(origin, direction, maximum=100.0):
    """Nearest ray intersection with cover, the yard floor, or perimeter."""
    ox, oy, oz = origin
    vx, vy, vz = direction
    closest = maximum
    if vz < -1e-7:
        closest = min(closest, -oz / vz)
    for val, vel, limit in ((ox, vx, LIMIT_X), (oy, vy, LIMIT_Y)):
        if abs(vel) > 1e-7:
            t = ((limit if vel > 0 else -limit) - val) / vel
            if 0 < t < closest and 0 <= oz + t * vz <= 5.0:
                closest = t
    for p in PROPS:
        a, b, c, d = p.bounds()
        near, far = 0.0, closest
        for value, vel, lo, hi in ((ox, vx, a, b), (oy, vy, c, d), (oz, vz, 0, p.h)):
            if abs(vel) < 1e-8:
                if not lo <= value <= hi:
                    far = -1
                    break
            else:
                t1, t2 = (lo - value) / vel, (hi - value) / vel
                near = max(near, min(t1, t2))
                far = min(far, max(t1, t2))
        if near <= far:
            closest = near
    return closest

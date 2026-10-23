"""Small, dependency-free vector exploration primitives for Economic-series exploration primitives: track indicator movement vectors, flag sharp directional changes using an angle threshold, and raycast across a bounded 2D indicator grid..

These are generic analytical utilities, not a replacement for domain-specific validation.
Raycasting uses a 2D occupancy grid where True means blocked.
"""
from __future__ import annotations

from math import acos, degrees, hypot
from typing import Iterable, Sequence

Point2 = tuple[float, float]
Vector2 = tuple[float, float]


def vector_track(points: Iterable[Sequence[float]]) -> list[dict[str, float]]:
    """Return segment vectors, magnitudes, and cumulative path distance.

    Each point must contain exactly two finite numeric coordinates.
    """
    coords: list[Point2] = []
    for point in points:
        if len(point) != 2:
            raise ValueError("each point must contain exactly two coordinates")
        x, y = float(point[0]), float(point[1])
        if not (x == x and y == y) or abs(x) == float("inf") or abs(y) == float("inf"):
            raise ValueError("coordinates must be finite")
        coords.append((x, y))

    result: list[dict[str, float]] = []
    distance = 0.0
    for index in range(1, len(coords)):
        dx = coords[index][0] - coords[index - 1][0]
        dy = coords[index][1] - coords[index - 1][1]
        magnitude = hypot(dx, dy)
        distance += magnitude
        result.append({
            "index": float(index),
            "dx": dx,
            "dy": dy,
            "magnitude": magnitude,
            "distance": distance,
        })
    return result


def angle_between_degrees(a: Sequence[float], b: Sequence[float]) -> float:
    """Return the unsigned angle [0, 180] between two 2D vectors."""
    if len(a) != 2 or len(b) != 2:
        raise ValueError("vectors must each contain exactly two coordinates")
    ax, ay, bx, by = float(a[0]), float(a[1]), float(b[0]), float(b[1])
    ma, mb = hypot(ax, ay), hypot(bx, by)
    if ma == 0 or mb == 0:
        raise ValueError("angle is undefined for a zero-length vector")
    cosine = max(-1.0, min(1.0, (ax * bx + ay * by) / (ma * mb)))
    return degrees(acos(cosine))


def angle_threshold_events(vectors: Iterable[Sequence[float]], threshold_degrees: float = 45.0) -> list[dict[str, float | int]]:
    """Report adjacent vector pairs whose turn angle meets/exceeds threshold."""
    if not 0.0 <= float(threshold_degrees) <= 180.0:
        raise ValueError("threshold_degrees must be between 0 and 180")
    raw_vectors = list(vectors)
    if any(len(v) != 2 for v in raw_vectors):
        raise ValueError("vectors must each contain exactly two coordinates")
    values = [(float(v[0]), float(v[1])) for v in raw_vectors]
    events: list[dict[str, float | int]] = []
    for index in range(1, len(values)):
        if hypot(*values[index - 1]) == 0 or hypot(*values[index]) == 0:
            continue
        angle = angle_between_degrees(values[index - 1], values[index])
        if angle >= threshold_degrees:
            events.append({"index": index, "angle_degrees": angle})
    return events


def raycast_grid(
    grid: Sequence[Sequence[bool]],
    origin: tuple[int, int],
    direction: Vector2,
    max_steps: int = 100,
) -> dict[str, int | bool | None]:
    """Step through a grid along a normalized direction until blocked/out of bounds.

    Returns the last in-bounds cell, the number of steps, and whether a blocker
    was hit. Grid rows are indexed y, columns x; True cells are obstacles.
    """
    if not grid or not grid[0] or any(len(row) != len(grid[0]) for row in grid):
        raise ValueError("grid must be a non-empty rectangle")
    if max_steps < 0:
        raise ValueError("max_steps must be non-negative")
    dx, dy = float(direction[0]), float(direction[1])
    if hypot(dx, dy) == 0:
        raise ValueError("direction must be non-zero")
    x, y = int(origin[0]), int(origin[1])
    width, height = len(grid[0]), len(grid)
    if not (0 <= x < width and 0 <= y < height):
        raise ValueError("origin must be inside the grid")
    sx, sy = dx / hypot(dx, dy), dy / hypot(dx, dy)
    last_x, last_y = x, y
    for step in range(1, max_steps + 1):
        nx, ny = round(origin[0] + sx * step), round(origin[1] + sy * step)
        if not (0 <= nx < width and 0 <= ny < height):
            return {"x": last_x, "y": last_y, "steps": step - 1, "hit": False}
        if grid[ny][nx]:
            return {"x": nx, "y": ny, "steps": step, "hit": True}
        last_x, last_y = nx, ny
    return {"x": last_x, "y": last_y, "steps": max_steps, "hit": False}

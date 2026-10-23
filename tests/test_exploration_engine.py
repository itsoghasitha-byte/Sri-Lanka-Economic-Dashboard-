import math
import pytest

from exploration_engine import (
    angle_between_degrees,
    angle_threshold_events,
    raycast_grid,
    vector_track,
)


def test_vector_track_tracks_delta_and_cumulative_distance():
    result = vector_track([(0, 0), (3, 4), (6, 4)])
    assert result[0]["magnitude"] == pytest.approx(5)
    assert result[0]["distance"] == pytest.approx(5)
    assert result[1]["dx"] == pytest.approx(3)
    assert result[1]["distance"] == pytest.approx(8)


def test_vector_track_empty_and_single_point():
    assert vector_track([]) == []
    assert vector_track([(2, 3)]) == []


def test_vector_track_rejects_bad_coordinates():
    with pytest.raises(ValueError):
        vector_track([(1, 2, 3)])
    with pytest.raises(ValueError):
        vector_track([(float("inf"), 0)])


def test_angle_between_perpendicular_vectors():
    assert angle_between_degrees((1, 0), (0, 1)) == pytest.approx(90)


def test_angle_threshold_events_detects_turn():
    events = angle_threshold_events([(1, 0), (0, 1), (0, 1)], 60)
    assert len(events) == 1
    assert events[0]["index"] == 1
    assert events[0]["angle_degrees"] == pytest.approx(90)


def test_angle_threshold_validation_and_zero_vectors():
    with pytest.raises(ValueError):
        angle_threshold_events([(1, 0)], 181)
    with pytest.raises(ValueError):
        angle_between_degrees((0, 0), (1, 0))


def test_raycast_hits_obstacle():
    grid = [
        [False, False, False, False],
        [False, False, True, False],
        [False, False, False, False],
    ]
    result = raycast_grid(grid, (0, 1), (1, 0), 10)
    assert result == {"x": 2, "y": 1, "steps": 2, "hit": True}


def test_raycast_stops_at_boundary_and_validates_inputs():
    grid = [[False, False], [False, False]]
    assert raycast_grid(grid, (0, 0), (1, 0), 10)["hit"] is False
    with pytest.raises(ValueError):
        raycast_grid(grid, (0, 0), (0, 0))
    with pytest.raises(ValueError):
        raycast_grid([], (0, 0), (1, 0))

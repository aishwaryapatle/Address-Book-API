
import pytest

from app.utils.geo import calculate_distance


def test_same_coordinates_return_zero():
    distance = calculate_distance(
        18.5204, 73.8567,
        18.5204, 73.8567,
    )

    assert distance == pytest.approx(0.0)


def test_distance_between_known_locations():
    # Approximate distance between Pune and Mumbai.
    distance = calculate_distance(
        18.5204, 73.8567,
        19.0760, 72.8777,
    )

    assert distance == pytest.approx(120.5, abs=1.0)


def test_distance_is_symmetric():
    distance_one = calculate_distance(
        18.5204, 73.8567,
        19.0760, 72.8777,
    )

    distance_two = calculate_distance(
        19.0760, 72.8777,
        18.5204, 73.8567,
    )

    assert distance_one == pytest.approx(distance_two)


def test_date_line_coordinates():
    # Points on opposite sides of the International Date Line.
    distance = calculate_distance(
        0.0, 179.9,
        0.0, -179.9,
    )

    assert distance == pytest.approx(22.24, abs=0.2)
